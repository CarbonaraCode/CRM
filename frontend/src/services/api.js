const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const SALES_BASE = `${API_BASE}/sales`;

async function httpGet(path) {
  const res = await fetch(path);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function fetchSalesData() {
  const endpoints = {
    clients: `${SALES_BASE}/clients/`,
    contacts: `${SALES_BASE}/contacts/`,
    opportunities: `${SALES_BASE}/opportunities/`,
    offers: `${SALES_BASE}/offers/`,
    orders: `${SALES_BASE}/orders/`,
    invoices: `${SALES_BASE}/invoices/`,
    contracts: `${SALES_BASE}/contracts/`,
  };

  const results = await Promise.all(
    Object.entries(endpoints).map(async ([key, url]) => {
      const data = await httpGet(url);
      return [key, data];
    })
  );

  return Object.fromEntries(results);
}

export async function createResource(resource, payload) {
  const res = await fetch(`${SALES_BASE}/${resource}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /${resource} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function updateResource(resource, id, payload) {
  const res = await fetch(`${SALES_BASE}/${resource}/${id}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PATCH /${resource}/${id} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function deleteResource(resource, id) {
  const res = await fetch(`${SALES_BASE}/${resource}/${id}/`, { method: 'DELETE' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`DELETE /${resource}/${id} failed: ${res.status} ${text}`);
  }
}
