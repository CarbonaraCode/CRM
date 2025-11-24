import React, { useState, useEffect } from 'react';
import { Menu, ChevronRight } from 'lucide-react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import DataTable from './components/DataTable';
import Modal from './components/Modal';
import InfoModal from './components/InfoModal';
import { fetchSalesData, createResource, updateResource, deleteResource } from './services/api';

// Stato iniziale con stats fittizie in attesa di un endpoint dedicato
const INITIAL_DATA = {
  stats: {
    revenue: 125000,
    orders: 45,
    tickets: 12,
    stockValue: 54000
  },
  clients: [],
  contacts: [],
    opportunities: [],
    offers: [],
  orders: [],
  invoices: [],
  contracts: [],
  products: [],
  tickets: []
};

const badge = (text, tone = 'blue') => {
  const palette = {
    blue: 'text-blue-700 bg-blue-100',
    green: 'text-green-700 bg-green-100',
    indigo: 'text-indigo-700 bg-indigo-100',
    amber: 'text-amber-700 bg-amber-100',
    emerald: 'text-emerald-700 bg-emerald-100',
    purple: 'text-purple-700 bg-purple-100',
    slate: 'text-slate-700 bg-slate-100',
  };
  const classes = palette[tone] || palette.blue;
  return (
    <span className={`${classes} px-2 py-1 rounded-full text-xs font-semibold`}>
      {text}
    </span>
  );
};

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value));
};

function App() {
  const [activeModule, setActiveModule] = useState('dashboard');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [data, setData] = useState(INITIAL_DATA);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modal, setModal] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    loadSalesData();
  }, []);

  const loadSalesData = async () => {
    setLoading(true);
    setError(null);
    try {
      const salesData = await fetchSalesData();
      setData((prev) => ({ ...prev, ...salesData }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectFromList = (items, label) => {
    if (!items.length) {
      alert(`Nessun elemento disponibile per ${label}`);
      return null;
    }
    const options = items
      .map((item, idx) => `${idx + 1}) ${label(item)}`)
      .join('\n');
    const choice = prompt(`Seleziona ${label.name || 'voce'}:\n${options}`);
    const idx = Number(choice) - 1;
    if (Number.isNaN(idx) || idx < 0 || idx >= items.length) return null;
    return items[idx];
  };

  const resourceMap = {
    clients: 'clients',
    contacts: 'contacts',
    opportunities: 'opportunities',
    offers: 'offers',
    orders: 'orders',
    invoices: 'invoices',
    contracts: 'contracts',
  };

  const fieldDefinitions = {
    clients: (state) => [
      { name: 'name', label: 'Nome', type: 'text' },
      { name: 'email', label: 'Email', type: 'email' },
      { name: 'vat_number', label: 'P.IVA', type: 'text' },
      { name: 'address', label: 'Indirizzo', type: 'text' },
      { name: 'city', label: 'Città', type: 'text' },
      { name: 'status', label: 'Stato', type: 'select', options: [
        { value: 'LEAD', label: 'Lead' },
        { value: 'ACTIVE', label: 'Attivo' },
        { value: 'INACTIVE', label: 'Inattivo' },
        { value: 'BAD_DEBT', label: 'Cattivo Pagatore' },
      ], default: 'LEAD' },
    ],
    contacts: (state) => [
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'first_name', label: 'Nome', type: 'text' },
      { name: 'last_name', label: 'Cognome', type: 'text' },
      { name: 'role', label: 'Ruolo', type: 'text' },
      { name: 'email', label: 'Email', type: 'email' },
      { name: 'phone', label: 'Telefono', type: 'text' },
      { name: 'is_primary', label: 'Primario', type: 'checkbox' },
    ],
    opportunities: (state) => [
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'name', label: 'Nome', type: 'text' },
      { name: 'description', label: 'Descrizione', type: 'text' },
      { name: 'stage', label: 'Stadio', type: 'select', options: [
        { value: 'NEW', label: 'Nuova' },
        { value: 'QUALIFICATION', label: 'Qualificazione' },
        { value: 'PROPOSAL', label: 'Proposta' },
        { value: 'NEGOTIATION', label: 'Negoziazione' },
        { value: 'WON', label: 'Chiusa Vinta' },
        { value: 'LOST', label: 'Chiusa Persa' },
      ], default: 'NEW' },
      { name: 'close_date', label: 'Data chiusura', type: 'date' },
    ],
    offers: (state) => [
      { name: 'opportunity', label: 'Opportunità', type: 'select', options: state.opportunities.map(o => ({ value: o.id, label: `${o.number || o.name} - ${o.client_name}` })) },
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'date', label: 'Data creazione', type: 'date' },
      { name: 'description', label: 'Descrizione', type: 'text' },
      { name: 'issued_date', label: 'Data emissione', type: 'date' },
      { name: 'accepted_date', label: 'Data accettazione', type: 'date' },
      { name: 'valid_until', label: 'Validità', type: 'date' },
      { name: 'type', label: 'Tipologia', type: 'text' },
      { name: 'status', label: 'Stato', type: 'select', options: [
        { value: 'DRAFT', label: 'Bozza' },
        { value: 'SENT', label: 'Inviata' },
        { value: 'ACCEPTED', label: 'Accettata' },
        { value: 'REJECTED', label: 'Rifiutata' },
        { value: 'EXPIRED', label: 'Scaduta' },
      ], default: 'DRAFT' },
    ],
    orders: (state) => [
      { name: 'from_offer', label: 'Offerta', type: 'select', options: state.offers.map(o => ({ value: o.id, label: `${o.number} - ${o.client_name}` })) },
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'date', label: 'Data', type: 'date' },
      { name: 'invoicing_date', label: 'Data fatturazione', type: 'date' },
      { name: 'status', label: 'Stato', type: 'select', options: [
        { value: 'PENDING', label: 'In Attesa' },
        { value: 'CONFIRMED', label: 'Confermato' },
        { value: 'SHIPPED', label: 'Spedito' },
        { value: 'DELIVERED', label: 'Consegnato' },
        { value: 'CANCELLED', label: 'Annullato' },
      ], default: 'PENDING' },
    ],
    invoices: (state) => [
      { name: 'order', label: 'Ordine', type: 'select', options: state.orders.map(o => ({ value: o.id, label: `${o.number} - ${o.client_name}` })) },
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'date', label: 'Data', type: 'date' },
      { name: 'due_date', label: 'Data scadenza', type: 'date' },
      { name: 'payment_method', label: 'Metodo pagamento', type: 'text' },
      { name: 'status', label: 'Stato', type: 'select', options: [
        { value: 'DRAFT', label: 'Bozza' },
        { value: 'ISSUED', label: 'Emessa' },
        { value: 'PAID', label: 'Pagata' },
        { value: 'OVERDUE', label: 'Scaduta' },
        { value: 'CANCELLED', label: 'Annullata' },
      ], default: 'DRAFT' },
    ],
    contracts: (state) => [
      { name: 'client', label: 'Cliente', type: 'select', options: state.clients.map(c => ({ value: c.id, label: c.name })) },
      { name: 'title', label: 'Titolo', type: 'text' },
      { name: 'start_date', label: 'Data inizio', type: 'date' },
      { name: 'end_date', label: 'Data fine', type: 'date' },
      { name: 'value', label: 'Valore', type: 'number' },
      { name: 'status', label: 'Stato', type: 'select', options: [
        { value: 'ACTIVE', label: 'Attivo' },
        { value: 'EXPIRED', label: 'Scaduto' },
        { value: 'RENEWED', label: 'Rinnovato' },
        { value: 'TERMINATED', label: 'Terminato' },
      ], default: 'ACTIVE' },
    ],
  };

  const openModal = (mode, type, record = {}) => {
    const fields = fieldDefinitions[type] ? fieldDefinitions[type](data) : [];
    const initial = {};
    fields.forEach((f) => {
      if (record && record[f.name] !== undefined) {
        initial[f.name] = record[f.name] ?? '';
      } else if (f.default !== undefined) {
        initial[f.name] = f.default;
      } else {
        initial[f.name] = f.type === 'checkbox' ? false : '';
      }
    });
    setFormValues(initial);
    setModal({ mode, type, fields, record });
  };

  const submitModal = async () => {
    if (!modal) return;
    const resource = resourceMap[modal.type];
    const payload = Object.fromEntries(
      Object.entries(formValues).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
    );
    try {
      if (modal.mode === 'create') {
        await createResource(resource, payload);
      } else if (modal.mode === 'edit' && modal.record?.id) {
        await updateResource(resource, modal.record.id, payload);
      }
      await loadSalesData();
      alert('Operazione completata');
      setModal(null);
    } catch (err) {
      alert(`Errore: ${err.message}`);
    }
  };

  const handleAdd = (type) => openModal('create', type);

  const handleEdit = (type, row) => openModal('edit', type, row);

  const handleDelete = async (type, row) => {
    const confirmDelete = confirm('Eliminare elemento?');
    if (!confirmDelete) return;
    const mapping = {
      clients: 'clients',
      contacts: 'contacts',
      opportunities: 'opportunities',
      offers: 'offers',
      orders: 'orders',
      invoices: 'invoices',
      contracts: 'contracts',
    };
    const resource = mapping[type];
    if (!resource) return;
    try {
      await deleteResource(resource, row.id);
      await loadSalesData();
      alert('Eliminato con successo');
    } catch (err) {
      alert(`Errore eliminazione: ${err.message}`);
    }
  };

  const openDetail = (type, record) => {
    const dataMap = {
      opportunities: {
        Numero: record.number,
        Nome: record.name,
        Descrizione: record.description,
        Cliente: record.client_name,
        Stadio: record.stage,
        'Data inserimento': record.inserted_date,
        'Data chiusura': record.close_date,
      },
      offers: {
        Numero: record.number,
        Cliente: record.client_name,
        Opportunità: record.opportunity_name,
        Descrizione: record.description,
        Stato: record.status,
        'Data creazione': record.date,
        'Data emissione': record.issued_date,
        'Data accettazione': record.accepted_date,
        'Validità': record.valid_until,
        Tipologia: record.type,
        Totale: formatCurrency(record.total_amount),
      },
    };
    if (!dataMap[type]) return;
    setDetail({ title: type === 'offers' ? 'Dettaglio Offerta' : 'Dettaglio Opportunità', data: dataMap[type] });
  };
  
  const renderContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard stats={data.stats} />;
      
      case 'clients':
        return <DataTable 
          title="Gestione Clienti" 
          columns={[
            { header: 'Azienda', accessor: 'name' },
            { header: 'Email', accessor: 'email' },
            { header: 'P.IVA', accessor: 'vat_number' },
            { header: 'Stato', accessor: 'status', render: r => badge(r.status, 'green') }
          ]}
          data={data.clients}
          onAdd={() => handleAdd('clients')}
          onEdit={(row) => handleEdit('clients', row)}
          onDelete={(row) => handleDelete('clients', row)}
        />;
      case 'contacts':
        return <DataTable 
          title="Contatti" 
          columns={[
            { header: 'Nome', accessor: 'first_name', render: r => `${r.first_name} ${r.last_name}` },
            { header: 'Ruolo', accessor: 'role' },
            { header: 'Email', accessor: 'email' },
            { header: 'Telefono', accessor: 'phone' },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Primario', accessor: 'is_primary', render: r => r.is_primary ? badge('Sì', 'green') : badge('No', 'slate') },
          ]}
          data={data.contacts}
          onAdd={() => handleAdd('contacts')}
          onEdit={(row) => handleEdit('contacts', row)}
          onDelete={(row) => handleDelete('contacts', row)}
        />;
      case 'opportunities':
        return <DataTable 
          title="Opportunità" 
          columns={[
            { header: 'Numero', accessor: 'number', render: r => <button className="text-blue-600 underline" onClick={() => openDetail('opportunities', r)}>{r.number}</button> },
            { header: 'Nome', accessor: 'name' },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Stadio', accessor: 'stage', render: r => badge(r.stage, 'indigo') },
            { header: 'Data inserimento', accessor: 'inserted_date' },
            { header: 'Data chiusura', accessor: 'close_date' },
            { header: 'Descrizione', accessor: 'description' },
          ]}
          data={data.opportunities}
          onAdd={() => handleAdd('opportunities')}
          onEdit={(row) => handleEdit('opportunities', row)}
          onDelete={(row) => handleDelete('opportunities', row)}
        />;
      case 'offers':
        return <DataTable 
          title="Offerte" 
          columns={[
            { header: 'Numero', accessor: 'number', render: r => <button className="text-blue-600 underline" onClick={() => openDetail('offers', r)}>{r.number}</button> },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Opportunità', accessor: 'opportunity_name', render: r => r.opportunity_name || '-' },
            { header: 'Stato', accessor: 'status', render: r => badge(r.status, 'amber') },
            { header: 'Totale', accessor: 'total_amount', render: r => formatCurrency(r.total_amount) },
            { header: 'Validità', accessor: 'valid_until' },
            { header: 'Emissione', accessor: 'issued_date' },
            { header: 'Accettazione', accessor: 'accepted_date' },
            { header: 'Tipologia', accessor: 'type' },
            { header: 'Descrizione', accessor: 'description' },
          ]}
          data={data.offers}
          onAdd={() => handleAdd('offers')}
          onEdit={(row) => handleEdit('offers', row)}
          onDelete={(row) => handleDelete('offers', row)}
        />;
      case 'orders_sales':
        return <DataTable 
          title="Ordini di Vendita" 
          columns={[
            { header: 'Numero', accessor: 'number' },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Da Offerta', accessor: 'offer_number', render: r => r.offer_number || '-' },
            { header: 'Stato', accessor: 'status', render: r => badge(r.status, 'blue') },
            { header: 'Totale', accessor: 'total_amount', render: r => formatCurrency(r.total_amount) },
            { header: 'Data', accessor: 'date' },
            { header: 'Data fatturazione', accessor: 'invoicing_date', render: r => r.invoicing_date || '-' },
          ]}
          data={data.orders}
          onAdd={() => handleAdd('orders')}
          onEdit={(row) => handleEdit('orders', row)}
          onDelete={(row) => handleDelete('orders', row)}
        />;
      case 'invoices_sales':
        return <DataTable 
          title="Fatture" 
          columns={[
            { header: 'Numero', accessor: 'number' },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Ordine', accessor: 'order_number', render: r => r.order_number || '-' },
            { header: 'Stato', accessor: 'status', render: r => badge(r.status, 'emerald') },
            { header: 'Totale', accessor: 'total_amount', render: r => formatCurrency(r.total_amount) },
            { header: 'Scadenza', accessor: 'due_date' },
          ]}
          data={data.invoices}
          onAdd={() => handleAdd('invoices')}
          onEdit={(row) => handleEdit('invoices', row)}
          onDelete={(row) => handleDelete('invoices', row)}
        />;
      case 'contracts':
        return <DataTable 
          title="Contratti" 
          columns={[
            { header: 'Titolo', accessor: 'title' },
            { header: 'Cliente', accessor: 'client_name' },
            { header: 'Periodo', accessor: 'start_date', render: r => `${r.start_date} → ${r.end_date}` },
            { header: 'Valore', accessor: 'value', render: r => formatCurrency(r.value) },
            { header: 'Stato', accessor: 'status', render: r => badge(r.status, 'purple') },
          ]}
          data={data.contracts}
          onAdd={() => handleAdd('contracts')}
          onEdit={(row) => handleEdit('contracts', row)}
          onDelete={(row) => handleDelete('contracts', row)}
        />;
      
      // INVENTARIO ESEMPIO
      case 'products':
        return <DataTable 
          title="Prodotti" 
          columns={[
            { header: 'Codice', accessor: 'code' },
            { header: 'Nome', accessor: 'name' },
            { header: 'Stock', accessor: 'stock' },
            { header: 'Prezzo', accessor: 'price', render: r => formatCurrency(r.price) }
          ]}
          data={data.products}
          onAdd={() => handleAdd('Prodotto')}
          onDelete={(id) => handleDelete('products', id)}
        />;

      // PLACEHOLDER PER MODULI VUOTI
      default:
        return (
          <div className="flex flex-col items-center justify-center h-96 text-slate-400 bg-white rounded-xl border border-slate-200 border-dashed">
            <h3 className="text-xl font-semibold mb-2">Modulo {activeModule}</h3>
            <p>In costruzione...</p>
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-slate-100 font-sans text-slate-900">
      <Sidebar 
        activeModule={activeModule} 
        setActiveModule={setActiveModule} 
        isMobileOpen={isMobileOpen}
        toggleMobile={() => setIsMobileOpen(!isMobileOpen)}
      />

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Mobile Header */}
        <div className="md:hidden bg-white h-16 border-b border-slate-200 flex items-center px-4 justify-between shadow-sm">
          <span className="font-bold text-lg text-slate-800">Nexus CRM</span>
          <button onClick={() => setIsMobileOpen(true)} className="text-slate-600">
            <Menu size={24} />
          </button>
        </div>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6 flex items-center text-sm text-slate-500">
              <span className="capitalize">{activeModule === 'dashboard' ? 'Home' : activeModule.replace('_', ' ')}</span>
              <ChevronRight className="h-4 w-4 mx-2" />
              <span className="font-semibold text-slate-800">Panoramica</span>
            </div>
            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 border border-red-200 text-sm">
                Errore caricamento dati: {error}
              </div>
            )}
            {loading && (
              <div className="mb-4 p-3 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 text-sm">
                Sincronizzo dati con il backend...
              </div>
            )}
            {renderContent()}
            {modal && (
              <Modal
                title={`${modal.mode === 'create' ? 'Nuovo' : 'Modifica'} ${modal.type}`}
                fields={modal.fields}
                values={formValues}
                onChange={(name, value) => setFormValues((prev) => ({ ...prev, [name]: value }))}
                onClose={() => setModal(null)}
                onSubmit={submitModal}
              />
            )}
            {detail && (
              <InfoModal
                title={detail.title}
                data={detail.data}
                onClose={() => setDetail(null)}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
