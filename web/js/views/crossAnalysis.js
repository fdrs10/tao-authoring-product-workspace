// Cross-analysis (§13/§29) + Product Backlog (§14/§30) — same canonical
// Admission field edited inline here, in Backlog and in the CAP editor (§11).

import { api, endpoints } from '../api.js';
import { el, capLink, moscowBadge, moscowBadge as MB, admissionBadge, reviewBadge, marketDotsFor, marketLegend, notice, table } from '../ui.js';
import { getMarkets } from '../components/capmodal.js';

const ADM = ['', 'COMMITTED', 'CANDIDATE', 'BACKLOG', 'DEFERRED', 'NOT PLANNED'];

function admissionInline(cap) {
  return el('select', { dataset: { testid: 'adm-edit', cap: cap.cap_id }, style: 'font-size:11.5px' },
    ADM.map((o) => el('option', { value: o, ...(o === (cap.roadmap_admission ?? '') ? { selected: '' } : {}) }, o === '' ? 'UNSET' : o))
  );
}

async function persistAdmission(select, cap, statusEl) {
  const v = select.value;
  const body = { version: cap.version, roadmap_admission: v === '' ? null : v };
  try {
    await api.patch(endpoints.capability(cap.cap_id), body);
    cap.version += 1; cap.roadmap_admission = v === '' ? null : v;
    statusEl.replaceChildren(admissionBadge(cap.roadmap_admission));
  } catch (err) {
    if (err.status === 409) {
      statusEl.replaceChildren(notice('warn', `Conflict: record now v${err.detail.current_version}; reload to reapply.`));
    } else {
      statusEl.replaceChildren(notice('error', JSON.stringify(err.detail || err.message)));
    }
  }
}

export async function renderCrossAnalysis(container) {
  const markets = await getMarkets();
  const caps = await api.get(endpoints.capabilities());
  container.appendChild(el('div', { class: 'small dim' },
    `Canonical capability universe: ${caps.count}. Product decision → final V2 capability. Roadmap Admission editable inline (same field as Backlog/Edit). UNSET preserved.`));
  container.appendChild(table(
    ['CAP', 'Capability', 'Category', 'Markets', 'MoSCoW', 'Decision', 'V2 mapping', 'Admission'],
    caps.items.map((c) => {
      const badge = el('span', { dataset: { testid: 'adm-badge' } }, admissionBadge(c.roadmap_admission));
      const sel = admissionInline(c);
      sel.addEventListener('change', () => persistAdmission(sel, c, badge));
      return el('tr', { dataset: { testid: 'xanalysis-row' } },
        el('td', {}, capLink(c.cap_id)),
        el('td', {}, c.working_name, ' ', reviewBadge(c.review_status)),
        el('td', {}, c.strategic_category),
        el('td', {}, marketDotsFor(c.markets, markets)),
        el('td', {}, moscowBadge(c.moscow)),
        el('td', {}, c.decision || '—'),
        el('td', { class: 'small dim' }, (c.v2_mapping || '—').slice(0, 60)),
        el('td', {}, badge, ' ', sel));
      }))
  );
  container.appendChild(marketLegend(markets));
}
