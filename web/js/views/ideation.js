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
  container.appendChild(el('h1', {}, '00 · Capability Candidates — active Ideation population'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'The active working population comes from the final Source analysis (34 reconciled candidates from 426 evidence signals).',
    el('br'),
    'The 15 Cross-market Focus Capabilities are a Product recommendation — a focus view, not a filter on truth. The historical 135-capability baseline is preserved separately (population = HISTORICAL_BASELINE_V1).'));
  const view = { mode: 'all', includeNotSelected: false };
  const toolbar = el('div', { class: 'road-toolbar' },
    el('div', { class: 'seg' },
      el('button', { class: 'active', dataset: { testid: 'cand-all' }, onclick: (e) => { view.mode = 'all'; e.target.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active')); e.target.classList.add('active'); draw(); } }, 'All Candidates'),
      el('button', { dataset: { testid: 'cand-focus' }, onclick: (e) => { view.mode = 'focus'; e.target.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active')); e.target.classList.add('active'); draw(); } }, 'Focus Capabilities')),
    el('button', { dataset: { testid: 'cand-mexcbt' }, onclick: (e) => { view.mexcbt = !view.mexcbt; e.target.classList.toggle('active', view.mexcbt); draw(); } }, 'MEXCBT / Uchida only'),
    el('button', { dataset: { testid: 'cand-include-not-selected' }, onclick: (e) => { view.includeNotSelected = !view.includeNotSelected; e.target.classList.toggle('active', view.includeNotSelected); draw(); } }, 'Include not-selected'));
  container.appendChild(toolbar);
  const mount = el('div', { dataset: { testid: 'candidates-mount' } });
  container.appendChild(mount);
  const res = await api.get(endpoints.candidates());
  const draw = () => {
    let rows = res.items;
    if (!view.includeNotSelected) rows = rows.filter((c) => c.ideation_disposition === 'ACTIVE FOR IDEATION');
    if (view.mode === 'focus') rows = rows.filter((c) => c.is_focus);
    if (view.mexcbt) rows = rows.filter((c) => c.mexcbt_signals > 0);
    mount.replaceChildren(...rows.map((c) => el('div', { class: 'mig-band', dataset: { testid: 'candidate-row', candidate: c.candidate_id } },
      el('h3', {}, `${c.candidate_id} · ${c.name}`,
        c.is_focus ? el('span', { class: 'badge ok-badge', style: 'margin-left:8px' }, 'FOCUS') : null,
        el('span', { class: 'badge', style: 'margin-left:8px' }, c.ideation_disposition)),
      el('div', { class: 'small' },
        `${c.signals} evidence signals · ${c.independent_sources} independent sources · Evidence strength ${c.evidence_strength} · Cross-market leverage ${c.cross_market_leverage} · Strategy alignment ${c.strategy_alignment}`),
      el('div', { class: 'small dim' }, `Markets: ${c.markets || '—'} · MEXCBT direct signals: ${c.mexcbt_signals}`),
      c.focus_markets ? el('div', { class: 'small dim' }, `Focus in: ${c.focus_markets}`) : null,
      c.disposition_rationale ? el('div', { class: 'small dim' }, `Rationale: ${c.disposition_rationale}`) : null,
      el('div', { class: 'small dim mono' }, `Source IDs: ${c.source_ids}`))));
  };
  draw();
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
