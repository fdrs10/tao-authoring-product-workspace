// REPORTS / DELIVERABLES (FINAL STRUCTURAL STEP) — predefined Product report
// contracts generated from canonical data. NOT a dashboard export: each
// report follows a fixed contract (docs/REPORT_TEMPLATE_CONTRACTS.md) with a
// publication-style print-friendly preview. Generating never mutates Product
// Truth — generations are recorded as snapshots.

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';

const PILOT_INTENDED = ['DEPP', 'INVALSI', 'NSA', 'NCCER'];

function stateBadge(state) {
  const cls = state === 'AVAILABLE' ? 'ok-badge' : state === 'PRODUCT DECISION REQUIRED' ? 'review' : 'dim';
  return el('span', { class: `badge ${cls}` }, state);
}

export async function renderReports(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'Reports / Deliverables — November Product deliverables'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'Application Product Truth → Report Contract → Generated Report. Reports are generated representations of Product Truth (never a second source); generating records a versioned snapshot and never mutates data.'));

  const status = el('div', { dataset: { testid: 'reports-status' } });
  container.appendChild(status);
  const res = await api.get(endpoints.reports());
  const list = el('div', { dataset: { testid: 'reports-list' } });

  for (const r of res.items) {
    const card = el('div', { class: 'mig-band', dataset: { testid: `report-card-${r.report_id}` } },
      el('h2', {}, `${r.report_id} — ${r.name}`),
      el('div', { class: 'small', style: 'margin-bottom:4px' },
        el('b', {}, `Target: ${r.target_delivery}`), ' · ',
        `${r.sections_available} / ${r.sections_total} sections available`, ' · Status: ',
        stateBadge(r.status),
        r.last_generated ? el('span', { class: 'dim' },
          ` · last generated ${r.last_generated.slice(0, 16).replace('T', ' ')} (v${r.last_version} by ${r.last_actor})`)
          : el('span', { class: 'dim' }, ' · never generated')),
      el('div', { class: 'small dim' }, `Consumes: ${r.consumes}`),
      el('div', { class: 'actions', style: 'margin-top:8px' },
        el('button', { dataset: { testid: `preview-${r.report_id}` }, onclick: () => preview(r.report_id) }, 'Preview Report'),
        el('button', { dataset: { testid: `generate-${r.report_id}` }, onclick: () => generate(r.report_id, null) }, 'Generate HTML'),
        r.report_id === 'D5' ? el('span', { class: 'd5-controls', dataset: { testid: 'd5-controls' } },
          el('label', { class: 'small' }, ' Select customer: ',
            el('select', { dataset: { testid: 'd5-customer-select' }, style: 'margin:0 6px' },
              el('option', { value: '' }, '— select governed customer —')))) : null));
    if (r.report_id === 'D5') {
      // governed customer select (only existing records; DEPP/INVALSI/NSA/NCCER
      // appear only when governed records exist — never invented)
      api.get(endpoints.customers()).then((cr) => {
        const sel = card.querySelector('[data-testid="d5-customer-select"]');
        if (!sel) return;
        sel.replaceChildren(
          el('option', { value: '' }, '— select governed customer —'),
          ...cr.items.map((cu) => el('option', { value: cu.customer_id },
            `${cu.customer_id} · ${cu.name} (${cu.migration_plan?.readiness_status || '—'})`)),
          res.governed_customers ? el('option', { value: '', disabled: '' }) : null);
        if (cr.count) {
          const pilotNote = el('div', { class: 'small dim', dataset: { testid: 'pilot-note' } },
            `Generate Customer Migration Pilot Set — initial intended pilot customers: ${PILOT_INTENDED.join(', ')}. `
            + 'Only governed customer records can be selected; intended-but-ungoverned customers are never invented.');
          sel.parentElement.appendChild(pilotNote);
          card.appendChild(el('div', { class: 'actions' },
            el('button', {
              dataset: { testid: 'pilot-generate' },
              onclick: () => {
                const chosen = sel.value;
                if (!chosen) { card.appendChild(notice('warn', 'Select a governed customer first.')); return; }
                generate('PILOT', { customer_ids: [chosen] });
              },
            }, 'Generate Customer Migration Pilot Set')));
        }
        sel.addEventListener('change', () => {
          const gid = card.querySelector('[data-testid="generate-D5"]');
          if (gid) gid.disabled = !sel.value;
        });
        const gid = card.querySelector('[data-testid="generate-D5"]');
        if (gid) gid.disabled = !sel.value;
      });
    }
    list.appendChild(card);
  }
  container.appendChild(list);

  async function preview(rid, customerId = null) {
    const url = `${endpoints.reports()}/${rid}/preview` + (customerId ? `?customer_id=${encodeURIComponent(customerId)}` : '');
    window.open(url, '_blank');   // publication preview: print-friendly HTML
  }

  async function generate(rid, params) {
    try {
      const res2 = await api.post(`${endpoints.reports()}/${rid}/generate`, params || {});
      const html = res2.report_type === 'pilot-set'
        ? res2.documents.map((d) => d.html).join('<hr>')
        : res2.html;
      const w = window.open('', '_blank');
      w.document.write(html);
      w.document.close();
      window.dispatchEvent(new CustomEvent('cap:changed'));  // refresh status
    } catch (err) {
      container.appendChild(notice('error', `Generate failed: ${JSON.stringify(err.detail || err.message)}`));
    }
  }
}
