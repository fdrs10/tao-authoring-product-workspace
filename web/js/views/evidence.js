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
      ['Evidence ID', 'Source', 'Signal', 'Strategic Category', 'Treatment', 'Candidate Family', 'Action'],
      rows.slice(0, 200).map((e) => el('tr', { dataset: { testid: 'evidence-explorer-row' } },
        el('td', { class: 'mono' }, e.evidence_id),
        el('td', { class: 'mono small' }, e.source_id),
        el('td', {}, e.signal_name),
        el('td', { class: 'small' }, e.strategic_category || '—'),
        el('td', { class: 'small' }, e.current_treatment || 'UNRECONCILED'),
        el('td', {}, e.reconciled_family_id
          ? el('span', { class: 'badge' }, e.reconciled_family_id)
          : el('span', { class: 'badge dim' }, 'unlinked')),
        el('td', {}, el('button', { class: 'small', dataset: { testid: 'evidence-open' },
          onclick: () => openEvidenceDetail(e) }, 'Open'))))));
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

function openEvidenceDetail(e) {
  document.querySelectorAll('.modal-overlay[data-evidmodal]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { evidmodal: '1', testid: 'evidence-modal' } });
  overlay.addEventListener('click', (ev) => { if (ev.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(640px,94vw)' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  drawer.appendChild(el('h1', {}, `Evidence ${e.evidence_id}`));
  drawer.appendChild(el('div', { class: 'kv' },
    ...[['Source', e.source_id], ['Signal', e.signal_name],
        ['Description', e.full_description], ['Evidence type', e.evidence_type],
        ['Extraction type', e.extraction_type], ['Confidence', e.source_confidence],
        ['Strategic category', e.strategic_category], ['Authoring scope', e.authoring_scope],
        ['Treatment', e.current_treatment || 'UNRECONCILED'],
        ['Candidate family', e.reconciled_family_id || 'not consolidated'],
        ['Reference', e.evidence_reference]]
      .flatMap(([k, v]) => [el('div', { class: 'k' }, k), el('div', { class: 'v' }, v || '—')])));
  // markets
  const mkts = [];
  if (e.market_k12) mkts.push('Traditional / K-12');
  if (e.market_prof) mkts.push('Professional / Credentialing');
  if (e.market_hed) mkts.push('Higher Education');
  if (e.market_formative) mkts.push('Governed Formative');
  if (e.market_ale) mkts.push('Assessment-led Learning');
  if (e.mexcbt_relevance) mkts.push('MEXCBT / Uchida');
  if (mkts.length) drawer.appendChild(el('div', { class: 'small', style: 'margin:4px 0' },
    'Markets: ' + mkts.join(', ')));
  drawer.appendChild(el('div', { class: 'actions', style: 'margin-top:10px;display:flex;gap:6px;flex-wrap:wrap' },
    el('button', { class: 'small', dataset: { testid: 'evidence-promote' },
      onclick: () => promoteEvidence(overlay, e) }, 'Promote to Product Consideration'),
    el('button', { class: 'small', onclick: () => overlay.remove() }, 'Close')));
}

function promoteEvidence(overlay, e) {
  const prompt_section = el('div', { class: 'edit-form', style: 'margin-top:10px;border-top:1px solid var(--border-2);padding-top:8px' },
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Capability name (required)'),
      el('input', { type: 'text', name: 'promote_name', style: 'width:100%' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Product rationale (required)'),
      el('textarea', { name: 'promote_rationale', rows: 2, style: 'width:100%' })),
    el('div', { class: 'actions' },
      el('button', { class: 'primary small', dataset: { testid: 'promote-confirm' },
        onclick: async () => {
          const name = overlay.querySelector('[name="promote_name"]').value.trim();
          const rationale = overlay.querySelector('[name="promote_rationale"]').value.trim();
          if (!name || !rationale) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Name and rationale are required.')); return; }
          try {
            const r = await api.post(`/api/candidates/F01/promote`, {
              evidence_id: e.evidence_id, name, rationale });
            overlay.querySelector('.modal-drawer').appendChild(notice('ok',
              `Promoted to ${r.candidate_id}.`));
          } catch (err) {
            overlay.querySelector('.modal-drawer').appendChild(notice('error',
              `Promotion failed: ${err.message}`));
          }
        } }, 'Promote'),
      el('button', { class: 'small', onclick: (ev) => { ev.target.closest('.edit-form').remove(); } }, 'Cancel')));
  overlay.querySelector('.modal-drawer').appendChild(prompt_section);
}

  bar.addEventListener('input', (e) => { const k = e.target.dataset?.ef; if (k) { state[k] = e.target.value; apply(); } });
  bar.addEventListener('change', (e) => { const k = e.target.dataset?.ef; if (k) { state[k] = e.target.value; apply(); } });
  apply();
}
