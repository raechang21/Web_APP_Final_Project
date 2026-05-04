# 🧠 Memory Copilot 三層記憶架構 - 完整實作

## 架構總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                    Personality Paradox ChatBot                  │
│                   Memory Copilot 記憶系統實作                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Working Memory  │      │  Session Memory  │      │ Long-Term Memory │
│    (短期記憶)     │      │    (中期記憶)     │      │    (長期記憶)     │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        │                         │                         │
        │                         │                         │
        ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  最近數輪對話     │      │  當次會話摘要     │      │  持續累積特質     │
│                  │      │                  │      │                  │
│ • chat_messages  │      │ • request_log    │      │ • user_traits    │
│   (完整內容)      │      │   (主題分類)      │      │ • topic_stats    │
│                  │      │                  │      │                  │
│ • 最近5輪        │      │ • 智能過濾       │      │ • 檔案持久化      │
│ • 即時互動       │      │ • 相關脈絡       │      │ • 跨session      │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        │                         │                         │
        └─────────────┬───────────┴─────────────────────────┘
                      ▼
              ┌───────────────┐
              │  AI Prompt    │
              │   組合生成     │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ 諮商師回應     │
              └───────────────┘
```

## 📝 Working Memory（短期記憶）

### 資料來源
- **最近輸對話**：用戶與 AI 的即時互動

### UI 展示位置
- **Active Session**（右側主區域）
- 即時顯示對話氣泡

### 資料結構
```python
st.session_state.chat_messages = [
    {
        "role": "user",
        "content": "我該如何提升我的盡責性？",
        "timestamp": "14:30"
    },
    {
        "role": "assistant",
        "content": "根據您的測驗結果...",
        "timestamp": "14:30"
    }
]
```

### 在 Prompt 中的應用
```python
# 最近 5 輪完整對話
conversation_history = "\n\n".join([
    f"{'來諮商者' if m['role'] == 'user' else '諮商師'}: {m['content']}"
    for m in st.session_state.chat_messages[-5:]
])
```

### 清除策略
- 點擊「🗑️ 清除對話」按鈕：清空
- **不影響** Long-Term Memory

---

## 🔄 Session Memory（中期記憶）

### 資料來源
- **當次會話的摘要**：每輪對話自動生成 10-15 字摘要
- **主題分類**：自動歸類到 6 大類別

### UI 展示位置
- **Request Log**（左側欄）
- 彩色主題標籤 + 時間戳記

### 資料結構
```python
st.session_state.request_log = [
    {
        "summary": "探討轉換跑道的可能性",
        "category": "職涯發展",
        "timestamp": "14:30"
    },
    {
        "summary": "如何改善拖延習慣",
        "category": "自我成長",
        "timestamp": "14:45"
    }
]
```

### 智能提取機制（核心創新）
```python
def generate_session_memory() -> str:
    """
    只提取與當前主題相關的歷史對話
    避免 prompt 過載，提升相關性
    """
    current_topic = st.session_state.current_topic  # 例如："職涯發展"
    
    # 從歷史中篩選同類別對話
    related_conversations = [
        log['summary'] 
        for log in st.session_state.request_log 
        if log['category'] == current_topic
    ]
    
    return f"您之前在「{current_topic}」主題討論過:\n" + \
           "\n".join([f"- {conv}" for conv in related_conversations[-3:]])
```

### 在 Prompt 中的應用
```
【Session Memory - 相關對話脈絡】
您之前在「職涯發展」主題討論過:
- 探討轉換跑道的可能性
- 分析自己的職業優勢
```

### 保留策略
- 最多顯示 10 條最近記錄
- 智能過濾：只注入相關主題

---

## 💾 Long-Term Memory（長期記憶）

### 資料來源
- **持續累積**：跨多次對話
- **跨對話**：檔案持久化

### UI 展示位置
- **User Persona**（左側欄上半部）
  - 對話中發現的關注點
- **討論主題分析**（左側欄下半部）
  - 視覺化長條圖

### 資料結構（Session State）
```python
# 對話中提取的關注點
st.session_state.user_traits = [
    "人際溝通困擾",
    "職涯方向迷茫",
    "時間管理挑戰"
]

# 主題統計
st.session_state.topic_categories = [
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
]
```

### 資料結構（檔案持久化）
**檔案路徑**：`data/memory_{MBTI類型}.json`

```json
{
  "user_traits": [
    "人際溝通困擾",
    "職涯方向迷茫"
  ],
  "topic_categories": [
    {
      "category": "職涯發展",
      "count": 8,
      "last_time": "14:30"
    }
  ],
  "last_updated": "2025-12-08 15:45:30"
}
```

### 持久化機制
```python
# 【載入】初始化時
def load_long_term_memory():
    memory_file = f"data/memory_{MBTI}.json"
    # 讀取 JSON → 合併到 session_state
    # 新舊數據智能合併，計數累加

# 【儲存】三個時機
1. 每次更新主題統計時：update_topic_statistics()
2. 離開頁面時：返回按鈕
3. 提取新特質時：extract_user_traits()
```

### 在 Prompt 中的應用
```
【來諮商者的人格特質 - Long-Term Memory】
MBTI: INTJ (建築師)
Big Five 特質: ...

對話中觀察到的關注點:
- 人際溝通困擾
- 職涯方向迷茫

您最常討論的議題:
- 職涯發展 (8次)
- 情緒管理 (5次)
```

### 保留策略
- **永久保存**：寫入檔案
- **跨 session 累積**：下次進入自動載入
- **自動合併**：新舊計數累加

---

## 🔄 三層記憶的協作流程

### 1️⃣ 用戶發送訊息
```
用戶: "我想轉換職業跑道，但不知道適合什麼"
```

### 2️⃣ 記錄到 Working Memory
```python
st.session_state.chat_messages.append({
    "role": "user",
    "content": "我想轉換職業跑道...",
    "timestamp": "14:30"
})
```

### 3️⃣ 組合三層記憶生成 Prompt
```python
prompt = f"""
【Long-Term Memory】
MBTI: INTJ (建築師)
Big Five: 開放性 4.5/6.0, 盡責性 5.2/6.0...
對話關注點: 職涯方向迷茫, 人際溝通困擾

【Session Memory】
您之前在「職涯發展」主題討論過:
- 探討自己的職業優勢
- 分析轉職的風險

【Working Memory】
最近對話:
來諮商者: 我想轉換職業跑道，但不知道適合什麼
"""
```

### 4️⃣ AI 生成回應
```
諮商師: "根據您的 INTJ 特質和高盡責性，您適合需要策略思維..."
```

### 5️⃣ 記錄回應 + 更新記憶

**Working Memory 更新：**
```python
st.session_state.chat_messages.append({
    "role": "assistant",
    "content": "根據您的 INTJ 特質...",
})
```

**Session Memory 更新：**
```python
# 生成摘要 + 分類
generate_conversation_summary(user_msg, ai_msg)
# → 加入 request_log: "[職涯發展] 探討轉職方向"
```

**Long-Term Memory 更新：**
```python
# 提取特質（每3輪）
extract_user_traits()
# → 加入 user_traits: "轉職焦慮"

# 更新主題統計
update_topic_statistics("職涯發展")
# → topic_categories["職涯發展"].count += 1

# 自動儲存到檔案
save_long_term_memory()
```

---

## 🎯 Memory Copilot 架構優勢

### 1. **脈絡精準度提升**
- ❌ 傳統：塞入全部歷史對話（無關內容干擾）
- ✅ 本系統：Session Memory 智能過濾相關主題

### 2. **個性化深度增強**
- ❌ 傳統：每次對話從零開始
- ✅ 本系統：Long-Term Memory 累積人格模型

### 3. **Token 使用效率**
- ❌ 傳統：prompt 過長，浪費 token
- ✅ 本系統：三層分級，按需載入

### 4. **用戶體驗優化**
- ❌ 傳統：AI 沒有「記憶」
- ✅ 本系統：AI 記得用戶的關注點和討論歷史

### 5. **跨 Session 連續性**
- ❌ 傳統：每次重新開始
- ✅ 本系統：持久化儲存，長期累積

---

## 📊 實作對照表

| Memory Copilot 概念 | 本專案實作 | 檔案位置 |
|-------------------|-----------|---------|
| **Working Memory** | `chat_messages` | `pages/chatbot.py:85-92` |
| **Session Memory** | `generate_session_memory()` | `pages/chatbot.py:659-680` |
| **Long-Term Memory** | `user_traits` + 檔案 | `pages/chatbot.py:717-795` |
| **Topic Routing** | `generate_conversation_summary()` | `pages/chatbot.py:564-598` |
| **Topic Shift Detection** | `detect_topic_shift()` | `pages/chatbot.py:619-657` |
| **Memory Storage** | `save_long_term_memory()` | `pages/chatbot.py:757-775` |
| **Memory Retrieval** | `load_long_term_memory()` | `pages/chatbot.py:718-755` |

---

## 🚀 使用建議

### 測試三層記憶
1. **第一次對話**：討論「職涯發展」
   - Working Memory 記錄即時對話
   - Session Memory 開始累積摘要
   - Long-Term Memory 提取關注點

2. **切換主題**：討論「情緒管理」
   - Session Memory 自動切換，只載入情緒相關歷史
   - Long-Term Memory 更新主題統計

3. **返回舊主題**：再次討論「職涯發展」
   - Session Memory 智能載入之前的職涯討論
   - AI 回應會參考上次的對話脈絡

4. **離開並重新進入**
   - Long-Term Memory 從檔案載入
   - 主題統計、關注點全部保留
   - 跨 session 連續性

### 查看記憶檔案
```bash
# 檔案位置
data/memory_INTJ.json  # 依 MBTI 類型命名

# 檔案內容
{
  "user_traits": ["職涯迷茫", "溝通困擾"],
  "topic_categories": [
    {"category": "職涯發展", "count": 8}
  ],
  "last_updated": "2025-12-08 15:45:30"
}
```

---

**架構設計**: Memory Copilot 三層記憶系統  
**實作完成度**: 100%  
**版本**: 3.0  
**更新日期**: 2025-12-08
