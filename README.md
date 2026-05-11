# Web_APP_Final_Project

這個專案是前後端分離架構：

- `frontend/`：React + Vite
- `backend/`：FastAPI + SQLite
- 聊天功能另外依賴本機 `Ollama`

## 啟動前準備

請先確認本機已安裝：

- Node.js 18+ 與 `npm`
- Python 3.10+ 與 `pip`
- 如果要使用聊天功能：`Ollama`

## 專案啟動方式

建議開兩個終端機，分別跑後端與前端。

### 1. 啟動後端

先進入後端資料夾，建立虛擬環境、安裝套件，並建立 `.env`：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
```

啟動 FastAPI：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

後端啟動後可用下面網址確認：

```text
http://localhost:8000/api/health
```

如果正常，會看到：

```json
{"ok": true}
```

### 2. 啟動前端

開另一個終端機：

```bash
cd frontend
npm install
npm run dev
```

前端預設網址：

```text
http://localhost:5173
```

## 聊天功能的額外設定

聊天功能會呼叫本機的 Ollama，預設模型是 `gemma3:4b`。如果你要使用聊天頁面，請先執行：

```bash
ollama serve
```

再下載模型：

```bash
ollama pull gemma3:4b
```

確認 Ollama 是否可用：

```text
http://localhost:8000/api/test-ollama
```

## 環境變數

後端 `.env` 可參考 `backend/.env.example`：

```env
SECRET_KEY=change-me-to-a-long-random-string
FRONTEND_ORIGIN=http://localhost:5173
DATABASE_URL=sqlite:///./personality_paradox.db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
SESSION_MAX_AGE=7200
```

一般本機開發直接使用這份預設值即可。

## 開發時的埠號對應

- 前端：`5173`
- 後端：`8000`
- Ollama：`11434`

前端 Vite 已經把 `/api` 代理到 `http://localhost:8000`，所以前後端一起啟動後即可正常連線。

## 常見問題

### 1. 前端打得開，但 API 失敗

先確認後端是否有啟動：

```text
http://localhost:8000/api/health
```

### 2. 聊天功能顯示無法連到 Ollama

請確認：

- 已安裝 Ollama
- 已執行 `ollama serve`
- 已下載 `gemma3:4b`

### 3. 第一次啟動時找不到資料庫

這是正常的，後端啟動時會自動建立 SQLite 資料庫檔案：

```text
backend/personality_paradox.db
```
