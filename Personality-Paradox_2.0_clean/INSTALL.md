# 安裝與執行指南

## 📋 前置需求

在開始之前，請確保你的電腦已安裝：
- Python 3.8 或更高版本
- 8 GB 以上記憶體（推薦）
- 穩定的網路連線（首次下載模型需要）

---

## 🚀 快速開始（3 步驟）

### 步驟 1: 安裝 Ollama

#### Windows
1. 前往 [Ollama 官網](https://ollama.ai/download)
2. 下載 Windows 版本
3. 執行安裝程式，按照指示完成安裝
4. 安裝完成後，Ollama 會自動在背景執行

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 步驟 2: 下載 AI 模型

開啟終端機（命令提示字元），執行：

```bash
ollama pull gemma3:4b
```

⏳ 這個步驟可能需要幾分鐘，請耐心等待下載完成。

### 步驟 3: 安裝 Python 套件並執行

```bash
# 進入專案資料夾
cd Personality-Paradox_3.0

# 安裝所需套件
pip install -r requirements_flask.txt

# 啟動 Flask 應用程式
python app_flask.py
```

🎉 完成！瀏覽器會自動開啟應用程式（通常是 http://127.0.0.1:5000）

或手動訪問：http://127.0.0.1:5000

---

## 🔧 疑難排解

### 問題 1: `ollama` 指令找不到

**解決方法:**
- Windows: 重新開機，讓系統環境變數生效
- macOS/Linux: 檢查是否正確安裝，執行 `which ollama` 確認路徑

### 問題 2: 應用程式無法連接到 Ollama

**解決方法:**
```bash
# 手動啟動 Ollama 服務
ollama serve
```

然後在另一個終端機視窗執行 `python app_flask.py`

### 問題 3: 中文顯示亂碼

**解決方法:**
- 確保終端機編碼設定為 UTF-8
- Windows 使用者可以在 PowerShell 執行：
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### 問題 4: Flask 無法啟動

**解決方法:**
- 確認是否有其他程式佔用 5000 端口
- Windows: `netstat -ano | findstr :5000`
- 修改 config.py 中的 PORT 設定

### 問題 5: Session 資料殘留

**解決方法:**
- 點擊左上角 Logo 或「重新開始」按鈕清除 Session
- 刪除 `flask_session/` 資料夾內的檔案

### 問題 6: 記憶體不足

**解決方法:**
- 關閉其他占用記憶體的程式
- 如果仍有問題，可以考慮使用更小的模型（但分析品質可能下降）

---

## 📦 套件說明

主要使用的 Python 套件：
- `streamlit`: Web 應用框架
- `plotly`: 互動式圖表
- `pandas`: 資料處理
- `reportlab`: PDF 生成
- `ollama-python`: Ollama API 客戶端

完整清單請參考 `requirements.txt`

---

## 🎯 首次使用建議

1. **完整體驗流程**: 建議完成所有測驗（包含黑暗三角）以獲得最完整的分析
2. **AI 分析速度**: 首次生成可能需要 5-10 秒，後續會更快
3. **測驗時間**: 完整流程約 10-15 分鐘
4. **結果保存**: 可使用「匯出文字」或「匯出 PDF」功能保存結果

---

## 💡 使用技巧

- **黑暗三角測驗**: 可選擇跳過，不影響其他分析
- **重新測驗**: 點擊「重新測驗」可清除所有資料重新開始
- **AI 對談**: 結果頁面提供 ChatBot 功能，可針對結果提問

---

## 🆘 需要幫助？

如果遇到其他問題：
1. 檢查 `README.md` 的完整說明
2. 確認所有步驟都正確執行
3. 查看終端機的錯誤訊息

---

## ⚠️ 注意事項

- 本系統僅供自我探索與學習用途
- 測驗結果不構成專業心理評估
- 如需專業諮詢，請尋求合格心理師協助
- 請勿將黑暗三角結果用於標籤或歧視他人

---

祝你使用愉快！🎉
