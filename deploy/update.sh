#!/usr/bin/env bash
#
# 一鍵更新部署。
# 會 git pull，然後依「這次改到哪幾層」自動：
#   - 後端相依變了 → pip install
#   - 後端程式變了 → 重啟 personality
#   - 前端變了     → (必要時 npm install) + npm run build
#   - nginx 設定變 → 複製到 /etc 並 reload nginx
#   - cloudflared 設定變 → 只提醒（含 tunnel-id，不自動覆蓋）
#
# 用法（在 Pi 上）：
#   bash ~/webapp/deploy/update.sh
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend"
VENV="$BACKEND_DIR/.venv"
NGINX_CONF_SRC="$REPO_DIR/deploy/nginx-psyche-test.conf"
NGINX_CONF_DST="/etc/nginx/sites-available/psyche-test"

info() { echo -e "\033[1;34m▶ $*\033[0m"; }
ok()   { echo -e "\033[1;32m✔ $*\033[0m"; }
warn() { echo -e "\033[1;33m! $*\033[0m"; }

OLD=$(git rev-parse HEAD)
info "拉取最新程式碼…"
git pull --ff-only
NEW=$(git rev-parse HEAD)

if [ "$OLD" = "$NEW" ]; then
  ok "已經是最新版，沒有需要更新的東西。"
  exit 0
fi

CHANGED=$(git diff --name-only "$OLD" "$NEW")
echo "本次變更檔案："
echo "$CHANGED" | sed 's/^/    /'

changed() { echo "$CHANGED" | grep -qE "$1"; }

RESTART_BACKEND=false

# --- 後端 ---
if changed '^backend/requirements\.txt$'; then
  info "requirements.txt 有變動，安裝後端套件…"
  "$VENV/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"
  RESTART_BACKEND=true
fi
if changed '^backend/'; then
  RESTART_BACKEND=true
fi
if $RESTART_BACKEND; then
  info "重啟後端 (personality)…"
  sudo systemctl restart personality
  ok "後端已重啟"
fi

# --- 前端 ---
if changed '^frontend/'; then
  if changed '^frontend/(package\.json|package-lock\.json)$'; then
    info "前端相依有變動，npm install…"
    ( cd "$FRONTEND_DIR" && npm install )
  fi
  info "重新 build 前端…"
  ( cd "$FRONTEND_DIR" && npm run build )
  ok "前端已重新 build（nginx 直接讀 dist，不需 reload）"
fi

# --- nginx 設定 ---
if changed '^deploy/nginx-.*\.conf$'; then
  info "nginx 設定有變動，套用…"
  sudo cp "$NGINX_CONF_SRC" "$NGINX_CONF_DST"
  sudo nginx -t && sudo systemctl reload nginx
  ok "nginx 已 reload"
fi

# --- cloudflared 設定（含 tunnel-id，不自動覆蓋）---
if changed '^deploy/cloudflared-config\.yml$'; then
  warn "deploy/cloudflared-config.yml 範本有更新。"
  warn "因為實際使用的 ~/.cloudflared/config.yml 含你的 <tunnel-id>，不自動覆蓋。"
  warn "請比對差異、手動更新後再套用："
  warn "  sudo cp ~/.cloudflared/config.yml /etc/cloudflared/config.yml && sudo systemctl restart cloudflared"
fi

ok "更新完成 → https://psyche-test.com"
