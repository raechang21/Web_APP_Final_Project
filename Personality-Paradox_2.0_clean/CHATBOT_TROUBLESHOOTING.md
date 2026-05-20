# ChatBot 錯誤排解指南

## 常見錯誤：「抱歉，發生錯誤，請稍後再試」

### 原因分析

此錯誤通常發生在以下情況：

1. **Ollama 服務未啟動** ⭐ 最常見
2. gemma3:4b 模型未下載
3. 網路連線問題
4. Ollama 版本不相容

## 解決步驟

### 步驟 1：啟動 Ollama 服務

**必須執行此步驟！** 這是最常見的問題。

#### Windows:
```powershell
ollama serve
```

#### Mac/Linux:
```bash
ollama serve
```

**重要提示：**
- 保持終端機視窗開啟
- 看到 "Ollama is running" 訊息表示成功
- 不要關閉此終端機視窗

### 步驟 2：確認模型已下載

在**另一個**終端機視窗執行：

```bash
ollama list
```

如果沒有看到 `gemma3:4b`，執行：

```bash
ollama pull gemma3:4b
```

下載時間約 5-10 分鐘（模型大小約 2.7 GB）

### 步驟 3：測試連線

訪問診斷頁面：
```
http://127.0.0.1:5000/diagnostic
```

此頁面會自動檢查：
- ✅ Flask 應用狀態
- ✅ Ollama 服務狀態
- ✅ 模型可用性

### 步驟 4：重新嘗試

1. 確認 Ollama 服務正在運行
2. 重新整理 ChatBot 頁面
3. 發送測試訊息

## 完整啟動流程

### 首次使用

```bash
# 終端機 1：下載模型（只需執行一次）
ollama pull gemma3:4b

# 終端機 1：啟動 Ollama
ollama serve

# 終端機 2：啟動 Flask
cd "你的專案路徑"
python app_flask.py
```

### 日常使用

```bash
# 終端機 1：啟動 Ollama
ollama serve

# 終端機 2：啟動 Flask
python app_flask.py
```

## 錯誤訊息解讀

### ❌ "無法連接到 Ollama 服務"

**原因：** Ollama 未啟動

**解決：** 執行 `ollama serve`

### ❌ "model 'gemma3:4b' not found"

**原因：** 模型未下載

**解決：** 執行 `ollama pull gemma3:4b`

### ❌ "connection refused"

**原因：** Ollama 服務未在正確端口運行

**解決：** 
1. 關閉所有 Ollama 進程
2. 重新執行 `ollama serve`

## 改進後的錯誤訊息

### 舊版本
```
抱歉，發生錯誤，請稍後再試。
```

### 新版本
```
❌ 無法連接到 Ollama 服務

可能原因：
1. Ollama 服務未啟動
2. 網路連線問題

解決方法：
• 開啟終端機執行：ollama serve
• 確認 Flask 應用正在運行
• 重新整理頁面後再試
```

## 系統狀態檢查清單

使用前請確認：

- [ ] Ollama 已安裝（執行 `ollama --version`）
- [ ] gemma3:4b 模型已下載（執行 `ollama list`）
- [ ] Ollama 服務正在運行（終端機顯示 "Ollama is running"）
- [ ] Flask 應用正在運行（訪問 http://127.0.0.1:5000）
- [ ] 已完成所有測驗（MBTI、Big Five、星座）

## 進階診斷

### 檢查 Ollama 進程

**Windows:**
```powershell
Get-Process -Name ollama
```

**Mac/Linux:**
```bash
ps aux | grep ollama
```

### 手動測試 Ollama

```bash
ollama run gemma3:4b "你好"
```

如果返回中文回應，表示 Ollama 正常運作。

### 檢查端口佔用

Ollama 預設使用 11434 端口：

**Windows:**
```powershell
netstat -ano | findstr :11434
```

**Mac/Linux:**
```bash
lsof -i :11434
```

## 已知問題

### 問題 1：Windows Defender 阻擋

**症狀：** Ollama 啟動後立即關閉

**解決：** 將 Ollama 加入 Windows Defender 例外清單

### 問題 2：記憶體不足

**症狀：** 模型載入緩慢或失敗

**解決：** 
- 確保至少 8 GB 可用 RAM
- 關閉其他大型應用程式

### 問題 3：網路代理問題

**症狀：** 無法下載模型

**解決：** 
```bash
# 設定代理（如需要）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
ollama pull gemma3:4b
```

## 快速參考

### 必要服務

| 服務 | 啟動命令 | 預設端口 | 狀態檢查 |
|------|---------|---------|---------|
| Ollama | `ollama serve` | 11434 | `ollama list` |
| Flask | `python app_flask.py` | 5000 | 訪問 http://127.0.0.1:5000 |

### 重要路徑

- 診斷頁面：`http://127.0.0.1:5000/diagnostic`
- ChatBot：`http://127.0.0.1:5000/chatbot`
- 對話歷史：`data/memory_*.json`

## 聯絡支援

如果問題仍未解決：

1. 訪問診斷頁面截圖
2. 複製終端機錯誤訊息
3. 記錄執行步驟
4. 提供系統資訊（OS、Python 版本）

## 更新日誌

### v2.1 - 錯誤處理改進
- ✅ 新增友善錯誤訊息
- ✅ 新增系統診斷頁面
- ✅ 改善 Ollama 連線錯誤處理
- ✅ 提供詳細排解步驟

---

**💡 記住：** 大部分問題都是因為忘記執行 `ollama serve`！
