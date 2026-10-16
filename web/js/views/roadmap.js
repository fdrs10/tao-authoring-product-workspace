// Roadmap (Phase 5) — behaviour recovered from legacy/TAO_Studio_Authoring_
// Action_Plan_Roadmap_v10.html, remapped to the canonical API (see
// docs/ROADMAP_MIGRATION_RECOVERY_SPEC.md).
//
// Recovered v10 behaviours: 27-month track math, Category → Big Rock/Market →
// capability hierarchy, independent branch expand/collapse, pointer drag /
// left+right resize / month snapping, red milestone lines labelled once per
// category, quarter report modal, horizon windows, design-rules content.
// NOT copied from v10/v38.6: localStorage persistence (API + version + audit
// instead), invented baseline content, commitment-type marks, random ids.

import { api, endpoints } from '../api.js';
import { el, capLink, moscowBadge, admissionBadge, marketDotsFor, marketLegend, notice } from '../ui.js';
import { openCapModal, getMarkets } from '../components/capmodal.js';

// ---- recovered timeline model (v10 months[]/quarters[], verbatim window) --
const MONTHS = [
  { y: 2026, m: 'Oct', q: '2026 Q4' }, { y: 2026, m: 'Nov', q: '2026 Q4' }, { y: 2026, m: 'Dec', q: '2026 Q4' },
  { y: 2027, m: 'Jan', q: '2027 Q1' }, { y: 2027, m: 'Feb', q: '2027 Q1' }, { y: 2027, m: 'Mar', q: '2027 Q1' },
  { y: 2027, m: 'Apr', q: '2027 Q2' }, { y: 2027, m: 'May', q: '2027 Q2' }, { y: 2027, m: 'Jun', q: '2027 Q2' },
  { y: 2027, m: 'Jul', q: '2027 Q3' }, { y: 2027, m: 'Aug', q: '2027 Q3' }, { y: 2027, m: 'Sep', q: '2027 Q3' },
  { y: 2027, m: 'Oct', q: '2027 Q4' }, { y: 2027, m: 'Nov', q: '2027 Q4' }, { y: 2027, m: 'Dec', q: '2027 Q4' },
  { y: 2028, m: 'Jan', q: '2028 Q1' }, { y: 2028, m: 'Feb', q: '2028 Q1' }, { y: 2028, m: 'Mar', q: '2028 Q1' },
  { y: 2028, m: 'Apr', q: '2028 Q2' }, { y: 2028, m: 'May', q: '2028 Q2' }, { y: 2028, m: 'Jun', q: '2028 Q2' },
  { y: 2028, m: 'Jul', q: '2028 Q3' }, { y: 2028, m: 'Aug', q: '2028 Q3' }, { y: 2028, m: 'Sep', q: '2028 Q3' },
  { y: 2028, m: 'Oct', q: '2028 Q4' }, { y: 2028, m: 'Nov', q: '2028 Q4' }, { y: 2028, m: 'Dec', q: '2028 Q4' },
];
const QUARTERS = ['2026 Q4', '2027 Q1', '2027 Q2', '2027 Q3', '2027 Q4',
  '2028 Q1', '2028 Q2', '2028 Q3', '2028 Q4'];
const TOTAL = 27;
// D-R2 horizon windows (views over the same data — no independent timing)
const HORIZONS = { full: [0, 26], '0-6': [0, 5], '7-24': [6, 23], tail: [24, 26] };
const HORIZON_LABELS = [['full', 'Full'], ['0-6', '0–6m'], ['7-24', '7–24m'], ['tail', 'Tail']];
const CAT_COLORS = {
  'Create & Design': 'blue', 'Manage & Govern': 'purple',
  'Collaborate & Assure Quality': 'green', 'Standards & Portability': 'teal',
  'AI-assisted Authoring': 'orange',
};

// ---- session state (in-memory only; canonical state always from the API) --
const session = {
  mode: 'roadmap',            // 'roadmap' | 'outcome'
  roadmapView: 'capabilities', // §19: 'capabilities' | 'features' — same Product data
  horizon: 'full',
  expanded: new Set(),        // `${category}::${band}` — independent branches
  filters: { market: '', moscow: '', visibility: '', admission: 'COMMITTED' },
  outcomeDraft: null,         // {horizon: {narrative, version}}
};
let milestones = [];

const monthLabel = (i) => `${MONTHS[i].m} ${MONTHS[i].y}`;
const catColor = (c) => CAT_COLORS[c] || 'grey';

async function loadCaps(filters) {
  const q = new URLSearchParams();
  if (filters.admission === 'UNSET') q.set('admission', 'UNSET');
  else if (filters.admission === 'All') q.set('admission', '');  // explicit empty: the API would otherwise apply its COMMITTED default
  else if (filters.admission) q.set('admission', filters.admission);
  if (filters.market) q.set('market', filters.market);
  if (filters.category) q.set('category', filters.category);
  const qs = q.toString();
  const res = await api.get(endpoints.roadmap() + (qs ? `?${qs}` : ''));
  return res.items;
}

// D-R1 (Product-confirmed): the Roadmap hierarchy is Strategic Category →
// Capability. Market is NOT a hierarchy level — it is metadata + a filter.
// Every canonical capability appears exactly once when Market = All; no bar
// is duplicated because a capability applies to several markets.
function categoryLanes(caps) {
  const groups = new Map();
  for (const c of caps) {
    const k = c.strategic_category;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(c);
  }
  return groups;
}

// ---- bars ------------------------------------------------------------------
function barGeom(c) {
  const start = c.start_month ?? 0;
  const dur = c.duration_months ?? 1;
  return { start, dur, left: start / TOTAL * 100, width: dur / TOTAL * 100 };
}

function barTitle(c) {
  const { start, dur } = barGeom(c);
  const jira = (c.jira || []).map((j) => `${j.jira_key} (${j.status || '—'}${j.target_release ? `, release ${j.target_release}` : ''})`).join('; ');
  return `${c.cap_id} · ${c.working_name}\n${monthLabel(start)} → ${monthLabel(Math.min(TOTAL - 1, start + dur - 1))}`
    + `\nMoSCoW ${c.moscow || '—'} · Admission ${c.roadmap_admission || 'UNSET'}`
    + (jira ? `\nJira: ${jira}` : '');
}

function renderBar(c, editable, compact = false) {
  const g = barGeom(c);
  const b = el('div', {
    class: `rbar b-${catColor(c.strategic_category)}${compact ? ' compact' : ''}`,
    dataset: { testid: 'cap-bar', cap: c.cap_id },
    style: `left:${g.left}%;width:${g.width}%`,
    title: barTitle(c),
  },
  el('span', { class: 'handle left', dataset: { testid: 'bar-handle-left' } }),
  el('span', { class: 'bar-title' }, compact ? `${c.cap_id} ${c.working_name}` : c.working_name),
  (c.jira && c.jira.length && compact)
    ? el('span', { class: 'bar-jira mono' }, c.jira.map((j) => j.jira_key).join(' '))
    : null,
  el('span', { class: 'handle right', dataset: { testid: 'bar-handle-right' } }));
  b.addEventListener('click', (e) => {
    if (b.dataset.dragged === '1') { b.dataset.dragged = '0'; return; }
    if (!e.target.classList.contains('handle')) openCapModal(c.cap_id);
  });
  if (editable) attachBarDrag(b, c);
  return b;
}

// v10 attachDrag(): month snapping via round(), clamped move/left/right,
// persist on pointerup through the API with optimistic version. A 409 never
// overwrites the other user's timing — the bar reverts to server state.
function attachBarDrag(bar, c) {
  let sx = 0, start = 0, dur = 1, mode = 'move', moved = false;
  bar.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    const h = e.target.closest('.handle');
    mode = h ? (h.classList.contains('left') ? 'left' : 'right') : 'move';
    sx = e.clientX; start = c.start_month ?? 0; dur = c.duration_months ?? 1; moved = false;
    bar.classList.add('dragging');
    bar.setPointerCapture(e.pointerId);
    e.stopPropagation();
  });
  bar.addEventListener('pointermove', (e) => {
    if (!bar.hasPointerCapture?.(e.pointerId)) return;
    const track = bar.parentElement;
    const rect = track.getBoundingClientRect();
    const delta = Math.round((e.clientX - sx) / (rect.width / TOTAL));
    if (delta !== 0) moved = true;
    if (mode === 'move') {
      c.start_month = Math.max(0, Math.min(TOTAL - dur, start + delta));
      c.duration_months = dur;
    } else if (mode === 'left') {
      const ns = Math.max(0, Math.min(start + dur - 1, start + delta));
      c.start_month = ns; c.duration_months = (start + dur) - ns;
    } else {
      c.start_month = start;
      c.duration_months = Math.max(1, Math.min(TOTAL - start, dur + delta));
    }
    bar.style.left = (c.start_month / TOTAL * 100) + '%';
    bar.style.width = (c.duration_months / TOTAL * 100) + '%';
  });
  bar.addEventListener('pointerup', async (e) => {
    try { bar.releasePointerCapture(e.pointerId); } catch (_) { /* released */ }
    bar.classList.remove('dragging');
    if (!moved) return;
    bar.dataset.dragged = '1';
    try {
      const res = await api.patch(endpoints.roadmapTiming(c.cap_id), {
        version: c.timing_version,
        start_month: c.start_month,
        duration_months: c.duration_months,
      });
      c.timing_version = res.version;
      flashStatus(`Saved ${c.cap_id}: ${monthLabel(c.start_month)} → ${monthLabel(Math.min(TOTAL - 1, c.start_month + c.duration_months - 1))} (v${res.version})`, 'ok');
    } catch (err) {
      // restore server truth — never silently overwrite (§7/§18)
      const fresh = await api.get(endpoints.roadmap(''));
      const cur = (fresh.items || []).find((x) => x.cap_id === c.cap_id);
      if (cur) {
        c.start_month = cur.start_month; c.duration_months = cur.duration_months;
        c.timing_version = cur.timing_version;
        bar.style.left = ((cur.start_month ?? 0) / TOTAL * 100) + '%';
        bar.style.width = ((cur.duration_months ?? 1) / TOTAL * 100) + '%';
      }
      flashStatus(err.status === 409
        ? `Timing conflict on ${c.cap_id}: server now v${err.detail?.current_version}. Your drag was NOT applied — review and redo.`
        : `Timing save failed for ${c.cap_id}: ${err.detail?.error || err.message}`, 'warn');
    }
  });
}

let statusLine = null;
function flashStatus(msg, kind) {
  if (!statusLine) return;
  statusLine.replaceChildren(el('span', { class: `notice ${kind}`, style: 'margin:0;display:inline-block;padding:3px 8px' }, msg));
  clearTimeout(flashStatus._t);
  flashStatus._t = setTimeout(() => statusLine.replaceChildren(), 6000);
}

// ---- milestones (shared dataset: Roadmap + Migration) ----------------------
function milestonesFor(categoryName) {
  return milestones.filter((m) => m.scope_type === 'global'
    || (m.scope_type === 'category' && m.scope_ref === categoryName));
}

function renderMilestoneLine(m, track, categoryName, editable, label, windowStart = 0, windowCount = TOTAL) {
  const pos = m.position_month;
  if (pos === null || pos === undefined) return null;
  if (pos < windowStart || pos >= windowStart + windowCount) return null;
  const line = el('div', {
    class: `milestone-line${m.scope_type === 'global' ? ' global' : ''}`,
    dataset: { testid: 'milestone-line', ms: m.milestone_id },
    style: `left:${(((pos - windowStart) + 0.5) / windowCount * 100)}%`,
    title: `${m.milestone_id} · ${m.name}${m.milestone_date ? ` · ${m.milestone_date}` : ''}${m.description ? `\n${m.description}` : ''}`,
  });
  if (label) line.appendChild(el('span', { class: 'milestone-label', dataset: { testid: 'milestone-label' } }, m.name));
  line.addEventListener('click', (e) => {
    if (line.dataset.dragged === '1') { line.dataset.dragged = '0'; return; }
    e.stopPropagation();
    openMilestoneEditor(m);
  });
  if (editable) attachMilestoneDrag(line, track, m);
  return line;
}

function attachMilestoneDrag(line, track, m) {
  let sx = 0, start = 0, moved = false;
  line.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    e.stopPropagation();
    sx = e.clientX; start = m.position_month; moved = false;
    line.setPointerCapture(e.pointerId);
  });
  line.addEventListener('pointermove', (e) => {
    if (!line.hasPointerCapture?.(e.pointerId)) return;
    const rect = track.getBoundingClientRect();
    const delta = Math.round((e.clientX - sx) / (rect.width / TOTAL));
    if (delta !== 0) moved = true;
    m.position_month = Math.max(0, Math.min(TOTAL - 1, start + delta));
    line.style.left = (((m.position_month) + 0.5) / TOTAL * 100) + '%';
  });
  line.addEventListener('pointerup', async (e) => {
    try { line.releasePointerCapture(e.pointerId); } catch (_) { /* released */ }
    if (!moved) return;
    line.dataset.dragged = '1';
    try {
      const res = await api.patch(endpoints.milestone(m.milestone_id),
        { version: m.version, position_month: m.position_month });
      m.version = res.version;
      flashStatus(`Milestone ${m.milestone_id} moved to ${monthLabel(m.position_month)} (v${res.version})`, 'ok');
    } catch (err) {
      const fresh = await api.get(endpoints.milestones());
      const cur = (fresh.items || []).find((x) => x.milestone_id === m.milestone_id);
      if (cur) { m.position_month = cur.position_month; m.version = cur.version; }
      flashStatus(err.status === 409
        ? `Milestone conflict on ${m.milestone_id}: server v${err.detail?.current_version}. Move NOT applied.`
        : `Milestone save failed: ${err.detail?.error || err.message}`, 'warn');
    }
  });
}

// ---- milestone editor (create/update via API; never prefilled content) -----
export function openMilestoneEditor(m = null, defaults = {}) {
  document.querySelectorAll('.modal-overlay[data-msmodal]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { msmodal: '1', testid: 'ms-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(560px,94vw)' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);

  const catSel = el('select', { name: 'scope_ref' });
  const isEdit = !!m;
  const val = (name, dflt = '') => drawer.querySelector(`[name="${name}"]`);
  drawer.appendChild(el('h1', {}, isEdit ? `Edit milestone · ${m.milestone_id}` : 'Add milestone'));
  const form = el('div', { class: 'edit-form', dataset: { testid: 'ms-form' } },
    el('label', {}, 'Milestone ID (governed, e.g. M1)',
      el('input', { type: 'text', name: 'milestone_id', dataset: { testid: 'ms-id' }, disabled: isEdit, value: m?.milestone_id || defaults.milestone_id || '' })),
    el('label', {}, 'Name (Product-supplied — never invented by the app)',
      el('input', { type: 'text', name: 'name', dataset: { testid: 'ms-name' }, value: m?.name || '' })),
    el('label', {}, 'Date',
      el('input', { type: 'date', name: 'milestone_date', dataset: { testid: 'ms-date' }, value: m?.milestone_date || '' })),
    el('label', {}, 'Position (month on the 27-month window)',
      el('select', { name: 'position_month', dataset: { testid: 'ms-pos' } },
        MONTHS.map((mo, i) => el('option', { value: i, ...((m?.position_month ?? defaults.position_month ?? 0) === i ? { selected: '' } : {}) }, `${monthLabel(i)} (index ${i})`)))),
    el('label', {}, 'Scope',
      el('select', { name: 'scope_type', dataset: { testid: 'ms-scope' } },
        el('option', { value: 'global', ...((m?.scope_type || 'global') === 'global' ? { selected: '' } : {}) }, 'Whole roadmap'),
        el('option', { value: 'category', ...((m?.scope_type) === 'category' ? { selected: '' } : {}) }, 'Strategic category'))),
    el('label', {}, 'Category (when scope = category)', catSel),
    el('label', {}, 'Description / exit condition',
      el('textarea', { name: 'description', dataset: { testid: 'ms-desc' }, rows: 3 }, m?.description || '')),
    el('div', { class: 'actions' },
      el('button', {
        class: 'primary', dataset: { testid: 'ms-save' },
        onclick: () => saveMilestone(overlay, isEdit ? m : null),
      }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel')));
  drawer.appendChild(form);
  // category options come from the canonical category list (no invention)
  api.get(endpoints.capabilities('?admission=')).then((res) => {
    const cats = [...new Set(res.items.map((x) => x.strategic_category))].sort();
    catSel.replaceChildren(...cats.map((cn) => el('option', { value: cn, ...(m?.scope_ref === cn ? { selected: '' } : {}) }, cn)));
  }).catch(() => {});
}

async function saveMilestone(overlay, existing) {
  const g = (n) => overlay.querySelector(`[name="${n}"]`);
  const body = {
    name: g('name').value.trim(),
    milestone_date: g('milestone_date').value || null,
    position_month: Number(g('position_month').value),
    scope_type: g('scope_type').value,
    scope_ref: g('scope_type').value === 'category' ? g('scope_ref').value || null : null,
    description: g('description').value.trim() || null,
  };
  if (!body.name) { overlay.querySelector('.ms-err')?.remove(); overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Milestone name is required (Product-supplied).')); return; }
  try {
    if (existing) {
      await api.patch(endpoints.milestone(existing.milestone_id), { ...body, version: existing.version });
    } else {
      const id = g('milestone_id').value.trim();
      if (!id) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Milestone ID is required (governed, e.g. M1).')); return; }
      await api.post(endpoints.milestones(), { milestone_id: id, ...body });
    }
    overlay.remove();
    window.dispatchEvent(new CustomEvent('cap:changed')); // both views refetch
  } catch (err) {
    overlay.querySelector('.ms-err')?.remove();
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 409 ? `Conflict: milestone now v${err.detail?.current_version}.`
        : `Save failed: ${JSON.stringify(err.detail || err.message)}`));
  }
}

// ---- overlays ---------------------------------------------------------------
function openOverlay(testid) {
  document.querySelectorAll(`.modal-overlay[data-testid="${testid}"]`).forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { testid } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  document.body.appendChild(overlay);
  return overlay;
}

// ---- Full view --------------------------------------------------------------
function renderFull(container, caps, markets) {
  const cats = [...new Set(caps.map((c) => c.strategic_category))].sort();
  const grid = el('div', { class: 'top-grid' },
    el('div', { class: 'headbox' }, 'Strategic Categories'),
    el('div', { class: 'headbox' }, 'Big Rock / Market'),
    el('div', { class: 'timeline-head' },
      el('div', { class: 'timeline-title' }, 'Timeframe (Quarter)'),
      el('div', { class: 'quarters' },
        QUARTERS.map((q, qi) => el('div', {
          class: 'q', dataset: { testid: 'quarter-head', q: String(qi) },
          onclick: () => openQuarter(qi, caps),
        }, q.replace(' ', '·'))))));
  container.appendChild(grid);

  if (!caps.length) {
    container.appendChild(el('div', { dataset: { testid: 'roadmap-empty' } },
      notice('info', 'No capabilities match the current Roadmap population. Default population is Roadmap Admission = COMMITTED (§34). Switch Admission to “All” to review other states; UNSET stays distinct from BACKLOG.')));
  }

  for (const cat of cats) {
    const catCaps = caps.filter((c) => c.strategic_category === cat);
    const color = catColor(cat);
    const group = el('div', { class: 'cat-group', dataset: { testid: 'cat-group', cat } });
    group.appendChild(el('div', { class: `category cat-${color}` },
      el('div', {}, cat),
      el('small', {}, `${catCaps.length} capabilities`)));
    const body = el('div', { class: 'category-body' });
    // D-R1: ONE capability lane per strategic category — each canonical
    // capability renders exactly once here.
    const key = `${cat}::capabilities`;
    const expanded = session.expanded.has(key);
    const lane = el('div', { class: 'lane', dataset: { testid: 'band-row', band: 'Capabilities' } });
    const label = el('div', { class: 'band' },
      el('div', { class: 'band-name' },
        el('span', {}, 'Capabilities'),
        el('button', {
          class: `lane-add${expanded ? ' expanded' : ''}`,
          dataset: { testid: 'band-toggle', cat, band: 'Capabilities' },
          title: expanded ? 'Collapse capabilities' : 'Expand capabilities',
          onclick: () => {
            if (session.expanded.has(key)) session.expanded.delete(key);
            else session.expanded.add(key);
            window.dispatchEvent(new CustomEvent('cap:changed'));
          },
        }, expanded ? '−' : '+')),
      el('small', {}, `${catCaps.length}`));
    const track = el('div', { class: 'track', dataset: { band: 'Capabilities' } },
      el('div', { class: 'month-grid', style: `grid-template-columns:repeat(${TOTAL},1fr)` },
        Array.from({ length: TOTAL }, () => el('span'))));
    for (const c of catCaps) if (c.start_month !== null) track.appendChild(renderBar(c, true));
    for (const m of milestonesFor(cat)) {
      track.appendChild(renderMilestoneLine(m, track, cat, true, m.scope_type === 'global'));
    }
    lane.appendChild(label); lane.appendChild(track);
    body.appendChild(lane);
    if (expanded) body.appendChild(renderDrilldown(cat, 'Capabilities', catCaps, markets));
    group.appendChild(body);
    container.appendChild(group);
  }
}

function renderDrilldown(cat, band, bandCaps, markets) {
  const wrap = el('div', { class: 'drilldown', dataset: { testid: 'band-drilldown', band } });
  if (!bandCaps.length) wrap.appendChild(el('div', { class: 'drill-empty' }, 'No capabilities in this band.'));
  for (const c of bandCaps) {
    const row = el('div', { class: 'drill-row', dataset: { testid: 'cap-row', cap: c.cap_id } });
    const label = el('div', { class: 'drill-label' });
    const link = el('span', { class: 'cap-link', dataset: { cap: c.cap_id }, onclick: (e) => { e.stopPropagation(); openCapModal(c.cap_id); } }, c.cap_id);
    label.appendChild(link);
    label.appendChild(el('span', { class: 'drill-name' }, c.working_name));
    label.appendChild(moscowBadge(c.moscow));
    label.appendChild(admissionBadge(c.roadmap_admission));
    if (c.jira && c.jira.length) {
      const j = c.jira[0];
      label.appendChild(el('span', { class: 'mono dim jira-ev', dataset: { testid: 'jira-evidence' }, title: j.status ? `Status: ${j.status}` : '' },
        `${j.jira_key}${j.target_release ? ` · ${j.target_release}` : ''}`));
    }
    const track = el('div', { class: 'drill-track' },
      el('div', { class: 'drill-grid', style: `grid-template-columns:repeat(${TOTAL},1fr)` },
        Array.from({ length: TOTAL }, () => el('span'))));
    if (c.start_month !== null) track.appendChild(renderBar(c, true, true));
    for (const m of milestonesFor(cat)) {
      const line = renderMilestoneLine(m, track, cat, false, false);
      if (line) track.appendChild(line);
    }
    row.appendChild(label); row.appendChild(track);
    wrap.appendChild(row);
  }
  return wrap;
}

// ---- horizon report views (D-R2; windows over the same data) ----------------
function renderHorizon(container, caps, markets) {
  const [w0, w1] = HORIZONS[session.horizon];
  const count = w1 - w0 + 1;
  const qCount = Math.ceil(count / 3);
  const wrap = el('div', { class: 'horizon-report', dataset: { testid: 'horizon-report' } });
  wrap.appendChild(el('div', { class: 'small dim', style: 'margin:2px 0 8px' },
    `${HORIZON_LABELS.find(([k]) => k === session.horizon)[1]} · ${monthLabel(w0)} → ${monthLabel(w1)} · ${count} months — report view over the same Roadmap data (edit timing in Full view).`));
  const head = el('div', { class: 'hz-header', style: `grid-template-columns:190px 230px repeat(${qCount},1fr)` },
    el('div', {}, 'Strategic Category'), el('div', {}, 'Capabilities'),
    Array.from({ length: qCount }, (_, qi) => el('div', { class: 'q' }, QUARTERS[Math.floor(w0 / 3) + qi] || '')));
  wrap.appendChild(head);
  const cats = [...new Set(caps.map((c) => c.strategic_category))].sort();
  let any = false;
  for (const cat of cats) {
    const catCaps = caps.filter((c) => c.strategic_category === cat);
    // D-R1: one row per category — each capability appears exactly once
    {
      const bandCaps = catCaps;
      const visible = bandCaps.filter((c) => c.start_month !== null
        && c.start_month < w1 + 1 && c.start_month + (c.duration_months ?? 1) > w0);
      if (!visible.length && !bandCaps.length) continue;
      any = any || visible.length > 0;
      const row = el('div', { class: 'hz-row', dataset: { testid: 'hz-row' } },
        el('div', { class: 'hz-cat' }, cat),
        el('div', { class: 'hz-band' }, 'Capabilities'),
        el('div', { class: 'hz-track', style: `--cols:${count}` },
          el('div', { class: 'hz-grid', style: `grid-template-columns:repeat(${count},1fr)` },
            Array.from({ length: count }, (_, i) => el('span', { class: i % 3 === 0 ? 'qsep' : '' }, MONTHS[w0 + i].m)))));
      for (const c of visible) {
        const vs = Math.max(c.start_month, w0);
        const ve = Math.min(c.start_month + c.duration_months, w1 + 1);
        row.querySelector('.hz-track').appendChild(el('div', {
          class: `rbar b-${catColor(cat)} compact`,
          dataset: { testid: 'hz-bar', cap: c.cap_id },
          style: `left:${(vs - w0) / count * 100}%;width:${(ve - vs) / count * 100}%`,
          title: barTitle(c),
          onclick: () => openCapModal(c.cap_id),
        }, el('span', { class: 'bar-title' }, `${c.cap_id} ${c.working_name}`)));
      }
      for (const m of milestonesFor(cat)) {
        if (m.position_month === null || m.position_month === undefined) continue;
        if (m.position_month < w0 || m.position_month > w1) continue;
        row.querySelector('.hz-track').appendChild(el('div', {
          class: 'hz-milestone', dataset: { testid: 'hz-milestone', ms: m.milestone_id },
          style: `left:${((m.position_month - w0) + 0.5) / count * 100}%`,
          title: `${m.milestone_id} · ${m.name}`, onclick: () => openMilestoneEditor(m),
        }, m.milestone_id));
      }
      wrap.appendChild(row);
    }
  }
  if (!any) wrap.appendChild(notice('info', 'No timed capabilities in this horizon window yet.'));
  container.appendChild(wrap);
}

// ---- Outcome view (v38.6 concept, now API-persisted) ------------------------
async function renderOutcome(container) {
  const res = await api.get(endpoints.outcomes());
  session.outcomeDraft = Object.fromEntries(res.items.map((o) => [o.horizon, { ...o }]));
  const panel = el('div', { class: 'outcome-panel', dataset: { testid: 'outcome-panel' } });
  panel.appendChild(el('div', { class: 'small dim', style: 'margin:0 0 8px' },
    'Product narrative per horizon (recovered from v38.6 Roadmap | Outcome). Versioned + audited server-side; never mixed with capability timing.'));
  for (const [h, label] of [['0-6m', '0–6 months'], ['7-24m', '7–24 months'], ['tail', 'Tail / long term']]) {
    const o = session.outcomeDraft[h];
    const ta = el('textarea', {
      class: 'outcome-text', rows: 6, dataset: { testid: `outcome-text-${h}` },
      placeholder: 'Product narrative for this horizon…',
    }, o.narrative || '');
    ta.addEventListener('input', () => { session.outcomeDraft[h].dirty = true; });
    panel.appendChild(el('div', { class: 'outcome-block' },
      el('h3', {}, label, el('span', { class: 'dim small' }, ` · v${o.version}`)),
      ta,
      el('div', { class: 'actions', style: 'margin-top:4px' },
        el('button', {
          dataset: { testid: `outcome-save-${h}` },
          onclick: async () => {
            try {
              const r = await api.patch(endpoints.outcome(h), {
                version: o.version, narrative: ta.value || null,
              });
              o.version = r.version; o.narrative = ta.value || null; o.dirty = false;
              flashStatus(`Outcome ${h} saved (v${r.version}).`, 'ok');
            } catch (err) {
              if (err.status === 409) {
                const fresh = await api.get(endpoints.outcomes());
                const cur = fresh.items.find((x) => x.horizon === h);
                o.version = cur.version; o.narrative = cur.narrative;
                ta.value = cur.narrative || '';
                flashStatus(`Outcome conflict: server now v${cur.version}; your text was replaced with the latest. Reapply intentionally.`, 'warn');
              } else {
                flashStatus(`Outcome save failed: ${JSON.stringify(err.detail || err.message)}`, 'warn');
              }
            }
          },
        }, 'Save'))));
  }
  container.appendChild(panel);
}

// ---- quarter report modal (v10 openQuarter, no add-feature buttons) ---------
function openQuarter(qi, caps) {
  const overlay = openOverlay('quarter-modal');
  const mi = qi * 3;
  const box = el('div', { class: 'modal-drawer', style: 'width:min(1100px,96vw)' });
  overlay.appendChild(box);
  box.appendChild(el('h1', { dataset: { testid: 'quarter-title' } }, `${QUARTERS[qi]} · month detail`));
  const qms = milestones.filter((m) => m.position_month !== null && m.position_month >= mi && m.position_month < mi + 3);
  if (qms.length) {
    box.appendChild(el('div', { style: 'margin-bottom:8px' },
      el('b', {}, 'Milestones: '),
      qms.map((m) => el('button', { class: 'ms-chip', onclick: () => { overlay.remove(); openMilestoneEditor(m); } },
        `${monthLabel(m.position_month)} · ${m.milestone_id} ${m.name}`))));
  }
  const grid = el('div', { class: 'month-detail', dataset: { testid: 'quarter-grid' } });
  grid.appendChild(el('div', { class: 'md-head' }, 'Strategic Category'));
  grid.appendChild(el('div', { class: 'md-head' }, 'Capabilities'));
  for (let x = 0; x < 3; x++) grid.appendChild(el('div', { class: 'md-head' }, monthLabel(mi + x)));
  const cats = [...new Set(caps.map((c) => c.strategic_category))].sort();
  for (const cat of cats) {
    const bandCaps = caps.filter((c) => c.strategic_category === cat);
    {
      grid.appendChild(el('div', { class: 'md-cell cat' }, cat));
      grid.appendChild(el('div', { class: 'md-cell band-name' }, 'Capabilities'));
      for (let off = 0; off < 3; off++) {
        const mth = mi + off;
        const active = bandCaps.filter((c) => c.start_month !== null
          && c.start_month <= mth && c.start_month + c.duration_months > mth);
        grid.appendChild(el('div', { class: 'md-cell', dataset: { testid: 'quarter-cell', m: String(mth) } },
          active.map((c) => el('div', {
            class: 'mini-item', dataset: { testid: 'quarter-chip', cap: c.cap_id },
            title: barTitle(c),
            onclick: () => { overlay.remove(); openCapModal(c.cap_id); },
          },
          `${c.cap_id} ${c.working_name}`,
          el('span', { class: 'mi-meta' }, `MoSCoW ${c.moscow || '—'} · ${c.roadmap_admission || 'UNSET'} · ${c.visibility}`),
          (c.jira && c.jira.length) ? el('span', { class: 'mi-meta mono' }, c.jira.map((j) => `${j.jira_key}${j.target_release ? ` · rel ${j.target_release}` : ''}`).join(' · ')) : null))));
      }
    }
  }
  box.appendChild(grid);
  box.appendChild(el('div', { class: 'actions', style: 'margin-top:10px' },
    el('button', { dataset: { testid: 'quarter-close' }, onclick: () => overlay.remove() }, 'Close')));
}

// ---- design rules (v10 rules tab content, verbatim intent) -------------------
const DESIGN_RULES = [
  ['Voice of Customer first.', 'Each capability records evidence from customers, prospects, RFPs, Sales and early adopters.'],
  ['6 + 18 horizon.', 'The first 6 months are high-confidence planning; the following 18 months are strategic direction. The final tail remains visible for the 3.x transition.'],
  ['Value before feature.', 'Each item records why it matters, for whom, the problem it solves and what it unlocks.'],
  ['Transition is explicit.', 'Studio evolution, 3.x freeze, coexistence, customer migration and retirement sit on the same roadmap.'],
  ['Customer transitions trace to Product.', 'Strategic programmes use shared Product capabilities rather than becoming separate products.'],
  ['Commitment vs Product bet.', 'Locked customer commitments and Product-led strategic investment remain visibly distinct (Roadmap Admission governs this now).'],
  ['Feature level.', 'This remains an executive roadmap. Jira owns epics, stories, engineering detail and execution breakdown.'],
  ['Migration ≠ parity.', 'Data, users, training, procedures, metadata, workflows and adoption are migration gates in addition to feature capability.'],
];

function renderRules(container) {
  const panel = el('details', { class: 'rules-panel', dataset: { testid: 'rules-panel' } },
    el('summary', {}, 'Roadmap design rules'));
  const grid = el('div', { class: 'rules-grid' });
  for (const [t, d] of DESIGN_RULES) grid.appendChild(el('div', { class: 'rule-card' }, el('b', {}, t), el('span', {}, d)));
  panel.appendChild(grid);
  container.appendChild(panel);
}

// ---- Features view (§12–§15/§19) ------------------------------------------
// Feature = Product-managed composition of canonical capabilities. This view
// shows the same canonical data from the composition side: each lane is a
// Feature; the bars are its constituent capabilities (DERIVED coverage — no
// second planning truth). Composition is a Product decision; nothing is
// auto-grouped. Jira Epics and Source Capabilities are never Features.
async function renderFeaturesView(container, markets) {
  const feats = (await api.get(endpoints.features())).items;
  container.appendChild(el('div', { class: 'small dim', style: 'margin:0 0 8px', dataset: { testid: 'features-note' } },
    'Feature view — Product-managed composition of canonical capabilities. Bars are derived from constituent capability timing (no independent Feature timing until Product defines it). Composition is a Product decision; never auto-generated.'));
  container.appendChild(el('div', { class: 'actions', style: 'margin-bottom:8px' },
    el('button', { dataset: { testid: 'feat-add' }, onclick: () => openFeatureEditor() }, '+ Feature')));
  if (!feats.length) {
    container.appendChild(el('div', { dataset: { testid: 'features-empty' } },
      notice('info', 'No Features defined yet. Product creates Features explicitly (FEAT-xxxx) and composes them from canonical capabilities — the app never invents Features or feature groupings.')));
  }
  for (const f of feats) {
    const group = el('div', { class: 'cat-group', dataset: { testid: 'feature-group', feat: f.feat_id } });
    group.appendChild(el('div', { class: 'category cat-grey' },
      el('div', { class: 'mono', style: 'font-size:10px' }, f.feat_id),
      el('div', {}, f.name),
      el('small', {}, `${f.status || '—'} · ${f.capabilities.length} capabilities · v${f.version}`)));
    const body = el('div', { class: 'category-body' });
    const lane = el('div', { class: 'lane' });
    const label = el('div', { class: 'band' },
      el('div', { class: 'band-name' }, el('span', {}, f.description || f.name)),
      el('button', { dataset: { testid: `feat-edit-${f.feat_id}` }, onclick: () => openFeatureEditor(f) }, 'Edit'));
    const track = el('div', { class: 'track' },
      el('div', { class: 'month-grid', style: `grid-template-columns:repeat(${TOTAL},1fr)` },
        Array.from({ length: TOTAL }, () => el('span'))));
    for (const c of f.capabilities) {
      if (c.start_month === null || c.start_month === undefined) continue;
      track.appendChild(renderBar({ ...c, working_name: c.working_name, cap_id: c.cap_id, jira: [], moscow: c.moscow, roadmap_admission: c.roadmap_admission, strategic_category: c.strategic_category }, false, true));
    }
    if (f.derived_timing_window) {
      const w = f.derived_timing_window;
      track.appendChild(el('div', {
        class: 'feature-derived-outline', dataset: { testid: 'feature-derived' },
        style: `left:${w.start_month / TOTAL * 100}%;width:${Math.max(1, (w.end_month_exclusive - w.start_month)) / TOTAL * 100}%`,
        title: `Derived coverage from constituent capabilities: months ${w.start_month}–${w.end_month_exclusive - 1} (no independent Feature timing)`,
      }));
    }
    lane.appendChild(label); lane.appendChild(track);
    body.appendChild(lane);
    if (f.capabilities.length) {
      const capsRow = el('div', { class: 'drilldown' },
        el('div', { class: 'small dim', style: 'padding:4px 8px' }, 'Constituent canonical capabilities:'));
      for (const c of f.capabilities) {
        capsRow.appendChild(el('div', { class: 'drill-row' },
          el('div', { class: 'drill-label' },
            capLink(c.cap_id), el('span', { class: 'drill-name' }, c.working_name), moscowBadge(c.moscow), admissionBadge(c.roadmap_admission),
            el('button', {
              class: 'danger small', dataset: { testid: `feat-unlink-${f.feat_id}-${c.cap_id}` },
              onclick: async () => { await api.del(`${endpoints.features()}/${f.feat_id}/capabilities/${c.cap_id}`); window.dispatchEvent(new CustomEvent('cap:changed')); },
            }, 'remove')),
          el('div', { class: 'drill-track' })));
      }
      body.appendChild(capsRow);
    }
    group.appendChild(body);
    container.appendChild(group);
  }
}

function openFeatureEditor(f = null) {
  document.querySelectorAll('.modal-overlay[data-featmodal]').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { featmodal: '1', testid: 'feat-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer', style: 'width:min(620px,94vw)' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  const isEdit = !!f;
  drawer.appendChild(el('h1', {}, isEdit ? `Edit Feature · ${f.feat_id}` : 'New Feature (Product-managed composition)'));
  const sel = (name, options, current) => el('select', { name },
    options.map((o) => el('option', { value: o, ...(o === (current ?? '') ? { selected: '' } : {}) }, o === '' ? '— choose —' : o)));
  drawer.appendChild(el('div', { class: 'edit-form', dataset: { testid: 'feat-form' } },
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Feature ID (governed, e.g. FEAT-0001)'),
      el('input', { type: 'text', name: 'feat_id', dataset: { testid: 'feat-id' }, disabled: isEdit, value: f?.feat_id || '' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Feature name'),
      el('input', { type: 'text', name: 'name', dataset: { testid: 'feat-name' }, value: f?.name || '' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Description'),
      el('textarea', { name: 'description', rows: 2, style: 'width:100%' }, f?.description || '')),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Product owner / PM'),
      el('input', { type: 'text', name: 'owner', value: f?.owner || '' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Status'),
      el('input', { type: 'text', name: 'status', value: f?.status || '', placeholder: 'e.g. Draft / Committed' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Notes'),
      el('input', { type: 'text', name: 'notes', value: f?.notes || '', style: 'width:100%' })),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Add constituent capability (CAP-ID)'),
      el('div', { style: 'display:flex;gap:6px' },
        el('input', { type: 'text', name: 'add_cap', placeholder: 'CAP-xxxx', dataset: { testid: 'feat-add-cap' }, style: 'width:160px' }),
        el('button', { dataset: { testid: 'feat-add-cap-btn' }, onclick: () => addFeatureCap(overlay, isEdit ? f : null) }, 'Add link'))),
    el('div', { class: 'actions', style: 'margin-top:12px' },
      el('button', { class: 'primary', dataset: { testid: 'feat-save' }, onclick: () => saveFeature(overlay, isEdit ? f : null) }, 'Save'),
      el('button', { onclick: () => overlay.remove() }, 'Cancel'))));
  // link management row for existing links
  if (isEdit && f.capabilities.length) {
    drawer.appendChild(el('h3', {}, 'Constituent capabilities'));
    for (const c of f.capabilities) {
      drawer.appendChild(el('div', { class: 'jira-row' },
        el('span', { class: 'mono' }, c.cap_id), el('span', { class: 'small' }, c.working_name),
        el('button', { class: 'danger small', onclick: async (e) => {
          await api.del(`${endpoints.features()}/${f.feat_id}/capabilities/${c.cap_id}`);
          e.target.closest('.jira-row').remove();
        } }, 'remove link')));
    }
  }
}

async function addFeatureCap(overlay, f) {
  const capId = overlay.querySelector('[name="add_cap"]').value.trim();
  if (!capId) return;
  if (!f) { overlay.querySelector('.modal-drawer').appendChild(notice('warn', 'Save the Feature first, then add capability links.')); return; }
  try {
    await api.post(`${endpoints.features()}/${f.feat_id}/capabilities/${capId}`);
    window.dispatchEvent(new CustomEvent('cap:changed'));
  } catch (err) {
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 404 ? `Not found: ${JSON.stringify(err.detail)}`
        : err.status === 409 ? 'Link already exists.' : `Add failed: ${err.message}`));
  }
}

async function saveFeature(overlay, existing) {
  const g = (n) => overlay.querySelector(`[name="${n}"]`);
  const body = {
    name: g('name').value.trim(), description: g('description').value.trim() || null,
    owner: g('owner').value.trim() || null, status: g('status').value.trim() || null,
    notes: g('notes').value.trim() || null,
  };
  if (!body.name) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Feature name is required.')); return; }
  try {
    if (existing) await api.patch(`${endpoints.features()}/${existing.feat_id}`, { ...body, version: existing.version });
    else {
      const id = g('feat_id').value.trim();
      if (!id) { overlay.querySelector('.modal-drawer').appendChild(notice('error', 'Feature ID is required (governed, e.g. FEAT-0001).')); return; }
      await api.post(endpoints.features(), { feat_id: id, ...body });
    }
    overlay.remove();
    window.dispatchEvent(new CustomEvent('cap:changed'));
  } catch (err) {
    overlay.querySelector('.modal-drawer').appendChild(notice('error',
      err.status === 409 ? `Conflict: feature now v${err.detail?.current_version}.`
        : `Save failed: ${JSON.stringify(err.detail || err.message)}`));
  }
}

// ---- entry -------------------------------------------------------------------
export async function renderRoadmap(container) {
  container.replaceChildren();
  const markets = await getMarkets();
  milestones = (await api.get(endpoints.milestones())).items;

  container.appendChild(el('h1', {}, 'Roadmap — Action Plan & Migration'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'Editable executive roadmap · Oct 2026 → Dec 2028 (27 months) · TAO Studio becomes the common authoring environment; TAO 3.x Authoring is progressively retired. Product timing only — Jira release fields are delivery evidence, never timing.'));

  // toolbar: view switch (Roadmap | Outcome), Capabilities | Features (§19), horizons, filters, milestone add
  const bar = el('div', { class: 'road-toolbar' },
    el('div', { class: 'seg' },
      el('button', {
        class: session.mode === 'roadmap' ? 'active' : '', dataset: { testid: 'view-roadmap' },
        onclick: () => { session.mode = 'roadmap'; window.dispatchEvent(new CustomEvent('cap:changed')); },
      }, 'Roadmap'),
      el('button', {
        class: session.mode === 'outcome' ? 'active' : '', dataset: { testid: 'view-outcome' },
        onclick: () => { session.mode = 'outcome'; window.dispatchEvent(new CustomEvent('cap:changed')); },
      }, 'Outcome')),
    el('div', { class: 'seg', dataset: { testid: 'roadmap-content-switch' } },
      el('button', {
        class: session.mode === 'roadmap' && session.roadmapView === 'capabilities' ? 'active' : '',
        dataset: { testid: 'content-capabilities' },
        onclick: () => { session.mode = 'roadmap'; session.roadmapView = 'capabilities'; window.dispatchEvent(new CustomEvent('cap:changed')); },
      }, 'Capabilities'),
      el('button', {
        class: session.mode === 'roadmap' && session.roadmapView === 'features' ? 'active' : '',
        dataset: { testid: 'content-features' },
        onclick: () => { session.mode = 'roadmap'; session.roadmapView = 'features'; window.dispatchEvent(new CustomEvent('cap:changed')); },
      }, 'Features')),
    el('div', { class: 'seg' },
      HORIZON_LABELS.map(([k, label]) => el('button', {
        class: session.mode === 'roadmap' && session.roadmapView === 'capabilities' && session.horizon === k ? 'active' : '',
        dataset: { testid: `hz-${k}` },
        onclick: () => { session.mode = 'roadmap'; session.roadmapView = 'capabilities'; session.horizon = k; window.dispatchEvent(new CustomEvent('cap:changed')); },
      }, label))),
    el('div', { class: 'seg grow' },
      el('button', { dataset: { testid: 'ms-add' }, onclick: () => openMilestoneEditor() }, '+ Milestone')),
  );
  container.appendChild(bar);

  // filters (§16) — never reset timing/expansion/outcome (session state)
  const fsel = (key, title, options) => el('label', { class: 'f' }, title,
    el('select', { dataset: { testid: `rfilter-${key}` },
      // inline handler: survives re-render races (a select replaced between
      // interaction and dispatch still updates state — QA-verified defect)
      onchange: (e) => { session.filters[key] = e.target.value; window.dispatchEvent(new CustomEvent('cap:changed')); } },
      options.map(([v, l]) => el('option', { value: v, ...(session.filters[key] === v ? { selected: '' } : {}) }, l))));
  const fbar = el('div', { class: 'filter-bar', dataset: { testid: 'roadmap-filters' } },
    fsel('admission', 'Roadmap admission', [
      ['COMMITTED', 'Committed (default)'], ['All', 'All states'], ['CANDIDATE', 'Candidate'],
      ['BACKLOG', 'Backlog'], ['DEFERRED', 'Deferred'], ['NOT PLANNED', 'Not planned'], ['UNSET', 'UNSET'],
    ]),
    fsel('market', 'Market', [['', 'Market · All'], ...markets.map((m) => [m.name, m.name])]),
    fsel('moscow', 'MoSCoW', [['', 'MoSCoW · All'], ['Must', 'Must'], ['Should', 'Should'], ['Could', 'Could'], ["Won't", "Won't"]]),
    fsel('visibility', 'Visibility', [['', 'Visibility · All'], ['Shared / common core', 'Shared / common core'], ['Shared / market-configured', 'Shared / market-configured'], ['Market-specific', 'Market-specific']]));
  container.appendChild(fbar);

  statusLine = el('div', { class: 'road-status', dataset: { testid: 'roadmap-status' } });
  container.appendChild(statusLine);

  const view = el('div', { dataset: { testid: 'roadmap-view' } });
  container.appendChild(view);
  container.appendChild(marketLegend(markets));

  const caps = await loadCaps(session.filters);
  // client-side MoSCoW/visibility narrowing (API covers market/admission)
  const narrowed = caps.filter((c) =>
    (!session.filters.moscow || c.moscow === session.filters.moscow)
    && (!session.filters.visibility || c.visibility === session.filters.visibility));

  if (session.mode === 'outcome') {
    view.replaceChildren();
    await renderOutcome(view);
  } else if (session.roadmapView === 'features') {
    view.replaceChildren();
    await renderFeaturesView(view, markets);
  } else {
    view.replaceChildren();
    if (session.horizon === 'full') renderFull(view, narrowed, markets);
    else renderHorizon(view, narrowed, markets);
  }
  renderRules(container);

  // (filter selects carry inline handlers — no bubbled listener needed here)
}
