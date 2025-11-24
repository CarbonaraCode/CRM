import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import App from './App';

vi.mock('./services/api', () => {
  return {
    fetchSalesData: vi.fn().mockResolvedValue({
      clients: [{ id: 'c1', name: 'Rossi S.r.l.', email: 'info@rossi.it', vat_number: '123' }],
      contacts: [],
      opportunities: [{ id: 'o1', number: 'OPP-2025-001', name: 'Upgrade', client: 'c1', client_name: 'Rossi S.r.l.' }],
      offers: [{ id: 'off1', number: 'OFF-2025-001', client: 'c1', client_name: 'Rossi S.r.l.', status: 'SENT' }],
      orders: [{ id: 'ord1', number: 'ORD-2025-050', client: 'c1', client_name: 'Rossi S.r.l.' }],
      invoices: [{ id: 'inv1', number: 'INV-2025-100', client: 'c1', client_name: 'Rossi S.r.l.' }],
      contracts: [],
    }),
    createResource: vi.fn().mockResolvedValue({}),
  };
});

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads sales data and shows clients table', async () => {
    render(<App />);
    fireEvent.click(await screen.findByText('Clienti'));

    expect(await screen.findByText('Gestione Clienti')).toBeInTheDocument();
    expect(await screen.findByText('Rossi S.r.l.')).toBeInTheDocument();
    expect(await screen.findByText('info@rossi.it')).toBeInTheDocument();
  });
});
