// Universal canonical Capability Detail/Edit drawer (§7–§11/§15/§18).
// ONE component used everywhere a CAP-ID appears. 409 conflicts surface as
// a reconciliation state, budgets keep NULL≠0, admission stays UNSET-able.

import { api, endpoints } from '../api.js';
import { el, esc, capLink, fmtHours, moscowBadge, admissionBadge, reviewBadge, marketDotsFor, marketLegend, notice, table } from '../ui.js';

let marketsCache = null;
export async function getMarkets() {
  if (!marketsCache) marketsCache = (await api.get(endpoints.markets())).items;
  return marketsCache;
}

const ADMISSIONS = ['', 'COMMITTED', 'CANDIDATE', 'BACKLOG', 'DEFERRED', 'NOT PLANNED'];
const CATEGORIES = ['Create & Design', 'Manage & Govern', 'Collaborate & Assure Quality', 'Standards & Portability', 'AI-assisted Authoring'];
const MOSCOW = ['', 'Must', 'Should', 'Could', "Won't"];
const PRODUCT_REVIEW_OPTIONS = ['', 'REVIEW_REQUIRED', 'CONFIRMED', 'CONFIRMED_WITH_CHANGES', 'REJECTED'];

export async function openCapModal(capId) {
  closeCapModal();
  const overlay = el('div', { class: 'modal-overlay', dataset: { testid: 'cap-modal' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeCapModal(); });
  const drawer = el('div', { class: 'modal-drawer' });
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  try {
    const cap = await api.get(endpoints.capability(capId));
    const markets = await getMarkets();
    renderDetail(drawer, cap, markets);
    if (cap.cap_id.startsWith('CAND-') || (cap.population || '').startsWith('SOURCE_ANALYSIS')) {
      try {
        const ce = await api.get(`${endpoints.candidates()}/${cap.cap_id.replace('CAND-', '')}`);
        renderCandidateEnrichment(drawer, ce.enrichment, ce);
      } catch (_) { /* enrichment is additive */ }
    }
  } catch (err) {
    drawer.appendChild(notice('error', `Failed to load ${capId}: ${err.detail || err.message}`));
  }
}

export function closeCapModal() {
  // Remove ONLY the CAP drawer overlay — other open layers (source drill-down
  // pane, customer-plan pane, quarter modal) are independent and must survive
  // closing a CAP drawer opened on top of them.
  document.querySelectorAll('.modal-overlay[data-testid="cap-modal"]').forEach((n) => n.remove());
}

function kv(k, v) {
  return el('div', { class: 'kv' }, el('div', { class: 'k' }, k), el('div', { class: 'v' }, v ?? el('span', { class: 'dim' }, '—')));
}

function renderCandidateEnrichment(drawer, e, ce) {
  if (!e) return;
  const sec = (t) => el('h3', {}, t);
  const p = (label, v, marker) => el('div', { class: 'kv' },
    el('div', { class: 'k' }, label, marker ? el('div', { class: 'small dim' }, marker) : null),
    el('div', { class: 'v' }, v || el('span', { class: 'dim' }, 'Evidence insufficient to determine')));
  const pd = e.product_definition || {};
  const ctx = e.product_context || {};
  const ev = e.evidence || {};
  const an = e.analysis_rationale || {};
  drawer.appendChild(sec('PRODUCT DEFINITION (PRODUCT INTERPRETATION — consolidated from source evidence)'));
  drawer.append(
    p('Functional definition', pd.functional_definition),
    p('What it enables', pd.what_it_enables),
    p('User / product problem addressed', pd.user_problem_addressed),
    p('Functional scope', pd.functional_scope),
    p('Out of scope', pd.out_of_scope));
  drawer.appendChild(sec('PRODUCT CONTEXT'));
  drawer.append(
    p('MEXCBT / Uchida', ctx.mexcbt_signals > 0 ? `${ctx.mexcbt_signals} direct signals` : 'no direct signals recorded'),
    p('Strategic relevance / alignment', ctx.strategy_alignment),
    p('Cross-market leverage', ctx.cross_market_leverage),
    p('Evidence strength', ctx.evidence_strength),
    p('Focus', ctx.is_focus ? `YES — focus markets: ${ctx.focus_markets || '—'}` : 'NO (not in the Cross-market Focus Set)'));
  drawer.appendChild(sec('EVIDENCE & RATIONALE'));
  drawer.append(
    p('Why this candidate exists', an.why_this_candidate),
    p('Consolidation rationale', an.consolidation_rationale),
    p(`Source evidence (${ev.count} signals)`,
      el('span', { class: 'small mono' }, (ev.signal_ids || []).join(', ')), el('br'),
      el('span', { class: 'small' }, 'Sources: ' + (ev.sources || []).join(', '))),
    p('Key evidence references', (ev.key_references || []).join(' · ')),
    p('Provenance', ev.provenance));
  drawer.appendChild(sec('DELIVERY EVIDENCE (Jira — work evidence, not Product truth)'));
  drawer.appendChild(el('div', { dataset: { testid: 'candidate-jira' } },
    (e.delivery_evidence?.jira || []).length
      ? table(['Key', 'Summary', 'Status', 'Target Release'],
          e.delivery_evidence.jira.map((j) => el('tr', {},
            el('td', {}, el('a', { class: 'mono', href: j.jira_url || '#', target: '_blank', rel: 'noopener' }, j.jira_key)),
            el('td', { class: 'small' }, j.summary || ''),
            el('td', {}, j.status || '—'),
            el('td', {}, j.target_release || '—'))))
      : el('span', { class: 'dim' }, 'No Jira relationships recorded for this candidate.')));
  const pr = e.product_review || {};
  drawer.appendChild(sec('PRODUCT DECISIONS REQUIRED'));
  drawer.appendChild(el('div', { class: 'notice warn small', dataset: { testid: 'candidate-open-questions' } },
    (pr.open_questions || []).map((q) => `• ${q}`).join('  ') || 'None recorded.'));
  drawer.appendChild(p('Uncertainty', pr.uncertainty));
}

function renderDetail(drawer, cap, markets, justSaved = false) {
  drawer.replaceChildren();
  const head = el('div', { class: 'drawer-head' },
    el('h1', {}, `${cap.cap_id} · ${cap.working_name}`),
    reviewBadge(cap.review_status),
    el('div', { class: 'actions' },
      el('button', { dataset: { testid: 'cap-edit-btn' }, onclick: () => renderEdit(drawer, cap, markets) }, 'Edit'),
      el('button', { onclick: closeCapModal }, 'Close')));

  if (justSaved) drawer.appendChild(notice('ok', 'Saved.'));

  const jiraRows = cap.jira.map((j) => el('div', { class: 'jira-row', dataset: { testid: 'jira-row' } },
    el('a', { class: 'key cap-link mono', href: j.jira_url || '#', target: '_blank', rel: 'noopener', style: 'color:var(--accent)' }, j.jira_key),
    el('span', { class: 'small' }, j.summary || ''),
    el('span', { class: 'badge' }, j.status || '—'),
    j.target_release ? el('span', { class: 'badge' }, `Rel ${j.target_release}`) : null));

  drawer.append(
    head,
    kv('CAP-ID', el('span', { class: 'mono' }, cap.cap_id)),
    kv('Working name', el('pre', {}, cap.working_name)),
    kv('Full functional description', el('pre', {}, cap.description)),
    kv('Strategic Category', cap.strategic_category),
    el('div', { class: 'kv' }, el('div', { class: 'k' }, 'Markets'),
      el('div', { class: 'v' }, marketDotsFor(cap.markets, markets), el('span', { class: 'dim small' }, ` ${cap.markets.length} markets`))),
    kv('MoSCoW', moscowBadge(cap.moscow)),
    kv('Roadmap Admission', admissionBadge(cap.roadmap_admission)),
    kv('Visibility', cap.visibility), kv('Scope', cap.scope),
    kv('Owner', cap.owner), kv('Origin (ideation provenance)', cap.origin),
    kv('Decision', cap.decision), kv('V2 mapping', el('pre', {}, cap.v2_mapping)),
    kv('Origin / Extraction provenance', el('span', {
      class: 'badge', dataset: { testid: 'extraction-origin' },
      title: 'How this information entered the system — historical provenance, never overwritten by review',
    }, cap.extraction_origin || '— (recorded during source reconstruction)')),
    kv('Product Review', el('span', {
      class: `badge ${cap.product_review_status ? 'ok-badge' : 'dim'}`,
      dataset: { testid: 'product-review' },
      title: 'Editable Product decision — separate from extraction provenance',
    }, cap.product_review_status || 'NOT REVIEWED YET')),
    cap.product_rationale ? kv('Product rationale', el('pre', {}, cap.product_rationale)) : null,
    cap.traceability_status === 'TRACEABILITY_REVIEW_REQUIRED' ? el('div', {
      class: 'notice warn small', dataset: { testid: 'traceability-warning' } },
      'TRACEABILITY_REVIEW_REQUIRED — no Source Capability reconciles to this CAP yet (or it is a Product-created capability without rationale).') : null,
    el('div', { class: 'notice warn small' },
      `Product Roadmap timing ≠ Jira Target Release — they are different truths (§35). Timing: start M${cap.roadmap_timing ? cap.roadmap_timing.start_month : '—'}, duration ${cap.roadmap_timing ? cap.roadmap_timing.duration_months : '—'} months.`),
    el('h3', {}, 'Sources & Evidence'),
    table(['SRC-ID', 'Document', 'Relationship'], cap.sources.map((s) =>
      el('tr', {}, el('td', {}, s.source_id), el('td', {}, s.title), el('td', {}, s.relationship || '—')))),
    el('h3', {}, 'Source capability lineage'),
    table(['Source Capability', 'Relationship', 'Canonical'], cap.source_capabilities.map((sc) =>
      el('tr', {}, el('td', {}, el('span', { class: 'mono' }, sc.source_capability_id), ' · ', sc.original_name || ''),
        el('td', {}, sc.reconciliation_relationship || '—'), el('td', {}, capLink(sc.canonical_cap_id))))),
    el('h3', {}, `Jira — delivery evidence (${cap.jira.length})`),
    el('div', { dataset: { testid: 'jira-list' } }, jiraRows.length ? jiraRows : el('span', { class: 'dim' }, 'No Jira links')),
    el('h3', {}, 'Budgets (hours)'),
    el('div', { class: 'kv' },
      el('div', { class: 'k' }, 'Analysis / Execution / Total'),
      el('div', { class: 'v', dataset: { testid: 'cap-budgets' } },
        `${fmtHours(cap.analysis_budget_hours)} / ${fmtHours(cap.execution_budget_hours)} / `,
        el('strong', {}, fmtHours(cap.total_budget_hours)),
        cap.analysis_budget_hours === null && cap.execution_budget_hours === null
          ? el('span', { class: 'dim small' }, '  · not estimated') : '')),
    kv('Notes', cap.notes ? el('pre', {}, cap.notes) : null),
    kv('Review status', reviewBadge(cap.review_status) || cap.review_status),
    kv('Version / updated', `v${cap.version} · ${cap.updated_at ? cap.updated_at.slice(0, 19) : '—'}`),
    marketLegend(markets));
}

function renderEdit(drawer, cap, markets) {
  drawer.replaceChildren();
  const sel = (name, options, current) => el('select', { name },
    options.map((o) => el('option', { value: o, ...(o === (current ?? '') ? { selected: '' } : {}) }, o === '' ? '— UNSET —' : o)));
  const num = (name, v) => el('input', { type: 'number', min: '0', step: '1', name, placeholder: 'not estimated', ...(v === null || v === undefined ? {} : { value: String(v) }) });
  const mkRow = (m) => el('label', { style: 'display:flex;gap:6px;align-items:center;margin:2px 0' },
    el('input', { type: 'checkbox', name: 'market', value: m.name, ...(cap.markets.some((x) => x.name === m.name) ? { checked: '' } : {}) }),
    el('span', { class: 'dot', style: `background:${m.color}` }), m.name);

  const form = el('div', { dataset: { testid: 'cap-edit-form' } },
    el('div', { class: 'fld-grid' },
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Working name'), el('input', { type: 'text', name: 'working_name', value: cap.working_name, style: 'width:100%' })),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Strategic Category'), sel('strategic_category', CATEGORIES, cap.strategic_category)),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'MoSCoW'), sel('moscow', MOSCOW, cap.moscow ?? undefined)),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Roadmap Admission (NULL = UNSET)'), sel('roadmap_admission', ADMISSIONS, cap.roadmap_admission ?? undefined)),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Visibility'), el('input', { type: 'text', name: 'visibility', value: cap.visibility || '' })),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Owner'), el('input', { type: 'text', name: 'owner', value: cap.owner || '' })),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Decision'), el('input', { type: 'text', name: 'decision', value: cap.decision || '' })),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Product Review (separate from extraction provenance)'), sel('product_review_status', PRODUCT_REVIEW_OPTIONS, cap.product_review_status ?? undefined)),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Ideation sheet'), el('input', { type: 'text', name: 'ideation_sheet', value: cap.ideation_sheet || '' })),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Analysis Budget (hours)'), num('analysis_budget_hours', cap.analysis_budget_hours)),
      el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Execution Budget (hours)'), num('execution_budget_hours', cap.execution_budget_hours))),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Full description'), el('textarea', { name: 'description', rows: '4', style: 'width:100%' }, cap.description || '')),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Product rationale (required once Origin = PRODUCT_CREATED)'), el('textarea', { name: 'product_rationale', rows: '2', style: 'width:100%', dataset: { testid: 'product-rationale' } }, cap.product_rationale || '')),
    el('label', { class: 'fld' }, el('span', { class: 'lbl' }, 'Notes'), el('input', { type: 'text', name: 'notes', value: cap.notes || '' , style: 'width:100%'})),
    el('h3', {}, 'Markets'), el('div', { dataset: { testid: 'mk-checkboxes' } }, markets.map(mkRow)),
    el('h3', {}, `Jira links (0..N) — delivery evidence`), 
    el('div', { dataset: { testid: 'jira-edit-rows' } }, cap.jira.map((j) => el('div', { class: 'jira-row' },
      el('span', { class: 'key mono' }, j.jira_key), el('span', { class: 'small' }, j.summary || ''),
      el('span', { class: 'badge' }, j.status || '—'),
      el('button', { class: 'danger', dataset: { testid: 'jira-remove', key: j.jira_key }, onclick: (e) => removeJira(e, cap, markets, j.jira_key) }, 'remove')))),
    el('div', { class: 'jira-row', style: 'margin-top:6px;border-bottom:none' },
      el('input', { type: 'text', name: 'new_jira_key', placeholder: 'Jira key, e.g. PCR-123', dataset: { testid: 'jira-add-input' } }),
      el('button', { dataset: { testid: 'jira-add-btn' }, onclick: (e) => addJira(e, cap, markets) }, '＋ Add Jira link')),
    el('div', { class: 'actions', style: 'margin-top:14px;display:flex;gap:8px' },
      el('button', { class: 'primary', dataset: { testid: 'cap-save-btn' }, onclick: (e) => save(e, cap, markets) }, 'Save'),
      el('button', { onclick: () => renderDetail(drawer, cap, markets) }, 'Cancel')));

  drawer.appendChild(form);
}

async function save(e, cap, markets) {
  const drawer = e.target.closest('.modal-drawer');
  e.target.disabled = true;
  const g = (n) => drawer.querySelector(`[name="${n}"]`);
  const numVal = (n) => { const v = g(n).value; return v === '' ? null : Number(v); };
  const body = { version: cap.version };
  const fields = ['working_name', 'strategic_category', 'moscow', 'roadmap_admission',
    'visibility', 'owner', 'decision', 'ideation_sheet', 'notes',
    'product_review_status', 'product_rationale'];
  for (const f of fields) {
    const v = g(f).value;
    const norm = v === '' ? null : v;
    if (norm !== (cap[f] ?? null)) body[f] = norm;
  }
  const desc = g('description').value;
  if (desc !== (cap.description ?? '')) body.description = desc;
  const a = numVal('analysis_budget_hours'), x = numVal('execution_budget_hours');
  if (a !== cap.analysis_budget_hours ? true : a !== null) body.analysis_budget_hours = a;
  if (x !== cap.execution_budget_hours ? true : x !== null) body.execution_budget_hours = x;
  const chosen = [...drawer.querySelectorAll('input[name="market"]:checked')].map((c) => c.value);
  if (JSON.stringify([...chosen].sort()) !== JSON.stringify([...cap.markets.map((m) => m.name)].sort())) body.markets = chosen;

  try {
    const resp = await api.patch(endpoints.capability(cap.cap_id), body);
    const fresh = await api.get(endpoints.capability(cap.cap_id));
    window.dispatchEvent(new CustomEvent('cap:changed', { detail: cap.cap_id }));
    renderDetail(drawer, fresh, markets, true);
  } catch (err) {
    e.target.disabled = false;
    if (err.status === 409) {
      renderConflict(drawer, cap, markets, err.detail);
    } else {
      drawer.prepend(notice('error', (err.detail && JSON.stringify(err.detail)) || err.message));
    }
  }
}

function renderConflict(drawer, cap, markets, detail) {
  drawer.replaceChildren();
  const cur = (detail || {}).current_version ?? 'unknown';
  drawer.append(
    el('h1', {}, `${cap.cap_id} · edit conflict`),
    notice('warn', `Another user saved this record after you opened it. The server holds version ${cur}; your edit used version ${cap.version}. Nothing was overwritten — review the latest state and reapply intentionally.`),
    el('div', { class: 'actions', style: 'display:flex;gap:8px' },
      el('button', { class: 'primary', dataset: { testid: 'conflict-reload' }, onclick: async () => {
        const fresh = await api.get(endpoints.capability(cap.cap_id));
        renderDetail(drawer, fresh, markets);
      } }, 'Show latest version'),
      el('button', { onclick: closeCapModal }, 'Close')));
}

async function addJira(e, cap, markets) {
  const drawer = e.target.closest('.modal-drawer');
  const input = drawer.querySelector('[name="new_jira_key"]');
  const key = input.value.trim();
  if (!key) return;
  try {
    await api.post(endpoints.jiraLink(cap.cap_id), { jira_key: key });
    const fresh = await api.get(endpoints.capability(cap.cap_id));
    renderEdit(drawer, fresh, markets);
  } catch (err) {
    drawer.prepend(notice('error', `Add Jira link failed: ${(err.detail && (typeof err.detail === 'string' ? err.detail : err.detail.error)) || err.message}`));
  }
}

async function removeJira(e, cap, markets, key) {
  const drawer = e.target.closest('.modal-drawer');
  try {
    await api.del(endpoints.jiraUnlink(cap.cap_id, key));
    const fresh = await api.get(endpoints.capability(cap.cap_id));
    renderEdit(drawer, fresh, markets);
  } catch (err) {
    drawer.prepend(notice('error', `Remove failed: ${err.detail || err.message}`));
  }
}
