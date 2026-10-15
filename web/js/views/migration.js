// MIGRATION PATH — intentional Phase 4 foundation placeholder (§17).
// Vertical VALUE | MIGRATION PATH | CUSTOMER TRANSITION layout recovers from
// v35.6 in its own phase; customers stay empty until governed data arrives.

import { api, endpoints } from '../api.js';
import { el, notice } from '../ui.js';
import { marketLegend } from '../ui.js';
import { getMarkets } from '../components/capmodal.js';

export async function renderMigrationPlaceholder(container) {
  container.replaceChildren();
  const [ms, cust, caps, markets] = await Promise.all([
    api.get(endpoints.milestones()),
    api.get(endpoints.customers()),
    api.get(endpoints.capabilities()),
    getMarkets(),
  ]);
  container.append(
    el('h1', {}, 'Migration Path'),
    notice('info', `Foundation phase: shared milestones (${ms.count}), customers (${cust.count}) and canonical capabilities (${caps.count}) are API-derived; unlocked capabilities will derive from Roadmap timing. The approved vertical layout recovers in the Migration phase — reference: REFERENCE_IMPLEMENTATION_MATRIX row 8. Customer transitions will use milestone intervals (M3 → M4), never TS codes.`),
    marketLegend(markets),
  );
}
