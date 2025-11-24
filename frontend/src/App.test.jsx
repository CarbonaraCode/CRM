import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import App from './App';

vi.mock('./services/api', () => {
  return {
    fetchSalesData: vi.fn().mockResolvedValue({
      clients: [{ id: 'c1', name: 'Rossi S.r.l.', email: 'info@rossi.it', vat_number: '123' }],
      contacts: [],
      opportunities: [{ id: 'o1', number: 'OPP-2025-001', name: 'Upgrade', description: 'Desc', client: 'c1', client_name: 'Rossi S.r.l.', attachment: 'https://files.test/opp.pdf' }],
      offers: [{ id: 'off1', number: 'OFF-2025-001', client: 'c1', client_name: 'Rossi S.r.l.', status: 'SENT', description: 'Off desc' }],
      orders: [{ id: 'ord1', number: 'ORD-2025-050', client: 'c1', client_name: 'Rossi S.r.l.' }],
      invoices: [{ id: 'inv1', number: 'INV-2025-100', client: 'c1', client_name: 'Rossi S.r.l.', total_amount: 100 }],
      contracts: [],
    }),
    fetchPurchaseData: vi.fn().mockResolvedValue({
      suppliers: [{ id: 's1', name: 'ACME', vat_number: 'IT999', email: 'a@acme.it', payment_terms: '30gg' }],
      orders: [{ id: 'po1', number: 'PO-1', supplier_name: 'ACME', total_amount: 50, status: 'DRAFT', date: '2025-01-01' }],
      invoices: [{ id: 'pinv1', number: 'PINV-1', supplier_name: 'ACME', total_amount: 50, status: 'RECEIVED', due_date: '2025-02-01', order_number: 'PO-1' }],
    }),
    createResource: vi.fn().mockResolvedValue({}),
    updateResource: vi.fn().mockResolvedValue({}),
    deleteResource: vi.fn().mockResolvedValue({}),
    createPurchaseResource: vi.fn().mockResolvedValue({}),
    updatePurchaseResource: vi.fn().mockResolvedValue({}),
    deletePurchaseResource: vi.fn().mockResolvedValue({}),
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

  it('loads dashboard stats from invoices/orders data', async () => {
    render(<App />);
    const cardTitle = await screen.findByText('Fatturato Mensile');
    const cardContainer = cardTitle.closest('div');
    expect(cardContainer?.textContent).toMatch(/100/);
  });

  it('shows attachment link inside opportunity detail modal', async () => {
    render(<App />);
    fireEvent.click(await screen.findByText(/Opportunit/i));
    const oppNumber = await screen.findByText('OPP-2025-001');
    fireEvent.click(oppNumber);

    expect(await screen.findByText('Dettaglio Opportunita')).toBeInTheDocument();
    const attachmentLink = await screen.findByRole('link', { name: /allegato/i });
    expect(attachmentLink).toHaveAttribute('href', 'https://files.test/opp.pdf');
  });

  it('adds attachment upload to opportunity modal and removes description column from table', async () => {
    render(<App />);
    fireEvent.click(await screen.findByText(/Opportunit/i));

    const headers = await screen.findAllByRole('columnheader');
    expect(headers.map((h) => h.textContent)).not.toContain('Descrizione');

    fireEvent.click(screen.getByText('Nuovo'));
    const fileInput = await screen.findByLabelText('Allegato');
    expect(fileInput).toHaveAttribute('type', 'file');
  });

  it('shows suppliers table from purchase data', async () => {
    render(<App />);
    fireEvent.click(await screen.findByText(/Fornitori/i));

    expect(await screen.findByText('ACME')).toBeInTheDocument();
    expect(await screen.findByText('IT999')).toBeInTheDocument();
  });
});
