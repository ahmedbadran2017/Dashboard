// Number / currency formatting. Numerals are always rendered LTR (the .num class)
// so they read correctly inside RTL Arabic copy.

export function n(v) {
  return Number(v || 0).toLocaleString("en-US");
}

// Compact money: 29,400 → "29.4K", 2,120,000 → "2.12M". Used for the hero value,
// COD tiles and marketing KPIs.
export function money(v) {
  const x = Number(v || 0);
  if (Math.abs(x) >= 1_000_000) return (x / 1_000_000).toFixed(2).replace(/\.?0+$/, "") + "M";
  if (Math.abs(x) >= 1_000) return (x / 1_000).toFixed(1).replace(/\.0$/, "") + "K";
  return n(Math.round(x));
}

// Full money with thousands separators (for tiles that show exact MAD).
export function moneyFull(v) {
  return n(Math.round(Number(v || 0)));
}

export function pct(v, digits = 1) {
  return Number(v || 0).toFixed(digits).replace(/\.0$/, "") + "%";
}

// Signed delta with sign: +3.2, -0.4
export function signed(v, digits = 1) {
  const x = Number(v || 0);
  const s = x.toFixed(digits).replace(/\.0$/, "");
  return (x > 0 ? "+" : "") + s;
}

export function initials(name) {
  const parts = String(name || "?").trim().split(/\s+/);
  return parts.slice(0, 2).map((p) => p[0]).join("").toUpperCase() || "?";
}
