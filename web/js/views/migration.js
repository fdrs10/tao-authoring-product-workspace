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
import { el, capLink, moscowBadge, admissionBadge, notice, table } from '../ui.js';
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

// §12: sub-state — COMMON MIGRATION PATH vs CUSTOMER MIGRATION PLANS.
// In-memory presentation state only.
const migTab = { view: 'path' }; // 'path' | 'plans'

export async function renderMigration(container) {
  container.replaceChildren();
  const [msRes, capsRes, custRes] = await Promise.all([
    api.get(endpoints.milestones()),
    api.get(endpoints.roadmap('') + (endpoints.roadmap('').includes('?') ? '&' : '?') + 'population=active'),  // CURRENT Product population only (§13)
    api.get(endpoints.customers()),
  ]);
  const milestones = msRes.items;
  const caps = capsRes.items;
  const customers = custRes.items;

  container.appendChild(el('h1', {}, 'Migration Path — 3.x → transition → Target Authoring'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'ONE Product Roadmap → ONE common Migration Path (below) → MULTIPLE Customer Migration Plans. Dependency on 3.x decreases; capability & value increase. One shared milestone dataset with the Roadmap — capability availability is derived from Product Roadmap timing, never duplicated here.'));

  const subtabs = el('div', { class: 'subtabs', dataset: { testid: 'migration-subtabs' } },
    el('a', { class: migTab.view === 'path' ? 'active' : '', href: '#/migration', dataset: { testid: 'mig-tab-path' }, onclick: (e) => { e.preventDefault(); migTab.view = 'path'; window.dispatchEvent(new CustomEvent('cap:changed')); } }, 'Migration Path'),
    el('a', { class: migTab.view === 'plans' ? 'active' : '', href: '#/migration', dataset: { testid: 'mig-tab-plans' }, onclick: (e) => { e.preventDefault(); migTab.view = 'plans'; window.dispatchEvent(new CustomEvent('cap:changed')); } }, 'Customer Plans'));
  container.appendChild(subtabs);

  const body = el('div', { dataset: { testid: 'migration-body' } });
  container.appendChild(body);

  if (migTab.view === 'plans') {
    renderCustomerPlans(body, customers, milestones);
    return;
  }
  renderCommonPath(body, { milestones, caps, customers });
}

function renderCommonPath(container, { milestones, caps, customers }) {

  // ---- band 1: VALUE / ROADMAP CAPABILITIES UNLOCKED (derived, §13) ------
  const committed = caps.filter((c) => c.roadmap_admission === 'COMMITTED');
  const valueBand = el('div', { class: 'mig-band', dataset: { testid: 'mig-band-value' } },
    el('h2', {}, 'VALUE / ROADMAP CAPABILITIES UNLOCKED'),
    el('div', { class: 'small dim', style: 'margin-bottom:6px' },
      `Derived from Roadmap timing + milestones for Roadmap Admission = COMMITTED (${committed.length} capabilities). Change Roadmap timing and this view changes — Migration owns no timing.`,
      committed.length === 0 ? el('div', { class: 'notice warn small', dataset: { testid: 'migration-awaiting' } },
        'Awaiting Product Roadmap Admission — no current Candidates are Roadmap-admitted yet, so no capability availability can be derived. The historical baseline is never inherited.') : null));
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

  // ---- band 3: CUSTOMER TRANSITION (summary — full plans under Customer Plans tab) ---
  const custBand = el('div', { class: 'mig-band', dataset: { testid: 'mig-band-customers' } },
    el('h2', {}, 'CUSTOMER TRANSITION PROJECTS — CUSTOMERS READY TO MOVE'),
    el('div', { class: 'small dim', style: 'margin-bottom:6px' },
      'Transition is expressed as a milestone interval (e.g. M3 → M4) against the shared milestones. Availability of required capabilities ≠ customer readiness: blockers beyond capability (workflow, governance, data, metadata, integrations, training, contracts, procedures, adoption, organisational readiness) live in the customer record. Full per-customer plans: switch to ',
      el('a', { href: '#/migration', onclick: (e) => { e.preventDefault(); migTab.view = 'plans'; window.dispatchEvent(new CustomEvent('cap:changed')); } }, 'Customer Plans'), '.'));
  if (!customers.length) {
    custBand.appendChild(el('div', { dataset: { testid: 'customers-empty' } },
      notice('info', 'No customer records yet — the governed customer dataset has not been supplied (contract D3). The model and API are ready (customers + customer_capabilities + earliest_milestone_interval); no production customers are invented.')));
  } else {
    const table = el('table', { class: 'compact', dataset: { testid: 'customer-table' } },
      el('tr', {}, ['Customer', 'Readiness', 'Earliest interval', 'Required capabilities', 'Migration blockers', 'Validation status', 'Version']
        .map((h) => el('th', {}, h))));
    for (const cu of customers) {
      const mp = cu.migration_plan || {};
      table.appendChild(el('tr', { dataset: { testid: 'customer-row', customer: cu.customer_id } },
        el('td', {}, el('b', {}, cu.name), ' ', el('span', { class: 'mono small' }, cu.customer_id)),
        el('td', {}, el('span', { class: 'badge', dataset: { testid: 'cust-readiness' }, title: mp.readiness_reason || '' }, mp.readiness_status || '—')),
        el('td', { class: 'mono', dataset: { testid: 'cust-interval' } },
          cu.earliest_milestone_interval || '—'),
        el('td', { class: 'small', dataset: { testid: 'cust-required' } },
          `${cu.required_capability_count ?? 0} (${mp.available_by_interval_start ?? 0} available by interval start)`),
        el('td', { class: 'small', dataset: { testid: 'cust-blockers' } }, cu.blockers || '—'),
        el('td', {}, cu.validation_status || 'Not assessed'),
        el('td', {}, `v${cu.version}`)));
    }
    custBand.appendChild(table);
    custBand.appendChild(el('div', { class: 'open-links' },
      el('a', { href: '#/migration', dataset: { testid: 'open-customer-plans' }, onclick: (e) => { e.preventDefault(); migTab.view = 'plans'; window.dispatchEvent(new CustomEvent('cap:changed')); } }, '→ Customer Migration Plans')));
  }
  container.appendChild(custBand);
}

// ---- Customer Migration Plans (FINAL UAT EVOLUTION §8–§14) -----------------
// ONE common Migration Path (shared milestones) applied to ONE customer at a
// time. Plans CONSUME Product Roadmap truth — no second timing. Product-
// managed working artifacts: persisted via API with actor/audit/version.
function renderCustomerPlans(container, customers, milestones) {
  container.appendChild(el('h2', {}, 'Customer Migration Plans'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px', dataset: { testid: 'plans-note' } },
    'Each plan applies the ONE common Migration Path to ONE customer. Required capabilities and their availability come from Product Roadmap truth (never duplicated). Plans are Product-managed working artifacts.'));
  if (!customers.length) {
    container.appendChild(el('div', { dataset: { testid: 'plans-empty' } },
      notice('info', 'No customers yet — the governed customer dataset has not been supplied (D3). Plans cannot be invented; they appear here as soon as Product registers customers.')));
    return;
  }
  const list = el('div', { class: 'mig-band', dataset: { testid: 'plans-list' } },
    el('h3', {}, 'Customers'));
  for (const cu of customers) {
    const mp = cu.migration_plan || {};
    list.appendChild(el('div', { class: 'milestone-row' },
      el('div', { class: 'milestone-body' },
        el('b', {}, cu.name), ' ', el('span', { class: 'mono small' }, cu.customer_id),
        el('div', { class: 'small' },
          el('span', { class: 'badge', dataset: { testid: 'plan-readiness' }, title: mp.readiness_reason || '' }, mp.readiness_status || '—'),
          ` · interval ${cu.earliest_milestone_interval || '—'} · ${cu.required_capability_count ?? 0} required caps · v${cu.version}`)),
      el('button', { dataset: { testid: `open-plan-${cu.customer_id}` }, onclick: () => openCustomerPlan(cu.customer_id) }, 'Open Migration Plan')));
  }
  container.appendChild(list);
  container.appendChild(el('div', { class: 'actions' },
    el('button', { dataset: { testid: 'customer-add' }, onclick: () => openCustomerEditor() }, '+ Register customer (Product-supplied data only)')));
}

function openCustomerEditor(existing = null) {
  document.querySelectorAll('.modal-overlay[data-custmodal]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { custmodal: '1', testid: 'customer-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(640px,94vw)' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  drawer.appendChild(el('h1', {}, existing ? `Edit customer · ${existing.customer_id}` : 'Register customer (Product-supplied data only)'));
  const fld = (name, label, value = '') => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('input', { type: 'text', name, value: existing?.[name] ?? value, style: 'width:100%', disabled: name === 'customer_id' && !!existing }));
  drawer.appendChild(el('div', { class: 'edit-form', dataset: { testid: 'customer-form' } },
    fld('customer_id', 'Customer ID (governed)'),
    fld('name', 'Customer name')),
    drawer.appendChild(el('div', { class: 'actions' },
      el('button', { class: 'primary', dataset: { testid: 'customer-save' }, onclick: () => saveCustomer(overlay, existing) }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel'))));
}

async function saveCustomer(overlay, existing) {
  const g = (n) => overlay.querySelector(`[name="${n}"]`);
  const body = { name: g('name').value.trim() };
  if (!body.name) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Customer name is required (Product-supplied).')); return; }
  try {
    if (existing) await api.patch(endpoints.customer(existing.customer_id), { ...body, version: existing.version });
    else {
      const id = g('customer_id').value.trim();
      if (!id) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Customer ID is required (governed).')); return; }
      await api.post(endpoints.customers(), { customer_id: id, ...body });
    }
    overlay.remove();
    window.dispatchEvent(new CustomEvent('cap:changed'));
  } catch (err) {
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 409 ? `Conflict: customer now v${err.detail?.current_version}.`
        : `Save failed: ${JSON.stringify(err.detail || err.message)}`));
  }
}

// Full Customer Migration Plan for one customer (§9 model, §12 UI).
async function openCustomerPlan(customerId) {
  const cust = await api.get(endpoints.customer(customerId));
  const mp = cust.migration_plan || {};
  const pane = (() => {
    document.querySelectorAll('.modal-overlay[data-planmodal]').forEach((n) => n.remove());
    const overlay = el('div', { class: 'modal-overlay', dataset: { planmodal: '1', testid: 'plan-overlay' } });
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
    const drawer = el('div', { class: 'modal-drawer', style: 'width:min(900px,96vw)' });
    overlay.appendChild(drawer);
    document.body.appendChild(overlay);
    return drawer;
  })();
  pane.appendChild(el('h1', { dataset: { testid: 'plan-title' } }, `Customer Migration Plan · ${cust.name} (${cust.customer_id})`));
  pane.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'Applies the ONE common Migration Path to this customer. Required-capability availability is derived from Product Roadmap truth; the plan never stores its own timing.'));

  pane.appendChild(el('h3', {}, `Migration readiness: ${mp.readiness_status || '—'}`));
  pane.appendChild(el('div', { class: 'small', dataset: { testid: 'plan-readiness-reason' } }, mp.readiness_reason || ''));

  pane.appendChild(el('h3', {}, 'Customer context & need'));
  pane.appendChild(el('div', { class: 'kv' },
    ...[['Current Authoring use', cust.current_use], ['Current environment', cust.current_environment],
        ['Relevant markets / use case', cust.relevant_markets],
        ['Minimum functionality today', cust.min_functionality_today],
        ['Minimum functionality in TAO Studio', cust.min_functionality_studio],
        ['Desired outcome', cust.desired_outcome], ['Value opportunity', cust.value_opportunity]]
      .flatMap(([k, v]) => [el('div', { class: 'k' }, k), el('div', { class: 'v' }, v || '—')])));

  pane.appendChild(el('h3', {}, `Product dependencies — required capabilities (${mp.required_capabilities?.length ?? 0})`));
  const reqRows = (mp.required_capabilities || []).map((rc) => el('tr', { dataset: { testid: 'plan-req-row', cap: rc.cap_id, available: String(rc.available_by_interval_start) } },
    el('td', {}, capLink(rc.cap_id)),
    el('td', { class: 'small' }, rc.working_name),
    el('td', {}, rc.roadmap_admission || 'UNSET'),
    el('td', {}, rc.start_month === null || rc.start_month === undefined ? '—' : `${rc.start_month}+${rc.duration_months}`),
    el('td', {}, rc.available_by_interval_start
      ? el('span', { class: 'badge ok-badge' }, 'available')
      : el('span', { class: 'badge review', title: rc.dependency }, 'blocked')),
    el('td', { class: 'small' }, rc.dependency),
    el('td', { class: 'small' }, rc.features.length ? rc.features.map((x) => x.feat_id).join(', ') : '—')));
  pane.appendChild(table(['CAP', 'Capability', 'Admission', 'Roadmap timing', 'By interval start', 'Dependency', 'Features'], reqRows));

  pane.appendChild(el('h3', {}, 'Common Migration Path milestones (shared)'));
  pane.appendChild(el('div', { class: 'small' },
    (mp.milestones || []).map((m) => `${m.milestone_id} ${m.name} (${m.milestone_date || '?'})`).join(' · ') || '—'));

  pane.appendChild(el('h3', {}, 'Migration'));
  pane.appendChild(el('div', { class: 'kv' },
    ...[['Earliest viable milestone interval', cust.earliest_milestone_interval],
        ['Proposed migration window', cust.proposed_migration_window],
        ['Customer-specific dependencies', cust.customer_dependencies],
        ['Blockers', cust.blockers], ['Assumptions', cust.assumptions],
        ['Exceptions', cust.exceptions]]
      .flatMap(([k, v]) => [el('div', { class: 'k' }, k), el('div', { class: 'v' }, v || '—')])));

  pane.appendChild(el('h3', {}, 'Validation'));
  pane.appendChild(el('div', { class: 'kv' },
    ...[['Validation status', cust.validation_status], ['Product notes', cust.notes],
        ['Customer feedback / evidence', cust.customer_feedback]]
      .flatMap(([k, v]) => [el('div', { class: 'k' }, k), el('div', { class: 'v' }, v || '—')])));

  pane.appendChild(el('div', { class: 'actions', style: 'margin-top:12px' },
    el('button', { dataset: { testid: 'plan-edit' }, onclick: () => openPlanEditor(cust, () => { pane.replaceChildren(); openCustomerPlanInto(pane, customerId); }) }, 'Edit plan'),
    el('button', { onclick: () => pane.closest('.modal-overlay').remove() }, 'Close')));
}
async function openCustomerPlanInto(pane, customerId) {
  const cust = await api.get(endpoints.customer(customerId));
  const mp = cust.migration_plan || {};
  pane.replaceChildren(
    el('h1', { dataset: { testid: 'plan-title' } }, `Customer Migration Plan · ${cust.name} (${cust.customer_id})`),
    el('div', { class: 'small' }, `Readiness: ${mp.readiness_status} — ${mp.readiness_reason}`));
}

function openPlanEditor(cust, onSaved) {
  document.querySelectorAll('.modal-overlay[data-planedit]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { planedit: '1', testid: 'plan-edit-overlay' } });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(720px,96vw);max-height:92vh;overflow:auto' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  drawer.appendChild(el('h1', {}, `Edit Customer Migration Plan · ${cust.customer_id}`));
  const ta = (name, label, v, rows = 2) => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('textarea', { name, rows, style: 'width:100%' }, v || ''));
  const fld = (name, label, v = '') => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('input', { type: 'text', name, value: v || '', style: 'width:100%' }));
  drawer.appendChild(el('div', { class: 'edit-form', dataset: { testid: 'plan-edit-form' } },
    fld('earliest_milestone_interval', 'Earliest viable milestone interval (e.g. M3 -> M4 — no TS codes)', cust.earliest_milestone_interval),
    fld('proposed_migration_window', 'Proposed migration window (Product/Customer agreed, free text)', cust.proposed_migration_window),
    fld('current_environment', 'Current TAO version / environment', cust.current_environment),
    fld('relevant_markets', 'Relevant markets / use case', cust.relevant_markets),
    ta('min_functionality_today', 'Minimum functionality required today', cust.min_functionality_today),
    ta('min_functionality_studio', 'Minimum functionality required in TAO Studio', cust.min_functionality_studio),
    ta('desired_outcome', 'Desired outcome', cust.desired_outcome),
    ta('value_opportunity', 'Value opportunity', cust.value_opportunity),
    ta('customer_dependencies', 'Customer-specific dependencies', cust.customer_dependencies),
    ta('blockers', 'Blockers', cust.blockers),
    ta('assumptions', 'Assumptions', cust.assumptions),
    ta('exceptions', 'Exceptions', cust.exceptions),
    fld('validation_status', 'Validation status (Not assessed / Hypothesis / Customer validated / Migration committed)', cust.validation_status),
    ta('customer_feedback', 'Customer feedback / evidence', cust.customer_feedback, 2),
    ta('notes', 'Product notes', cust.notes),
    el('div', { class: 'actions', style: 'margin-top:10px' },
      el('button', { class: 'primary', dataset: { testid: 'plan-save' }, onclick: async () => {
        const g = (n) => overlay.querySelector(`[name="${n}"]`);
        const body = {};
        for (const n of ['earliest_milestone_interval', 'proposed_migration_window', 'current_environment',
          'relevant_markets', 'min_functionality_today', 'min_functionality_studio', 'desired_outcome',
          'value_opportunity', 'customer_dependencies', 'blockers', 'assumptions', 'exceptions',
          'validation_status', 'customer_feedback', 'notes']) {
          const v = g(n).value; body[n] = v === '' ? null : v;
        }
        try {
          await api.patch(endpoints.customer(cust.customer_id), { ...body, version: cust.version });
          overlay.remove(); onSaved();
        } catch (err) {
          drawer.appendChild(notice('error', err.status === 409
            ? `Conflict: customer now v${err.detail?.current_version}; your edit was NOT applied — reopen and reapply.`
            : `Save failed: ${JSON.stringify(err.detail || err.message)}`));
        }
      } }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel'))));
}
