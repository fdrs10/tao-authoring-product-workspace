// IDEATION view: compact vertical index (01–06, §27) + working sheets.
// Sheet 01 uses the approved V2 geometry, never redesigned (§33/§45).
// Sheets 02–05 are API-backed decision-sheet foundations; 06 = Cross-analysis.

import { api, endpoints } from '../api.js';
import { el, capLink, moscowBadge, admissionBadge, reviewBadge, marketDotsFor, marketLegend, notice, table, capFilterBar } from '../ui.js';
import { getMarkets } from '../components/capmodal.js';
import { renderCrossAnalysis } from './crossAnalysis.js';

export const SHEETS = [
  { n: '01', id: 'v2-position', title: 'V2 Position / Product Definition' },
  { n: '02', id: 'v1', title: 'V1 Carry-forward' },
  { n: '03', id: '3x', title: '3.x Direct Migration' },
  { n: '04', id: 'new', title: 'New Needs & Gaps' },
  { n: '05', id: 'disc', title: 'Discontinued' },
  { n: '06', id: 'xanalysis', title: 'Cross-analysis' },
];

const SHEET_TO_FILTER = {
  '02': 'V1 Carry-forward',
  '03': '3.x Direct Migration to V2',
  '04': 'New Needs & Gaps / Developments',
  '05': 'Discontinued',
};

export async function renderIdeation(container, sheetNum = '00') {
  container.replaceChildren();
  if (sheetNum === '00') return renderCandidates(container);
  const idx = el('div', { class: 'ideation-index' },
    el('a', { class: `idx-item ${sheetNum === '00' ? 'active' : ''}`, href: '#/ideation/00', dataset: { testid: 'ideation-idx-00' } },
      el('span', { class: 'num' }, '00'), 'Capability Candidates (active)'),
    SHEETS.map((s) =>
    el('a', { class: `idx-item ${s.n === sheetNum ? 'active' : ''}`, href: `#/ideation/${s.n}`, dataset: { testid: `ideation-idx-${s.n}` } },
      el('span', { class: 'num' }, s.n), s.title)));
  const content = el('div', { dataset: { testid: 'ideation-content' } });
  container.appendChild(el('div', { class: 'layout-ideation' }, idx, content));

  if (sheetNum === '01') return renderV2Position(content);
  if (sheetNum === '06') {
    const tabs = el('div', { class: 'subtabs' },
      el('a', { class: 'active', href: '#/ideation/06' }, '06 · Cross-analysis'),
      el('a', { href: '#/backlog', dataset: { testid: 'open-backlog' } }, 'Product Backlog'));
    content.append(tabs, el('h1', {}, 'Cross-analysis — What does the final V2 capability become?'));
    return renderCrossAnalysis(content);
  }
  const filter = SHEET_TO_FILTER[sheetNum];
  if (filter) return renderSheet(content, filter, sheetNum === '05');
}

async function renderCandidates(container) {
  container.appendChild(el('h1', {}, '00 · Capability Candidates — Product Review workspace'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'The active working population: 34 reconciled candidates from 426 evidence signals (9 sources).',
    el('br'),
    'The 15 Cross-market Focus Capabilities are a Product recommendation. The historical 135-capability baseline is preserved separately.'));
  // governed funnel (§5)
  const funnel = await api.get(endpoints.funnel()).catch(() => null);
  if (funnel) {
    const f = funnel.funnel;
    container.appendChild(el('div', { class: 'filter-bar', dataset: { testid: 'funnel-banner' } },
      el('span', { class: 'flow-step' }, `${f.sources} Sources`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.evidence_signals} Evidence Signals`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.capability_candidates} Active Candidates`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.focus_capabilities} Focus Capabilities`)));
  }
  const [res, markets, sources] = await Promise.all([
    api.get(endpoints.candidates()), getMarkets(), api.get(endpoints.sources())]);
  const countNote = el('span', { class: 'small dim', dataset: { testid: 'candidate-count' } });
  const state = { q: '', market: '', mexcbt: false, focus: false, review: '', disposition: '', source: '' };
  const sel = (key, title, options) => el('label', { class: 'f' }, title,
    el('select', { dataset: { cf: key } }, options.map(([v, l]) => el('option', { value: v }, l))));
  const bar = el('div', { class: 'filter-bar', dataset: { testid: 'candidate-filters' } },
    el('label', { class: 'f' }, 'Search', el('input', { type: 'search', dataset: { cf: 'q' }, style: 'min-width:180px' })),
    sel('market', 'Market', [['', 'Market · All'], ...markets.map((m) => [m.name, m.name])]),
    sel('mexcbt', 'MEXCBT / Uchida', [['', 'All'], ['yes', 'MEXCBT-relevant only']]),
    sel('focus', 'Focus', [['', 'All'], ['yes', 'Focus only'], ['no', 'Non-focus']]),
    sel('review', 'Product Review', [['', 'All'], ['not reviewed', 'Not reviewed'], ['CONFIRMED', 'CONFIRMED'], ['REVIEW_REQUIRED', 'REVIEW_REQUIRED']]),
    sel('disposition', 'Ideation status', [['', 'All'], ['ACTIVE FOR IDEATION', 'ACTIVE FOR IDEATION'], ['NOT SELECTED FOR IDEATION', 'NOT SELECTED FOR IDEATION']]),
    sel('source', 'Source', [['', 'Source · All'], ...sources.items.map((s) => [s.source_id, s.source_id])]),
    el('button', { dataset: { testid: 'cand-filter-clear' }, onclick: () => { bar.querySelectorAll('select, input').forEach((n) => { n.value = ''; }); Object.keys(state).forEach((k) => state[k] = ''); apply(res.items); } }, 'Clear filters'),
    countNote);
  container.appendChild(bar);
  const mount = el('div', { dataset: { testid: 'candidates-mount' } });
  container.appendChild(mount);

  const apply = () => {
    let rows = res.items;
    const q = state.q.trim().toLowerCase();
    if (q) rows = rows.filter((c) => (c.name + ' ' + (c.markets || '') + ' ' + (c.source_ids || '')).toLowerCase().includes(q));
    if (state.market) rows = rows.filter((c) => (c.markets || '').includes(state.market));
    if (state.mexcbt === 'yes') rows = rows.filter((c) => c.mexcbt_signals > 0);
    if (state.focus === 'yes') rows = rows.filter((c) => c.is_focus);
    if (state.focus === 'no') rows = rows.filter((c) => !c.is_focus);
    if (state.review === 'not reviewed') rows = rows.filter((c) => !c.enrichment);
    if (state.disposition) rows = rows.filter((c) => c.ideation_disposition === state.disposition);
    if (state.source) rows = rows.filter((c) => (c.source_ids || '').includes(state.source));
    countNote.textContent = `Showing ${rows.length} of ${res.items.length} Candidates`;
    mount.replaceChildren(table(
      ['CAP-ID', 'Capability', 'Strategic Category', 'Markets', 'MEXCBT / Uchida', 'Evidence', 'Sources', 'Focus', 'Product Review', 'Ideation Status', 'Jira Evidence', 'Action'],
      rows.map((c) => el('tr', { dataset: { testid: 'candidate-row', candidate: c.candidate_id } },
        el('td', {}, el('span', { class: 'cap-link mono', dataset: { cap: c.cap_id }, onclick: () => openCapModal(c.cap_id) }, c.cap_id)),
        el('td', {}, c.name),
        el('td', { class: 'small' }, 'Awaiting Product data'),
        el('td', { class: 'small' }, c.markets || '—'),
        el('td', {}, c.mexcbt_signals > 0 ? `YES (${c.mexcbt_signals})` : '—'),
        el('td', {}, String(c.signals)),
        el('td', { class: 'small mono', title: c.source_ids }, String(c.independent_sources)),
        el('td', {}, c.is_focus ? el('span', { class: 'badge ok-badge' }, 'FOCUS') : '—'),
        el('td', {}, 'not reviewed'),
        el('td', { class: 'small' }, c.ideation_disposition),
        el('td', {}, '—'),
        el('td', {}, el('button', { class: 'small', onclick: () => openCapModal(c.cap_id) }, 'Open'))))));
  };
  bar.addEventListener('input', (e) => { const k = e.target.dataset?.cf; if (k) { state[k] = e.target.value; apply(res.items); } });
  bar.addEventListener('change', (e) => { const k = e.target.dataset?.cf; if (k) { state[k] = e.target.value; apply(res.items); } });
  apply(res.items);
}

function renderV2Position(content) {
  const open = (n, label) => el('a', { href: `#/ideation/${n}`, class: 'btn', dataset: { testid: `v2-open-${n}` } }, `OPEN · ${label}`);
  content.append(
    el('h1', {}, '01 · V2 Position / Product Definition'),
    el('div', { class: 'formula', dataset: { testid: 'v2-formula' } },
      'V1 Carry-forward  +  3.x Direct Migration  +  New Needs & Gaps  −  Discontinued  =  TAO Studio V2 Authoring Target Scope  →  Cross-analysis (not a summand)'),
    el('div', { class: 'v2-figure' }, el('img', { src: '/assets/v2-position.png', alt: 'Approved V2 Position diagram' })),
    el('div', { class: 'open-links' },
      open('02', '02 V1 Carry-forward'), open('03', '03 3.x Direct Migration'),
      open('04', '04 New Needs & Gaps'), open('05', '05 Discontinued'),
      el('a', { href: '#/ideation/06', class: 'btn' }, '→ 06 Cross-analysis')));
}

async function renderSheet(content, sheetName, isDisc) {
  content.appendChild(el('h1', {}, sheetName + (isDisc ? ' (OUT — not a V2 summand)' : '')));
  content.appendChild(el('div', { class: 'notice info' }, 'Loading…'));
  const [caps, markets, sources] = await Promise.all([
    api.get(endpoints.capabilities(`?ideation_sheet=${encodeURIComponent(sheetName)}`)),
    getMarkets(),
    api.get(endpoints.sources()),
  ]);
  content.querySelector('.notice.info')?.remove();
  if (caps.count === 0) { content.appendChild(notice('info', 'No capabilities on this sheet.')); return; }
  const { bar, apply } = capFilterBar({ markets, sources: sources.items });
  content.appendChild(bar);
  const mount = el('div', { dataset: { testid: 'sheet-mount' } });
  content.appendChild(mount);
  const draw = () => {
    const filtered = apply(caps.items);
    mount.replaceChildren();
    if (!filtered.length) { mount.appendChild(notice('info', 'No capabilities match the current filters.')); return; }
    const groups = {};
    for (const c of filtered) (groups[c.decision || '(no decision)'] ||= []).push(c);
    for (const [decision, rows] of Object.entries(groups).sort()) {
      mount.appendChild(el('h2', {}, `${decision} (${rows.length})`));
      mount.appendChild(table(['CAP', 'Capability', 'Category', 'Markets', 'MoSCoW', 'Admission', isDisc ? '' : ''], rows.map((c) =>
        el('tr', { dataset: { testid: 'sheet-row' } },
          el('td', {}, capLink(c.cap_id)),
          el('td', {}, c.working_name, ' ', reviewBadge(c.review_status)),
          el('td', {}, c.strategic_category),
          el('td', {}, marketDotsFor(c.markets, markets)),
          el('td', {}, moscowBadge(c.moscow)),
          el('td', {}, admissionBadge(c.roadmap_admission)),
          isDisc ? el('td', {}, el('span', { class: 'badge disc' }, 'OUT')) : el('td', {}, c.visibility || '—')))));
    }
  };
  draw();
  content.appendChild(marketLegend(markets));
}
