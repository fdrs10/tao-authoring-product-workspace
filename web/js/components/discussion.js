// Discussion component — reusable across all entity types (Phase A).
// Usage: renderDiscussion(container, entityType, entityId)
// Loads existing comments, provides add + resolve.

import { api, endpoints } from '../api.js';
import { el } from '../ui.js';

export async function renderDiscussion(container, entityType, entityId) {
  const res = await api.get(`/api/comments?entity_type=${encodeURIComponent(entityType)}&entity_id=${encodeURIComponent(entityId)}`);
  const items = res.items || [];

  container.replaceChildren(
    el('h3', {}, 'DISCUSSION'),
    ...(items.length ? items.map((c) => el('div', { class: 'jira-row', style: c.resolved ? 'opacity:0.5' : '' },
      el('span', { class: 'small' }, `${c.author}: ${c.comment}`),
      el('span', { class: 'small dim' }, c.created_at ? c.created_at.slice(0, 16).replace('T', ' ') : ''),
      !c.resolved ? el('button', { class: 'small', dataset: { testid: 'comment-resolve' },
        onclick: async () => {
          await api.patch(`/api/comments/${c.comment_id}/resolve`, { resolved: true });
          renderDiscussion(container, entityType, entityId);
        } }, 'resolve') : null)) : [el('span', { class: 'small dim' }, 'No comments yet.')]),
    el('div', { style: 'display:flex;gap:6px;margin:6px 0' },
      el('input', { type: 'text', placeholder: 'Add a comment…', style: 'flex:1',
        dataset: { testid: 'comment-input' } }),
      el('button', { class: 'small', dataset: { testid: 'comment-add' },
        onclick: async (e) => {
          const input = e.target.parentElement.querySelector('input');
          if (!input.value.trim()) return;
          await api.post('/api/comments/create', {
            entity_type: entityType, entity_id: entityId, comment: input.value.trim() });
          renderDiscussion(container, entityType, entityId);
        } }, 'Add'))
  );
}
