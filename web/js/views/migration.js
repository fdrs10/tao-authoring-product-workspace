// Migration Path (Phase 5) — recovered from
// legacy/TAO_Authoring_v35_6_MIGRATION_DIAGRAM(1).zip (Slide 3), remapped to
// the canonical API (see docs/ROADMAP_MIGRATION_RECOVERY_SPEC.md).
//
// Recovered layout: VALUE / CAPABILITIES UNLOCKED → MIGRATION PATH
// (milestones + intervals) → CUSTOMERS READY TO MOVE (transition projects).
// Recovered rule (§13): Migration does NOT own capability timing — what a
// customer can move to is DERIVED from Product Roadmap timing + the shared
// milestone dataset. Intervals are milestone intervals (M3 -> M4); the
// historical TS1/TS2/TS3 vocabulary is NOT restored (§14; API 422s TS codes).
// No milestone names/dates/customers are invented — empty states are honest.

import { api, endpoints } from '../api.js';
import { el, moscowBadge, admissionBadge, notice } from '../ui.js';
import { openCapModal } from '../components/capmodal.js';
import { openMilestoneEditor } from './roadmap.js';

const MONTH_START = ['Oct 2026', 'Nov 2026', 'Dec 2026', 'Jan 2027', 'Feb 2027', 'Mar 2027',
  'Apr 2027', 'May 2027', 'Jun 2027', 'Jul 2027', 'Aug 2027', 'Sep 2027', 'Oct 2027', 'Nov 2027',
  'Dec 2027', 'Jan 2028', 'Feb 2028', 'Mar 2028', 'Apr 2028', 'May 2028', 'Jun 2028', 'Jul 2028',
  'Aug 2028', 'Sep 2028', 'Oct 2028', 'Nov 2028', 'Dec 2028'];
const TOTAL = 27;

// D-M1: interval windows between milestones (lead-in + between + post-EOL)
function intervals(ms) {
  const sorted = ms.filter((m) => m.position_month !== null && m.position_month !== undefined)
    .sort((a, b) => a.position_month - b.position_month);
  const out = [];
  let prev = 0;
  for (const m of sorted) {
    out.push({ from: prev, to: m.position_month, label: prev === 0 ? `Lead-in → ${m.milestone_id}` : `${prevMilestoneId(sorted, prev)} → ${m.milestone_id}`, endMilestone: m });
    prev = m.position_month;
  }
  out.push({
    from: prev, to: TOTAL,
    label: sorted.length ? `${sorted[sorted.length - 1].milestone_id} → post-EOL` : 'No milestones defined',
    endMilestone: null,
  });
  return out;
}
const prevMilestoneId = (sorted, pos) =>
  (sorted.filter((m) => m.position_month <= pos).pop() || {}).milestone_id || 'M0';

function capChips(caps, testidPrefix) {
  if (!caps.length) return el('span', { class: 'dim small' }, '—');
  return el('span', { class: 'chip-list' },
    caps.map((c) => el('span', {
      class: 'cap-chip', dataset: { testid: testidPrefix, cap: c.cap_id },
      title: `${c.cap_id} · ${c.working_name} — ${monthSpan(c)}`,
      onclick: () => openCapModal(c.cap_id),
    },
    `${c.cap_id}`,
    el('span', { class: 'small' }, ` ${c.working_name}`),
    moscowBadge(c.moscow))));
}

const monthSpan = (c) =>
  (c.start_month === null || c.start_month === undefined)
    ? 'untimed'
    : `${MONTH_START[c.start_month]} → ${MONTH_START[Math.min(TOTAL - 1, c.start_month + (c.duration_months ?? 1) - 1)]}`;

export async function renderMigration(container) {
  container.replaceChildren();
  const [msRes, capsRes, custRes] = await Promise.all([
    api.get(endpoints.milestones()),
    api.get(endpoints.roadmap('')),                    // all admission states; derivation filters below
    api.get(endpoints.customers()),
  ]);
  const milestones = msRes.items;
  const caps = capsRes.items;
  const customers = custRes.items;

  container.appendChild(el('h1', {}, 'Migration Path — 3.x → transition → Target Authoring'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'Dependency on 3.x decreases; capability & value increase. One shared milestone dataset with the Roadmap — capability availability is derived from Product Roadmap timing, never duplicated here.'));

  // ---- band 1: VALUE / ROADMAP CAPABILITIES UNLOCKED (derived, §13) ------
  const committed = caps.filter((c) => c.roadmap_admission === 'COMMITTED');
  const valueBand = el('div', { class: 'mig-band', dataset: { testid: 'mig-band-value' } },
    el('h2', {}, 'VALUE / ROADMAP CAPABILITIES UNLOCKED'),
    el('div', { class: 'small dim', style: 'margin-bottom:6px' },
      `Derived from Roadmap timing + milestones for Roadmap Admission = COMMITTED (${committed.length} capabilities). Change Roadmap timing and this view changes — Migration owns no timing.`));
  const ivs = intervals(milestones);
  for (const [i, iv] of ivs.entries()) {
    const unlocked = committed.filter((c) => c.start_month !== null
      && c.start_month + c.duration_months <= iv.from);
    const inFlight = committed.filter((c) => c.start_month !== null
      && c.start_month < iv.to && c.start_month + c.duration_months > iv.from);
    valueBand.appendChild(el('div', { class: 'mig-interval', dataset: { testid: 'interval-row', interval: String(i) } },
      el('div', { class: 'mig-interval-label' },
        el('b', {}, iv.label),
        el('span', { class: 'small dim' }, ` months ${iv.from}–${iv.to - 1}${iv.endMilestone ? ` (ends at ${iv.endMilestone.milestone_id})` : ''}`)),
      el('div', { class: 'mig-interval-body' },
        el('div', {}, el('b', { class: 'small' }, 'Unlocked by the start of this interval: '), capChips(unlocked, 'interval-unlocked')),
        el('div', {}, el('b', { class: 'small' }, 'In flight during this interval: '), capChips(inFlight, 'interval-inflight')))));
  }
  if (!milestones.length) {
    valueBand.appendChild(notice('info',
      'No milestones are defined yet (the governed milestone dataset has not been supplied; contract §10/D2). Availability is derived per milestone interval as soon as milestones exist. Nothing is invented here.'));
  }
  container.appendChild(valueBand);

  // ---- band 2: MIGRATION PATH / MILESTONES (shared dataset) ---------------
  const pathBand = el('div', { class: 'mig-band', dataset: { testid: 'mig-band-path' } },
    el('h2', {}, 'MIGRATION PATH / MILESTONES'),
    el('div', { class: 'small dim', style: 'margin-bottom:6px' },
      'Shared with the Roadmap (one dataset — edit here or there, both views update). Names and dates come from Product only.'));
  if (!milestones.length) {
    pathBand.appendChild(el('div', { dataset: { testid: 'milestones-empty' } },
      notice('info', 'No milestones yet. Add one with “+ Milestone” when Product supplies the governed list — the app never invents milestone names or dates.')));
  } else {
    for (const m of milestones) {
      pathBand.appendChild(el('div', { class: 'milestone-row', dataset: { testid: 'milestone-row', ms: m.milestone_id } },
        el('div', { class: 'milestone-marker' }, m.milestone_id),
        el('div', { class: 'milestone-body' },
          el('b', {}, m.name),
          el('span', { class: 'small dim' },
            ` · ${m.milestone_date || (m.position_month !== null ? MONTH_START[m.position_month] : 'no date')}`
            + `${m.scope_type === 'category' ? ` · scope: ${m.scope_ref}` : ''}${m.version ? ` · v${m.version}` : ''}`),
          m.description ? el('div', { class: 'small' }, m.description) : null),
        el('button', {
          class: 'small', dataset: { testid: `ms-edit-${m.milestone_id}` },
          onclick: () => openMilestoneEditor(m),
        }, 'Edit')));
    }
  }
  pathBand.appendChild(el('div', { class: 'actions', style: 'margin-top:6px' },
    el('button', { dataset: { testid: 'mig-ms-add' }, onclick: () => openMilestoneEditor() }, '+ Milestone')));
  container.appendChild(pathBand);

  // ---- band 3: CUSTOMER TRANSITION PROJECTS (empty until governed data) ---
  const custBand = el('div', { class: 'mig-band', dataset: { testid: 'mig-band-customers' } },
    el('h2', {}, 'CUSTOMER TRANSITION PROJECTS — CUSTOMERS READY TO MOVE'),
    el('div', { class: 'small dim', style: 'margin-bottom:6px' },
      'Transition is expressed as a milestone interval (e.g. M3 → M4) against the shared milestones. Availability of required capabilities ≠ customer readiness: blockers beyond capability (workflow, governance, data, metadata, integrations, training, contracts, procedures, adoption, organisational readiness) live in the customer record.'));
  if (!customers.length) {
    custBand.appendChild(el('div', { dataset: { testid: 'customers-empty' } },
      notice('info', 'No customer records yet — the governed customer dataset has not been supplied (contract D3). The model and API are ready (customers + customer_capabilities + earliest_milestone_interval); no production customers are invented.')));
  } else {
    const table = el('table', { class: 'compact', dataset: { testid: 'customer-table' } },
      el('tr', {}, ['Customer', 'Current use', 'Desired outcome', 'Value opportunity', 'Required capabilities', 'Migration blockers', 'Earliest interval', 'Validation status', 'Version']
        .map((h) => el('th', {}, h))));
    for (const cu of customers) {
      table.appendChild(el('tr', { dataset: { testid: 'customer-row', customer: cu.customer_id } },
        el('td', {}, el('b', {}, cu.name)),
        el('td', { class: 'small' }, cu.current_use || '—'),
        el('td', { class: 'small' }, cu.desired_outcome || '—'),
        el('td', { class: 'small' }, cu.value_opportunity || '—'),
        el('td', { class: 'small', dataset: { testid: 'cust-required' } },
          String(cu.required_capability_count ?? 0)),
        el('td', { class: 'small', dataset: { testid: 'cust-blockers' } }, cu.blockers || '—'),
        el('td', { class: 'mono', dataset: { testid: 'cust-interval' } },
          cu.earliest_milestone_interval || '—'),
        el('td', {}, cu.validation_status || 'Not assessed'),
        el('td', {}, `v${cu.version}`)));
    }
    custBand.appendChild(table);
  }
  container.appendChild(custBand);
}
