import React, { useState } from 'react';
import { Menu, ChevronRight } from 'lucide-react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import DataTable from './components/DataTable';

// --- DATI FINTI INIZIALI (In attesa del Backend) ---
const INITIAL_DATA = {
  stats: {
    revenue: 125000,
    orders: 45,
    tickets: 12,
    stockValue: 54000
  },
  clients: [
    { id: 1, name: 'Rossi S.r.l.', email: 'info@rossi.it', piva: '12345678901', status: 'Attivo' },
    { id: 2, name: 'Bianchi SpA', email: 'contact@bianchi.com', piva: '09876543210', status: 'Attivo' },
  ],
  products: [
    { id: 1, code: 'MAT-001', name: 'Laptop Pro X', stock: 15, price: 1200 },
    { id: 2, code: 'MAT-002', name: 'Monitor 4K', stock: 8, price: 450 },
  ],
  tickets: [
    { id: 101, subject: 'Errore fattura', priority: 'Alta', status: 'Aperto' },
    { id: 102, subject: 'Reso merce', priority: 'Media', status: 'In lavorazione' },
  ]
};

function App() {
  const [activeModule, setActiveModule] = useState('dashboard');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [data, setData] = useState(INITIAL_DATA);

  const handleAdd = (type) => alert(`Modale creazione ${type} (WIP)`);
  
  const handleDelete = (type, id) => {
    if(confirm('Eliminare elemento?')) {
      setData(prev => ({
        ...prev,
        [type]: prev[type].filter(i => i.id !== id)
      }));
    }
  };

  const renderContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard stats={data.stats} />;
      
      // VENDITE ESEMPIO
      case 'clients':
        return <DataTable 
          title="Gestione Clienti" 
          columns={[
            { header: 'Azienda', accessor: 'name' },
            { header: 'Email', accessor: 'email' },
            { header: 'P.IVA', accessor: 'piva' },
            { header: 'Stato', accessor: 'status', render: r => <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs">{r.status}</span> }
          ]}
          data={data.clients}
          onAdd={() => handleAdd('Cliente')}
          onDelete={(id) => handleDelete('clients', id)}
        />;
      
      // INVENTARIO ESEMPIO
      case 'products':
        return <DataTable 
          title="Prodotti" 
          columns={[
            { header: 'Codice', accessor: 'code' },
            { header: 'Nome', accessor: 'name' },
            { header: 'Stock', accessor: 'stock' },
            { header: 'Prezzo', accessor: 'price', render: r => `€ ${r.price}` }
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
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
