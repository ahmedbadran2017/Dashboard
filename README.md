# Justyol Ops Dashboard

Mobile-first **operations dashboard** for Justyol, installable as a **PWA** on the phone. Bilingual **Arabic (RTL, default) / English (LTR)**, light/dark theme, reading live numbers from **ERPNext**.

Built as a **Frappe app** (same stack as the other Justyol portals): Vue 3 + Vite + Tailwind SPA frontend, whitelisted Python API endpoints that aggregate Sales Order data server-side.

## Screens

| Tab | What it shows |
|-----|---------------|
| **الرئيسية / Home** | Order count + sales value (with deltas), 7-day sparkline, end-of-day forecast, order funnel (new → confirmed → dispatched → delivered), 4 rate cards (confirmation / delivery / AOV / returns), COD collected vs pending, late/stuck strip, daily report actions |
| **الأقسام / Departments** | 7 departments with live headline KPIs + daily-target progress; tap for a detail view (2×2 stats, 7-day trend, top performers) |
| **الأوردرات / Orders** | Filterable order list (status / city / search) with per-status counts; tap an order for the detail sheet (timeline, WhatsApp, tracking) |
| **الفريق / Team** | Per-agent leaderboards (confirmation is live via `custom_allocated_to`) |
| **التنبيهات / Alerts** | Live operational exceptions (stuck orders, overdue COD, confirmation backlog, return-rate spike, low stock) |

## Data mapping (live ERPNext)

All KPIs derive from `tabSales Order` custom fields (see `ops_dashboard/api/_base.py`):

- **Funnel / rates** — `custom_sales_status` (Confirmed…), `custom_logistics_status` (Delivered/Returned/Shipped…), `custom_track_shipment_status`, `custom_shipped_at`
- **COD collected vs pending** — carrier remittance reference (`CATH…` / `RDF…`) present on the Sales Order / Invoice. This mirrors the accounting portal's `cod.py` — the authoritative "carrier remitted the cash" signal. Wire the invoice-ref join in `_cod()` if you want it identical to the accounting portal's collected figure.
- **Cities** — `custom_shipping_city` · **Team** — `custom_allocated_to`
- Targets live in `api/departments.py::TARGETS` — edit to retune (or move to a Settings doctype later).

## Install (on your bench)

```bash
cd ~/frappe-bench
# get the app onto the bench (copy this folder into apps/, or push to git and get-app)
bench get-app ops_dashboard /path/to/ops_dashboard      # or: cp -r … apps/ops_dashboard
bench --site <your-site> install-app ops_dashboard
bench build --app ops_dashboard
bench --site <your-site> clear-cache
```

The SPA is served at **`/ops/home`**. Log in with any ERPNext user that has dashboard access; open on the phone and **Add to Home Screen** to install the PWA.

## Develop the frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:8082/ops/home
```

- With **no bench reachable**, the app runs on a **live snapshot** (`src/lib/demo.js`) — real numbers from the 2026-07-07 ERPNext pull + the design dataset — so every screen renders standalone. Force it with `window.__OPS_DEMO__ = true`.
- With a **bench on :8000**, Vite proxies `/api`; set `window.__OPS_LIVE__ = true` (or just have a Frappe session) to hit the real endpoints.

Build into the app: `npm run build` → emits `ops_dashboard/public/ops_dashboard.bundle.{js,css}`.

## PWA

- `public/manifest.webmanifest` — installable, standalone, portrait, RTL, Justyol icons (`public/icons/`)
- `public/sw.js` — service worker: app shell stale-while-revalidate, API network-first with cached fallback (last-known numbers offline)
- Registered from `templates/pages/ops.html`

## Design

Recreated from the Claude Design handoff (`Justyol Ops Dashboard`) — high-fidelity, Justyol DS tokens (`src/index.css`), Tajawal (AR) / Instrument Sans (EN), brand orange `#ff9500`.
