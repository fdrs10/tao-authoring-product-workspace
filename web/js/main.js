// Application shell + hash router (§2). API is authoritative; nothing
// canonical is cached in JS or LocalStorage (§19: only X-User-Ref as a
// personal preference).

import { setUserRef, getUserRef } from './api.js';
import { renderIdeation } from './views/ideation.js';
import { renderSources } from './views/sources.js';
import { renderBacklog } from './views/backlog.js';
import { renderRoadmap } from './views/roadmap.js';
import { renderMigration } from './views/migration.js';
import { renderCustomers } from './views/customers.js';
import { renderOutcomes } from './views/outcomes.js';
import { renderReports } from './views/reports.js';
import { renderHome } from './views/home.js';
import { renderEvidenceExplorer } from './views/evidence.js';
import { openCapModal } from './components/capmodal.js';
import { el } from './ui.js';

const main = document.getElementById('app-main');

function setActive(route) {
  document.querySelectorAll('#main-nav a').forEach((a) => {
    a.classList.toggle('active', a.dataset.route === route);
  });
}

// Serialized routing: concurrent renders (cap:changed bursts, quick filter
// changes) must interleave destructively — last requested render wins.
let routeChain = Promise.resolve();
async function runRoute() {
  const hash = location.hash || '#/home';
  const parts = hash.replace(/^#\//, '').split('/');
  const [root, sub] = parts;
  try {
    if (root === 'ideation') { setActive('ideation'); await renderIdeation(main, sub || '01'); }
    else if (root === 'sources') { setActive('sources'); await renderSources(main); }
    else if (root === 'roadmap') { setActive('roadmap'); await renderRoadmap(main); }
    else if (root === 'migration') { setActive('migration'); await renderMigration(main); }
    else if (root === 'customers') { setActive('customers'); await renderCustomers(main); }
    else if (root === 'outcomes') { setActive('outcomes'); await renderOutcomes(main); }
    else if (root === 'reports') { setActive('reports'); await renderReports(main); }
    else if (root === 'backlog') { setActive('ideation'); await renderBacklog(main); }
    else if (root === 'home') { setActive('home'); await renderHome(main); }
    else if (root === 'evidence') { setActive('evidence'); await renderEvidenceExplorer(main); }
    else { location.hash = '#/home'; }
  } catch (err) {
    main.replaceChildren(el('div', { class: 'notice error' },
      `Render failed: ${err.detail ? JSON.stringify(err.detail) : err.message}`));
    throw err; // surfaced in smoke tests as page error
  }
}

function route() {
  routeChain = routeChain.then(runRoute)
    .catch((err) => console.error("route failed:", err && (err.message || err)));
  return routeChain;
}

// universal CAP-ID interaction (§7/§23)
window.addEventListener('open-cap', (e) => openCapModal(e.detail));
// cross-view refresh when canonical data changes via the modal/editors
window.addEventListener('cap:changed', () => { route().catch(() => {}); });

const chip = document.getElementById('user-ref');
chip.textContent = getUserRef();
chip.addEventListener('click', () => {
  const v = prompt('DEV identity (X-User-Ref):', getUserRef());
  if (v !== null) { setUserRef(v); chip.textContent = getUserRef(); }
});

window.addEventListener('hashchange', () => {
  // Real navigation closes any open overlay (source drill-down pane, CAP
  // drawer, quarter/milestone modals): an overlay pinned to document.body
  // otherwise blocks the nav bar entirely. In-view re-renders (cap:changed)
  // keep overlays — only genuine navigation clears them.
  document.querySelectorAll('.modal-overlay').forEach((n) => n.remove());
  route().catch(() => {});
});
route();
