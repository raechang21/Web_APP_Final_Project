# 從多元人格測驗到諮詢小助手

專案結合 MBTI、五大人格、星座、黑暗三角人格的互動式人格測驗與結果分析，旨在協助使用者透過多元人格評估工具，更全面地探索與理解自身人格特質。除此之外，系統整合 Gemini API，提供具有「類」專業心理諮詢師取向的個性化分析和 AI 對話。

## 技術架構
       
- `frontend/`: React + Vite
- `backend/`: FastAPI + SQLite
- `AI`：Gemini-3.1-flash-lite

## 安裝需求

請先確認電腦已安裝以下工具：

- Node.js 18+ and `npm`
- Python 3.10+ and `pip`

- Google AI Studio: API key

## 如何執行專案

建議使用兩個終端機視窗：一個執行後端，另一個執行前端。

### 1. 啟動後端

進入後端資料夾：

```bash
cd backend
```

建立虛擬環境：

#### Windows
```bash
python -m venv .venv
.venv/Scripts/activate
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

安裝套件，並建立 `.env` 檔案：

```bash
cp .env.example .env
pip install -r requirements.txt
```

Gemini API Key 設定：

將你的 API Key 複製到 `backend/.env`

啟動 FastAPI:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

後端啟動後，可以透過以下網址確認是否正常運作：

```text
http://localhost:8000/api/health
```

如果運作正常，應該會看到：

```json
{"ok": true}
```

Gemini API 連線檢查：

```text
http://localhost:8000/api/test-gemini
```

如果 Gemini 設定正常，應該會看到類似以下回應：

```json
{
  "status": "success",
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "response": "OK"
}
```

### 2. 啟動前端

開啟另一個終端機，進入前端資料夾，安裝前端依賴套件，啟動前端開發伺服器：

```bash
cd frontend
npm install
npm run dev
```

前端預設網址：

```text
http://localhost:5173
```

## 環境變數

後端的 `.env` 可以參考 `backend/.env.example` 建立：

```env
SECRET_KEY=change-me-to-a-long-random-string
FRONTEND_ORIGIN=http://localhost:5173
DATABASE_URL=sqlite:///./personality_paradox.db
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
SESSION_MAX_AGE=7200
```

## 預設連接埠

- 前端： `5173`
- 後端： `8000`

Vite 已設定將 /api 請求代理到：

```text
http://localhost:8000
```