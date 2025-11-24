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

const buildBody = (payload = {}) => {
  const hasFile = Object.values(payload).some((val) => val instanceof File);
  if (!hasFile) {
    return {
      body: JSON.stringify(payload),
      headers: { 'Content-Type': 'application/json' },
    };
  }
  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    if (value instanceof File) {
      formData.append(key, value);
    } else if (typeof value === 'object') {
      formData.append(key, JSON.stringify(value));
    } else {
      formData.append(key, value);
    }
  });
  return { body: formData, headers: {} };
};

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
  const { body, headers } = buildBody(payload);
  const res = await fetch(`${SALES_BASE}/${resource}/`, {
    method: 'POST',
    headers,
    body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /${resource} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function updateResource(resource, id, payload) {
  const { body, headers } = buildBody(payload);
  const res = await fetch(`${SALES_BASE}/${resource}/${id}/`, {
    method: 'PATCH',
    headers,
    body,
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
