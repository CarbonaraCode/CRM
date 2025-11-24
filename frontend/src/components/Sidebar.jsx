import React from 'react';
import { 
  LayoutDashboard, Users, ShoppingCart, Package, FileText, 
  Settings, Truck, ScrollText, CreditCard, Ticket, 
  BarChart3, Globe, LogOut, X 
} from 'lucide-react';

const Sidebar = ({ activeModule, setActiveModule, isMobileOpen, toggleMobile }) => {
  const menuGroups = [
    {
      title: 'Vendite',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'clients', label: 'Clienti', icon: Users },
        { id: 'contacts', label: 'Contatti', icon: Users },
        { id: 'opportunities', label: 'Opportunità', icon: BarChart3 },
        { id: 'offers', label: 'Offerte', icon: FileText },
        { id: 'orders_sales', label: 'Ordini Vendita', icon: ShoppingCart },
        { id: 'invoices_sales', label: 'Fatture', icon: FileText },
        { id: 'contracts', label: 'Contratti', icon: ScrollText },
      ]
    },
    {
      title: 'Acquisti',
      items: [
        { id: 'suppliers', label: 'Fornitori', icon: Truck },
        { id: 'orders_purchase', label: 'Ordini Acquisto', icon: ShoppingCart },
        { id: 'invoices_purchase', label: 'Fatture Acquisto', icon: FileText },
      ]
    },
    {
      title: 'Inventario & Controllo',
      items: [
        { id: 'products', label: 'Prodotti/Matricole', icon: Package },
        { id: 'management', label: 'Controllo Gestione', icon: BarChart3 },
        { id: 'tickets', label: 'Ticket', icon: Ticket },
        { id: 'expenses', label: 'Note Spese', icon: CreditCard },
        { id: 'credit_notes', label: 'Note Credito', icon: FileText },
      ]
    },
    {
      title: 'Sistema',
      items: [
        { id: 'cms', label: 'CMS', icon: Globe },
        { id: 'config', label: 'Configurazione', icon: Settings },
      ]
    }
  ];

  return (
    <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-slate-100 transition-transform duration-300 ease-in-out transform ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:relative flex flex-col`}>
      <div className="h-16 flex items-center justify-between px-6 border-b border-slate-700">
        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Nexus CRM</span>
        <button onClick={toggleMobile} className="md:hidden text-slate-400 hover:text-white">
          <X size={24} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        {menuGroups.map((group, idx) => (
          <div key={idx} className="mb-6 px-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">{group.title}</h3>
            <div className="space-y-1">
              {group.items.map((item) => (
                <button
                  key={item.id}
                  onClick={() => { setActiveModule(item.id); toggleMobile(); }}
                  className={`w-full flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeModule === item.id 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' 
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-4 border-t border-slate-700">
        <button className="flex items-center w-full px-2 py-2 text-sm font-medium text-red-400 hover:text-red-300 hover:bg-slate-800 rounded-md">
          <LogOut className="mr-3 h-5 w-5" />
          Esci
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
