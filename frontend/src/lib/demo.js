// Live snapshot for standalone preview (no Frappe bench reachable).
//
// Numbers taken from the live ERPNext pull on 2026-07-07 (156 orders today, 244k
// total, etc.) plus the design dataset, so the preview is faithful.
//
// DEFAULT IS LIVE. The snapshot is only reachable from a standalone Vite dev
// build (import.meta.env.DEV) with no Frappe session — the production bundle
// (import.meta.env.DEV === false, dead-code-eliminated) can NEVER fall into demo
// mode by accident, so real users always hit the real endpoints. Escape hatches:
//   window.__OPS_DEMO__ = true  → force the snapshot (e.g. demoing in prod)
//   window.__OPS_LIVE__ = true  → force real calls (e.g. dev proxied to a bench)
export function isDemo() {
  if (typeof window === "undefined") return false;
  if (window.__OPS_LIVE__ === true) return false;
  if (window.__OPS_DEMO__ === true) return true;
  return !!import.meta.env.DEV && !hasFrappeSession();
}

function hasFrappeSession() {
  return typeof window !== "undefined" && !!(window.csrf_token || window.frappe?.csrf_token);
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

function srcOf(id) {
  if (id.startsWith("YC-")) return "youcan";
  if (id.startsWith("J-")) return "landing";
  if (id.startsWith("SAL-")) return "agent";
  return "shopify";
}

const ORDERS = [
  { id: "#247198", customer: "Lamiaa Lamiaa", city: "الدار البيضاء", amount: 174, status: "new", time: "10:12" },
  { id: "#247197", customer: "Faiza Khoudri", city: "الرباط", amount: 277, status: "new", time: "10:04" },
  { id: "J-001013", customer: "Fatima Zahra Laachari", city: "مراكش", amount: 169, status: "conf", time: "09:51" },
  { id: "#247195", customer: "Fatine Bartot", city: "طنجة", amount: 193, status: "conf", time: "09:36" },
  { id: "#247189", customer: "Hajar Bouchkou", city: "فاس", amount: 319, status: "conf", time: "09:10" },
  { id: "YC-88231", customer: "Imane Berrada", city: "الدار البيضاء", amount: 246, status: "conf", time: "09:02" },
  { id: "#247184", customer: "Vitalis Vitalis", city: "أكادير", amount: 324, status: "disp", time: "08:44" },
  { id: "#247169", customer: "Sanaa Drissi", city: "الدار البيضاء", amount: 424, status: "disp", time: "08:19" },
  { id: "#247166", customer: "Sara Z", city: "سلا", amount: 522, status: "disp", time: "08:02" },
  { id: "#247174", customer: "فدوى", city: "الدار البيضاء", amount: 159, status: "del", time: "07:58" },
  { id: "SAL-0042", customer: "Khalid Amrani", city: "الرباط", amount: 210, status: "del", time: "07:45" },
  { id: "#247165", customer: "Sara Elouardi", city: "القنيطرة", amount: 288, status: "del", time: "07:40" },
  { id: "#247156", customer: "Manal Manal", city: "مكناس", amount: 377, status: "del", time: "07:22" },
  { id: "#246384", customer: "أمينة واموّل", city: "وجدة", amount: 129, status: "ret", time: "أمس" },
  { id: "#246202", customer: "برزيك رشيدة", city: "تطوان", amount: 204, status: "ret", time: "أمس" },
].map((o) => ({ ...o, source: srcOf(o.id) }));

// Live 30-day shape from the 2026-07-07 pull (8017 / 119 / 29 / 10), scaled per period.
const SOURCES = {
  today: [
    { id: "shopify", orders: 149, value: 28100, share: 95.5, conf_rate: 78, ret_rate: 9.3 },
    { id: "youcan", orders: 4, value: 610, share: 2.6, conf_rate: 71, ret_rate: 11.2 },
    { id: "landing", orders: 2, value: 390, share: 1.3, conf_rate: 88, ret_rate: 6.1 },
    { id: "agent", orders: 1, value: 300, share: 0.6, conf_rate: 95, ret_rate: 2.0 },
  ],
  d7: [
    { id: "shopify", orders: 2489, value: 460000, share: 95.3, conf_rate: 76, ret_rate: 9.0 },
    { id: "youcan", orders: 71, value: 13200, share: 2.7, conf_rate: 70, ret_rate: 10.8 },
    { id: "landing", orders: 38, value: 7300, share: 1.5, conf_rate: 86, ret_rate: 6.4 },
    { id: "agent", orders: 14, value: 2500, share: 0.5, conf_rate: 94, ret_rate: 2.2 },
  ],
  d30: [
    { id: "shopify", orders: 11060, value: 2043000, share: 96.3, conf_rate: 75, ret_rate: 9.5 },
    { id: "youcan", orders: 251, value: 46000, share: 2.2, conf_rate: 69, ret_rate: 11.0 },
    { id: "landing", orders: 121, value: 22800, share: 1.1, conf_rate: 85, ret_rate: 6.8 },
    { id: "agent", orders: 48, value: 8200, share: 0.4, conf_rate: 93, ret_rate: 2.5 },
  ],
};

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

// Build a plausible detail for ANY department (the standalone preview used to
// show Confirmation's data for every dept). Mirrors the backend's per-dept shape.
function genDetail(deptId) {
  const statsByDept = {
    conf: [
      { l: "confirmed_today", v: 121, d: 11 }, { l: "awaiting", v: 27, d: null },
      { l: "rate", v: 78, unit: "%", d: null }, { l: "total", v: 156, d: 14 },
    ],
    del: [
      { l: "delivered_today", v: 29, d: 4 }, { l: "dispatched", v: 96, d: null },
      { l: "rate", v: 71, unit: "%", d: null }, { l: "returned", v: 34, d: null },
    ],
    ret: [
      { l: "returned", v: 34, d: 5 }, { l: "rate", v: 9.4, unit: "%", d: null },
      { l: "delivered", v: 29, d: null }, { l: "total", v: 156, d: null },
    ],
  };
  const stats = statsByDept[deptId] || [
    { l: "orders", v: 156, d: 14 }, { l: "confirmed", v: 121, d: null },
    { l: "dispatched", v: 96, d: null }, { l: "delivered", v: 29, d: null },
  ];
  const barSeed = {
    conf: [289, 301, 266, 322, 298, 292, 121], wh: [270, 288, 250, 305, 281, 279, 96],
    disp: [255, 270, 240, 290, 262, 268, 96], del: [244, 262, 231, 280, 259, 251, 29],
    ret: [31, 28, 35, 26, 30, 33, 12], cod: [52, 61, 47, 70, 58, 64, 41],
    mkt: [26100, 28800, 25000, 30500, 28100, 27900, 29400],
  };
  const top = (DEPTS.detail[deptId] && DEPTS.detail[deptId].top) || [
    { name: "الدار البيضاء", value: 74, pct: 90 },
    { name: "الرباط", value: 71, pct: 84 },
    { name: "مراكش", value: 63, pct: 70 },
  ];
  return { id: deptId, stats, bars: withDates(barSeed[deptId] || barSeed.conf), top };
}

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

// ── Business metrics (real numbers from the 2026-07-07 pull) ──
const STOREFRONT = {
  today: { needs_config: false, sessions: 20800, carts: 802, checkouts: 229, conversion: 0.75, cart_rate: 3.9, checkout_rate: 1.1 },
  d7: { needs_config: false, sessions: 145709, carts: 5617, checkouts: 1602, conversion: 0.41, cart_rate: 3.9, checkout_rate: 1.1 },
  d30: { needs_config: false, sessions: 612000, carts: 23800, checkouts: 6800, conversion: 0.44, cart_rate: 3.9, checkout_rate: 1.1 },
};
const TOP_PRODUCTS = [
  { item_code: "SPICE12-GRY", name: "Set de 12 pots à épices avec support - Gris", qty: 185, value: 29611 },
  { item_code: "JAR12-1700", name: "Set de 12 bocaux carrés de conservation 1700 ml", qty: 183, value: 28671 },
  { item_code: "BOX4-6L", name: "Set de 4 boîtes de rangement 6 L", qty: 171, value: 20498 },
  { item_code: "CONT12-1205", name: "Set de 12 contenants carrés 1205 ml noirs", qty: 170, value: 20332 },
  { item_code: "SPICE12-ANT", name: "Set de 12 pots à épices anthracite 555 ml", qty: 155, value: 12716 },
  { item_code: "OIL2-750", name: "Set de 2 bouteilles d'huile 750 ml + support bois", qty: 64, value: 5895 },
];
const LOW_STOCK = [
  { item_code: "MCH100013-box", name: "MCH100013-box", qty: 10, sold: 66 },
  { item_code: "MAG360", name: "Magnésium bisglycinate 360 mg - 60 gélules", qty: 15, sold: 62 },
  { item_code: "TERLIK-39", name: "Chaussons Orthopédiques Unisexes - Vison / 39", qty: 26, sold: 51 },
  { item_code: "TERLIK-36", name: "Chaussons Orthopédiques Unisexes - Vison / 36", qty: 13, sold: 42 },
  { item_code: "SAC-MOODS", name: "Sac Bandoulière Femme MOODS - Brown", qty: 30, sold: 41 },
];
const CASH = {
  currency: "MAD", bank_total: 1173364, carrier_float: 453133, card_total: 662400,
  total: 2288897,
  accounts: [
    { name: "BMCE-…130355", bal: 918294, kind: "bank" },
    { name: "Kuveyttürk Credit Card …7778", bal: 476619, kind: "card" },
    { name: "Cathedis Transactions", bal: 453133, kind: "carrier" },
    { name: "Credit Card …332506", bal: 160000, kind: "card" },
    { name: "CIH-…950128", bal: 93535, kind: "bank" },
    { name: "Petty Cash", bal: 68550, kind: "bank" },
  ],
};
const PROFIT = {
  currency: "MAD", company: "Justyol Morocco", window: "30d",
  revenue: 396037, cogs: 185398, opex: 7246, gross: 210639, net: 203393, margin: 53.2,
  top_expenses: [
    { name: "Cost of Goods Sold", amount: 185398 },
    { name: "Mix Digital Marketing", amount: 7000 },
    { name: "Depreciation", amount: 217 },
    { name: "Round Off", amount: 29 },
  ],
  supplier_payable: 22103812,
};

export async function demoResolve(method, params = {}) {
  let p = params.period || "today";
  // custom range → nearest dataset by span (the real backend aggregates exactly)
  if (params.from_date && params.to_date) {
    const span = Math.round((new Date(params.to_date) - new Date(params.from_date)) / 86400000) + 1;
    p = span <= 1 ? "today" : span <= 10 ? "d7" : "d30";
  } else if (!HOME[p]) {
    p = "today";
  }
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
    case "counts": {
      if (params.source && params.source !== "all") {
        const rows = ORDERS.filter((o) => o.source === params.source);
        const by = (st) => rows.filter((o) => o.status === st).length;
        return { all: rows.length, new: by("new"), conf: by("conf"), disp: by("disp"), del: by("del"), ret: by("ret") };
      }
      return STATUS_COUNT[p] || STATUS_COUNT.today;
    }
    case "sources":
      return SOURCES[p] || SOURCES.today;
    case "list_orders": {
      let rows = ORDERS.slice();
      if (params.source && params.source !== "all") rows = rows.filter((o) => o.source === params.source);
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
      return genDetail(params.dept || "conf");
    case "sections":
      return TEAM;
    case "list_alerts":
      return ALERTS;
    case "badge_count":
      return ALERTS.length;
    case "storefront":
      return STOREFRONT[p] || STOREFRONT.d7;
    case "top_products":
      return TOP_PRODUCTS;
    case "low_stock":
      return LOW_STOCK;
    case "cash":
      return CASH;
    case "profit":
      return PROFIT;
    default:
      return null;
  }
}
