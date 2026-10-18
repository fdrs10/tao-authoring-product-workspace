// Sources & Evidence (§5/§20). Priority workflow — SRC-JIRA-001 behaves as
// a real Source (Operational / Delivery Evidence, never capability truth).
// Source Truth is displayed verbatim, never rewritten (§10/§18).

import { api, endpoints } from '../api.js';
import { el, capLink, notice, table } from '../ui.js';
import { openCapModal } from '../components/capmodal.js';

export async function renderSources(container) {
  container.replaceChildren();
  // CONTROLLED OPERATION: Source-analysis funnel (§10) — governed counts
  const funnel = await api.get(endpoints.funnel()).catch(() => null);
  if (funnel) {
    const f = funnel.funnel;
    container.appendChild(el('div', { class: 'filter-bar', dataset: { testid: 'funnel-banner' } },
      el('span', { class: 'flow-step' }, `${f.sources} Sources`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.evidence_signals} Evidence Signals`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.capability_candidates} Capability Candidates`),
      el('span', { class: 'flow-arrow' }, '→'),
      el('span', { class: 'flow-step' }, `${f.focus_capabilities} Focus Capabilities`)));
  }
  const tabs = el('div', { class: 'subtabs' },
    el('a', { class: 'active', dataset: { tab: 'sources', testid: 'tab-sources' } }, 'Source Registry'),
    el('a', { dataset: { tab: 'capabilities', testid: 'tab-src-capabilities' } }, 'Capabilities'),
    el('a', { dataset: { tab: 'evidence', testid: 'tab-evidence' } }, 'Extracted Authoring Evidence'),
    el('a', { dataset: { tab: 'analysis', testid: 'tab-analysis' } }, 'Capability Analysis'),
    el('a', { dataset: { tab: 'candidates', testid: 'tab-candidates' } }, 'Capability Candidates'),
    el('a', { dataset: { tab: 'focus', testid: 'tab-focus' } }, 'Focus Capability Sets'),
    el('a', { dataset: { tab: 'customers', testid: 'tab-customers' } }, 'Customers'));
  const body = el('div', { dataset: { testid: 'sources-body' } });
  container.append(el('h1', {}, 'Sources & Evidence'), tabs, body);
  tabs.addEventListener('click', (e) => {
    const t = e.target.dataset.tab;
    if (!t) return;
    tabs.querySelectorAll('a').forEach((a) => a.classList.toggle('active', a.dataset.tab === t));
    if (t === 'sources') renderSourceList(body);
    if (t === 'evidence') renderEvidence(body);
    if (t === 'analysis') renderAnalysis(body);
    if (t === 'candidates') renderCandidatesTab(body, 'all');
    if (t === 'focus') renderCandidatesTab(body, 'focus');
    if (t === 'capabilities') renderAllSourceCaps(body);
    if (t === 'customers') renderCustomers(body);
  });
  await renderSourceList(body);
}

async function renderEvidence(body) {
  body.replaceChildren();
  body.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'Extracted Authoring Evidence — the 426-signal evidence universe (Source Truth layer, NOT canonical Product Truth).'));
  const res = await api.get(endpoints.evidence());
  body.appendChild(table(['Evidence ID', 'Source', 'Signal', 'Strategic Category', 'Authoring Scope', 'Extraction', 'Treatment'],
    res.items.map((e) => el('tr', { dataset: { testid: 'evidence-row' } },
      el('td', { class: 'mono' }, e.evidence_id),
      el('td', { class: 'mono' }, e.source_id),
      el('td', {}, e.signal_name),
      el('td', {}, e.strategic_category || '—'),
      el('td', { class: 'small' }, e.authoring_scope || '—'),
      el('td', { class: 'small' }, e.extraction_type || '—'),
      el('td', { class: 'small' }, e.current_treatment || '—')))));
}

async function renderAnalysis(body) {
  body.replaceChildren();
  body.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    'Capability Analysis — how the evidence universe became the Candidate set (consolidation, disposition, provenance).'));
  const res = await api.get(endpoints.evidence());
  body.appendChild(table(['Evidence / Analysis ID', 'Source', 'Signal', 'Authoring Scope', 'MEXCBT / Uchida', 'Treatment', 'Evidence / Reference'],
    res.items.map((e) => el('tr', { dataset: { testid: 'analysis-row' } },
      el('td', { class: 'mono' }, e.evidence_id),
      el('td', { class: 'mono' }, e.source_id),
      el('td', {}, e.signal_name),
      el('td', { class: 'small' }, e.authoring_scope || '—'),
      el('td', { class: 'small' }, e.mexcbt_relevance || '—'),
      el('td', { class: 'small' }, e.current_treatment || '—'),
      el('td', { class: 'small mono' }, e.evidence_reference || '—')))));
}

async function renderCandidatesTab(body, mode) {
  body.replaceChildren();
  body.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:6px' },
    mode === 'focus'
      ? 'Focus Capability Sets — the 15 Cross-market Focus Capabilities (Product recommendation, subset of the Candidates).'
      : 'Capability Candidates — the initial active Product set (34 reconciled candidates).'));
  const res = await api.get(endpoints.candidates(), mode === 'focus' ? { focus: 'yes' } : {});
  body.appendChild(table(['Candidate', 'Working Capability', 'Markets', 'MEXCBT / Uchida', 'Signals', 'Strength', 'Cross-market', 'Status'],
    res.items.map((c) => el('tr', { dataset: { testid: 'candidate-analysis-row' } },
      el('td', { class: 'mono' }, c.candidate_id),
      el('td', {}, c.name),
      el('td', { class: 'small' }, c.markets || '—'),
      el('td', {}, String(c.mexcbt_signals)),
      el('td', {}, String(c.signals)),
      el('td', {}, c.evidence_strength || '—'),
      el('td', {}, c.cross_market_leverage || '—'),
      el('td', { class: 'small' }, c.package_status || '—')))));
}

async function renderSourceList(body) {
  body.replaceChildren();
  const srcs = await api.get(endpoints.sources());
  body.appendChild(table(
    ['SRC-ID', 'Document', 'Owner', 'Type', 'Date / Version', 'Extracted', 'Artifact', 'Actions'],
    srcs.items.map((s) => el('tr', { dataset: { testid: 'source-row' } },
      el('td', { class: 'mono' }, s.source_id),
      el('td', {}, el('strong', {}, s.title)),
      el('td', {}, s.owner || '—'),
      el('td', {}, s.source_type || '—'),
      el('td', {}, [s.source_date, s.version_label].filter(Boolean).join(' · ') || '—'),
      el('td', { class: 'right', dataset: { testid: 'extracted-count' } }, String(s.extracted_capability_count)),
      el('td', {}, el('span', {
        class: s.document_available ? 'badge ok-badge' : 'badge dim',
        dataset: { testid: 'artifact-availability' },
        title: s.document_uri || 'no artifact registered',
      }, s.document_available ? 'available' : 'unavailable')),
      el('td', {},
        el('button', { dataset: { testid: 'open-source', src: s.source_id }, onclick: () => openSourceDetail(s.source_id) }, 'Open Source'),
        ' ',
        el('button', { dataset: { testid: 'view-extracted', src: s.source_id }, onclick: () => openSourceCaps(s.source_id) }, 'View Extracted'))))));
}

async function openSourceDetail(sourceId) {
  const s = await api.get(endpoints.source(sourceId));
  openPane(`${s.source_id} · ${s.title}`, (pane) => {
    pane.append(
      el('div', { class: 'kv' }, ...[
        ['SRC-ID', s.source_id], ['Document', s.title], ['Type', s.source_type],
        ['Owner', s.owner], ['Input form', s.input_form], ['Status', s.status],
        ['Upstream', s.upstream_reference], ['Location', s.document_uri],
        ['Summary', s.summary],
      ].flatMap(([k, v]) => [el('div', { class: 'k' }, k), el('div', { class: 'v' }, v || '—')])),
    );
    // §3: Open Source opens the ACTUAL artifact — or states explicitly that it
    // is unavailable. Never a fake action, never an invented URL.
    const docSection = el('div', { class: 'source-doc', dataset: { testid: 'source-artifact' } });
    pane.appendChild(docSection);
    fetch(`${endpoints.source(sourceId)}/document`)
      .then(async (res) => {
        if (!res.ok) {
          docSection.appendChild(notice('warn',
            'Source document unavailable — the original artifact could not be recovered. '
            + 'See docs/SOURCE_DOCUMENT_COVERAGE_REPORT.md; Product may supply it as a source package.'));
          return;
        }
        const ctype = res.headers.get('content-type') || '';
        docSection.appendChild(el('h3', {}, 'Original artifact'));
        if (ctype.includes('text/plain') || ctype.includes('markdown')) {
          const text = await res.text();
          docSection.appendChild(el('pre', {
            class: 'doc-preview', dataset: { testid: 'doc-preview' },
            style: 'max-height:340px;overflow:auto;border:1px solid var(--border-2);background:var(--bg-alt);padding:8px;font-size:10.5px;white-space:pre-wrap',
          }, text));
        } else {
          docSection.appendChild(el('p', { class: 'small' },
            `Artifact available (${ctype}). Open/download below — rendering is not forced in-app.`));
        }
        docSection.appendChild(el('div', { class: 'open-links' },
          el('a', { class: 'btn', href: `${endpoints.source(sourceId)}/document`, target: '_blank', rel: 'noopener', dataset: { testid: 'doc-open' } }, 'Open raw artifact')));
      })
      .catch(() => docSection.appendChild(notice('warn', 'Source document unavailable.')));
    if (s.source_type === 'Operational / Delivery Evidence') {
      pane.appendChild(el('h3', {}, 'Jira backlog tickets (delivery evidence — never capability truth)'));
      api.get(endpoints.jira()).then((j) => {
        pane.appendChild(table(['Key', 'Issue type', 'Summary', 'Status', 'Treatment', 'Linked CAPs'],
          j.items.map((t) => el('tr', { dataset: { testid: 'src-jira-row' } },
            el('td', { class: 'mono' }, t.jira_key),
            el('td', {}, t.issue_type || '—'),
            el('td', { class: 'small' }, (t.summary || '').slice(0, 70)),
            el('td', {}, t.status || '—'),
            el('td', {}, t.capability_treatment || '—'),
            el('td', {},
              el('button', { class: 'small', dataset: { testid: 'src-jira-expand', key: t.jira_key },
                onclick: async (e) => {
                  const d = await api.get(endpoints.jiraTicket(t.jira_key));
                  const tds = e.target.parentElement;
                  tds.replaceChildren(...(d.capabilities.length
                    ? d.capabilities.map((c) => capLink(c.cap_id))
                    : [el('span', { class: 'dim' }, 'none')]));
              } }, String(t.linked_capability_count)))))));
      });
    }
  });
}

async function openSourceCaps(sourceId) {
  const data = await api.get(endpoints.sourceCaps(sourceId));
  openPane(`${sourceId} — extracted Source Capabilities (${data.count})`, (pane) => {
    if (data.count === 0) {
      pane.appendChild(notice('info', 'No extracted source capabilities on this source.'));
    } else {
      pane.appendChild(table(
        ['Source Capability', 'Original name', 'Original description', 'Evidence', 'Category', 'Confidence', 'Reconciliation', 'Canonical CAP'],
        data.items.map((sc) => el('tr', { dataset: { testid: 'srccap-row' } },
          el('td', { class: 'mono' }, sc.source_capability_id),
          el('td', {}, sc.original_name || '—'),
          el('td', { class: 'small' }, (sc.original_description || '').slice(0, 90)),
          el('td', { class: 'small' }, (sc.evidence_reference || '—').slice(0, 50)),
          el('td', {}, sc.source_category || '—'),
          el('td', {}, sc.source_confidence || '—'),
          el('td', {}, el('span', { class: 'badge' }, sc.reconciliation_relationship || '—')),
          el('td', {}, sc.canonical_cap_id ? capLink(sc.canonical_cap_id) : el('span', { class: 'dim' }, 'unmapped'))))));
    }
  });
}

async function renderAllSourceCaps(body) {
  body.replaceChildren();
  body.appendChild(notice('info', 'All extracted Source Capabilities across registered Sources (Source Truth verbatim).'));
  const srcs = await api.get(endpoints.sources());
  const all = (await Promise.all(srcs.items.map((s) => api.get(endpoints.sourceCaps(s.source_id)))))
    .flatMap((r) => r.items);
  if (!all.length) { body.appendChild(notice('info', 'No extracted capabilities.')); return; }
  body.appendChild(table(
    ['Source', 'Source Capability', 'Original name', 'Reconciliation', 'Canonical CAP'],
    all.map((sc) => el('tr', { dataset: { testid: 'srccap-row-all' } },
      el('td', { class: 'mono' }, sc.source_id),
      el('td', { class: 'mono' }, sc.source_capability_id),
      el('td', {}, sc.original_name || '—'),
      el('td', {}, sc.reconciliation_relationship || '—'),
      el('td', {}, sc.canonical_cap_id ? capLink(sc.canonical_cap_id) : el('span', { class: 'dim' }, 'unmapped'))))),
  );
}

async function renderCustomers(body) {
  body.replaceChildren();
  const data = await api.get(endpoints.customers());
  body.appendChild(
    notice('info', 'Customer master data is API-available; the governed customer dataset has not been supplied yet (contract D3). No records are invented.'),
    table(['Customer ID', 'Name', 'Earliest transition', 'Validation'], data.items.map((c) =>
      el('tr', {}, el('td', { class: 'mono' }, c.customer_id), el('td', {}, c.name),
        el('td', {}, c.earliest_milestone_interval || '—'), el('td', {}, c.validation_status || '—')))));
}

// simple right-hand pane
function openPane(title, build) {
  document.querySelectorAll('.modal-overlay').forEach((n) => n.remove());
  const overlay = el('div', { class: 'modal-overlay', dataset: { testid: 'pane-overlay' } });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  const drawer = el('div', { class: 'modal-drawer' },
    el('div', { class: 'drawer-head' }, el('h1', {}, title),
      el('div', { class: 'actions' }, el('button', { onclick: () => overlay.remove() }, 'Close'))));
  overlay.appendChild(drawer);
  document.body.appendChild(overlay);
  build(drawer);
}
