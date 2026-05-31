"""
Prompt 模板
"""

from pathlib import Path
from ..models.test_result import MBTIResult, BigFiveResult, ZodiacResult
from typing import List, Tuple


DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class PromptTemplates:
    """Prompt 模板類別"""
    
    @staticmethod
    def mbti_analysis(mbti: MBTIResult) -> str:
        """
        MBTI 深度分析 prompt
        
        Args:
            mbti: MBTI 結果
            
        Returns:
            Prompt 字串
        """
        return f"""請用 150-200 字的繁體中文，直接描述 MBTI 類型 {mbti.type} 使用者的性格特質：

請涵蓋：
1. 核心性格特質
2. 主要優勢
3. 可能面臨的挑戰或盲點
4. 典型行為模式

重要要求：
- 必須以「{mbti.type} 通常展現出...」或「{mbti.type} 的人...」作為開頭，然後轉換為第二人稱「你」繼續描述
- 例如：「INTJ 通常展現出深度思考、獨立自主的特質。你擁有強烈的邏輯思維...」
- 不要使用客套話或稱呼語
語氣：專業、溫暖、具啟發性
格式：流暢的段落，不要使用條列式

分析："""
    
    @staticmethod
    def bigfive_analysis(bigfive: BigFiveResult) -> str:
        """
        Big Five 綜合分析 prompt
        
        Args:
            bigfive: Big Five 結果
            
        Returns:
            Prompt 字串
        """
        scores = bigfive.to_dict()
        score_text = "\n".join([
            f"- {dim_en}（{dim_zh}）：{score:.1f}/6.0"
            for (dim_en, score), dim_zh in zip(
                scores.items(),
                ["開放性", "盡責性", "外向性", "友善性", "神經質"]
            )
        ])
        
        return f"""請針對以下 Big Five 人格特質分數提供 150-200 字的繁體中文分析：

{score_text}

請涵蓋：
1. 整體人格特質解讀
2. 各維度之間如何相互影響
3. 這樣的人格組合如何影響生活

重要要求：
- 必須以「你的性格...」或「從你的特質來看...」作為開頭
- 使用第二人稱「你」
- 不要使用「很高興為你提供人格特質的分析」、「作為一位心理學家」等客套話
- 不要使用「這個個體」、「這樣的人」等稱呼
語氣：專業、溫和、具啟發性
格式：流暢的段落

分析："""
    
    @staticmethod
    def zodiac_analysis(zodiac: ZodiacResult) -> str:
        """
        星座性格分析 prompt
        
        Args:
            zodiac: 星座結果
            
        Returns:
            Prompt 字串
        """
        return f"""請用 100-150 字的繁體中文，針對 {zodiac.sign} 的使用者提供性格特質描述。

請涵蓋：
1. 核心性格特質與個性傾向
2. 在生活中的典型行為模式
3. 情感表達與人際互動方式

【重要】回答格式要求：
- 第一句話必須是：「作為 {zodiac.sign}，你的性格...」（不可有其他開頭）
- 全文使用第二人稱「你」
- 絕對不要出現「性格分析：」、「以下是分析」、「你好」等標籤或客套話
- 不要用「{zodiac.sign} 的人」等第三人稱稱呼
- 直接開始描述性格，不要任何前言

語氣：專業但親切、具體、貼近個人
請直接開始撰寫，第一個字就是「作為」："""
    
    @staticmethod
    def integration_analysis(
        mbti: MBTIResult,
        bigfive: BigFiveResult,
        zodiac: ZodiacResult,
        dark_triad=None
    ) -> str:
        """
        綜合分析 prompt
        
        Args:
            mbti: MBTI 結果
            bigfive: Big Five 結果
            zodiac: 星座結果
            dark_triad: 黑暗三角結果（可選）
            
        Returns:
            Prompt 字串
        """
        bf_scores = bigfive.to_dict()
        
        # 根據是否有黑暗三角測驗，調整提示詞
        if dark_triad:
            from ..models.dark_triad_result import DarkTriadResult
            test_count = "四種"
            test_list = f"""1. MBTI：{mbti.type}
2. Big Five：開放性 {bf_scores['openness']:.1f}、盡責性 {bf_scores['conscientiousness']:.1f}、外向性 {bf_scores['extraversion']:.1f}
3. 星座：{zodiac.sign}
4. 黑暗三角：策略性 {dark_triad.machiavellianism:.1f}、自信 {dark_triad.narcissism:.1f}"""
            word_count = "150-180"
        else:
            test_count = "三種"
            test_list = f"""1. MBTI：{mbti.type}
2. Big Five：開放性 {bf_scores['openness']:.1f}、盡責性 {bf_scores['conscientiousness']:.1f}、外向性 {bf_scores['extraversion']:.1f}
3. 星座：{zodiac.sign}"""
            word_count = "120-150"
        
        return f"""整合以下測驗，用 {word_count} 字分析：

{test_list}

重點：
1. 整體人格面貌
2. 不同測驗的共通點
3. 對行為和決策的影響

以「你的性格...」開頭，使用第二人稱，專業語氣。

分析："""

    @staticmethod
    def reflection_prompt(
        mbti: MBTIResult,
        bigfive: BigFiveResult,
        zodiac: ZodiacResult,
        contradictions: List[Tuple[str, str]]
    ) -> str:
        """
        反思語句生成 prompt
        
        Args:
            mbti: MBTI 結果
            bigfive: Big Five 結果
            zodiac: 星座結果
            contradictions: 矛盾點列表 [(測驗1, 測驗2), ...]
            
        Returns:
            Prompt 字串
        """
        contradiction_text = ""
        if contradictions:
            contradiction_text = "矛盾點：" + "、".join([f"{c[0]} vs {c[1]}" for c in contradictions])
        else:
            contradiction_text = "測驗結果一致"
        
        return f"""測驗：MBTI {mbti.type}、Big Five、星座 {zodiac.sign}

{contradiction_text}

用 80-100 字提醒：
1. 測驗的價值與限制
2. 人格是光譜非分類
3. 不過度標籤化

以「這些測驗結果，呈現的是...」開頭，專業語氣。
不要使用粗體(**文字**)或標題格式，保持純文字段落。

反思："""
    
    @staticmethod
    def dark_triad_analysis(dark_triad) -> str:
        """
        黑暗三角分析 prompt
        
        Args:
            dark_triad: 黑暗三角結果
            
        Returns:
            Prompt 字串
        """
        from ..models.dark_triad_result import DarkTriadResult

        return f"""請用 150-200 字的繁體中文，針對以下黑暗三角人格特質分數提供分析：

馬基維利主義（策略思維）：{dark_triad.machiavellianism:.1f}/6.0
自戀（自信表現）：{dark_triad.narcissism:.1f}/6.0
精神病態（行為風格）：{dark_triad.psychopathy:.1f}/6.0

請涵蓋：
1. 這三個維度如何影響你的決策風格和人際策略
2. 你在目標達成、自我肯定與規則態度上的傾向
3. 這些特質在不同情境下的表現

【重要】回答格式要求：
- 第一句話必須是：「你的性格在策略運用、自信程度與行為彈性上...」（不可有其他開頭）
- 全文使用第二人稱「你」
- 使用中性、客觀的語言，避免負面標籤
- 強調這些是「策略傾向」而非「性格缺陷」
- 絕對不要出現「分析：」、「以下是分析」等標籤或客套話

語氣：專業、客觀、中性
請直接開始撰寫："""
    
    # ========== Flask 版本使用的靜態方法（接受字典參數） ==========
    
    @staticmethod
    def get_bigfive_prompt(scores: dict) -> str:
        """
        Big Five 分析 prompt（接受分數字典）
        
        Args:
            scores: 分數字典 {'openness': 80, 'conscientiousness': 70, ...}
            
        Returns:
            Prompt 字串
        """
        dimension_names = {
            'openness': '開放性',
            'conscientiousness': '盡責性',
            'extraversion': '外向性',
            'agreeableness': '友善性',
            'neuroticism': '神經質'
        }
        
        score_text = "\n".join([
            f"- {dimension_names[dim]}：{score}/100"
            for dim, score in scores.items()
        ])
        
        return f"""請針對以下 Big Five 人格特質分數提供 150-200 字的繁體中文分析：

{score_text}

請涵蓋：
1. 整體人格特質解讀
2. 各維度之間如何相互影響
3. 這樣的人格組合如何影響生活

重要要求：
- 必須以「你的性格...」或「從你的特質來看...」作為開頭
- 使用第二人稱「你」
- 不要使用「很高興為你提供人格特質的分析」、「作為一位心理學家」等客套話
- 不要使用「這個個體」、「這樣的人」等稱呼
語氣：專業、溫和、具啟發性
格式：流暢的段落

分析："""
    
    @staticmethod
    def get_mbti_template(mbti_type: str) -> dict:
        """
        獲取 MBTI 模板(從 JSON 文件讀取靜態數據)
        
        Args:
            mbti_type: MBTI 類型字串
            
        Returns:
            分析字典
        """
        import json
        
        template_path = DATA_DIR / "mbti_templates.json"

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # 如果找到該類型,返回模板
            if mbti_type in templates:
                return templates[mbti_type]
        except Exception as e:
            print(f"❌ 讀取 MBTI 模板失敗: {e}")
        
        # 如果找不到特定類型或讀取失敗,返回通用模板
        return {
            'nickname': mbti_type,
            'description': f'你的 MBTI 類型是 {mbti_type}',
            'strengths': ['請參考專業 MBTI 解讀'],
            'growth_areas': ['請參考專業 MBTI 解讀'],
            'career_suggestions': '請參考 16Personalities 網站獲取詳細分析',
            'interaction_style': '請參考專業 MBTI 資源'
        }
    
    @staticmethod
    def get_zodiac_template(zodiac: str) -> dict:
        """
        獲取星座模板(從 JSON 文件讀取靜態數據)
        
        Args:
            zodiac: 星座名稱
            
        Returns:
            分析字典
        """
        import json
        
        template_path = DATA_DIR / "zodiac_templates.json"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # 如果找到該星座,返回模板
            if zodiac in templates:
                return templates[zodiac]
        except Exception as e:
            print(f"❌ 讀取星座模板失敗: {e}")
        
        # 如果找不到特定星座或讀取失敗,返回通用模板
        return {
            'emoji': '⭐',
            'date_range': '未知',
            'element': '未知',
            'description': f'{zodiac}的特質',
            'strengths': ['請參考專業星座解讀'],
            'growth_areas': ['請參考專業星座解讀'],
            'compatibility': '待補充',
            'career': '請參考專業星座資源',
            'interaction': '請參考專業星座資源',
            'life_motto': '做最好的自己'
        }
    
    @staticmethod
    def get_dark_triad_template(scores: dict) -> str:
        """
        獲取黑暗三角分析(從 JSON 文件讀取分數範圍模板)
        
        Args:
            scores: 黑暗三角分數字典,包含 machiavellianism, narcissism, psychopathy
            
        Returns:
            分析文字
        """
        import json
        
        template_path = DATA_DIR / "dark_triad_templates_new.json"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # 判斷分數等級的函數
            def get_level(score):
                if score <= 2.66:
                    return 'low'
                elif score <= 4.33:
                    return 'medium'
                else:
                    return 'high'
            
            # 獲取每個維度的分析
            mach_level = get_level(scores['machiavellianism'])
            narc_level = get_level(scores['narcissism'])
            psyc_level = get_level(scores['psychopathy'])
            
            mach_data = templates['machiavellianism'][mach_level]
            narc_data = templates['narcissism'][narc_level]
            psyc_data = templates['psychopathy'][psyc_level]
            
            # 組合分析文字（純文字格式，不使用 Markdown）
            # 只顯示分數，不顯示範圍標籤（那些資訊是給 LLM 內部參考用的）
            analysis = f"""🎭 黑暗三角人格特質分析

📊 馬基維利主義：{scores['machiavellianism']:.1f}/6.0
{mach_data['interpretation']}
💡 {mach_data['suggestion']}

👑 自戀：{scores['narcissism']:.1f}/6.0
{narc_data['interpretation']}
💡 {narc_data['suggestion']}

🧀 精神病態特質：{scores['psychopathy']:.1f}/6.0
{psyc_data['interpretation']}
💡 {psyc_data['suggestion']}

────────────────────

🔮 綜合評估
"""
            
            # 判斷綜合分析類型
            levels = [mach_level, narc_level, psyc_level]
            if levels.count('medium') == 3:
                analysis += templates['general_analysis']['balanced']['text']
            elif levels.count('low') >= 2:
                analysis += templates['general_analysis']['low_overall']['text']
            elif levels.count('high') >= 2:
                analysis += templates['general_analysis']['high_overall']['text']
            else:
                analysis += templates['general_analysis']['mixed']['text']
            
            return analysis
            
        except Exception as e:
            print(f"❌ 讀取黑暗三角模板失敗: {e}")
            # 返回簡單分析
            return f"""基於黑暗三角測驗結果：
馬基維利主義：{scores['machiavellianism']:.1f}/6.0
自戀：{scores['narcissism']:.1f}/6.0
精神病態：{scores['psychopathy']:.1f}/6.0

這些特質反映了你在策略思維、自信心和情緒穩定性方面的傾向。請參考專業心理資源獲取更詳細的解讀。"""
    
    @staticmethod
    def get_bigfive_template(scores: dict) -> str:
        """
        獲取 Big Five 分析(從 JSON 文件讀取分數範圍模板)
        
        Args:
            scores: Big Five 分數字典,包含五個維度的分數
            
        Returns:
            分析文字
        """
        import json
        
        template_path = DATA_DIR / "bigfive_templates_new.json"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # 判斷分數等級的函數
            def get_level(score):
                if score <= 2.5:
                    return 'low'
                elif score <= 4.5:
                    return 'medium'
                else:
                    return 'high'
            
            # 五大維度（順序必須與 config.py 的 BIG_FIVE_DIMENSIONS 一致）
            from collections import OrderedDict
            dimensions = OrderedDict([
                ('openness', '開放性'),
                ('conscientiousness', '盡責性'),
                ('extraversion', '外向性'),
                ('agreeableness', '友善性'),
                ('neuroticism', '神經質')
            ])
            
            analysis = "🌟 Big Five 人格特質分析\n\n"
            
            # 為每個維度生成分析（純文字格式，受試者版本 - 只顯示分數）
            for dim_key, dim_name in dimensions.items():
                if dim_key in scores:
                    score = scores[dim_key]
                    level = get_level(score)
                    dim_data = templates[dim_key][level]
                    
                    # 只顯示分數，不顯示等級標籤和範圍（那些資訊是給 LLM 內部參考用的）
                    analysis += f"""{dim_name}：{score:.1f}/6.0
{dim_data['interpretation']}
✨ 優勢：{', '.join(dim_data['strengths'])}
💡 建議：{dim_data['suggestion']}

"""
            
            return analysis.strip()
            
        except Exception as e:
            print(f"❌ 讀取 Big Five 模板失敗: {e}")
            # 返回簡單分析
            result = "基於 Big Five 人格測驗結果：\n\n"
            for key, value in scores.items():
                result += f"{key}: {value:.1f}/6.0\n"
            result += "\n請參考專業心理資源獲取更詳細的解讀。"
            return result
