// Product Backlog (§30): canonical Target Authoring universe with filters.
// Admission editable inline — the SAME canonical field as Cross-analysis/CAP
// editor (§11). Default compact view shows MUST; All is always available.

import { api, endpoints } from '../api.js';
import { el, capLink, moscowBadge, admissionBadge, reviewBadge, marketDotsFor, marketLegend, notice, table } from '../ui.js';
import { getMarkets } from '../components/capmodal.js';

const ADM = ['', 'COMMITTED', 'CANDIDATE', 'BACKLOG', 'DEFERRED', 'NOT PLANNED'];

export async function renderBacklog(container) {
  container.replaceChildren();
  container.appendChild(el('h1', {}, 'Product Backlog — TAO Studio V2 Authoring Target Scope'));
  const [markets, sources, caps] = await Promise.all([
    getMarkets(), api.get(endpoints.sources()), api.get(endpoints.capabilities()),
  ]);

  const state = { category: '', market: '', moscow: 'Must', admission: '', visibility: '', source: '' };
  const fsel = (name, options, current, title) => el('div', { class: 'f' },
    el('label', {}, title),
    el('select', { dataset: { f: name, testid: `filter-${name}` } },
      options.map((o) => el('option', { value: o.value, ...(o.value === current ? { selected: '' } : {}) }, o.label))));

  const any = (l) => ({ value: '', label: l });
  const fbar = el('div', { class: 'filter-bar' },
    fsel('category', [any('Category · All'), ...['Create & Design', 'Manage & Govern', 'Collaborate & Assure Quality', 'Standards & Portability', 'AI-assisted Authoring'].map((v) => ({ value: v, label: v }))], state.category, 'Strategic category'),
    fsel('market', [any('Market · All'), ...markets.map((m) => ({ value: m.name, label: m.name }))], state.market, 'Market'),
    fsel('moscow', [any('MoSCoW · All'), 'Must', 'Should', 'Could', "Won't"].map((v) => (typeof v === 'string' ? { value: v, label: v } : v)), state.moscow, 'MoSCoW (default MUST)'),
    fsel('admission', [any('Admission · All'), 'UNSET', ...ADM.filter(Boolean)].map((v) => (typeof v === 'string' ? { value: v, label: v } : v)), state.admission, 'Roadmap admission'),
    fsel('visibility', [any('Visibility · All'), 'Shared / common core', 'Shared / market-configured', 'Market-specific'].map((v) => (typeof v === 'string' ? { value: v, label: v } : v)), state.visibility, 'Visibility'),
    fsel('source', [any('Source · All'), ...sources.items.map((s) => ({ value: s.source_id, label: `${s.source_id} · ${s.title}` }))], state.source, 'Source'));

  const countNote = el('div', { class: 'small dim', dataset: { testid: 'backlog-count' } });
  const mount = el('div');
  container.append(fbar, countNote, mount);

  const apply = async () => {
    const qs = new URLSearchParams();
    if (state.category) qs.set('category', state.category);
    if (state.market) qs.set('market', state.market);
    if (state.moscow) qs.set('moscow', state.moscow);
    if (state.admission) qs.set('admission', state.admission === 'UNSET' ? 'UNSET' : state.admission);
    if (state.visibility) qs.set('visibility', state.visibility);
    if (state.source) qs.set('source', state.source);
    const q = qs.toString() ? `?${qs.toString()}` : '';
    const res = await api.get(endpoints.capabilities(q));
    countNote.textContent = `${res.count} capabilities${state.moscow === 'Must' ? ' — default MoSCoW=MUST (set MoSCoW · All for the full universe)' : ''}`;
    mount.replaceChildren(
      table(['CAP', 'Capability', 'Category', 'Markets', 'MoSCoW', 'Admission', 'Visibility', 'Source(s)'], res.items.map((c) => {
        const badge = el('span', { dataset: { testid: 'adm-badge' } }, admissionBadge(c.roadmap_admission));
        const sel = el('select', { dataset: { testid: 'adm-edit', cap: c.cap_id }, style: 'font-size:11.5px' },
          ADM.map((o) => el('option', { value: o, ...(o === (c.roadmap_admission ?? '') ? { selected: '' } : {}) }, o === '' ? 'UNSET' : o)));
        sel.addEventListener('change', async () => {
          try {
            await api.patch(endpoints.capability(c.cap_id), {
              version: c.version, roadmap_admission: sel.value === '' ? null : sel.value });
            c.version += 1; c.roadmap_admission = sel.value === '' ? null : sel.value;
            badge.replaceChildren(admissionBadge(c.roadmap_admission));
          } catch (err) {
            badge.replaceChildren(notice('warn', err.status === 409 ? `Conflict: now v${err.detail.current_version}` : String(err.detail)));
          }
        });
        return el('tr', { dataset: { testid: 'backlog-row' } },
          el('td', {}, capLink(c.cap_id)),
          el('td', {}, c.working_name, ' ', reviewBadge(c.review_status)),
          el('td', {}, c.strategic_category),
          el('td', {}, marketDotsFor(c.markets, markets)),
          el('td', {}, moscowBadge(c.moscow)),
          el('td', {}, badge, ' ', sel),
          el('td', { dataset: { testid: 'visibility-cell' } }, c.visibility || '—'),
          (() => {
            const srcList = c.sources || [];
            return el('td', { class: 'small', dataset: { testid: 'sources-cell', sources: srcList.join(',') },
              title: srcList.join(', ') || 'no sources linked' },
              srcList.length ? `${srcList.length} source${srcList.length === 1 ? '' : 's'}` : '—');
          })());
      }))
    );
    mount.appendChild(marketLegend(markets));
  };
  fbar.addEventListener('change', (e) => {
    const k = e.target.dataset.f;
    if (k) { state[k] = e.target.value; apply(); }
  });
  await apply();
}
