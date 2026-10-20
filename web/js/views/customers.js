// CUSTOMERS — Customer workspace (Phase D).
// Customer = governed entity with context, needs, required Product, migration plan.

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';
import { renderDiscussion } from '../components/discussion.js';
import { openCapModal } from '../components/capmodal.js';

export async function renderCustomers(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'Customers'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'Governed customer records. Customer requirements are PRODUCT HYPOTHESIS until explicitly validated by the Customer (§26).'));

  const [custRes, featRes] = await Promise.all([
    api.get(endpoints.customers()),
    api.get(endpoints.features()),
  ]);
  const customers = custRes.items;
  const features = featRes.items;

  const state = { q: '' };
  const bar = el('div', { class: 'filter-bar', dataset: { testid: 'customer-filters' } },
    el('label', { class: 'f' }, 'Search',
      el('input', { type: 'search', dataset: { cf: 'q' }, style: 'min-width:180px' })),
    el('button', { class: 'primary', dataset: { testid: 'customer-new' },
      onclick: () => openCustomerEditor() }, '+ New Customer'));
  container.appendChild(bar);

  const mount = el('div', { dataset: { testid: 'customers-mount' } });
  container.appendChild(mount);

  const draw = () => {
    let rows = customers;
    if (state.q) rows = rows.filter((c) => (c.name + ' ' + (c.customer_id || '')).toLowerCase().includes(state.q.toLowerCase()));
    mount.replaceChildren();
    if (!rows.length) {
      mount.appendChild(notice('info',
        'No customers yet — the governed customer dataset has not been supplied (D3). Customer Migration Plans cannot be invented.'));
      return;
    }
    for (const cu of rows) {
      const mp = cu.migration_plan || {};
      mount.appendChild(makeCustomerCard(cu, mp, features));
    }
  };
  draw();

  bar.addEventListener('input', (e) => { const k = e.target.dataset?.cf; if (k) { state[k] = e.target.value; draw(); } });
}

function makeCustomerCard(cu, mp, features) {
  const card = el('div', { class: 'mig-band', dataset: { testid: 'customer-card', customer: cu.customer_id } });
  card.appendChild(el('div', { style: 'display:flex;justify-content:space-between;align-items:baseline' },
    el('h3', {}, `${cu.name} (${cu.customer_id})`),
    el('span', { class: 'badge' }, mp.readiness_status || '—')));
  card.appendChild(el('div', { class: 'small dim' },
    `v${cu.version} · Validation: ${cu.validation_status || 'Not assessed'}`));

  const actions = el('div', { class: 'actions', style: 'margin:6px 0' },
    el('button', { class: 'small', dataset: { testid: `open-plan-${cu.customer_id}` },
      onclick: () => openCustomerPlan(cu.customer_id) }, 'Open Migration Plan'),
    el('button', { class: 'small', dataset: { testid: `edit-customer-${cu.customer_id}` },
      onclick: () => openCustomerEditor(cu) }, 'Edit'),
    el('button', { class: 'small', dataset: { testid: `open-matrix-${cu.customer_id}` },
      onclick: () => openFeatureMatrix(cu.customer_id, features) }, 'Feature Matrix'));
  card.appendChild(actions);

  // discussion
  const discDiv = el('div', { dataset: { testid: `customer-discussion-${cu.customer_id}` } });
  card.appendChild(discDiv);
  renderDiscussion(discDiv, 'customer', cu.customer_id);

  return card;
}

function openCustomerEditor(existing = null) {
  document.querySelectorAll('.modal-overlay[data-custedit]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { custedit: '1', testid: 'customer-editor-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(680px,94vw);max-height:92vh;overflow:auto' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  const isEdit = !!existing;

  drawer.appendChild(el('h1', {}, isEdit ? `Edit Customer · ${existing.customer_id}` : '+ New Customer'));
  drawer.appendChild(el('p', { class: 'small dim' }, 'Product-supplied data only. Customer requirements are PRODUCT HYPOTHESIS until Customer-validated.'));

  const fld = (name, label, v = '') => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('input', { type: 'text', name, value: v || '', style: 'width:100%', disabled: name === 'customer_id' && isEdit }));
  const ta = (name, label, v = '', rows = 2) => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('textarea', { name, rows, style: 'width:100%' }, v || ''));

  drawer.appendChild(el('div', { class: 'edit-form', dataset: { testid: 'customer-form' } },
    el('h3', {}, 'CONTEXT'),
    fld('customer_id', 'Customer ID (governed)', existing?.customer_id || ''),
    fld('name', 'Customer name', existing?.name || ''),
    fld('owner', 'Owner / PM', existing?.owner || ''),
    fld('current_environment', 'Current TAO environment / version', existing?.current_environment || ''),
    ta('current_use', 'Current Authoring use', existing?.current_use || ''),
    fld('relevant_markets', 'Market / use case', existing?.relevant_markets || ''),
    el('h3', {}, 'NEEDS'),
    ta('min_functionality_today', 'Minimum functionality today', existing?.min_functionality_today || ''),
    ta('min_functionality_studio', 'Minimum functionality required in TAO Studio', existing?.min_functionality_studio || ''),
    ta('desired_outcome', 'Desired outcome', existing?.desired_outcome || ''),
    ta('value_opportunity', 'Value opportunity', existing?.value_opportunity || ''),
    el('h3', {}, 'DEPENDENCIES'),
    ta('customer_dependencies', 'Customer-specific dependencies', existing?.customer_dependencies || ''),
    ta('blockers', 'Blockers', existing?.blockers || ''),
    ta('assumptions', 'Assumptions', existing?.assumptions || ''),
    ta('exceptions', 'Exceptions', existing?.exceptions || ''),
    el('h3', {}, 'VALIDATION'),
    fld('validation_status', 'Validation status (Not assessed / Hypothesis / Customer validated / Migration committed)', existing?.validation_status || ''),
    ta('customer_feedback', 'Customer feedback / evidence', existing?.customer_feedback || ''),
    ta('notes', 'Product notes', existing?.notes || ''),
    el('div', { class: 'actions', style: 'margin-top:10px' },
      el('button', { class: 'primary', dataset: { testid: 'customer-save' }, onclick: () => saveCustomer(overlay, isEdit ? existing : null) }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel'))));
}

async function saveCustomer(overlay, existing) {
  const g = (n) => overlay.querySelector(`[name="${n}"]`);
  const body = {};
  for (const n of ['name', 'owner', 'current_environment', 'relevant_markets',
    'min_functionality_today', 'min_functionality_studio', 'desired_outcome',
    'value_opportunity', 'customer_dependencies', 'blockers', 'assumptions',
    'exceptions', 'validation_status', 'customer_feedback', 'notes']) {
    const v = g(n).value;
    body[n] = v === '' ? null : v;
  }
  try {
    if (existing) {
      await api.patch(endpoints.customer(existing.customer_id), { ...body, version: existing.version });
    } else {
      const id = g('customer_id').value.trim();
      if (!id) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Customer ID is required.')); return; }
      await api.post(endpoints.customers(), { customer_id: id, ...body });
    }
    overlay.remove();
    window.dispatchEvent(new CustomEvent('cap:changed'));
  } catch (err) {
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 409 ? `Conflict: customer now v${err.detail?.current_version}.` : `Save failed: ${err.message}`));
  }
}

// Feature Matrix — cross-customer view (§28)
function openFeatureMatrix(customerId, features) {
  document.querySelectorAll('.modal-overlay[data-matrix]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { matrix: '1', testid: 'feature-matrix-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(900px,96vw);max-height:92vh;overflow:auto' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);

  Promise.all([api.get(endpoints.customers()), api.get(endpoints.customerFeatures())]).then(([custRes, cfRes]) => {
    const allCustomers = custRes.items;
    const relationships = cfRes.items;
    const allFeatIds = [...new Set(relationships.map((r) => r.feat_id))].sort();
    drawer.appendChild(el('h1', {}, 'Customer × Feature Matrix'));
    const t = el('table', { class: 'compact' });
    t.appendChild(el('tr', {}, ['Feature', ...allCustomers.map((c) => c.customer_id)].map((h) => el('th', {}, h))));
    for (const fid of allFeatIds) {
      const row = el('tr', {});
      row.appendChild(el('td', { class: 'mono' }, fid));
      for (const cu of allCustomers) {
        const rel = relationships.find((r) => r.customer_id === cu.customer_id && r.feat_id === fid);
        row.appendChild(el('td', {},
          rel ? el('span', { class: 'badge', title: rel.rationale || '' }, rel.importance)
              : el('span', { class: 'dim small' }, '—')));
      }
      t.appendChild(row);
    }
    drawer.appendChild(t);
    drawer.appendChild(el('div', { class: 'actions', style: 'margin-top:8px' },
      el('button', { onclick: () => overlay.remove() }, 'Close')));
  }).catch(() => drawer.appendChild(notice('error', 'Failed to load matrix.')));
}

// openCustomerPlan is already in migration.js — re-export if needed
