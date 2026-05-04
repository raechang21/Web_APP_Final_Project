# ChatBot 諮商助手功能說明

## 🧠 Memory Copilot 三層記憶架構

本系統完整實作了 Memory Copilot 的 LLM 記憶系統，包含三層記憶結構：

### 📝 Working Memory（短期記憶）
**來源**：最近數輪對話  
**介面區塊**：Active Session（右側對話區）  
**功能**：決定模型「當下」可讀的上下文

**實作細節**：
- `chat_messages[]`：完整對話訊息
- `request_log[]`：最近 3 條對話摘要
- 每次 prompt 注入最近 5 輪完整對話
- 提供即時互動脈絡

### 🔄 Session Memory（中期記憶）
**來源**：當次會話的摘要  
**介面區塊**：Request Log（左側欄）  
**功能**：作為目前 prompt 的內容

**實作細節**：
- 自動提取**與當前主題相關**的歷史對話
- 智能過濾：只注入同類別的過往討論
- 例如：討論「職涯發展」時，自動載入之前的職涯相關對話
- 避免 prompt 過載，提升相關性

**新增函數**：`generate_session_memory()`
```python
# 範例輸出
"您之前在「自我成長」主題討論過:
- 如何提升自信心
- 克服拖延症的方法"
```

### 💾 Long-Term Memory（長期記憶）
**來源**：持續累積、跨對話  
**介面區塊**：User Persona + 討論主題分析（左側欄）  
**功能**：形成使用者模型與專屬歷史

**實作細節**：
- `user_traits[]`：對話中發現的關注點（持久化）
- `topic_categories[]`：主題統計（持久化）
- **檔案儲存**：`data/memory_{MBTI}.json`
- **跨 session 累積**：下次進入自動載入
- **自動合併**：新舊主題統計合併計算

**持久化機制**：
```python
# 每次更新主題時自動儲存
save_long_term_memory()

# 初始化時自動載入
load_long_term_memory()

# 離開頁面時儲存
save_long_term_memory()
```

---

## 🎯 新增功能（基於 Mermaid 流程圖改進）

### 1. **主題自動分類系統**
對話內容會自動歸類到以下六大類別：
- 🌱 **職涯發展**：工作選擇、職業規劃相關
- 👥 **人際關係**：社交困擾、人際互動
- 💪 **自我成長**：個人提升、能力發展
- 🎭 **情緒管理**：情緒調節、壓力處理
- 🔍 **性格分析**：測驗解讀、特質探討
- ⚙️ **其他**：一般性話題

### 2. **主題轉換偵測 (Topic Shift Detection)**
- 系統會自動偵測用戶是否從一個話題轉換到另一個話題
- 記錄主題轉換歷史（包含時間戳記）
- 幫助諮商師 AI 理解對話脈絡變化

### 3. **長期主題追蹤 (Long Term Topics)**
**Request Log 增強：**
- 每條記錄顯示主題類別標籤（彩色標記）
- 記錄時間戳記
- 最多顯示最近 10 筆對話

**新增「討論主題分析」區塊：**
- 統計各主題討論次數
- 視覺化長條圖顯示關注程度
- 最多顯示前 5 大主題
- 幫助用戶了解自己最關注的領域

### 4. **User Persona 持續更新**
- **對話中發現的關注點**：從對話內容提取新特質
- **主題趨勢分析**：追蹤用戶長期關注的議題
- **動態人格檔案**：隨對話深入逐步豐富

## 📊 UI 改進

### 彩色主題標籤系統
每個主題類別使用專屬顏色：
- 職涯發展：綠色 `#4CAF50`
- 人際關係：藍色 `#2196F3`
- 自我成長：橙色 `#FF9800`
- 情緒管理：紫色 `#9C27B0`
- 性格分析：青色 `#00BCD4`
- 其他：灰色 `#757575`

### Request Log 升級顯示
```
[職涯發展] 11:30
探討轉換跑道的可能性
```

### 主題分析圖表
```
職涯發展          █████████████ (4次討論)
情緒管理          ████████      (3次討論)
自我成長          █████         (2次討論)
```

## 🔄 工作流程

```mermaid
用戶發送訊息
    ↓
AI 生成回應
    ↓
生成對話摘要 + 主題分類 → 更新 Request Log
    ↓
偵測主題轉換 → 記錄轉換歷史
    ↓
提取關注點 (每3輪) → 更新 User Persona
    ↓
更新主題統計 → 刷新「討論主題分析」圖表
```

## 💡 與 Memory Copilot 架構的完整對應

| Memory Copilot 架構 | 本專案實作 | 技術細節 |
|-------------------|-----------|---------|
| **Working Memory** | ✅ `chat_messages` + `request_log` | 最近 5 輪對話 + 3 條摘要 |
| **Session Memory** | ✅ `generate_session_memory()` | 智能提取同主題歷史對話 |
| **Long-Term Memory** | ✅ `user_traits` + `topic_categories` + 檔案持久化 | JSON 儲存，跨 session 累積 |
| **Topic Shift Detection** | ✅ `detect_topic_shift()` | LLM 判斷主題轉換 |
| **Topic Routing & Summary** | ✅ `generate_conversation_summary()` | 摘要 + 6 類別分類 |
| **Update Topics** | ✅ `update_topic_statistics()` | 即時更新統計 + 自動儲存 |
| **Memory Storage** | ✅ `save_long_term_memory()` | 寫入 `data/memory_{MBTI}.json` |
| **Memory Retrieval** | ✅ `load_long_term_memory()` | 啟動時自動載入 |

---

## 🔄 完整工作流程（三層記憶協作）

```
用戶發送訊息
    ↓
【Working Memory】記錄到 chat_messages
    ↓
AI 生成 prompt
    ├─ Long-Term Memory: User Persona（測驗結果 + 累積特質）
    ├─ Session Memory: 相關主題的歷史對話
    └─ Working Memory: 最近 5 輪完整對話
    ↓
AI 生成回應
    ↓
【Working Memory】生成對話摘要 + 主題分類
    ↓
【Session Memory】偵測主題轉換
    ↓
【Long-Term Memory】提取關注點（每3輪）
    ↓
【Long-Term Memory】更新主題統計 → 自動儲存到檔案
```

---

## 🚀 使用方式

1. 完成所有測驗（MBTI、Big Five、星座、Dark Triad）
2. 進入「AI深度對談」頁面
3. 與諮商師開始對話
4. 系統會自動：
   - 分類每次對話主題
   - 偵測主題轉換
   - 統計關注領域
   - 提取個人關注點

## 📈 數據展示

### 左側欄（User Persona）
- **測驗結果**：MBTI、Big Five、星座、Dark Triad
- **對話關注點**：從對話提取的特質
- **Request Log**：對話歷程（含主題標籤）
- **討論主題分析**：視覺化統計圖

### 右側欄（Active Session）
- 即時對話內容
- 諮商師個性化回應
- 輸入表單

## 🎨 技術亮點

1. **三層記憶架構**：完整實作 Memory Copilot 設計模式
2. **智能分類**：LLM 自動判斷對話類別
3. **Session Memory 智能提取**：只注入相關主題的歷史對話
4. **視覺化追蹤**：長條圖顯示主題熱度
5. **脈絡感知**：主題轉換偵測提升連貫性
6. **動態學習**：User Persona 隨對話豐富
7. **色彩編碼**：快速識別對話類型
8. **跨 session 持久化**：Long-Term Memory 永久保存
9. **自動合併**：新舊數據智能合併，避免覆蓋

## 📁 資料儲存結構

### Long-Term Memory 檔案格式
**位置**：`data/memory_{MBTI類型}.json`

```json
{
  "user_traits": [
    "人際溝通困擾",
    "職涯方向迷茫",
    "時間管理挑戰"
  ],
  "topic_categories": [
    {
      "category": "職涯發展",
      "count": 8,
      "last_time": "14:30"
    },
    {
      "category": "情緒管理",
      "count": 5,
      "last_time": "15:45"
    }
  ],
  "last_updated": "2025-12-08 15:45:30"
}
```

### 資料持久化策略
- **儲存時機**：每次主題統計更新、離開頁面時
- **載入時機**：初始化 session state 時
- **合併邏輯**：新舊主題計數累加，特質去重合併
- **容錯處理**：檔案讀寫失敗靜默處理，不影響體驗

---

## 🔍 與傳統 Chatbot 的差異

| 特性 | 傳統 Chatbot | 本系統（Memory Copilot 架構） |
|-----|------------|---------------------------|
| **記憶深度** | 僅保留當次對話 | 三層記憶：短/中/長期 |
| **上下文理解** | 線性對話歷史 | 智能提取相關脈絡 |
| **個性化程度** | 基於當次對話 | 基於累積的人格模型 |
| **跨 session** | 無記憶 | 持久化儲存，累積學習 |
| **主題感知** | 無 | 自動分類與轉換偵測 |
| **Prompt 效率** | 塞入全部歷史 | 智能過濾相關內容 |

---

## 💻 核心函數說明

### Memory 管理
- `initialize_session_state()`：初始化三層記憶結構
- `load_long_term_memory()`：載入持久化數據
- `save_long_term_memory()`：儲存 Long-Term Memory
- `generate_session_memory()`：智能提取 Session Memory

### 對話處理
- `process_message()`：處理訊息 + 觸發記憶更新
- `generate_counselor_prompt()`：組合三層記憶生成 prompt
- `generate_conversation_summary()`：摘要 + 分類

### 主題分析
- `detect_topic_shift()`：偵測主題轉換
- `update_topic_statistics()`：更新統計 + 觸發儲存
- `extract_user_traits()`：提取關注點

---

**版本**: 3.0（Memory Copilot 完整實作）  
**更新日期**: 2025-12-08  
**架構參考**: Memory Copilot LLM 記憶系統
