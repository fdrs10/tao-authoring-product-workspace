// Shared UI primitives: badges, market dots/legends (§26), CAP links (§23),
// formatting with strict NULL semantics (§11/§12).

export function el(tag, attrs = {}, ...children) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') n.className = v;
    else if (k === 'dataset') Object.assign(n.dataset, v);
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else if (k === 'html') n.innerHTML = v;
    else n.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null) continue;
    n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return n;
}

export const esc = (s) => String(s ?? '');

// NULL = not estimated -> em dash, never 0. 0 = explicit zero -> "0".
export function fmtHours(v) {
  if (v === null || v === undefined) return '—';
  return String(Number(v));
}

export function capLink(capId) {
  return el('span', { class: 'cap-link', dataset: { cap: capId },
    onclick: (e) => { e.stopPropagation(); window.dispatchEvent(new CustomEvent('open-cap', { detail: capId })); } },
    capId);
}

export function moscowBadge(v) {
  if (!v) return el('span', { class: 'dim' }, '—');
  return el('span', { class: `badge moscow-${v.toLowerCase().replace("'", '')}` }, v);
}

export function admissionBadge(v) {
  if (!v) return el('span', { class: 'badge admission-UNSET', title: 'Roadmap Admission is UNSET (Product undecided)' }, 'UNSET');
  return el('span', { class: `badge admission-${v.replace(' ', '\\.')}` }, v);
}

export function reviewBadge(v) {
  if (!v) return null;
  if (v === 'PRODUCT_SCOPE_REVIEW_REQUIRED')
    return el('span', { class: 'badge review', title: 'Marked for Product scope review (Phase 1 audit)' }, 'SCOPE REVIEW');
  if (v === 'REVIEW_REQUIRED')
    return el('span', { class: 'badge review', title: 'Missing ideation sheet / review status — awaiting Product' }, 'REVIEW');
  if (v === 'AI PROPOSED · PRODUCT REVIEW REQUIRED')
    return el('span', { class: 'badge', title: v }, 'AI PROPOSED');
  return el('span', { class: 'badge', title: v }, v);
}

export function marketDotsFor(names, markets) {
  const wrap = el('span', { class: 'market-dots' });
  // colors by passed markets [{name,color}]
  const byName = new Map(markets.map((m) => [m.name, m.color]));
  for (const n of names || []) {
    const c = (n && n.name !== undefined) ? n.color : byName.get(n);
    const name = (n && n.name !== undefined) ? n.name : n;
    wrap.appendChild(el('span', { class: 'dot', style: `background:${c || '#999'}`, title: name }));
  }
  return wrap;
}

export function marketLegend(markets) {
  const box = el('div', { class: 'market-legend' }, el('strong', {}, 'Markets'));
  for (const m of markets)
    box.appendChild(el('span', { class: 'ml' },
      el('span', { class: 'dot', style: `background:${m.color}` }), m.name));
  return box;
}

export function notice(kind, msg) {
  return el('div', { class: `notice ${kind}` }, msg);
}

export function table(headers, rows) {
  const t = el('table', { class: 'compact' });
  const tr = el('tr', {}, headers.map((h) => el('th', {}, h)));
  t.appendChild(tr);
  for (const r of rows) t.appendChild(r);
  return t;
}
