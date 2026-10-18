// API client — the Phase 3 API is the only source of Product truth (§19).
// DEV identity via X-User-Ref; kept as a *personal* preference (§19).

const ACTOR_KEY = 'tao.userRef';
export function getUserRef() {
  return localStorage.getItem(ACTOR_KEY) || 'dev-user';
}
export function setUserRef(v) {
  localStorage.setItem(ACTOR_KEY, v.trim() || 'dev-user');
}

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'X-User-Ref': getUserRef() },
  };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const err = new Error(`API ${res.status}`);
    err.status = res.status;
    err.detail = (data && data.detail) || data;
    throw err;
  }
  return data;
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, body) => request('POST', p, body ?? {}),
  patch: (p, body) => request('PATCH', p, body),
  del: (p) => request('DELETE', p),
};

export const endpoints = {
  capabilities: (params = '') => `/api/capabilities${params}`,
  capability: (id) => `/api/capabilities/${encodeURIComponent(id)}`,
  jiraLink: (id) => `/api/capabilities/${encodeURIComponent(id)}/jira`,
  jiraUnlink: (id, key) => `/api/capabilities/${encodeURIComponent(id)}/jira/${encodeURIComponent(key)}`,
  sources: () => '/api/sources',
  source: (id) => `/api/sources/${encodeURIComponent(id)}`,
  sourceCaps: (id) => `/api/sources/${encodeURIComponent(id)}/capabilities`,
  jira: () => '/api/jira',
  jiraTicket: (k) => `/api/jira/${encodeURIComponent(k)}`,
  markets: () => '/api/markets',
  roadmap: (params = '') => `/api/roadmap${params}`,
  roadmapTiming: (id) => `/api/roadmap/${encodeURIComponent(id)}`,
  milestones: () => '/api/milestones',
  milestone: (id) => `/api/milestones/${encodeURIComponent(id)}`,
  outcomes: () => '/api/outcomes',
  outcome: (h) => `/api/outcomes/${encodeURIComponent(h)}`,
  features: () => '/api/features',
  reports: () => '/api/reports',
  customers: () => '/api/customers',
  customer: (id) => `/api/customers/${encodeURIComponent(id)}`,
};
