import React, { useState } from 'react';
import { Search, Plus, MoreVertical, Trash2 } from 'lucide-react';

const DataTable = ({ title, columns, data, onAdd, onDelete, onEdit }) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Safe check for data
  const safeData = Array.isArray(data) ? data : [];

  const filteredData = safeData.filter(item => 
    Object.values(item).some(val => 
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-center gap-4">
        <h2 className="text-lg font-bold text-slate-800">{title}</h2>
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-none">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <input 
              type="text" 
              placeholder="Cerca..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button onClick={onAdd} className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus className="h-4 w-4 mr-2" />
            Nuovo
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {col.header}
                </th>
              ))}
              <th className="px-6 py-3 text-right">Azioni</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {filteredData.length > 0 ? (
              filteredData.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-slate-50 transition-colors">
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">
                      {col.render ? col.render(row) : row[col.accessor]}
                    </td>
                  ))}
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {onEdit && (
                      <button onClick={() => onEdit(row)} className="text-slate-400 hover:text-blue-600 mr-3">
                        <MoreVertical size={16}/>
                      </button>
                    )}
                    {onDelete && <button onClick={() => onDelete(row)} className="text-red-400 hover:text-red-600"><Trash2 size={16}/></button>}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length + 1} className="px-6 py-12 text-center text-slate-500">
                  Nessun dato trovato
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;
