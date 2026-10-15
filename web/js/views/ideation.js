// IDEATION view: compact vertical index (01–06, §27) + working sheets.
// Sheet 01 uses the approved V2 geometry, never redesigned (§33/§45).
// Sheets 02–05 are API-backed decision-sheet foundations; 06 = Cross-analysis.

import { api, endpoints } from '../api.js';
import { el, capLink, moscowBadge, admissionBadge, reviewBadge, marketDotsFor, marketLegend, notice, table } from '../ui.js';
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

export async function renderIdeation(container, sheetNum = '01') {
  container.replaceChildren();
  const idx = el('div', { class: 'ideation-index' }, SHEETS.map((s) =>
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
  const [caps, markets] = await Promise.all([
    api.get(endpoints.capabilities(`?ideation_sheet=${encodeURIComponent(sheetName)}`)),
    getMarkets(),
  ]);
  content.querySelector('.notice.info')?.remove();
  if (caps.count === 0) { content.appendChild(notice('info', 'No capabilities on this sheet.')); return; }
  const groups = {};
  for (const c of caps.items) (groups[c.decision || '(no decision)'] ||= []).push(c);
  for (const [decision, rows] of Object.entries(groups).sort()) {
    content.appendChild(el('h2', {}, `${decision} (${rows.length})`));
    content.appendChild(table(['CAP', 'Capability', 'Category', 'Markets', 'MoSCoW', 'Admission', isDisc ? '' : ''], rows.map((c) =>
      el('tr', { dataset: { testid: 'sheet-row' } },
        el('td', {}, capLink(c.cap_id)),
        el('td', {}, c.working_name, ' ', reviewBadge(c.review_status)),
        el('td', {}, c.strategic_category),
        el('td', {}, marketDotsFor(c.markets, markets)),
        el('td', {}, moscowBadge(c.moscow)),
        el('td', {}, admissionBadge(c.roadmap_admission)),
        isDisc ? el('td', {}, el('span', { class: 'badge disc' }, 'OUT')) : el('td', {})))));
  }
  content.appendChild(marketLegend(markets));
}
