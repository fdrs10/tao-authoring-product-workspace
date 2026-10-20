// EVIDENCE EXPLORER — browse/search/filter all 426 evidence signals (§11–§13).
// The PM can find a signal, understand its treatment, and promote it to
// Product consideration (rationale required, audited).

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';
import { openCapModal } from '../components/capmodal.js';

export async function renderEvidenceExplorer(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'Evidence Explorer'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'All 426 evidence signals from the governed Source analysis. Search, filter and promote signals into Product consideration (rationale required).'));

  const [evRes, candRes] = await Promise.all([
    api.get(endpoints.evidence()),
    api.get(endpoints.candidates()),
  ]);
  const allEvidence = evRes.items;
  const candByFamily = {};
  for (const c of candRes.items) candByFamily[c.candidate_id] = c;

  // governed funnel
  const funnel = await api.get(endpoints.funnel()).catch(() => null);
  if (funnel) {
    const f = funnel.funnel;
    container.appendChild(el('div', { class: 'filter-bar', dataset: { testid: 'evidence-funnel' } },
      el('span', { class: 'flow-step' }, `${f.sources} Sources`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.evidence_signals} Evidence Signals`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.capability_candidates} Active Candidates`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.focus_capabilities} Focus Capabilities`)));
  }

  // filters
  const state = { q: '', source: '', mexcbt: false, treatment: '', family: '' };
  const countNote = el('span', { class: 'small dim', dataset: { testid: 'evidence-count' } });
  const sel = (key, title, options) => el('label', { class: 'f' }, title,
    el('select', { dataset: { ef: key } }, options.map(([v, l]) => el('option', { value: v }, l))));
  const sources = [...new Set(allEvidence.map((e) => e.source_id))].sort();
  const treatments = [...new Set(allEvidence.map((e) => e.current_treatment || 'UNRECONCILED'))].sort();
  const families = [...new Set(allEvidence.map((e) => e.reconciled_family_id).filter(Boolean))].sort();

  const bar = el('div', { class: 'filter-bar', dataset: { testid: 'evidence-filters' } },
    el('label', { class: 'f' }, 'Search', el('input', { type: 'search', dataset: { ef: 'q' }, style: 'min-width:180px' })),
    sel('source', 'Source', [['', 'Source · All'], ...sources.map((s) => [s, s])]),
    sel('mexcbt', 'MEXCBT / Uchida', [['', 'All'], ['yes', 'MEXCBT-relevant only']]),
    sel('treatment', 'Treatment', [['', 'Treatment · All'], ...treatments.map((t) => [t, t])]),
    sel('family', 'Candidate family', [['', 'Family · All'], ...families.map((f2) => [f2, f2])]),
    el('button', { dataset: { testid: 'evidence-clear' }, onclick: () => { bar.querySelectorAll('select, input').forEach((n) => { n.value = ''; }); Object.keys(state).forEach((k) => state[k] = ''); apply(); } }, 'Clear filters'),
    countNote);

  const mount = el('div', { dataset: { testid: 'evidence-mount' } });
  container.appendChild(bar);
  container.appendChild(mount);

  const apply = () => {
    let rows = allEvidence;
    const q = state.q.trim().toLowerCase();
    if (q) rows = rows.filter((e) => (e.signal_name + ' ' + (e.full_description || '')).toLowerCase().includes(q));
    if (state.source) rows = rows.filter((e) => e.source_id === state.source);
    if (state.mexcbt) rows = rows.filter((e) => (e.mexcbt_relevance || '').toUpperCase() === 'YES');
    if (state.treatment) rows = rows.filter((e) => (e.current_treatment || 'UNRECONCILED') === state.treatment);
    if (state.family) rows = rows.filter((e) => e.reconciled_family_id === state.family);
    countNote.textContent = `Showing ${rows.length} of ${allEvidence.length} evidence signals`;
    mount.replaceChildren(table(
      ['Evidence ID', 'Source', 'Signal', 'Strategic Category', 'Treatment', 'Candidate Family'],
      rows.slice(0, 200).map((e) => el('tr', { dataset: { testid: 'evidence-explorer-row' } },
        el('td', { class: 'mono' }, e.evidence_id),
        el('td', { class: 'mono small' }, e.source_id),
        el('td', {}, e.signal_name),
        el('td', { class: 'small' }, e.strategic_category || '—'),
        el('td', { class: 'small' }, e.current_treatment || 'UNRECONCILED'),
        el('td', {}, e.reconciled_family_id
          ? el('span', { class: 'badge' }, e.reconciled_family_id)
          : el('span', { class: 'badge dim' }, 'unlinked'))))));
    if (rows.length > 200) {
      mount.appendChild(el('p', { class: 'small dim' }, `Showing first 200 of ${rows.length} matching signals. Refine filters to narrow.`));
    }
  };

  function table(headers, rows) {
    const t = el('table', { class: 'compact' });
    t.appendChild(el('tr', {}, headers.map((h2) => el('th', {}, h2))));
    for (const r of rows) t.appendChild(r);
    return t;
  }

  bar.addEventListener('input', (e) => { const k = e.target.dataset?.ef; if (k) { state[k] = e.target.value; apply(); } });
  bar.addEventListener('change', (e) => { const k = e.target.dataset?.ef; if (k) { state[k] = e.target.value; apply(); } });
  apply();
}
