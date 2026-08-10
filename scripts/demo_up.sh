#!/usr/bin/env bash
# Jarvis — presentation launcher. See docs/DEMO.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "  Jarvis demo"
echo "  -----------"
echo ""

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "  Created .env from .env.example"
  echo "  Set GEMINI_API_KEY in .env for live chat."
  echo ""
fi

python scripts/check_dev_env.py

if ! (echo >/dev/tcp/127.0.0.1/8787) 2>/dev/null; then
  echo "  Starting brain..."
  python scripts/run_brain.py &
  sleep 3
else
  echo "  Brain already on :8787"
fi

WEB="$ROOT/clients/web"
if [[ ! -d "$WEB/node_modules" ]]; then
  echo "  Installing web dependencies (first run)..."
  (cd "$WEB" && npm install)
fi

if ! (echo >/dev/tcp/127.0.0.1/5173) 2>/dev/null; then
  echo "  Starting web UI..."
  (cd "$WEB" && npm run dev) &
  sleep 4
else
  echo "  Web dev server already on :5173"
fi

echo ""
echo "  Open:   http://localhost:5173"
echo "  Health: http://localhost:8787/health"
echo "  Guide:  docs/DEMO.md"
echo ""

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:5173" || true
elif command -v open >/dev/null 2>&1; then
  open "http://localhost:5173" || true
fi
