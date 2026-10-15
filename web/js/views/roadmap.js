// ROADMAP — intentional Phase 4 foundation placeholder (§17). The renderer
// behavioural recovery is its own phase using the verified v10 reference;
// nothing simplified/redesigned is substituted here.

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';

export async function renderRoadmapPlaceholder(container) {
  container.replaceChildren();
  const [roadmap, ms] = await Promise.all([
    api.get(endpoints.roadmap()),
    api.get(endpoints.milestones()),
  ]);
  container.append(
    el('h1', {}, 'Roadmap'),
    notice('info', `Foundation phase: canonical data flows through the API (COMMITTED-admission default per §34: ${roadmap.count} capabilities currently; shared milestones: ${ms.count}). The stable three-level Roadmap renderer (Category → Big Rock → Feature, drag/resize/snap, horizons, Quarter View) is recovered in the dedicated Roadmap phase — reference: REFERENCE_IMPLEMENTATION_MATRIX row 6.`),
    el('p', { class: 'small dim' }, 'Nothing here recreates Product state; use Product Backlog (IDEATION · 06/Cross-analysis tab) for the editing view in the meantime.'),
  );
}
