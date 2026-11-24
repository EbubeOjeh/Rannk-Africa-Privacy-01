export const fmtScore = (n, decimals = 1) =>
  n === null || n === undefined ? '—' : Number(n).toFixed(decimals);

// Render a score on the /100 scale, e.g. "73.4 / 100".
export const fmtScore100 = (n) =>
  n === null || n === undefined ? '— / 100' : `${Number(n).toFixed(1)} / 100`;

// Render a sub-score on its category's max, e.g. "8 / 10" or "32.5 / 40".
export const fmtScoreOf = (n, outOf, decimals = 1) =>
  n === null || n === undefined
    ? `— / ${outOf}`
    : `${Number(n).toFixed(decimals)} / ${outOf}`;

export const fmtRank = (n) => (n ? `#${n}` : '—');
export const fmtNumber = (n) => Intl.NumberFormat().format(Number(n || 0));
export const fmtPercent = (n, decimals = 0) =>
  n === null || n === undefined ? '—' : `${(Number(n) * 100).toFixed(decimals)}%`;
