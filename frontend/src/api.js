const API_BASE = '/api/v1';

async function fetchJSON(url, options = {}) {
  const resp = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return resp.json();
}

export async function getHealth() {
  const resp = await fetch('/health');
  if (!resp.ok) throw new Error(`Health check failed: ${resp.status}`);
  return resp.json();
}

export async function getReady() {
  const resp = await fetch('/ready');
  return resp.json();
}

export async function getDashboard() {
  return fetchJSON('/admin/dashboard');
}

export async function getModels() {
  return fetchJSON('/models');
}

export async function pullModel(name) {
  return fetchJSON('/models/pull', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

export async function quantizeModel(name, bits = 4, method = 'awq') {
  return fetchJSON('/models/quantize', {
    method: 'POST',
    body: JSON.stringify({ name, bits, method }),
  });
}

export async function getSafetyStatus() {
  return fetchJSON('/safety/status');
}

export async function getSafetyPolicies() {
  return fetchJSON('/safety/policies');
}

export async function getAuditLog(start = '', end = '', limit = 100) {
  const params = new URLSearchParams({ start, end, limit });
  return fetchJSON(`/safety/audit?${params}`);
}

export async function safetyCheck(prompt = '', response = '') {
  const params = new URLSearchParams({ prompt, response });
  return fetchJSON(`/safety/check?${params}`);
}

export async function getMemoryStats() {
  return fetchJSON('/memory/stats');
}

export async function searchMemory(query, collection = 'default', topK = 5) {
  const params = new URLSearchParams({ q: query, collection, top_k: topK });
  return fetchJSON(`/memory/search?${params}`);
}

export async function ingestMemory(text, collection = 'default', source = 'api') {
  return fetchJSON('/memory/ingest', {
    method: 'POST',
    body: JSON.stringify({ text, collection, source }),
  });
}

export async function getApprovals() {
  return fetchJSON('/admin/governance/approvals');
}

export async function approveRequest(id) {
  return fetchJSON(`/admin/governance/approve/${id}`, { method: 'POST' });
}
