// November Outcomes overview (FINAL UAT EVOLUTION §15) — a lightweight
// navigation/orientation layer over the five connected Product outcomes.
// NOT a source of Product Truth: every link goes to the existing working
// areas; statuses describe state, they do not create data.

import { el } from '../ui.js';

const OUTCOMES = [
  {
    n: 1,
    title: 'Authoring Product Definition — Ideation & Target Scope',
    purpose: 'What Authoring function do we want TAO to have? V1 carry-forward + 3.x direct migration + new needs & gaps − discontinued → Cross-analysis → TAO Studio Creator V2 Authoring Target Scope.',
    link: { label: 'Ideation & Cross-analysis', hash: '#/ideation/01' },
    dependency: 'Source documents & extracted Source Capabilities (source-by-source reconstruction is the next controlled operation)',
    productInput: 'Admission of capabilities into the Target Scope; source reconstruction reviews',
    testid: 'outcome-1',
  },
  {
    n: 2,
    title: 'TAO Studio Creator V2 — Product Backlog',
    purpose: 'The governed set of Product capabilities resulting from Ideation and Product analysis. Answers: what do we want the Authoring product to contain? (Not when — that is Roadmap Admission and planning.)',
    link: { label: 'Product Backlog', hash: '#/backlog' },
    dependency: 'Ideation outcomes; Product Review; Feature composition where applicable',
    productInput: 'Product Review statuses; capability edits; Feature composition',
    testid: 'outcome-2',
  },
  {
    n: 3,
    title: 'TAO Studio Creator V2 — Product Roadmap',
    purpose: 'Which Product capabilities are we committing to develop or evolve, and when? Roadmap Admission + timing at Capability level (Features are a composition view only).',
    link: { label: 'Product Roadmap', hash: '#/roadmap' },
    dependency: 'Product Backlog (same canonical capabilities); Market/visibility metadata',
    productInput: 'Roadmap Admission decisions; Roadmap timing; M1–M6 baseline upkeep',
    testid: 'outcome-3',
  },
  {
    n: 4,
    title: 'TAO 3.x → TAO Studio Authoring — Common Migration Path',
    purpose: 'The shared transition framework from TAO 3.x Authoring to TAO Studio Authoring: value unlocked → M1–M6 milestones and intervals → customer transition. ONE path for all customers.',
    link: { label: 'Migration Path', hash: '#/migration' },
    dependency: 'Roadmap delivers capabilities → capabilities enable milestones → milestones make customer transitions possible',
    productInput: 'Milestone baseline upkeep (M1–M6, editable); capability commitments',
    testid: 'outcome-4',
  },
  {
    n: 5,
    title: 'Customer Migration Plans',
    purpose: 'For each customer on TAO 3.x Authoring: a Product-proposed plan showing how they move through the common Migration Path — required capabilities, earliest viable interval, blockers — so they can start preparing their own implementation plan.',
    link: { label: 'Customer Migration Plans', hash: '#/migration' },
    dependency: 'Common Migration Path (M1–M6); Product Roadmap timing (consumed, never duplicated); governed customer data (D3)',
    productInput: 'Governed customer dataset; per-customer plan fields; validation',
    testid: 'outcome-5',
  },
];

export async function renderOutcomes(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'November Outcomes — Authoring Product Definition to Customer Migration Plans'));
  container.appendChild(el('div', { class: 'small dim', style: 'margin-bottom:10px' },
    'The Product workflow: SOURCES & EVIDENCE → SOURCE CAPABILITIES → PRODUCT ANALYSIS / IDEATION → AUTHORING TARGET SCOPE → PRODUCT BACKLOG → PRODUCT ROADMAP → COMMON MIGRATION PATH → CUSTOMER MIGRATION PLANS. One Product Roadmap; one common Migration Path; multiple Customer Migration Plans.'));

  const flow = el('div', { class: 'outcome-flow', dataset: { testid: 'outcomes-flow' } },
    ['Sources & Evidence', 'Source Capabilities', 'Ideation', 'Target Scope', 'Backlog', 'Roadmap', 'Migration Path', 'Customer Plans']
      .flatMap((s, i) => i === 0 ? [el('span', { class: 'flow-step' }, s)]
        : [el('span', { class: 'flow-arrow' }, '→'), el('span', { class: 'flow-step' }, s)]));
  container.appendChild(flow);

  for (const o of OUTCOMES) {
    container.appendChild(el('div', { class: 'mig-band', dataset: { testid: o.testid } },
      el('h2', {}, `${o.n}. ${o.title}`),
      el('p', { class: 'small', style: 'margin:4px 0' }, o.purpose),
      el('div', { class: 'kv' },
        el('div', { class: 'k' }, 'Working area'),
        el('div', { class: 'v' }, el('a', { href: o.link.hash, class: 'btn', style: 'display:inline-block' }, o.link.label)),
        el('div', { class: 'k' }, 'Main dependency'),
        el('div', { class: 'v small' }, o.dependency),
        el('div', { class: 'k' }, 'Product input still required'),
        el('div', { class: 'v small' }, o.productInput))));
  }
  container.appendChild(el('div', { class: 'small dim', style: 'margin-top:8px' },
    'This page orients — it does not store Product Truth. All data lives in the API/PostgreSQL and is edited in the working areas above.'));
}
