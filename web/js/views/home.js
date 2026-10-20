// HOME — My Product Workspace (Phase A: PM Shell)
// Orientation layer: NEEDS YOUR ATTENTION + CONTINUE WORKING + QUICK ACTIONS + RECENT CHANGES.
// NOT a source of Product Truth — all data lives in the API/PostgreSQL.

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';

export async function renderHome(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'My Product Workspace'));

  const data = await api.get(endpoints.home()).catch(() => null);
  if (!data) {
    container.appendChild(notice('error', 'Failed to load Home data.'));
    return;
  }

  const counts = data.counts || {};
  const attention = data.attention || {};
  const recent = data.recent_changes || [];

  // ---- NEEDS YOUR ATTENTION ----
  const attentionBand = el('div', { class: 'mig-band', dataset: { testid: 'home-attention' } },
    el('h2', {}, 'NEEDS YOUR ATTENTION'));
  const attentionItems = [];
  if (attention.candidates_needing_review > 0)
    attentionItems.push({
      label: `${attention.candidates_needing_review} Candidates awaiting Product Review`,
      link: '#/ideation/00',
    });
  if (attention.open_comments > 0)
    attentionItems.push({
      label: `${attention.open_comments} open discussion item(s)`,
      link: null,
    });
  if (counts.customers === 0)
    attentionItems.push({
      label: 'Customer dataset pending — Customer Migration Plans blocked (D3)',
      link: null,
    });
  if (attentionItems.length) {
    for (const a of attentionItems) {
      attentionBand.appendChild(el('div', { class: 'milestone-row' },
        el('div', { class: 'milestone-marker', style: 'color:#e6ae2d' }, '●'),
        el('div', { class: 'milestone-body' }, a.label),
        a.link ? el('a', { class: 'btn small', href: a.link }, 'Go') : null));
    }
  } else {
    attentionBand.appendChild(el('p', { class: 'small dim' }, 'Nothing needs immediate attention.'));
  }
  container.appendChild(attentionBand);

  // ---- CONTINUE WORKING ----
  const continueBand = el('div', { class: 'mig-band', dataset: { testid: 'home-continue' } },
    el('h2', {}, 'CONTINUE WORKING'));
  const areas = [
    { label: 'Review Capabilities', desc: `${counts.active_candidates} active Candidates`, link: '#/ideation/00' },
    { label: 'Define Target Scope', desc: 'Cross-analysis → what each Candidate becomes in V2', link: '#/ideation/06' },
    { label: 'Compose Features', desc: `${counts.features} Features defined`, link: '#/roadmap' },
    { label: 'Plan Roadmap', desc: 'Roadmap Admission + timing', link: '#/roadmap' },
    { label: 'Review Customer requirements', desc: `${counts.customers} customer record(s)`, link: '#/migration' },
    { label: 'Build Migration Plans', desc: 'M1–M6 + Customer intervals', link: '#/migration' },
  ];
  for (const a of areas) {
    continueBand.appendChild(el('div', { class: 'milestone-row' },
      el('div', { class: 'milestone-body' },
        el('a', { href: a.link, style: 'font-weight:700;color:var(--accent)' }, a.label),
        el('div', { class: 'small dim' }, a.desc))));
  }
  container.appendChild(continueBand);

  // ---- QUICK ACTIONS ----
  const quickBand = el('div', { class: 'mig-band', dataset: { testid: 'home-quick' } },
    el('h2', {}, 'QUICK ACTIONS'),
    el('div', { class: 'actions', style: 'flex-wrap:wrap' },
      el('a', { class: 'btn', href: '#/evidence', dataset: { testid: 'qa-evidence' } }, 'Explore Evidence'),
      el('button', { class: 'btn', dataset: { testid: 'qa-capability' }, onclick: () => { window.dispatchEvent(new CustomEvent('open-cap', { detail: 'NEW' })); } }, 'New Capability'),
      el('a', { class: 'btn', href: '#/features', dataset: { testid: 'qa-feature' } }, 'New Feature'),
      el('a', { class: 'btn', href: '#/customers', dataset: { testid: 'qa-customer' } }, 'New Customer'),
      el('a', { class: 'btn', href: '#/reports', dataset: { testid: 'qa-report' } }, 'Generate Deliverable')));

  // ---- GOVERNED COUNTS ----
  quickBand.appendChild(el('div', { class: 'small dim', style: 'margin-top:8px', dataset: { testid: 'home-counts' } },
    `${counts.sources} Sources · ${counts.evidence_signals} Evidence Signals · ${counts.active_candidates} Active Candidates · ${counts.focus_capabilities || 15} Focus · ${counts.historical_baseline || 135} Historical · ${counts.milestones} Milestones (M1–M6) · ${counts.customers} Customers · ${counts.features} Features`));
  container.appendChild(quickBand);

  // ---- RECENT CHANGES ----
  const recentBand = el('div', { class: 'mig-band', dataset: { testid: 'home-recent' } },
    el('h2', {}, 'RECENT CHANGES'));
  if (recent.length) {
    for (const rc of recent) {
      recentBand.appendChild(el('div', { class: 'milestone-row' },
        el('div', { class: 'milestone-body' },
          el('span', { class: 'small' },
            `${rc.actor} ${rc.action}d ${rc.entity_type} ${rc.entity_id} — ${rc.created_at ? rc.created_at.slice(0, 16) : ''}`))));
    }
  } else {
    recentBand.appendChild(el('p', { class: 'small dim' }, 'No recent changes.'));
  }
  container.appendChild(recentBand);
}
