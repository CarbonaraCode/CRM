import React from 'react';
import { BarChart3, ShoppingCart, Ticket, Package } from 'lucide-react';

const DashboardWidget = ({ title, value, icon: Icon, trend, color }) => (
  <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      {trend && (
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${trend > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {trend > 0 ? '+' : ''}{trend}%
        </span>
      )}
    </div>
    <h3 className="text-slate-500 text-sm font-medium mb-1">{title}</h3>
    <p className="text-2xl font-bold text-slate-800">{value}</p>
  </div>
);

const Dashboard = ({ stats }) => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-slate-800">Panoramica Aziendale</h1>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <DashboardWidget 
        title="Fatturato Mensile" 
        value={`€ ${stats.revenue.toLocaleString()}`} 
        icon={BarChart3} 
        trend={12} 
        color="bg-blue-500" 
      />
      <DashboardWidget 
        title="Nuovi Ordini" 
        value={stats.orders} 
        icon={ShoppingCart} 
        trend={5} 
        color="bg-indigo-500" 
      />
      <DashboardWidget 
        title="Ticket Aperti" 
        value={stats.tickets} 
        icon={Ticket} 
        trend={-2} 
        color="bg-orange-500" 
      />
      <DashboardWidget 
        title="Valore Magazzino" 
        value={`€ ${stats.stockValue.toLocaleString()}`} 
        icon={Package} 
        color="bg-emerald-500" 
      />
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-64 flex flex-col items-center justify-center">
        <BarChart3 className="h-12 w-12 text-slate-300 mb-2" />
        <p className="text-slate-400 italic">Analisi Vendite (In arrivo)</p>
      </div>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-64 flex flex-col items-center justify-center">
        <ShoppingCart className="h-12 w-12 text-slate-300 mb-2" />
        <p className="text-slate-400 italic">Analisi Acquisti (In arrivo)</p>
      </div>
    </div>
  </div>
);

export default Dashboard;
