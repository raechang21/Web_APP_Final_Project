
# Personality Paradox 3.0 - 多面向人格測驗與心理反思平台

## 專案簡介
Personality Paradox 是一個結合 MBTI、Big Five、星座、黑暗三角人格的互動式人格測驗與心理反思平台。以 Flask 為主體，整合本地 LLM（Ollama gemma3:4b），提供專業心理諮商師取向的 AI 對話、個性化分析、視覺化圖表與報告匯出。

## 主要功能
- ✨ MBTI/Big Five/星座/黑暗三角人格測驗
- 🤖 AI 諮商師對話（SSE 串流、專業諮商技巧）
- 📊 個性化分析與綜合報告（智能化 Big Five 維度排序）
- 🎨 Notion 風格 UI、互動式 Plotly 圖表
- 💾 對話歷史自動保存/載入（可視化狀態指示）
- 🔄 完善的 Session 管理（防止用戶資料混淆）
- 🎯 分數查詢智能攔截（精確回答 vs 描述性建議）
- 🔍 診斷頁面（即時檢查系統狀態與 Session 資料）

## 安裝與啟動

### 1. 安裝 Ollama 並下載模型
```bash
# 下載 Ollama (https://ollama.ai/)
# 安裝後執行
ollama pull gemma3:4b
```

### 2. 安裝 Python 套件
```bash
pip install -r requirements_flask.txt
```

### 3. 啟動 Flask 應用
```bash
python app_flask.py
```
預設網址：http://127.0.0.1:5000

### 4. 使用流程
1. 進入首頁，輸入姓名
2. 選擇星座
3. 輸入 MBTI 類型（4 個字母）
4. 完成 Big Five 測驗（15 題）
5. 選擇是否完成 Dark Triad 測驗（19 題，可跳過）
6. 查看綜合分析結果
7. 使用 AI 諮商助手進行深入對話

## 專案結構
```
Personality-Paradox_3.0/
├── app_flask.py              # Flask 主應用（路由、API、Session 管理）
├── config.py                 # 配置檔案（Ollama 設定、Session 配置）
├── requirements_flask.txt    # Python 依賴套件清單
│
├── analysis/                 # 分析模組
│   ├── __init__.py
│   ├── integration.py        # 整合分析（綜合報告生成）
│   ├── reflection.py         # 反思語句生成
│   └── scoring.py            # 分數計算與驗證
│
├── llm/                      # LLM 相關模組
│   ├── __init__.py
│   ├── ollama_client.py      # Ollama 客戶端（SSE 串流）
│   ├── prompt_templates.py   # Prompt 模板（諮商師 Prompt、Big Five 模板）
│   └── chatbot_prompts.py    # ChatBot Prompt 生成（智能分數攔截）
│
├── models/                   # 資料模型
│   ├── __init__.py
│   ├── user_profile.py       # 用戶資料結構
│   ├── test_result.py        # 測驗結果資料結構
│   └── dark_triad_result.py  # 黑暗三角結果
│
├── templates/                # Jinja2 模板
│   ├── base.html             # 基礎模板（導航列、Session 清除路由）
│   ├── welcome.html          # 首頁（姓名輸入）
│   ├── zodiac_selection.html # 星座選擇
│   ├── mbti_input.html       # MBTI 輸入
│   ├── bigfive_test.html     # Big Five 測驗
│   ├── dark_triad_intro.html # Dark Triad 介紹頁
│   ├── dark_triad_test.html  # Dark Triad 測驗
│   ├── results.html          # 測驗結果頁
│   ├── deep_analysis.html    # 深度分析頁
│   ├── chatbot.html          # AI 諮商助手（自動保存指示器）
│   ├── diagnostic.html       # 診斷頁面（Session 檢查）
│   ├── 404.html              # 404 錯誤頁
│   └── 500.html              # 500 錯誤頁
│
├── static/                   # 靜態檔案
│   ├── css/                  # 樣式表（目前為空，樣式內嵌於 templates）
│   └── js/                   # JavaScript（目前為空，腳本內嵌於 templates）
│
├── data/                     # 測驗資料與範本
│   ├── bigfive_questions.json       # Big Five 題目（15 題）
│   ├── bigfive_templates.json       # Big Five 分析模板（統一「友善性」命名）
│   ├── dark_triad_questions.json    # Dark Triad 題目（19 題）
│   ├── dark_triad_templates.json    # Dark Triad 分析模板
│   ├── mbti_templates.json          # MBTI 16 型人格模板
│   ├── zodiac_templates.json        # 12 星座模板
│   └── chat_histories/              # 對話歷史保存資料夾
│       └── *_memory.json            # 用戶對話記憶檔案
│
├── utils/                    # 工具模組
│   ├── __init__.py
│   ├── data_loader.py        # JSON 資料載入器
│   └── zodiac_helper.py      # 星座計算輔助工具
│
├── visualization/            # 視覺化模組
│   ├── __init__.py
│   ├── charts.py             # Plotly 圖表生成
│   └── report_generator.py   # PDF 報告生成（保留未使用，供未來開發）
│
├── tests/                    # 測試檔案（開發用）
│   ├── __init__.py
│   ├── bigfive_test.py       # Big Five 測驗測試
│   ├── mbti_test.py          # MBTI 測試
│   └── zodiac_selector.py    # 星座選擇器測試
│
├── flask_session/            # Flask Session 儲存目錄
├── debug_session_data.py     # Session 除錯工具（開發用）
│
└── 文件檔案（Markdown）
    ├── README.md                    # 專案說明文件
    ├── INSTALL.md                   # 安裝指南
    ├── CHATBOT_FEATURES.md          # ChatBot 功能說明
    ├── CHATBOT_INTEGRATION.md       # ChatBot 整合指南
    ├── CHATBOT_TROUBLESHOOTING.md   # ChatBot 疑難排解
    ├── FLASK_CHATBOT_README.md      # Flask ChatBot 使用說明
    ├── FLASK_TEST_README.md         # Flask 測試說明
    └── MEMORY_ARCHITECTURE.md       # 記憶架構說明
```

**說明**：
- `static/css/` 和 `static/js/` 目前為空，所有樣式和腳本都內嵌於 HTML 模板中
- `tests/` 資料夾包含開發測試用的程式碼
- 所有 Python 模組都包含 `__init__.py` 檔案
- `debug_session_data.py` 和 `flask_session/` 為開發除錯用途
- `visualization/report_generator.py` 保留供未來 PDF 匯出功能開發

## 注意事項
- ⚠️ Ollama 需先執行 `ollama serve`
- ⚠️ PDF 匯出需安裝中文字體（Windows: msjh.ttc, Linux/Mac: STSong-Light）
- ⚠️ 諮商助手僅供參考，不取代專業心理諮商
- 🔄 點擊「重新開始」或左上角 Logo 會清除 Session，確保多用戶資料不混淆
- 💾 對話歷史會自動保存，無需手動操作

---
PSS1141 社會科學程式設計 期末專案  
NTU 2025

## 🛠️ 技術堆疊

- **Web 框架**：Flask 3.0.0
- **前端**：Bootstrap 5 + Custom CSS（Notion 風格）
- **LLM**：Ollama (gemma3:4b)
- **串流技術**：Server-Sent Events (SSE)
- **視覺化**：Plotly 5.17.0（互動式圖表）
- **PDF 生成**：ReportLab 4.4.5（中文字體支援）
- **資料處理**：Pandas, Python dataclasses, JSON
- **Session 管理**：Flask-Session（檔案系統儲存）

## 🌟 特色功能說明

### 1. Big Five 測驗
- 15 題精簡版本，涵蓋五大人格維度
- 六點量尺（1=非常不同意 ~ 6=非常同意）
- 即時進度顯示
- 彩色視覺化呈現

### 2. 黑暗三角人格測驗
- 選做功能，可跳過
- 使用中性語言（策略思維、自信表現、行為風格）
- 19 題評估，基於 SD3（Short Dark Triad）量表
- 彩色進度條視覺化

### 3. AI 分析
- **MBTI**：16 型人格專業模板，含優勢、成長空間、職業建議
- **星座**：12 星座模板，涵蓋性格特質、相性分析、人生格言
- **Big Five**：LLM 生成整合五大維度的交互影響分析
- **黑暗三角**：中性化描述，強調特質而非病理
- **綜合分析**：整合所有測驗的深度洞察（200-300字）
- **反思語句**：提醒人格的流動性，避免標籤化

### 4. 心理諮商助手（專業取向）
- **諮商師角色定位**：
  - 心理諮商碩士背景
  - 精通人本取向、CBT、敘事治療
  - 以個案為中心，不評判、不標籤化
  
- **對話特色**：
  - ✅ 自然對話風格（非分析報告）
  - ✅ 隱性運用人格資料（不直接提及測驗分數）
  - ✅ 專業諮商技巧（反映情感、開放式提問、具體化）
  - ✅ 傾聽優先，鼓勵個案表達
  - ✅ 智能分數攔截：直接詢問特定分數時提供精確數字，其他情況使用描述性語言
  
- **技術功能**：
  - 即時 SSE 串流回應
  - 對話歷史自動保存與載入（可視化狀態指示：💾 對話自動保存中... → ✅ 已保存）
  - 依用戶名稱分類記錄（儲存於 `data/chat_histories/{name}_memory.json`）
  - 智能對話記憶管理（保留最近 3 輪對話，避免 Context 過長）
  - 清除對話功能
  - 分數查詢智能攔截（Regex 檢測 → 直接回答 vs LLM 生成描述）

- **個性化回應範例**：
  ```
  ❌ 舊風格：「根據您的 INTJ 類型和高盡責性分數（5.1），您可能對自己要求很高...」
  
  ✅ 新風格（一般對話）：「聽起來工作讓你感到蠻大的壓力。能多說一點是什麼讓你感到壓力嗎？」
  （內部參考：INTJ + 高盡責性 → 可能自我要求高，適時引導放鬆標準）
  
  ✅ 新風格（分數查詢）：
  用戶：「我的開放性分數是多少？」
  助手：「您的開放性（Openness）分數是 4.2，處於中等偏高的水平...」
  ```

- **自動保存機制**：
  - 每次對話完成後自動觸發保存
  - 狀態指示器提供即時視覺回饋
  - 無需手動操作，提升用戶體驗

### 5. Notion 風格介面
- **首頁**：沉浸式大標題、浮動動畫、極簡卡片
- **測驗頁**：聚焦式輸入、清晰進度指示
- **結果頁**：優雅的 Plotly 互動式圖表、舒適的閱讀體驗
- **諮商頁**：溫暖的對話空間、柔和的配色
- **診斷頁**：即時系統狀態檢查、Session 資料檢視

## ⚠️ 注意事項

- 首次生成分析時，Ollama 可能需要 5-10 秒載入模型
- 確保 Ollama 服務正在運行（`ollama serve`）
- 確保 Flask 應用程式正在運行（`python app_flask.py`）
- 黑暗三角測驗為選做，結果僅供參考，不代表心理診斷
- **重要**：點擊任何「重新開始」按鈕、「首頁」按鈕或左上角 Logo 時，會自動清除 Session 資料，避免不同用戶資料混淆
- ChatBot 對話歷史會自動保存在 `data/chat_histories/{name}_memory.json`
- 對話會自動保存，無需手動操作（介面會顯示 "✅ 已保存" 狀態）
- 諮商助手提供的建議僅供參考，不替代專業心理諮商
- **注意**：目前版本尚未實作 PDF 匯出功能（visualization/report_generator.py 保留供未來開發使用）

## 🔧 疑難排解

### ChatBot 無法連接
1. 確認 Ollama 正在運行：`ollama list`
2. 確認模型已下載：`ollama pull gemma3:4b`
3. 訪問診斷頁面：http://127.0.0.1:5000/diagnostic
4. 查看 Flask 終端機的錯誤訊息

### Big Five 分數顯示錯誤
- Big Five 各維度會按照標準順序顯示：開放性 → 盡責性 → 外向性 → 友善性 → 神經質
- 分數範圍：0.0-7.0（系統會自動驗證並修正超出範圍的分數）
- 如有疑問，可使用 ChatBot 詢問特定維度的分數

### Session 資料殘留問題
- **症狀**：看到前一位用戶的測驗資料或分析結果
- **解決方法**：點擊左上角 Logo、「首頁」或「重新開始」按鈕，系統會自動清除 Session
- **預防措施**：每次新用戶使用前，建議點擊「重新開始」確保乾淨的 Session

### 對話自動保存失敗
- 檢查 `data/chat_histories/` 資料夾是否存在且有寫入權限
- 查看瀏覽器 Console 是否有錯誤訊息
- 確認 Flask 應用正在運行

## 📚 更新紀錄

### v3.0 - Flask 重構 + 諮商取向 + Session 管理優化（2025/12/13）

**主要更新**：
- ✨ 從 Streamlit 遷移至 Flask Web 框架
- ✨ 採用 Notion 風格極簡設計
- ✨ ChatBot 改為專業諮商師取向
  - 隱性運用人格資料，避免標籤化
  - 專業諮商技巧整合（同理心、開放式提問）
  - 自然對話風格，非分析報告
- ✨ SSE 串流技術實現即時回應
- ✨ 沉浸式首頁設計
- ✨ 大字輸入框 MBTI 介面

**Bug 修復與優化**：
- 🐛 **修復 Session 污染問題**：所有導航按鈕（Logo、首頁、重新開始、重新測驗）現在都使用 `/restart` 路由，確保 Session 完全清除
- 🐛 **修復 Big Five 維度排序問題**：使用 `OrderedDict` 確保維度始終按照標準順序顯示（開放性 → 盡責性 → 外向性 → 友善性 → 神經質）
- 🐛 **統一 Big Five 命名**：將所有 "親和性" 統一為 "友善性"（Agreeableness）
- 🐛 修復 Big Five 分數驗證過嚴問題
- 🐛 移除重複的診斷路由（AssertionError 修復）
- 🐛 優化錯誤處理與用戶提示

**UX 改進**：
- 💾 **自動保存狀態指示器**：移除手動「儲存對話」按鈕，改為自動保存並顯示視覺化狀態（💾 對話自動保存中... → ✅ 已保存）
- 🎯 **智能分數攔截系統**：
  - 當用戶詢問特定分數時（如「我的開放性是多少？」），系統直接回傳精確數字
  - 一般對話情況下，LLM 使用描述性語言（如「較高」、「中等」），避免提及具體分數
- 🔄 **完善的 Session 管理**：所有「返回首頁」相關按鈕都會清除 Session，防止多用戶資料混淆
- 📊 **診斷頁面增強**：http://127.0.0.1:5000/diagnostic 可查看 Session 狀態與測試資料

**技術改進**：
- ⚡ 對話記憶優化：僅保留最近 3 輪對話，減少 Context 長度，提升 LLM 回應速度
- 📁 對話歷史儲存路徑調整：`data/chat_histories/{name}_memory.json`（以用戶名稱為檔名）
- 🎨 右側邊欄預設折疊，提供更聚焦的閱讀體驗

### v2.0 - ChatBot 功能更新
- ✨ 新增人格分析諮商助手對話系統
- ✨ 串流回應與打字動畫效果
- ✨ 智能主題分類與統計
- ✨ 對話歷史保存與載入
- ✨ 馬卡龍色系溫馨介面設計
- 🐛 修復 HTML 標籤顯示問題
- 🐛 優化分析結果快取機制

### v1.0 - 初始版本（Streamlit，已於 v3.0 移除）
- 基礎測驗功能（MBTI、Big Five、星座、黑暗三角）
- AI 分析與視覺化
- PDF 報告匯出
- **注意**：Streamlit 舊版程式碼（`.streamlit/`、`pages/`、`requirements.txt`）已於 v3.0 完全移除

## 👥 作者

PSS1141 社會科學程式設計 - 期末專案  
NTU 2025

## 📄 授權

本專案僅供學術用途使用。

## 🙏 致謝

- Ollama 團隊提供本地 LLM 支援
- Flask 社群的優秀文檔與資源
- Notion 設計團隊的介面靈感
