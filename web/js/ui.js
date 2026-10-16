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

// §20 — compact Ideation filter layer. Presentation state ONLY: it never
// mutates Product Truth. Returns { bar, apply(baseCaps) } where apply filters
// a copy of the base list, updates the "Showing X of Y" note and returns the
// filtered array. `sources` is the governed source list for the Source filter.
export function capFilterBar({ markets, sources, decisions = [] }) {
  const state = { q: '', category: '', market: '', moscow: '', visibility: '',
    product_review: '', review_flag: '', admission: '', decision: '', source: '' };
  const sel = (key, title, options) => el('label', { class: 'f' }, title,
    el('select', { dataset: { f: key } },
      options.map(([v, l]) => el('option', { value: v }, l))));
  const countNote = el('span', { dataset: { testid: 'filter-count' }, class: 'small dim' });
  const search = el('input', {
    type: 'search', name: 'q', placeholder: 'Search CAP / name / description…',
    dataset: { f: 'q' }, style: 'min-width:200px',
  });
  const fbar = el('div', { class: 'filter-bar', dataset: { testid: 'ideation-filters' } },
    el('label', { class: 'f' }, 'Search', search),
    sel('category', 'Strategic category', [
      ['', 'Category · All'], ['Create & Design', 'Create & Design'],
      ['Manage & Govern', 'Manage & Govern'], ['Collaborate & Assure Quality', 'Collaborate & Assure Quality'],
      ['Standards & Portability', 'Standards & Portability'], ['AI-assisted Authoring', 'AI-assisted Authoring']]),
    sel('market', 'Market', [['', 'Market · All'], ...markets.map((m) => [m.name, m.name])]),
    sel('moscow', 'MoSCoW', [['', 'MoSCoW · All'], ['Must', 'Must'], ['Should', 'Should'], ['Could', 'Could'], ["Won't", "Won't"]]),
    sel('visibility', 'Visibility', [['', 'Visibility · All'], ['Shared / common core', 'Shared / common core'], ['Shared / market-configured', 'Shared / market-configured'], ['Market-specific', 'Market-specific']]),
    sel('product_review', 'Product review', [['', 'Product review · All'], ['Not reviewed yet', 'Not reviewed yet'], ['REVIEW_REQUIRED', 'REVIEW_REQUIRED'], ['CONFIRMED', 'CONFIRMED'], ['CONFIRMED_WITH_CHANGES', 'CONFIRMED_WITH_CHANGES'], ['REJECTED', 'REJECTED']]),
    sel('review_flag', 'Review flag', [['', 'Review flag · All'], ['AI PROPOSED · PRODUCT REVIEW REQUIRED', 'AI PROPOSED · PRODUCT REVIEW REQUIRED'], ['PRODUCT_SCOPE_REVIEW_REQUIRED', 'PRODUCT_SCOPE_REVIEW_REQUIRED'], ['REVIEW_REQUIRED', 'REVIEW_REQUIRED']]),
    sel('admission', 'Admission', [['', 'Admission · All'], ['UNSET', 'UNSET'], ['COMMITTED', 'COMMITTED'], ['CANDIDATE', 'CANDIDATE'], ['BACKLOG', 'BACKLOG'], ['DEFERRED', 'DEFERRED'], ['NOT PLANNED', 'NOT PLANNED']]),
    sel('decision', 'Decision', [['', 'Decision · All'], ...(decisions || []).map((d) => [d, d])]),
    sel('source', 'Source', [['', 'Source · All'], ...sources.map((s) => [s.source_id, `${s.source_id} · ${s.title}`])]),
    el('button', { dataset: { testid: 'filter-clear' }, onclick: () => {
      for (const k of Object.keys(state)) state[k] = '';
      fbar.querySelectorAll('select, input').forEach((n) => { n.value = ''; });
      if (apply.lastBase) apply(apply.lastBase);
    } }, 'Clear filters'),
    countNote);
  fbar.addEventListener('input', (e) => { const k = e.target.dataset?.f; if (k) { state[k] = e.target.value; if (apply.lastBase) apply(apply.lastBase); } });
  fbar.addEventListener('change', (e) => { const k = e.target.dataset?.f; if (k) { state[k] = e.target.value; if (apply.lastBase) apply(apply.lastBase); } });
  const apply = (base) => {
    apply.lastBase = base;
    const q = state.q.trim().toLowerCase();
    const out = base.filter((c) =>
      (!q || [c.cap_id, c.working_name, c.description].some((v) => (v || '').toLowerCase().includes(q)))
      && (!state.category || c.strategic_category === state.category)
      && (!state.market || (c.markets || []).includes(state.market))
      && (!state.moscow || c.moscow === state.moscow)
      && (!state.visibility || c.visibility === state.visibility)
      && (!state.product_review
        || (state.product_review === 'Not reviewed yet' ? !c.product_review_status : c.product_review_status === state.product_review))
      && (!state.review_flag || c.review_status === state.review_flag)
      && (!state.admission || (state.admission === 'UNSET' ? !c.roadmap_admission : c.roadmap_admission === state.admission))
      && (!state.decision || (c.decision || '(no decision)') === state.decision)
      && (!state.source || (c.sources || []).includes(state.source)));
    countNote.textContent = `Showing ${out.length} of ${base.length} capabilities`;
    return out;
  };
  return { bar: fbar, apply };
}
