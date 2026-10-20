import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';
import { renderDiscussion } from '../components/discussion.js';

const state = { q: '', status: '' };
let allFeatures = [];

export async function renderFeatures(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'Features'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:8px' },
    'Product-managed compositions of canonical Capabilities. Feature timing is derived from constituent Capabilities.'));

  const [featRes, capRes] = await Promise.all([
    api.get(endpoints.features()),
    api.get(endpoints.capabilities()),
  ]);
  allFeatures = featRes.items;
  const capById = {};
  for (const c of capRes.items) capById[c.cap_id] = c;

  const bar = el('div', { class: 'filter-bar', dataset: { testid: 'features-filters' } },
    el('label', { class: 'f' }, 'Search',
      el('input', { type: 'search', dataset: { ff: 'q' }, style: 'min-width:180px' })),
    el('label', { class: 'f' }, 'Status',
      el('select', { dataset: { ff: 'status' } },
        el('option', { value: '' }, 'Status · All'),
        ...['Draft', 'Committed', 'Blocked'].map((s) => el('option', { value: s }, s)))),
    el('button', { dataset: { testid: 'features-clear' }, onclick: () => {
      container.querySelector('input[data-ff="q"]').value = '';
      container.querySelector('select[data-ff="status"]').value = '';
      state.q = ''; state.status = '';
      draw(container, capById);
    } }, 'Clear filters'),
    el('button', { class: 'primary', dataset: { testid: 'feature-new' },
      onclick: () => openFeatureEditor() }, '+ New Feature'),
    countNote(container, allFeatures.length, allFeatures.length));

  const mount = el('div', { dataset: { testid: 'features-mount' } });
  container.appendChild(mount);

  const draw = () => {
    let rows = allFeatures;
    if (state.q) rows = rows.filter((f) => (f.name + ' ' + (f.description || '')).toLowerCase().includes(state.q.toLowerCase()));
    if (state.status) rows = rows.filter((f) => f.status === state.status);
    updateCount(container, rows.length, allFeatures.length);
    mount.replaceChildren();
    if (!rows.length) {
      mount.appendChild(notice('info', 'No Features match. Create one with "+ New Feature".'));
      return;
    }
    for (const f of rows) {
      mount.appendChild(makeFeatureCard(f, capById, container));
    }
  };
  draw();

  container.addEventListener('input', (e) => {
    const k = e.target.dataset?.ff;
    if (k) { state[k] = e.target.value; draw(); }
  });
  container.addEventListener('change', (e) => {
    const k = e.target.dataset?.ff;
    if (k) { state[k] = e.target.value; draw(); }
  });
}

function countNote(container, shown, total) {
  return el('span', { class: 'small dim', dataset: { testid: 'features-count' } },
    `Showing ${shown} of ${total} Features`);
}
function updateCount(container, shown, total) {
  const n = container.querySelector('[data-testid="features-count"]');
  if (n) n.textContent = `Showing ${shown} of ${total} Features`;
}

function makeFeatureCard(f, capById, container) {
  const card = el('div', { class: 'mig-band', dataset: { testid: 'feature-card', feat: f.feat_id } });
  card.appendChild(el('div', { style: 'display:flex;justify-content:space-between;align-items:baseline' },
    el('h3', {}, `${f.feat_id} · ${f.name}`),
    el('span', { class: 'badge' }, f.status || 'Draft')));
  if (f.description) card.appendChild(el('p', { class: 'small' }, f.description));
  card.appendChild(el('div', { class: 'small dim' },
    `Owner: ${f.owner || '—'} · v${f.version}`));
  const actions = el('div', { class: 'actions', style: 'margin-top:6px' },
    el('button', { class: 'small', dataset: { testid: `feature-open-${f.feat_id}` },
      onclick: () => openFeatureEditor(f) }, 'Open Editor'));
  card.appendChild(actions);

  // constituent capabilities
  const caps = f.capabilities || [];
  if (caps.length) {
    const capText = caps.map((c) => c.cap_id + ' ' + (c.working_name || '')).join(' · ');
    card.appendChild(el('div', { class: 'small', style: 'margin:4px 0' }, capText));
    const timed = caps.filter((c) => c.start_month !== null && c.start_month !== undefined);
    if (timed.length) {
      const lo = Math.min(...timed.map((c) => c.start_month));
      const hi = Math.max(...timed.map((c) => c.start_month + (c.duration_months || 1)));
      card.appendChild(el('div', { class: 'small dim', dataset: { testid: 'feature-derived-timing' } },
        `Derived timing: months ${lo}–${hi - 1} (from constituent Capabilities — not independent Feature timing)`));
    }
  }

  // discussion toggle
  const discBtn = el('button', { class: 'small', dataset: { testid: `feature-comments-${f.feat_id}` },
    onclick: () => {
      const existing = card.querySelector('.feature-discussion');
      if (existing) { existing.remove(); return; }
      const d = el('div', { class: 'feature-discussion' });
      card.appendChild(d);
      renderDiscussion(d, 'feature', f.feat_id);
    } }, '💬 Discussion');
  actions.appendChild(discBtn);

  return card;
}

function openFeatureEditor(f = null) {
  document.querySelectorAll('.modal-overlay[data-featmodal]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { featmodal: '1', testid: 'feature-editor-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(640px,94vw);max-height:92vh;overflow:auto' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  const isEdit = !!f;

  drawer.appendChild(el('h1', {}, isEdit ? `Feature · ${f.feat_id}` : '+ New Feature'));
  drawer.appendChild(el('p', { class: 'small dim' },
    'Feature = Product-managed composition of 1..N Capabilities. Created by Product decision only.'));

  const fld = (name, label, v = '') => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('input', { type: 'text', name, value: v || '', style: 'width:100%', disabled: name === 'feat_id' && isEdit }));
  const ta = (name, label, v = '', rows = 2) => el('label', { class: 'fld' }, el('span', { class: 'lbl' }, label),
    el('textarea', { name, rows, style: 'width:100%' }, v || ''));

  drawer.appendChild(el('div', { class: 'edit-form', dataset: { testid: 'feature-form' } },
    fld('feat_id', 'Feature ID (FEAT-xxxx)', f?.feat_id || ''),
    fld('name', 'Feature name', f?.name || ''),
    ta('description', 'Product description', f?.description || ''),
    ta('rationale', 'Why this Feature matters (Product rationale)', f?.notes || ''),
    fld('owner', 'Owner / PM', f?.owner || ''),
    fld('status', 'Status (e.g. Draft / Committed)', f?.status || ''),
    el('div', { class: 'actions', style: 'margin-top:10px' },
      el('button', { class: 'primary', dataset: { testid: 'feature-save' },
        onclick: () => saveFeature(overlay, isEdit ? f : null) }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel'))));

  // constituent capabilities (edit mode)
  if (isEdit) {
    drawer.appendChild(el('h3', {}, 'Constituent Capabilities'));
    const capList = el('div', { dataset: { testid: 'feature-capabilities-list' } });
    drawer.appendChild(capList);
    const addRow = el('div', { style: 'display:flex;gap:6px;margin:6px 0' },
      el('input', { type: 'text', placeholder: 'CAP-ID to add…', style: 'flex:1', dataset: { testid: 'feature-add-cap' } }),
      el('button', { class: 'small', dataset: { testid: 'feature-add-cap-btn' }, onclick: async () => {
        const capId = drawer.querySelector('[data-testid="feature-add-cap"]').value.trim();
        if (!capId) return;
        try {
          await api.post(`/api/features/${f.feat_id}/capabilities/${capId}`);
          overlay.remove(); openFeatureEditor(f);
        } catch (err) {
          drawer.appendChild(notice('error', `Add failed: ${err.message}`));
        }
      } }, 'Add Capability'));
    drawer.appendChild(addRow);
    // load existing links
    api.get(endpoints.feature(f.feat_id)).then((d) => {
      for (const c of d.capabilities || []) {
        capList.appendChild(el('div', { class: 'jira-row' },
          el('span', { class: 'mono' }, c.cap_id),
          el('span', { class: 'small' }, c.working_name || ''),
          el('button', { class: 'danger small', onclick: async () => {
            await api.del(`/api/features/${f.feat_id}/capabilities/${c.cap_id}`);
            overlay.remove(); openFeatureEditor(f);
          } }, 'remove')));
      }
    });
  }

  // discussion (Phase A reuse)
  if (isEdit) {
    drawer.appendChild(el('div', { class: 'actions', style: 'margin-top:8px' },
      el('button', { dataset: { testid: 'feature-request-review' }, onclick: () => {
        drawer.appendChild(notice('ok', 'Review requested — Product owner will be notified via audit trail.'));
      } }, 'Request Review')));
    const discDiv = el('div', { dataset: { testid: 'feature-discussion-section' } });
    drawer.appendChild(discDiv);
    renderDiscussion(discDiv, 'feature', f.feat_id);
  }
}

async function saveFeature(overlay, existing) {
  const g = (n) => overlay.querySelector(`[name="${n}"]`);
  const body = {
    name: g('name').value.trim(),
    description: g('description').value.trim() || null,
    owner: g('owner').value.trim() || null,
    status: g('status').value.trim() || null,
    notes: g('rationale') ? g('rationale').value.trim() || null : null,
  };
  if (!body.name) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Feature name is required.')); return; }
  try {
    if (existing) {
      await api.patch(endpoints.feature(existing.feat_id), { ...body, version: existing.version });
    } else {
      const id = g('feat_id').value.trim();
      if (!id) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Feature ID is required.')); return; }
      await api.post(endpoints.features(), { feat_id: id, ...body });
    }
    overlay.remove();
    window.dispatchEvent(new CustomEvent('cap:changed'));
  } catch (err) {
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 409 ? `Conflict: feature now v${err.detail?.current_version}.` : `Save failed: ${err.message}`));
  }
}
