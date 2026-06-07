# 部署到 Raspberry Pi 5（psyche-test.com）

架構：
```
瀏覽器 ──HTTPS──> Cloudflare 邊緣 ──加密 Tunnel──> cloudflared(Pi)
        └─> nginx(Pi) ─ /        → frontend/dist  (React 靜態檔)
                       └ /api/    → 127.0.0.1:8000 (uvicorn / FastAPI)
                                        └─ SQLite + Gemini API
```
- 不需 port forwarding、不怕 CGNAT / 浮動 IP
- HTTPS 由 Cloudflare 自動處理（不用 certbot）
- 三個服務都用 systemd 常駐：`personality`(uvicorn)、`nginx`、`cloudflared`

本資料夾檔案：
| 檔案 | 用途 | 放到 Pi 的位置 |
| --- | --- | --- |
| `personality.service` | uvicorn systemd 服務 | `/etc/systemd/system/personality.service` |
| `nginx-psyche-test.conf` | nginx 站台設定 | `/etc/nginx/sites-available/psyche-test` |
| `cloudflared-config.yml` | Tunnel 設定 | `~/.cloudflared/config.yml` |
| `backend.env.production.example` | 後端環境變數範本 | 複製成 `backend/.env` |

> 預設專案放在 Pi 的 `/home/keye/webapp`、使用者為 `keye`。若不同，請一併修改上面各檔內的路徑/使用者。

---

## 0. Pi 基礎環境（Raspberry Pi OS 64-bit）

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv git nginx
# Node.js LTS（給前端 build）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

## 1. 取得程式碼

```bash
mkdir -p /home/keye/webapp && cd /home/keye/webapp
git clone <你的 repo 網址> .
git checkout main        # 或你要部署的分支
```

## 2. 後端

```bash
cd /home/keye/webapp/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 建立 .env
cp ../deploy/backend.env.production.example .env
openssl rand -hex 32        # 把輸出填到 .env 的 SECRET_KEY
nano .env                   # 填 SECRET_KEY 與 GEMINI_API_KEY
```

啟用 uvicorn 服務：
```bash
sudo cp /home/keye/webapp/deploy/personality.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now personality
sudo systemctl status personality          # 應為 active (running)
curl http://127.0.0.1:8000/api/health      # 應回 {"ok":true}
```

## 3. 前端

```bash
cd /home/keye/webapp/frontend
npm install
npm run build          # 產生 dist/
```
> 前端 API 全用相對路徑 `/api/...`，與後端同網域，**不需任何環境變數或改設定**。
> 若 Pi build 時記憶體吃緊，可在自己電腦 build 完，把 `dist/` 上傳到 Pi 同位置。

## 4. nginx

```bash
sudo cp /home/keye/webapp/deploy/nginx-psyche-test.conf /etc/nginx/sites-available/psyche-test
sudo ln -s /etc/nginx/sites-available/psyche-test /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default     # 移除預設站台
sudo nginx -t && sudo systemctl reload nginx
```
（讓 nginx 讀得到 dist：確認 `/home/keye` 對 `www-data` 可進入，必要時 `chmod o+x /home/keye`。）

## 5. Cloudflare Tunnel

前提：網域 `psyche-test.com` 已在 Cloudflare（你已完成）。

```bash
# 裝 cloudflared (arm64)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

cloudflared tunnel login                 # 瀏覽器授權 psyche-test.com
cloudflared tunnel create personality    # 產生 ~/.cloudflared/<tunnel-id>.json

# 設定檔
cp /home/keye/webapp/deploy/cloudflared-config.yml ~/.cloudflared/config.yml
nano ~/.cloudflared/config.yml           # 把 <tunnel-id> 換成實際檔名 id

# 綁定 DNS（在 Cloudflare 自動建立 CNAME）
cloudflared tunnel route dns personality psyche-test.com
cloudflared tunnel route dns personality www.psyche-test.com

# 裝成開機服務
# 注意：service install 以 root 執行，會找 /etc/cloudflared/config.yml，
# 不是你家目錄的 ~/.cloudflared/config.yml，所以要先複製過去。
sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/config.yml /etc/cloudflared/config.yml
sudo cloudflared service install
sudo systemctl enable --now cloudflared
sudo systemctl status cloudflared
```
> `config.yml` 裡的 `credentials-file:` 指向 `/home/keye/.cloudflared/<id>.json` 即可，root 讀得到，不必搬移那個憑證檔。

## 6. 驗證

開瀏覽器到 `https://psyche-test.com` —— 應看到網站、能做測驗、chatbot 串流正常。

---

## 日常維運

**更新部署：**
```bash
cd /home/keye/webapp && git pull
# 後端有改：
cd backend && source .venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart personality
# 前端有改：
cd ../frontend && npm install && npm run build
# nginx 直接讀 dist，不必 reload；改了 nginx 設定才需 sudo systemctl reload nginx
```

**看日誌：**
```bash
sudo journalctl -u personality -f      # 後端
sudo journalctl -u cloudflared -f      # tunnel
sudo tail -f /var/log/nginx/error.log  # nginx
```

**備份**（重要：SQLite 與聊天紀錄）：
```bash
cp /home/keye/webapp/backend/personality_paradox.db ~/backup/pp-$(date +%F).db
tar czf ~/backup/chat-$(date +%F).tgz /home/keye/webapp/backend/data/chat_histories
```

## Cloudflare 後台建議設定
- SSL/TLS 模式設 **Full**（邊緣到 Pi 走 Tunnel 已加密）
- 開 **Always Use HTTPS**
- 視需要加 WAF / Rate Limiting 保護（免費方案有基本規則）
