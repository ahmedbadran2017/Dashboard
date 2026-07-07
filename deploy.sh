#!/usr/bin/env bash
# Build the SPA, commit the refreshed bundle, and push.
# Run from the repo root: ./deploy.sh "optional commit message"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/frontend"

echo "▸ Building SPA…"
[ -d node_modules ] || npm install
npm run build

cd "$ROOT"
MSG="${1:-build: refresh SPA bundle}"

if git diff --quiet && git diff --cached --quiet; then
  echo "▸ Nothing changed — bundle already current."
  exit 0
fi

echo "▸ Committing…"
git add -A
git commit -m "$MSG"

echo "▸ Pushing…"
git push
echo "✓ Pushed. Now on the server: cd ~/frappe-bench/apps/ops_dashboard && git pull,"
echo "  then: bench --site admin.justyol.com clear-cache && bench restart (see DEPLOY.md)."
