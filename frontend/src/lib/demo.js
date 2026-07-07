// Live snapshot for standalone preview (no Frappe bench reachable).
//
// In production the SPA is served by Frappe, which injects `window.csrf_token`;
// there we hit the real whitelisted endpoints. In standalone Vite dev that global
// is absent, so we answer from this snapshot — numbers taken from the live ERPNext
// pull on 2026-07-07 (156 orders today, 244k total, etc.) plus the design dataset,
// so the preview is faithful. Set window.__OPS_LIVE__=true to force real calls,
// or window.__OPS_DEMO__=true to force the snapshot.
export function isDemo() {
  if (typeof window === "undefined") return false;
  if (window.__OPS_LIVE__ === true) return false;
  if (window.__OPS_DEMO__ === true) return true;
  return !window.csrf_token; // no Frappe session → snapshot
}

const HOME = {
  today: {
    period: "today", currency: "MAD",
    orders: 156, orders_delta_pct: 9,
    value: 29400, value_delta_pct: 9,
    funnel: { new: 156, confirmed: 121, dispatched: 96, delivered: 29 },
    rates: {
      confirmation: { value: 78, delta: 3.2 },
      delivery: { value: 71, delta: 1.8 },
      aov: { value: 188, delta: 4 },
      returns: { value: 9.4, delta: 0.6 },
    },
    cod: { collected: 5540, pending: 41270, overdue: 12100 },
    late: 23,
    week: [312, 358, 341, 402, 371, 394, 156],
    forecast: 430,
  },
  d7: {
    period: "d7", currency: "MAD",
    orders: 2612, orders_delta_pct: 6,
    value: 483000, value_delta_pct: 6,
    funnel: { new: 2612, confirmed: 1985, dispatched: 1812, delivered: 1244 },
    rates: {
      confirmation: { value: 76, delta: 1.1 },
      delivery: { value: 68, delta: -0.7 },
      aov: { value: 185, delta: 2 },
      returns: { value: 9.1, delta: -0.3 },
    },
    cod: { collected: 312000, pending: 171000, overdue: 34000 },
    late: 57,
    week: [312, 358, 341, 402, 371, 394, 156],
    forecast: null,
  },
  d30: {
    period: "d30", currency: "MAD",
    orders: 11480, orders_delta_pct: 14,
    value: 2120000, value_delta_pct: 14,
    funnel: { new: 11480, confirmed: 8610, dispatched: 7995, delivered: 7580 },
    rates: {
      confirmation: { value: 75, delta: 0.4 },
      delivery: { value: 66, delta: 2.1 },
      aov: { value: 185, delta: 6 },
      returns: { value: 9.6, delta: 0.2 },
    },
    cod: { collected: 1310000, pending: 402000, overdue: 89000 },
    late: 89,
    week: [312, 358, 341, 402, 371, 394, 156],
    forecast: null,
  },
};

function withDates(week) {
  const out = [];
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    out.push({ date: d.toISOString().slice(0, 10), count: week[6 - i] });
  }
  return out;
}

const ORDERS = [
  { id: "#247198", customer: "Lamiaa Lamiaa", city: "الدار البيضاء", amount: 174, status: "new", time: "10:12" },
  { id: "#247197", customer: "Faiza Khoudri", city: "الرباط", amount: 277, status: "new", time: "10:04" },
  { id: "J-001013", customer: "Fatima Zahra Laachari", city: "مراكش", amount: 169, status: "conf", time: "09:51" },
  { id: "#247195", customer: "Fatine Bartot", city: "طنجة", amount: 193, status: "conf", time: "09:36" },
  { id: "#247189", customer: "Hajar Bouchkou", city: "فاس", amount: 319, status: "conf", time: "09:10" },
  { id: "#247184", customer: "Vitalis Vitalis", city: "أكادير", amount: 324, status: "disp", time: "08:44" },
  { id: "#247169", customer: "Sanaa Drissi", city: "الدار البيضاء", amount: 424, status: "disp", time: "08:19" },
  { id: "#247166", customer: "Sara Z", city: "سلا", amount: 522, status: "disp", time: "08:02" },
  { id: "#247174", customer: "فدوى", city: "الدار البيضاء", amount: 159, status: "del", time: "07:58" },
  { id: "#247165", customer: "Sara Elouardi", city: "القنيطرة", amount: 288, status: "del", time: "07:40" },
  { id: "#247156", customer: "Manal Manal", city: "مكناس", amount: 377, status: "del", time: "07:22" },
  { id: "#246384", customer: "أمينة واموّل", city: "وجدة", amount: 129, status: "ret", time: "أمس" },
  { id: "#246202", customer: "برزيك رشيدة", city: "تطوان", amount: 204, status: "ret", time: "أمس" },
];

const DEPTS = {
  list: [
    { id: "conf", kpi: 78, kpi_unit: "%", count: 121, total: 156, trend: 3.2, target_pct: 92, on_track: true },
    { id: "wh", kpi: 96, kpi_unit: "", trend: 8, target_pct: 80, on_track: true },
    { id: "disp", kpi: 96, kpi_unit: "", stuck: 23, trend: 5, target_pct: 74, on_track: false },
    { id: "del", kpi: 71, kpi_unit: "%", count: 29, trend: 1.8, target_pct: 89, on_track: true },
    { id: "ret", kpi: 9.4, kpi_unit: "%", count: 34, trend: 0.6, target_pct: 63, on_track: false },
    { id: "cod", kpi: 41300, kpi_unit: "MAD", overdue: 12100, trend: 0, target_pct: 55, on_track: false },
    { id: "mkt", kpi: 29400, kpi_unit: "MAD", aov: 188, trend: 9, target_pct: 84, on_track: true },
  ],
  detail: {
    conf: {
      id: "conf",
      stats: [
        { l: "confirmed_today", v: 121, d: 11 }, { l: "awaiting", v: 27, d: null },
        { l: "rate", v: 78, unit: "%", d: null }, { l: "total", v: 156, d: 14 },
      ],
      bars: [289, 301, 266, 322, 298, 292, 121].map((c, i) => ({ date: "", count: c })),
      top: [
        { name: "سلمى الإدريسي", value: 38, pct: 95 },
        { name: "يوسف بناني", value: 33, pct: 82 },
        { name: "خديجة العلوي", value: 29, pct: 72 },
      ],
    },
  },
};

const TEAM = [
  {
    id: "conf", metric: "confirmed", needs_source: false,
    members: [
      { rank: 1, name: "سلمى الإدريسي", initials: "سا", value: 38, sub: "82%", pct: 95 },
      { rank: 2, name: "يوسف بناني", initials: "يب", value: 33, sub: "79%", pct: 82 },
      { rank: 3, name: "خديجة العلوي", initials: "خا", value: 29, sub: "77%", pct: 72 },
      { rank: 4, name: "أمين رشدي", initials: "أر", value: 21, sub: "71%", pct: 52 },
    ],
  },
  {
    id: "wh", metric: "picked", needs_source: false,
    members: [
      { rank: 1, name: "عمر الفاسي", initials: "عف", value: 31, sub: "1.8h", pct: 92 },
      { rank: 2, name: "حمزة الزياني", initials: "حز", value: 27, sub: "2.0h", pct: 78 },
      { rank: 3, name: "نادية شكري", initials: "نش", value: 22, sub: "2.3h", pct: 64 },
      { rank: 4, name: "كريم عزيز", initials: "كع", value: 16, sub: "2.6h", pct: 46 },
    ],
  },
  {
    id: "ret", metric: "closed", needs_source: false,
    members: [
      { rank: 1, name: "إيمان صابر", initials: "إص", value: 7, sub: "4.9d", pct: 88 },
      { rank: 2, name: "رشيد لمراني", initials: "رل", value: 5, sub: "5.6d", pct: 62 },
    ],
  },
];

const ALERTS = [
  { key: "stuck", severity: "red", count: 23, value: null, hours_ago: 1 },
  { key: "cod_overdue", severity: "red", count: null, value: 12100, hours_ago: 2 },
  { key: "no_confirm_call", severity: "orange", count: 12, value: null, hours_ago: 3 },
  { key: "return_rate", severity: "orange", count: null, value: 9.6, hours_ago: 5 },
  { key: "low_stock", severity: "blue", count: 4, value: null, hours_ago: 6 },
];

const STATUS_COUNT = { today: { all: 156, new: 27, conf: 121, disp: 96, del: 29, ret: 34 },
  d7: { all: 2612, new: 420, conf: 1985, disp: 1812, del: 1244, ret: 238 },
  d30: { all: 11480, new: 1870, conf: 8610, disp: 7995, del: 7580, ret: 1102 } };

export async function demoResolve(method, params = {}) {
  const p = params.period || "today";
  const m = method.split(".").pop();
  await new Promise((r) => setTimeout(r, 90)); // small latency for realistic loaders
  switch (m) {
    case "me":
      return { user: "owner@justyol.com", name: "Justyol Owner", initials: "JO",
        companies: ["Justyol"], roles: ["System Manager"] };
    case "home": {
      const h = HOME[p] || HOME.today;
      return { ...h, week: withDates(h.week) };
    }
    case "counts":
      return STATUS_COUNT[p] || STATUS_COUNT.today;
    case "list_orders": {
      let rows = ORDERS.slice();
      if (params.status && params.status !== "all") rows = rows.filter((o) => o.status === params.status);
      if (params.city && params.city !== "all") rows = rows.filter((o) => o.city === params.city);
      if (params.search) {
        const q = String(params.search).toLowerCase();
        rows = rows.filter((o) => o.id.toLowerCase().includes(q) || o.customer.toLowerCase().includes(q));
      }
      return rows;
    }
    case "cities":
      return [...new Set(ORDERS.map((o) => o.city))];
    case "get_order": {
      const o = ORDERS.find((x) => x.id === params.name) || ORDERS[0];
      const step = { new: 1, conf: 2, disp: 3, del: 4, ret: 3 }[o.status] || 1;
      return { id: o.id, customer: o.customer, city: o.city, phone: "+212 6 61 44 87 20",
        amount: o.amount, status: o.status, items_count: 2, courier: "Cathedis",
        tracking_url: "", attempts: 2, step_done: step };
    }
    case "list_departments":
      return DEPTS.list;
    case "department_detail":
      return DEPTS.detail[params.dept] || DEPTS.detail.conf;
    case "sections":
      return TEAM;
    case "list_alerts":
      return ALERTS;
    case "badge_count":
      return ALERTS.length;
    default:
      return null;
  }
}
