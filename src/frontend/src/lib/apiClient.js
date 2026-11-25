// Same-origin local API. Model credentials never enter the browser.
let csrfToken = null;
const baseUrl = '/api';
export const getBaseUrl = () => baseUrl;
export const setBaseUrl = (url) => {
  if ((url || '').replace(/\/+$/, '') !== '/api') throw new Error('This deployment uses the same-origin /api backend.');
};
export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}
async function request(path, options = {}, refreshed = false) {
  if (options.method && options.method !== 'GET' && !csrfToken) {
    const config = await request('/config'); csrfToken = config.csrfToken;
  }
  let response;
  try {
    response = await fetch(`${baseUrl}${path}`, { ...options, headers: {
      'Content-Type': 'application/json', ...(csrfToken ? {'X-Demo-Token': csrfToken} : {}), ...(options.headers || {}) } });
  } catch (error) { throw new ApiError(`Backend connection unavailable: ${error.message}`); }
  let data;
  try { data = await response.json(); } catch { throw new ApiError('Backend returned an unreadable response.', response.status); }
  // A rejected request has not been dispatched; refresh the token once after a backend restart.
  if (response.status === 403 && options.method && options.method !== 'GET' && !refreshed) {
    csrfToken = null;
    return request(path, options, true);
  }
  if (!response.ok) throw new ApiError([data.kind, data.error, data.field ? `Field: ${data.field}` : ''].filter(Boolean).join(' · ') || `Request failed (${response.status})`, response.status);
  if (path === '/config') csrfToken = data.csrfToken;
  return data;
}
export const api = {
  getConfig: () => request('/config'),
  prepareRun: payload => request('/runs/prepare', {method: 'POST', body: JSON.stringify(payload)}),
  startRun: payload => request('/runs/start', {method: 'POST', body: JSON.stringify(payload)}),
  getStatus: id => request(`/runs/${encodeURIComponent(id)}/status`),
  getEvents: id => request(`/runs/${encodeURIComponent(id)}/events`),
  getDiscussions: id => request(`/runs/${encodeURIComponent(id)}/discussions`),
  getFiles: id => request(`/runs/${encodeURIComponent(id)}/files`),
  getHistory: () => request('/runs/history'),
  getHistoricalBenchmark: () => request('/benchmark/historical'),
  fileDownloadUrl: (runId, file) => `${baseUrl}/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent(file.fileId || file.id)}/download`,
};
export default api;
