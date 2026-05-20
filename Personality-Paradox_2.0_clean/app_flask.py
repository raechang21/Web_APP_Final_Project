"""
Flask 版本的 Personality Paradox 應用程式
使用 Flask + htmx + Bootstrap 5
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, Response, stream_with_context
import json
import os
import ollama
from datetime import datetime, timedelta

# 引入現有模組
from models.user_profile import UserProfile
from models.test_result import MBTIResult, BigFiveResult, ZodiacResult
from models.dark_triad_result import DarkTriadResult
from utils.data_loader import load_bigfive_questions, load_dark_triad_questions
from analysis.scoring import calculate_bigfive_scores, calculate_dark_triad_scores
from llm.ollama_client import OllamaClient
from llm.prompt_templates import PromptTemplates
from llm.chatbot_prompts import ChatBotPrompts

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # 生產環境請更改
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# 初始化伺服器端 session
from flask_session import Session
Session(app)

# 初始化 Ollama 客戶端
ollama_client = OllamaClient()

# ========== 首頁路由 ==========
@app.route('/')
def index():
    """歡迎頁面"""
    return render_template('welcome.html')

# ========== 快速登入路由 ==========
@app.route('/quick_login', methods=['POST'])
def quick_login():
    """快速登入 - 檢查用戶是否有完整測驗記錄"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({
                'success': False,
                'message': '請輸入名字'
            }), 400
        
        # 檢查記憶檔案是否存在
        memory_file = os.path.join('data', 'chat_histories', f'{name}_memory.json')
        
        if not os.path.exists(memory_file):
            return jsonify({
                'success': False,
                'message': f'找不到「{name}」的測驗記錄，請先完成測驗'
            })
        
        # 載入記憶檔案並檢查是否有完整的測驗結果
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # 檢查必要的測驗結果
            has_mbti = memory_data.get('mbti') is not None
            has_bigfive = memory_data.get('bigfive_scores') is not None
            
            if not has_mbti or not has_bigfive:
                return jsonify({
                    'success': False,
                    'message': f'「{name}」的測驗記錄不完整，請重新完成測驗'
                })
            
            # 載入測驗結果到 session
            session['user_name'] = name
            session['mbti'] = memory_data.get('mbti')
            session['bigfive_scores'] = memory_data.get('bigfive_scores')
            session['zodiac'] = memory_data.get('zodiac')
            session['dark_triad_scores'] = memory_data.get('dark_triad_scores')
            session['chat_messages'] = []  # 清空對話記錄
            session['quick_login'] = True  # 標記為快速登入
            
            # 生成歡迎回來訊息
            welcome_message = f"嗨，{name}，歡迎回來！很高興再次見到你。"
            
            # 如果有上次對話記錄，表達關心
            summaries = memory_data.get('conversation_summaries', [])
            if summaries and len(summaries) > 0:
                last_conversation = summaries[-1]
                last_topics = last_conversation.get('topics', [])
                if last_topics:
                    # 取第一個主題作為關心的內容
                    first_topic = last_topics[0]
                    # 簡化主題內容（取前20字）
                    topic_preview = first_topic[:20] + '...' if len(first_topic) > 20 else first_topic
                    
                    # 根據主題類型決定後續問候語
                    follow_up = ""
                    if '？' in first_topic or '?' in first_topic:
                        # 提問型：用戶問問題，詢問是否有嘗試或想法
                        follow_up = "有試著做看看嗎？"
                    elif any(word in first_topic for word in ['被罵', '難過', '生氣', '傷心', '困擾', '壓力', '焦慮', '煩惱', '挫折', '失望', '沮喪']):
                        # 情緒型：負面情緒或困擾，詢問後續狀況
                        follow_up = "後來還好嗎？"
                    elif any(word in first_topic for word in ['不好', '不開心', '不舒服', '痛苦', '難受']):
                        # 負面狀態：詢問改善情況
                        follow_up = "現在好一點了嗎？"
                    else:
                        # 一般陳述：用較中性的問候
                        follow_up = "後來怎麼樣了？"
                    
                    welcome_message += f" 我記得上次你提到『{topic_preview}』，{follow_up}"
            else:
                welcome_message += " 今天想聊什麼呢？"
            
            session['welcome_message'] = welcome_message
            session.modified = True
            
            print(f"✅ 快速登入成功: {name}")
            
            return jsonify({
                'success': True,
                'message': f'歡迎回來，{name}！',
                'redirect': url_for('chatbot')
            })
            
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'message': f'「{name}」的記錄檔案損壞，請重新完成測驗'
            })
        except Exception as e:
            print(f"❌ 載入記憶檔案失敗: {e}")
            return jsonify({
                'success': False,
                'message': '載入記錄時發生錯誤，請稍後再試'
            })
    
    except Exception as e:
        print(f"❌ 快速登入處理失敗: {e}")
        return jsonify({
            'success': False,
            'message': '發生錯誤，請稍後再試'
        }), 500

# ========== MBTI 輸入頁面 ==========
@app.route('/mbti', methods=['GET', 'POST'])
def mbti_input():
    """MBTI 類型輸入"""
    if request.method == 'POST':
        mbti_type = request.form.get('mbti_type', '').upper().strip()
        
        # 驗證 MBTI 類型
        valid_types = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 
                      'INFJ', 'INFP', 'ENFJ', 'ENFP',
                      'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 
                      'ISTP', 'ISFP', 'ESTP', 'ESFP']
        
        if mbti_type in valid_types:
            session['mbti'] = mbti_type
            return redirect(url_for('bigfive_test'))
        else:
            return render_template('mbti_input.html', error='請輸入有效的 MBTI 類型')
    
    return render_template('mbti_input.html')

# ========== Big Five 測驗 ==========
@app.route('/bigfive', methods=['GET', 'POST'])
def bigfive_test():
    """Big Five 人格測驗"""
    if 'mbti' not in session:
        return redirect(url_for('mbti_input'))
    
    if request.method == 'POST':
        # 收集答案
        answers = {}
        questions, scale_labels = load_bigfive_questions()
        
        for q in questions:
            answer = request.form.get(f"q_{q['id']}")
            if answer:
                answers[q['id']] = int(answer)
        
        # 計算分數
        if len(answers) == len(questions):
            scores = calculate_bigfive_scores(answers, questions)
            session['bigfive_scores'] = scores
            return redirect(url_for('zodiac_selection'))
        else:
            return render_template('bigfive_test.html', 
                                 questions=questions,
                                 error='請回答所有問題')
    
    questions, scale_labels = load_bigfive_questions()
    return render_template('bigfive_test.html', questions=questions)

# ========== 星座選擇 ==========
@app.route('/zodiac', methods=['GET', 'POST'])
def zodiac_selection():
    """星座選擇"""
    if 'bigfive_scores' not in session:
        return redirect(url_for('bigfive_test'))
    
    if request.method == 'POST':
        zodiac = request.form.get('zodiac')
        if zodiac:
            session['zodiac'] = zodiac
            return redirect(url_for('dark_triad_intro'))
    
    zodiacs = ['牡羊座', '金牛座', '雙子座', '巨蟹座', '獅子座', '處女座',
               '天秤座', '天蠍座', '射手座', '摩羯座', '水瓶座', '雙魚座']
    return render_template('zodiac_selection.html', zodiacs=zodiacs)

# ========== 黑暗三角介紹 ==========
@app.route('/dark-triad-intro')
def dark_triad_intro():
    """黑暗三角測驗介紹頁面"""
    if 'zodiac' not in session:
        return redirect(url_for('zodiac_selection'))
    
    return render_template('dark_triad_intro.html')

# ========== 黑暗三角測驗 ==========
@app.route('/dark-triad', methods=['GET', 'POST'])
def dark_triad_test():
    """黑暗三角人格測驗"""
    if 'zodiac' not in session:
        return redirect(url_for('zodiac_selection'))
    
    if request.method == 'POST':
        answers = {}
        questions = load_dark_triad_questions()
        
        for q in questions:
            answer = request.form.get(f"q_{q['id']}")
            if answer:
                answers[q['id']] = int(answer)
        
        if len(answers) == len(questions):
            scores = calculate_dark_triad_scores(answers, questions)
            session['dark_triad_scores'] = scores
            return redirect(url_for('results'))
    
    questions = load_dark_triad_questions()
    return render_template('dark_triad_test.html', questions=questions)

# ========== 跳過黑暗三角測驗 ==========
@app.route('/skip-dark-triad')
def skip_dark_triad():
    """跳過黑暗三角測驗"""
    session['dark_triad_scores'] = None
    return redirect(url_for('results'))

# ========== 結果頁面 ==========
@app.route('/results')
def results():
    """顯示測驗結果（四種人格測驗分析）"""
    if 'mbti' not in session or 'bigfive_scores' not in session or 'zodiac' not in session:
        return redirect(url_for('index'))
    
    # 準備數據
    mbti = session.get('mbti')
    bigfive_scores = session.get('bigfive_scores')
    zodiac = session.get('zodiac')
    dark_triad_scores = session.get('dark_triad_scores')
    
    # 生成分析（如果尚未生成）
    if 'analysis' not in session:
        print("📊 開始生成分析...")
        
        # 使用模板獲取 MBTI 和星座分析（快速）
        mbti_analysis = PromptTemplates.get_mbti_template(mbti)
        zodiac_analysis = PromptTemplates.get_zodiac_template(zodiac)
        bigfive_analysis = PromptTemplates.get_bigfive_template(bigfive_scores)
        print("✅ MBTI、星座、Big Five 分析完成")
        
        # 使用模板獲取黑暗三角分析（如果有數據）
        dark_triad_analysis = None
        if dark_triad_scores:
            print("📋 使用模板生成黑暗三角分析...")
            dark_triad_analysis = PromptTemplates.get_dark_triad_template(dark_triad_scores)
            print("✅ 黑暗三角分析完成")
        
        print("💾 儲存分析結果到 session")
        session['analysis'] = {
            'mbti': mbti_analysis,
            'bigfive': bigfive_analysis,
            'zodiac': zodiac_analysis,
            'dark_triad': dark_triad_analysis
        }
    
    # 顯示測驗結果頁面
    return render_template('results.html',
                         mbti=mbti,
                         bigfive_scores=bigfive_scores,
                         zodiac=zodiac,
                         dark_triad_scores=dark_triad_scores,
                         analysis=session.get('analysis'))

@app.route('/deep-analysis')
def deep_analysis():
    """顯示綜合分析頁面"""
    if 'mbti' not in session or 'bigfive_scores' not in session or 'zodiac' not in session:
        return redirect(url_for('index'))
    
    # 標記用戶已查看綜合分析
    session['viewed_deep_analysis'] = True
    
    # 準備數據
    mbti = session.get('mbti')
    bigfive_scores = session.get('bigfive_scores')
    zodiac = session.get('zodiac')
    dark_triad_scores = session.get('dark_triad_scores')
    analysis = session.get('analysis', {})
    
    # 檢查是否已有綜合分析
    has_analysis = 'comprehensive' in analysis
    
    return render_template('deep_analysis.html',
                         mbti=mbti,
                         bigfive_scores=bigfive_scores,
                         zodiac=zodiac,
                         dark_triad_scores=dark_triad_scores,
                         analysis=analysis,
                         has_analysis=has_analysis)

# ========== API: 生成綜合分析 ==========
@app.route('/api/generate-comprehensive-analysis', methods=['GET'])
def api_generate_comprehensive_analysis():
    """生成綜合分析(SSE 串流)"""
    if 'mbti' not in session or 'bigfive_scores' not in session:
        return jsonify({'error': '缺少測驗數據'}), 400
    
    mbti = session.get('mbti')
    bigfive_scores = session.get('bigfive_scores')
    zodiac = session.get('zodiac')
    dark_triad_scores = session.get('dark_triad_scores')
    
    # 構建測驗結果文字,並加入高低判斷
    def interpret_score(score):
        """將分數轉換為描述性詞彙"""
        if score <= 2.0:
            return "極低"
        elif score <= 3.0:
            return "偏低"
        elif score <= 4.0:
            return "中等"
        elif score <= 5.0:
            return "偏高"
        else:
            return "極高"
    
    # 構建 Big Five 分數解讀(內部分析用)
    bigfive_analysis = {
        'openness': interpret_score(bigfive_scores['openness']),
        'conscientiousness': interpret_score(bigfive_scores['conscientiousness']),
        'extraversion': interpret_score(bigfive_scores['extraversion']),
        'agreeableness': interpret_score(bigfive_scores['agreeableness']),
        'neuroticism': interpret_score(bigfive_scores['neuroticism'])
    }
    
    dark_triad_analysis = {}
    dark_triad_text = ""
    if dark_triad_scores:
        dark_triad_analysis = {
            'machiavellianism': interpret_score(dark_triad_scores['machiavellianism']),
            'narcissism': interpret_score(dark_triad_scores['narcissism']),
            'psychopathy': interpret_score(dark_triad_scores['psychopathy'])
        }
        dark_triad_text = f"""
- 黑暗三角特質：
  · 馬基維利主義：{dark_triad_scores['machiavellianism']:.1f}/6.0
  · 自戀：{dark_triad_scores['narcissism']:.1f}/6.0
  · 心理病態：{dark_triad_scores['psychopathy']:.1f}/6.0
"""
    
    comprehensive_prompt = f"""你是專業的心理學分析師。基於以下人格測驗結果，請撰寫一篇整合性分析。

【測驗結果】
- MBTI 類型：{mbti}
- Big Five 人格特質：
  · 開放性：{bigfive_scores['openness']:.1f}/6.0
  · 盡責性：{bigfive_scores['conscientiousness']:.1f}/6.0
  · 外向性：{bigfive_scores['extraversion']:.1f}/6.0
  · 友善性：{bigfive_scores['agreeableness']:.1f}/6.0
  · 神經質：{bigfive_scores['neuroticism']:.1f}/6.0
- 星座：{zodiac}{dark_triad_text}

【分數判讀標準】（僅供你內部分析使用，不要在回答中顯示此標準）
根據上述分數，實際程度判讀如下：
- 開放性: {bigfive_analysis['openness']}
- 盡責性: {bigfive_analysis['conscientiousness']}
- 外向性: {bigfive_analysis['extraversion']}
- 友善性: {bigfive_analysis['agreeableness']}
- 神經質: {bigfive_analysis['neuroticism']}"""
    
    if dark_triad_scores:
        comprehensive_prompt += f"""
- 馬基維利主義: {dark_triad_analysis['machiavellianism']}
- 自戀: {dark_triad_analysis['narcissism']}
- 心理病態: {dark_triad_analysis['psychopathy']}"""
    
    comprehensive_prompt += """

判讀規則: ≤2.0=極低 | 2.1-3.0=偏低 | 3.1-4.0=中等 | 4.1-5.0=偏高 | >5.0=極高

【分析要求】
1. **使用第二人稱「你」**：全文以「你」稱呼
2. **必須整合所有測驗結果**：
   - 開頭先從「MBTI 類型」切入，簡述該類型的核心特徵
   - 接著用 Big Five 分數來「驗證」或「補充」MBTI 的描述
   - 提及「星座」特質如何與上述結果相呼應或產生矛盾
   - 若有黑暗三角數據，分析其如何影響整體人格表現
3. **嚴格依照「分數判讀標準」描述 Big Five 特質高低**：例如外向性若判讀為「極低」，必須描述為「極低的外向性」或「高度內向」，絕對不可說「中等外向性」
4. **聚焦於不同測驗結果之間的「呼應」與「矛盾」**：例如 MBTI 的 I/E 是否與外向性分數一致？星座特質是否與 Big Five 衝突？
5. **不要在文中提及具體分數**：避免寫出「1.0/6.0」等數值
6. **嚴格控制字數在 400-450 字以內**

【禁止事項】
✗ 不要使用「這位客人」「該受測者」等第三人稱
✗ 不要在分析文中寫出具體分數
✗ 不要誤判分數高低（務必參考「分數判讀標準」）
✗ 不要只分析 Big Five 而忽略 MBTI 和星座
✗ 不要分段標題
✗ 不要超過 450 字
✗ 絕對不要使用任何 Markdown 格式（包括 * 粗體、** 斜體、# 標題、- 列表等）

請直接開始分析，用流暢的段落形式書寫，使用純文字不要任何格式標記。"""
    
    def clean_markdown(text: str) -> str:
        """移除 Markdown 格式標記"""
        import re
        # 移除粗體標記 **text** 或 __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        # 移除斜體標記 *text* 或 _text_
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # 移除開頭的列表標記
        text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
        # 移除標題標記
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 移除行首的獨立星號或破折號
        text = re.sub(r'^\s*[\*\-]\s*\*\*', '', text, flags=re.MULTILINE)
        return text
    
    def generate():
        """SSE 生成器"""
        full_analysis = ""
        try:
            # 使用更大的 token 限制
            response = ollama.generate(
                model='gemma3:4b',
                prompt=comprehensive_prompt,
                system="你是一位專業的心理學分析師。請使用繁體中文，提供完整且深入的分析。確保所有分析段落都完整輸出。回應時請使用純文字，不要使用任何 Markdown 格式標記（如 *, **, _, #, - 等）。",
                stream=True,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2048  # 增加到 2048 tokens
                }
            )
            
            for chunk in response:
                if 'response' in chunk:
                    # 清理 Markdown 格式
                    text = clean_markdown(chunk['response'])
                    full_analysis += text
                    yield f"data: {json.dumps({'chunk': text})}\n\n"
            
            # 保存到 session
            analysis = session.get('analysis', {})
            analysis['comprehensive'] = full_analysis
            session['analysis'] = analysis
            session.modified = True
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

# ========== API: 獲取圖表數據 ==========
@app.route('/api/bigfive-chart')
def api_bigfive_chart():
    """返回 Big Five 雷達圖 JSON 數據"""
    if 'bigfive_scores' not in session:
        return jsonify({'error': 'No data'}), 404
    
    scores = session.get('bigfive_scores')
    
    # 構建 Plotly 圖表數據
    chart_data = {
        'data': [{
            'type': 'scatterpolar',
            'r': [scores['openness'], scores['conscientiousness'], 
                  scores['extraversion'], scores['agreeableness'], 
                  scores['neuroticism']],
            'theta': ['開放性', '盡責性', '外向性', '友善性', '神經質'],
            'fill': 'toself',
            'name': 'Big Five'
        }],
        'layout': {
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, 6],
                    'tickvals': [1, 2, 3, 4, 5, 6]
                }
            },
            'showlegend': False,
            'title': 'Big Five 人格特質'
        }
    }
    
    return jsonify(chart_data)

# ==========  頁面 ==========
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    """心理諮商助手對話頁面"""
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            # 第一次：詢問名字
            if 'name' not in session:
                session['name'] = user_message
                response_message = "你好！我是你的心理諮商小助手 😊\n很高興能在這裡與你相遇。\n在開始對話之前，想請問你叫什麼名字呢？😊😊"
                return jsonify({
                    'user_message': user_message,
                    'response_message': response_message
                })
            else:
                # 第二次：回應姓名，只說一次很高興認識你
                name = session['name']
                if session.get('greeted_name') != True:
                    response_message = f"很高興認識你，{name}！我們可以從你今天想談的任何地方開始，你現在最想讓我知道的是什麼呢？"
                    session['greeted_name'] = True
                else:
                    response_message = f"{name}你好！我們可以從你今天想談的任何地方開始，你現在最想讓我知道的是什麼呢？"
                return jsonify({
                    'user_message': user_message,
                    'response_message': response_message
                })

    # GET 請求：判斷是否有測驗結果
    has_results = 'mbti' in session and 'bigfive_scores' in session and 'zodiac' in session
    user_persona = None
    if has_results:
        user_persona = {
            'mbti': {'type': session.get('mbti')},
            'bigfive': session.get('bigfive_scores'),
            'zodiac': {'sign': session.get('zodiac')}
        }
    
    # 檢查是否為快速登入
    is_quick_login = session.get('quick_login', False)
    welcome_message = session.get('welcome_message', None)
    user_name = session.get('user_name', None)
    
    # 獲取聊天記錄（如果有）
    messages = session.get('chat_messages', [])
    
    # 如果是快速登入，不清空 user_name，並保留歡迎訊息
    # 如果不是快速登入但已有用戶名，保留 user_name 和 chat_messages（避免 F5 重新詢問名字）
    if not is_quick_login:
        # 只在沒有用戶名時才清空聊天記錄
        if not user_name and 'chat_messages' in session:
            del session['chat_messages']
            messages = []
        session.modified = True
    else:
        # 快速登入後，清除標記（避免重複使用）
        if 'quick_login' in session:
            del session['quick_login']
        if 'welcome_message' in session:
            del session['welcome_message']
        session.modified = True
    
    # 導入 datetime 以提供當前時間
    from datetime import datetime
    now = datetime.now()
    # Debug: 印出 chat page 重要變數以便排查前端無訊息問題
    print("[ChatBot DEBUG] Rendering /chatbot: ")
    try:
        print(f"[ChatBot DEBUG] has_results={has_results}, is_quick_login={is_quick_login}, user_name={user_name}, welcome_message={welcome_message}")
        print(f"[ChatBot DEBUG] messages_count={len(messages) if messages is not None else 0}")
    except Exception as e:
        print(f"[ChatBot DEBUG] Error printing debug info: {e}")
    
    return render_template('chatbot.html', 
                         has_results=has_results, 
                         user_persona=user_persona,
                         is_quick_login=is_quick_login,
                         welcome_message=welcome_message,
                         user_name=user_name,
                         messages=messages,
                         now=now)

# ========== ChatBot SSE 串流 ==========
@app.route('/chatbot/stream', methods=['POST'])
def chatbot_stream():
    """SSE 串流端點 - 即時回應"""
    print(f"[ChatBot] ========== 收到 POST 請求 ==========")
    print(f"[ChatBot] Request Method: {request.method}")
    print(f"[ChatBot] Request Path: {request.path}")
    print(f"[ChatBot] Content-Type: {request.content_type}")
    
    try:
        print(f"[ChatBot] 正在解析 JSON...")
        data = request.get_json()
        print(f"[ChatBot] 解析成功，資料: {data}")
        user_message = data.get('message', '').strip()
        print(f"[ChatBot] 提取訊息: '{user_message}'")
        
        if not user_message:
            print(f"[ChatBot] 錯誤：訊息為空")
            return jsonify({'error': 'Empty message'}), 400
        
        print(f"[ChatBot] 收到訊息: {user_message}")
        
        # 檢查是否為首次對話(詢問名字)
        user_name = session.get('user_name')
        chat_history = session.get('chat_messages', [])
        
        # ========== 新邏輯：首次對話直接視為名字，用資料庫判斷新舊用戶 ==========
        if len(chat_history) == 0 and not user_name:
            # 首次對話，直接將輸入視為名字（保留大小寫，不同大小寫視為不同用戶）
            potential_name = user_message.strip()
            memory_file = os.path.join('data', 'chat_histories', f'{potential_name}_memory.json')
            is_returning_user = os.path.exists(memory_file)
            
            print(f"[ChatBot] 首次對話，輸入視為名字: {potential_name}")
            print(f"[ChatBot] 檢查記憶檔案: {memory_file}")
            print(f"[ChatBot] 是舊用戶: {is_returning_user}")
            
            if is_returning_user:
                # 舊用戶回來了 - 載入記憶並歡迎
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memory_data = json.load(f)
                    
                    # 設定 session
                    session['user_name'] = potential_name
                    session['mbti'] = memory_data.get('mbti')
                    session['bigfive_scores'] = memory_data.get('bigfive_scores')
                    session['zodiac'] = memory_data.get('zodiac')
                    session['dark_triad_scores'] = memory_data.get('dark_triad_scores')
                    session['chat_messages'] = []
                    session.modified = True
                    
                    # 歡迎回來訊息 (加入對上次對話的關心)
                    welcome_back_message = f"嗨，{potential_name}，歡迎回來！很高興再次見到你。"
                    
                    # 如果有上次對話記錄，表達關心
                    summaries = memory_data.get('conversation_summaries', [])
                    if summaries and len(summaries) > 0:
                        last_conversation = summaries[-1]
                        last_topics = last_conversation.get('topics', [])
                        if last_topics:
                            # 取第一個主題作為關心的內容
                            first_topic = last_topics[0]
                            # 簡化主題內容（取前20字）
                            topic_preview = first_topic[:20] + '...' if len(first_topic) > 20 else first_topic
                            welcome_back_message += f" 我記得上次你提到『{topic_preview}』，後來還好嗎？"
                    else:
                        welcome_back_message += " 今天想聊什麼呢？"
                    
                    # 不將名字加入歷史，保持歷史為空
                    # 這樣AI不會看到"soh"並誤以為是對話內容
                    session.modified = True
                    
                    print(f"[ChatBot] 舊用戶 {potential_name} 回來了，已載入記憶")
                    
                    def generate_welcome_back():
                        yield f"data: {json.dumps({'chunk': welcome_back_message}, ensure_ascii=False)}\n\n"
                        yield f"data: {json.dumps({'done': True})}\n\n"
                    
                    return Response(generate_welcome_back(), mimetype='text/event-stream')
                    
                except Exception as e:
                    print(f"[ChatBot] 載入 {potential_name} 記憶失敗: {e}")
                    # 載入失敗，當作新用戶處理
            
            # 新用戶 - 直接開啟新對話
            user_name = potential_name
            session['user_name'] = user_name
            session.modified = True
            
            # 固定的回應訊息
            welcome_message = f"嗨，{user_name}，歡迎你來這裡。今天想聊什麼呢？"
            
            # 不將名字加入歷史，避免AI誤解
            # 歷史保持為空，從下一則訊息開始記錄
            session['chat_messages'] = []
            session.modified = True
            
            print(f"[ChatBot] 新用戶 {user_name}，開啟新對話")
            
            # 使用 SSE 格式返回
            def generate_welcome():
                yield f"data: {json.dumps({'chunk': welcome_message}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(generate_welcome(), mimetype='text/event-stream')
        
        # ========== 正常對話流程（已有用戶名） ==========
        mbti = session.get('mbti')
        bigfive_scores = session.get('bigfive_scores')
        zodiac = session.get('zodiac')
        dark_triad_scores = session.get('dark_triad_scores')
        
        print(f"[ChatBot] MBTI: {mbti}, Big Five: {bigfive_scores is not None}")
        print(f"[ChatBot] Big Five 詳細分數: {bigfive_scores}")
        
        # 構建結果對象（添加容錯處理）
        mbti_result = MBTIResult(type=mbti) if mbti else None
        
        # Big Five 分數驗證與容錯
        bigfive_result = None
        if bigfive_scores:
            try:
                bigfive_result = BigFiveResult(**bigfive_scores)
            except ValueError as e:
                print(f"[ChatBot] Big Five 驗證失敗: {e}")
                print(f"[ChatBot] 嘗試修正分數範圍...")
                # 修正超出範圍的分數
                corrected_scores = {}
                for key, value in bigfive_scores.items():
                    if value < 0.0:
                        corrected_scores[key] = 0.0
                    elif value > 7.0:
                        corrected_scores[key] = 7.0
                    else:
                        corrected_scores[key] = value
                print(f"[ChatBot] 修正後分數: {corrected_scores}")
                bigfive_result = BigFiveResult(**corrected_scores)
        
        zodiac_result = ZodiacResult(sign=zodiac) if zodiac else None
        dark_triad_result = DarkTriadResult(**dark_triad_scores) if dark_triad_scores else None
        
        # 使用完整版諮商 prompt (從第二次訊息開始就提供完整諮商服務)
        system_prompt = ChatBotPrompts.system_prompt_with_results(
            mbti=mbti_result,
            bigfive=bigfive_result,
            zodiac=zodiac_result,
            dark_triad=dark_triad_result
        )
        
        # Debug: 打印 BigFive 資料和完整 system_prompt
        if bigfive_result:
            print(f"\n[DEBUG] BigFive 測驗結果:")
            print(f"  - 開放性: {bigfive_result.openness:.1f}")
            print(f"  - 盡責性: {bigfive_result.conscientiousness:.1f}")
            print(f"  - 外向性: {bigfive_result.extraversion:.1f}")
            print(f"  - 友善性: {bigfive_result.agreeableness:.1f}")
            print(f"  - 神經質: {bigfive_result.neuroticism:.1f}")
        
        print(f"\n[DEBUG] System Prompt 中的個案資料部分:")
        if "【個案資料" in system_prompt:
            start_idx = system_prompt.find("【個案資料")
            end_idx = system_prompt.find("【如何運用測驗資料", start_idx)
            if end_idx > start_idx:
                print(system_prompt[start_idx:end_idx])
        
        # ========== 檢測是否為分數查詢問題（方案3）==========
        def check_score_query(message: str):
            """檢測用戶是否在查詢測驗分數"""
            import re
            
            # 查詢關鍵字模式
            query_patterns = [
                r'(我的|我|自己的?)(.{0,3})(開放性|盡責性|外向性|友善性|神經質|conscientiousness|openness|extraversion|agreeableness|neuroticism)(.{0,5})(是?幾分|多少分|分數|是多少)',
                r'(開放性|盡責性|外向性|友善性|神經質)(.{0,3})(幾分|多少|分數)',
                r'(測驗結果|分數|成績)(.{0,3})(是什麼|是多少|代表什麼)',
            ]
            
            for pattern in query_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return True
            return False
        
        def generate_score_response(bigfive_result, mbti_result, zodiac_result):
            """直接生成分數回答，不經過LLM"""
            response = ""
            
            # 如果問題明確提到某個特質
            trait_map = {
                '開放性': ('openness', '開放性'),
                '盡責性': ('conscientiousness', '盡責性'),
                '外向性': ('extraversion', '外向性'),
                '友善性': ('agreeableness', '友善性'),
                '神經質': ('neuroticism', '神經質')
            }
            
            # 檢查用戶問的是哪個特質
            asked_trait = None
            for trait_name in trait_map.keys():
                if trait_name in user_message:
                    asked_trait = trait_name
                    break
            
            if asked_trait and bigfive_result:
                attr_name, display_name = trait_map[asked_trait]
                score = getattr(bigfive_result, attr_name)
                
                # 解讀分數
                if score <= 2.0:
                    level = "極低"
                    desc = "相對較少"
                elif score <= 3.0:
                    level = "偏低"
                    desc = "中等偏少"
                elif score <= 4.0:
                    level = "中等"
                    desc = "適中"
                elif score <= 5.0:
                    level = "偏高"
                    desc = "中等偏多"
                else:
                    level = "高"
                    desc = "相對突出"
                
                response = f"根據你的測驗結果，你的{display_name}分數是 {score:.1f}/6.0，屬於「{level}」的程度。這表示你在這個特質上{desc}。\n\n"
                response += "有什麼想進一步了解的嗎？例如這個特質對你的影響，或是如何運用這個特點？"
                
            elif bigfive_result:
                # 如果沒有指定特質，顯示完整結果
                response = "這是你的 Big Five 測驗結果：\n\n"
                response += f"• 開放性：{bigfive_result.openness:.1f}/6.0\n"
                response += f"• 盡責性：{bigfive_result.conscientiousness:.1f}/6.0\n"
                response += f"• 外向性：{bigfive_result.extraversion:.1f}/6.0\n"
                response += f"• 友善性：{bigfive_result.agreeableness:.1f}/6.0\n"
                response += f"• 神經質：{bigfive_result.neuroticism:.1f}/6.0\n\n"
                response += "想聊聊這些特質對你的影響嗎？"
            else:
                response = "你還沒有完成測驗呢！要不要先去做測驗，了解自己的人格特質？"
            
            return response
        
        # 檢查是否為分數查詢
        if check_score_query(user_message):
            print("[ChatBot] 檢測到分數查詢問題，直接回答不經過LLM")
            direct_answer = generate_score_response(bigfive_result, mbti_result, zodiac_result)
            
            # 保存對話歷史
            chat_history = session.get('chat_messages', [])
            chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            chat_history.append({
                'role': 'assistant',
                'content': direct_answer,
                'timestamp': datetime.now().isoformat()
            })
            session['chat_messages'] = chat_history
            session.modified = True
            
            # 保存到長期記憶
            save_chat_memory()
            
            # 返回直接答案
            def generate_direct():
                yield f"data: {json.dumps({'chunk': direct_answer}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(
                stream_with_context(generate_direct()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
        
        # 獲取對話歷史（只保留最近 3 輪對話，即 6 條訊息）
        chat_history = session.get('chat_messages', [])[-6:]
        
        # 格式化訊息
        formatted_message = ChatBotPrompts.format_user_message(user_message, chat_history)
        
        print(f"[ChatBot] 開始生成回應...")
        
        # 保存用戶訊息
        chat_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        def generate():
            """生成器函數 - 串流回應"""
            full_response = ""
            
            try:
                print("[ChatBot] 調用 ollama_client.generate_stream")
                for chunk in ollama_client.generate_stream(formatted_message, system_prompt):
                    if chunk:
                        # 只回傳最新 chunk，不累加 full_response 到前端
                        yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                        full_response += chunk
                
                print(f"[ChatBot] 生成完成，長度: {len(full_response)}")
                
                # 發送結束信號
                yield f"data: {json.dumps({'done': True})}\n\n"
                
                # 保存助手回應
                chat_history.append({
                    'role': 'assistant',
                    'content': full_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # 更新 session
                session['chat_messages'] = chat_history
                session.modified = True
                
                # 保存到長期記憶
                save_chat_memory()
                
            except Exception as e:
                print(f"[ChatBot] 錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    except Exception as e:
        print(f"[ChatBot] 初始化錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ChatBot 輔助功能 ==========
@app.route('/chatbot/clear', methods=['POST'])
def chatbot_clear():
    """清除對話歷史"""
    session['chat_messages'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/chatbot/save', methods=['POST'])
def chatbot_save():
    """手動保存對話"""
    save_chat_memory()
    return jsonify({'success': True, 'message': '對話已保存'})

@app.route('/chatbot/history')
def chatbot_history():
    """獲取當前對話"""
    messages = session.get('chat_messages', [])
    return jsonify({'messages': messages})

@app.route('/chatbot/history/all')
def chatbot_history_all():
    """獲取用戶的所有歷史對話記錄"""
    user_name = session.get('user_name')
    
    if not user_name:
        return jsonify({'histories': []})
    
    history_dir = os.path.join('data', 'chat_histories', user_name)
    
    if not os.path.exists(history_dir):
        return jsonify({'histories': []})
    
    histories = []
    
    try:
        # 讀取所有對話記錄文件
        for filename in sorted(os.listdir(history_dir), reverse=True):  # 最新的在前
            if filename.endswith('.json'):
                filepath = os.path.join(history_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    histories.append({
                        'filename': filename,
                        'timestamp': history_data.get('timestamp'),
                        'message_count': len(history_data.get('messages', [])),
                        'preview': history_data.get('messages', [{}])[0].get('content', '')[:50] if history_data.get('messages') else ''
                    })
        
        return jsonify({
            'user_name': user_name,
            'histories': histories
        })
    except Exception as e:
        print(f"❌ 讀取歷史記錄失敗: {e}")
        return jsonify({'error': str(e)}), 500


# ========== ChatBot 記憶管理函數 ==========
def generate_user_persona():
    """從測驗結果生成 User Persona"""
    mbti = session.get('mbti')
    bigfive_scores = session.get('bigfive_scores')
    zodiac = session.get('zodiac')
    dark_triad_scores = session.get('dark_triad_scores')
    
    if not mbti:
        return None
    
    # 載入模板
    mbti_template = PromptTemplates.get_mbti_template(mbti)
    zodiac_template = PromptTemplates.get_zodiac_template(zodiac) if zodiac else {}
    
    persona = {
        'mbti': {
            'type': mbti,
            'nickname': mbti_template.get('nickname', ''),
            'description': mbti_template.get('description', '')[:100] + '...'
        }
    }
    
    if bigfive_scores:
        persona['bigfive'] = bigfive_scores
    
    if zodiac:
        persona['zodiac'] = {
            'sign': zodiac,
            'description': zodiac_template.get('description', '')[:80] + '...'
        }
    
    if dark_triad_scores:
        persona['dark_triad'] = dark_triad_scores
    
    return persona

def load_chat_memory():
    """載入用戶的歷史對話記憶"""
    user_name = session.get('user_name')
    if not user_name:
        return None
    
    memory_file = os.path.join('data', 'chat_histories', f'{user_name}_memory.json')
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                return memory_data
        except Exception as e:
            print(f"載入 {user_name} 的記憶失敗: {e}")
            return None
    return None

def save_chat_memory():
    """保存用戶的對話記憶"""
    user_name = session.get('user_name')
    if not user_name:
        return
    
    # 確保目錄存在
    memory_dir = os.path.join('data', 'chat_histories')
    os.makedirs(memory_dir, exist_ok=True)
    
    memory_file = os.path.join(memory_dir, f'{user_name}_memory.json')
    
    try:
        # 載入現有記憶
        existing_memory = {}
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                existing_memory = json.load(f)
        
        # 提取本次對話的關鍵主題
        chat_messages = session.get('chat_messages', [])
        key_topics = []
        if len(chat_messages) > 0:
            # 提取用戶的主要訊息作為關鍵主題
            for msg in chat_messages:
                if msg['role'] == 'user':
                    content = msg['content']
                    # 只保存有意義的內容（排除太短的）
                    if len(content) > 5:
                        key_topics.append(content)
        
        # 保存最近3次對話的摘要（避免記憶檔案過大）
        summaries = existing_memory.get('conversation_summaries', [])
        if key_topics:
            summaries.append({
                'date': datetime.now().isoformat(),
                'topics': key_topics[:3]  # 只保存前3個主題
            })
            # 只保留最近3次對話
            summaries = summaries[-3:]
        
        # 更新記憶數據（包含完整測驗結果）
        memory_data = {
            'user_name': user_name,
            'mbti': session.get('mbti'),
            'bigfive_scores': session.get('bigfive_scores'),
            'zodiac': session.get('zodiac'),
            'dark_triad_scores': session.get('dark_triad_scores'),
            'last_updated': datetime.now().isoformat(),
            'total_conversations': existing_memory.get('total_conversations', 0) + 1,
            'conversation_summaries': summaries,
            'key_topics': key_topics[:5]  # 保存本次對話的前5個主題
        }
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 已保存 {user_name} 的記憶")
    except Exception as e:
        print(f"❌ 保存 {user_name} 的記憶失敗: {e}")

def save_chat_to_history():
    """將當前對話保存到歷史記錄"""
    user_name = session.get('user_name')
    chat_messages = session.get('chat_messages', [])
    
    if not chat_messages or len(chat_messages) == 0:
        return
    
    # 如果沒有用戶名字,使用臨時標識
    if not user_name:
        user_name = f"訪客_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 確保目錄存在
    history_dir = os.path.join('data', 'chat_histories', user_name)
    os.makedirs(history_dir, exist_ok=True)
    
    # 保存到歷史文件(以時間戳命名)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_file = os.path.join(history_dir, f'conversation_{timestamp}.json')
    
    try:
        history_data = {
            'user_name': user_name,
            'timestamp': datetime.now().isoformat(),
            'mbti': session.get('mbti'),
            'bigfive_scores': session.get('bigfive_scores'),
            'zodiac': session.get('zodiac'),
            'dark_triad_scores': session.get('dark_triad_scores'),
            'messages': chat_messages
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 已保存 {user_name} 的對話歷史到: {history_file}")
    except Exception as e:
        print(f"❌ 保存對話歷史失敗: {e}")

# ========== 重新開始測驗 ==========
@app.route('/restart')
def restart():
    """清除 session，重新開始測驗"""
    session.clear()
    return redirect(url_for('index'))

# ========== Ollama 測試 ==========
@app.route('/test-ollama')
def test_ollama():
    """測試 Ollama 連接"""
    try:
        import ollama
        models = ollama.list()
        response = ollama.generate(
            model='gemma3:4b',
            prompt='請用繁體中文簡短回答：你好嗎？',
            options={'num_predict': 20}
        )
        return jsonify({
            'status': 'success',
            'models_count': len(models.models),
            'response': response['response']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/setup-test-data')
def setup_test_data():
    """設置測試數據（用於快速測試 ChatBot）"""
    session['mbti'] = 'INTJ'
    session['bigfive_scores'] = {
        'openness': 5.2,
        'conscientiousness': 4.8,
        'extraversion': 2.5,
        'agreeableness': 3.9,
        'neuroticism': 3.1
    }
    session['zodiac'] = '摩羯座'
    session['dark_triad_scores'] = {
        'machiavellianism': 3.2,
        'narcissism': 2.8,
        'psychopathy': 2.3
    }
    session.modified = True
    return jsonify({
        'status': 'success',
        'message': '測試數據已設置！現在可以訪問 ChatBot 了。',
        'redirect': '/chatbot'
    })

# ========== 錯誤處理 ==========
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ========== 診斷路由（僅用於開發環境）==========
@app.route('/diagnostic')
def diagnostic():
    """診斷工具：檢查當前session數據"""
    diagnostic_data = {
        'session_id': request.cookies.get('session'),
        'mbti': session.get('mbti', '未設置'),
        'zodiac': session.get('zodiac', '未設置'),
        'bigfive_scores': session.get('bigfive_scores', {}),
        'dark_triad_scores': session.get('dark_triad_scores', {}),
        'has_analysis': 'analysis' in session
    }
    
    if 'analysis' in session:
        analysis = session['analysis']
        diagnostic_data['analysis_keys'] = list(analysis.keys())
        
        # 檢查 BigFive 分析中的數據
        if 'bigfive' in analysis:
            bf_text = analysis['bigfive']
            # 提取分析文字中的分數（用於檢查是否與實際分數一致）
            diagnostic_data['bigfive_analysis_preview'] = bf_text[:500] if bf_text else 'N/A'
    
    return render_template('diagnostic.html', data=diagnostic_data)

if __name__ == '__main__':
    # 確保模板目錄存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, port=5000)
