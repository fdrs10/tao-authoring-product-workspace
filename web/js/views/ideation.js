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
  // §4–§7: analysis lenses over evidence — NOT independent capability universes.
  const LENS = {
    'V1 Carry-forward': { sources: ['SRC-V1-001'], label: 'V1 Carry-forward Analysis',
      question: 'How does V1 evidence contribute to the current Candidates?' },
    '3.x Direct Migration to V2': { sources: ['SRC-3X-001'], label: '3.x Direct Migration Analysis',
      question: 'How does 3.x functionality/evidence contribute to the current Candidates?' },
    'New Needs & Gaps / Developments': { sources: ['SRC-NEW-001', 'SRC-NYSED-001'],
      label: 'New Needs & Gaps Analysis',
      question: 'What new-needs evidence exists, and which Candidates absorbed it?' },
  };
  if (isDisc) return renderDiscontinuedAnalysis(content);
  const lens = LENS[sheetName];
  if (!lens) { content.appendChild(notice('info', 'Analysis lens not defined for this sheet.')); return; }

  content.appendChild(el('h1', {}, lens.label));
  content.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    lens.question, ' This is an analysis lens over Product evidence — the historical 135-baseline is preserved separately (population = HISTORICAL_BASELINE_V1).'));

  const [evRes, candRes] = await Promise.all([
    api.get(endpoints.evidence()),
    api.get(endpoints.candidates()),
  ]);
  const byFamily = {};
  for (const c of candRes.items) byFamily[c.candidate_id] = c;
  const signals = evRes.items.filter((e) => lens.sources.includes(e.source_id));
  const families = {};
  for (const e of signals) {
    const f = e.reconciled_family_id;
    if (f) (families[f] ||= { signals: [], candidate: byFamily[f] }).signals.push(e);
    else (families.UNREPRESENTED ||= { signals: [], candidate: null }).signals.push(e);
  }
  content.appendChild(el('div', { class: 'filter-bar' },
    el('span', { class: 'badge' }, `${signals.length} evidence signals`),
    el('span', { class: 'small dim', dataset: { testid: 'lens-count' } },
      ` · ${Object.keys(families).filter((k) => k !== 'UNREPRESENTED').length} consolidated families`)));
  const mount = el('div', { dataset: { testid: 'lens-mount' } });
  content.appendChild(mount);

  for (const [fam, group] of Object.entries(families)) {
    if (fam === 'UNREPRESENTED') {
      mount.appendChild(el('div', { class: 'notice warn', dataset: { testid: 'lens-unrepresented' } },
        `UNREPRESENTED EVIDENCE — PRODUCT REVIEW REQUIRED: ${group.signals.length} signal(s) not consolidated into any current Candidate. `
        + 'Product may promote via the Capability Analysis area (never automatic).'));
      continue;
    }
    const cand = group.candidate;
    mount.appendChild(el('div', { class: 'mig-band', dataset: { testid: 'lens-family', family: fam } },
      el('h3', {}, `${fam} · ${cand ? cand.name : fam}`,
        cand && cand.is_focus ? el('span', { class: 'badge ok-badge', style: 'margin-left:8px' }, 'FOCUS') : null),
      el('div', { class: 'small', style: 'margin:2px 0' },
        `Current definition: consolidated from ${group.signals.length} signal(s).`),
      table(['Evidence ID', 'Signal', 'Historical CAP reference', 'Treatment', 'What carries forward / Product question'],
        group.signals.map((e) => el('tr', { dataset: { testid: 'lens-evidence-row' } },
          el('td', { class: 'mono' }, e.evidence_id),
          el('td', {}, e.signal_name),
          el('td', { class: 'small mono' }, e.current_canonical_cap_id || '—'),
          el('td', { class: 'small' }, e.current_treatment || '—'),
          el('td', { class: 'small' },
            cand && cand.is_focus ? 'Carries forward into the Focus set.' : 'Contributes to the active Candidate set — Product review pending.'))))));
  }
  if (!signals.length) mount.appendChild(notice('info', AWAITING));
}

async function renderDiscontinuedAnalysis(content) {
  // §7: historical decision input — NOT active V2 capabilities.
  content.appendChild(el('h1', {}, 'Discontinued Analysis — historical decision input'));
  content.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'The historical discontinuation decisions (135-baseline era) preserved as decision evidence. These records do NOT enter the active V2 scope; the active population remains the 34 Capability Candidates.'));
  const [hist, evRes] = await Promise.all([
    api.get(endpoints.capabilities() + '?ideation_sheet=Discontinued&population=historical'),
    api.get(endpoints.evidence()),
  ]);
  const evByCap = {};
  for (const e of evRes.items) {
    if (e.current_canonical_cap_id) (evByCap[e.current_canonical_cap_id] ||= []).push(e);
  }
  if (!hist.items.length) { content.appendChild(notice('info', AWAITING)); return; }
  content.appendChild(table(
    ['Historical CAP', 'Capability (HISTORICAL BASELINE V1)', 'Decision', 'Evidence', 'Current Candidate affected', 'Validation required'],
    hist.items.map((c) => {
      const linked = evByCap[c.cap_id] || [];
      const fams = [...new Set(linked.map((e) => e.reconciled_family_id).filter(Boolean))];
      return el('tr', { dataset: { testid: 'sheet-row' } },
        el('td', { class: 'mono' }, c.cap_id),
        el('td', {}, c.working_name),
        el('td', {}, el('span', { class: 'badge disc' }, 'DISCONTINUED (historical)')),
        el('td', { class: 'small' }, linked.length ? `${linked.length} signal(s)` : 'no evidence linked'),
        el('td', { class: 'small' }, fams.length
          ? `Consolidated into: ${fams.map((f) => byFamily[f] ? byFamily[f].name : f).join(', ')}`
          : 'No current Candidate affected'),
        el('td', { class: 'small' }, 'Product to validate the discontinuation against the current Candidate set.'));
    })));
  content.appendChild(notice('info',
    'These are historical decision records (HISTORICAL BASELINE V1). They are not active V2 capabilities and do not count toward the 34-Candidate population.'));
}

const AWAITING = 'Awaiting Product data';
