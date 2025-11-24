import React from 'react';
import { X } from 'lucide-react';

const Modal = ({ title, fields, values, onChange, onClose, onSubmit }) => {
  return (
    <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-xl border border-slate-200">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>
        <div className="p-5 space-y-4 max-h-[70vh] overflow-y-auto">
          {fields.map((field) => {
            const value = values[field.name] ?? '';
            const common = {
              id: field.name,
              name: field.name,
              value,
              onChange: (e) => onChange(field.name, e.target.value),
              className:
                'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            };

            if (field.type === 'file') {
              return (
                <div key={field.name}>
                  <label className="text-sm font-medium text-slate-700 mb-1 block" htmlFor={field.name}>
                    {field.label}
                  </label>
                  <div className="space-y-2">
                    <input
                      id={field.name}
                      name={field.name}
                      type="file"
                      accept={field.accept}
                      onChange={(e) => onChange(field.name, e.target.files?.[0] || null)}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {field.existingUrl && (
                      <a
                        href={field.existingUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 text-sm underline"
                      >
                        Visualizza allegato corrente
                      </a>
                    )}
                    {field.hint && <p className="text-xs text-slate-500">{field.hint}</p>}
                  </div>
                </div>
              );
            }

            if (field.type === 'select') {
              return (
                <div key={field.name}>
                  <label className="text-sm font-medium text-slate-700 mb-1 block" htmlFor={field.name}>
                    {field.label}
                  </label>
                  <select {...common}>
                    <option value="">Seleziona...</option>
                    {field.options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              );
            }

            if (field.type === 'checkbox') {
              return (
                <label key={field.name} className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={!!values[field.name]}
                    onChange={(e) => onChange(field.name, e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                  />
                  {field.label}
                </label>
              );
            }

            if (field.type === 'items') {
              const lines = Array.isArray(values[field.name]) ? values[field.name] : [];
              const updateLine = (idx, key, val) => {
                const copy = lines.map((l, i) => (i === idx ? { ...l, [key]: val } : l));
                onChange(field.name, copy);
              };
              const addLine = () => onChange(field.name, [...lines, { product: '', description: '', quantity: 1, unit_price: 0, tax_rate: 0 }]);
              const removeLine = (idx) => {
                const copy = lines.filter((_, i) => i !== idx);
                onChange(field.name, copy);
              };
              const subtotal = lines.reduce((sum, l) => sum + Number(l.quantity || 0) * Number(l.unit_price || 0), 0);
              const tax = lines.reduce((sum, l) => sum + Number(l.quantity || 0) * Number(l.unit_price || 0) * (Number(l.tax_rate || 0) / 100), 0);
              return (
                <div key={field.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-slate-700">{field.label}</label>
                    <button type="button" onClick={addLine} className="text-blue-600 text-sm underline">Aggiungi riga</button>
                  </div>
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="min-w-full text-sm">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-3 py-2 text-left">Prodotto</th>
                          <th className="px-3 py-2 text-left">Descrizione</th>
                          <th className="px-3 py-2 text-right">Q.tà</th>
                          <th className="px-3 py-2 text-right">Prezzo</th>
                          <th className="px-3 py-2 text-right">IVA %</th>
                          <th className="px-3 py-2 text-right">Totale</th>
                          <th className="px-3 py-2"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {lines.length ? lines.map((line, idx) => (
                          <tr key={idx} className="border-t border-slate-200">
                            <td className="px-3 py-2"><input className="w-full border border-slate-200 rounded px-2 py-1" value={line.product} onChange={(e) => updateLine(idx, 'product', e.target.value)} /></td>
                            <td className="px-3 py-2"><input className="w-full border border-slate-200 rounded px-2 py-1" value={line.description} onChange={(e) => updateLine(idx, 'description', e.target.value)} /></td>
                            <td className="px-3 py-2 text-right"><input type="number" step="0.01" className="w-20 text-right border border-slate-200 rounded px-2 py-1" value={line.quantity} onChange={(e) => updateLine(idx, 'quantity', Number(e.target.value))} /></td>
                            <td className="px-3 py-2 text-right"><input type="number" step="0.01" className="w-24 text-right border border-slate-200 rounded px-2 py-1" value={line.unit_price} onChange={(e) => updateLine(idx, 'unit_price', Number(e.target.value))} /></td>
                            <td className="px-3 py-2 text-right"><input type="number" step="0.01" className="w-20 text-right border border-slate-200 rounded px-2 py-1" value={line.tax_rate} onChange={(e) => updateLine(idx, 'tax_rate', Number(e.target.value))} /></td>
                            <td className="px-3 py-2 text-right">{(Number(line.quantity || 0) * Number(line.unit_price || 0)).toFixed(2)}</td>
                            <td className="px-3 py-2 text-right"><button type="button" onClick={() => removeLine(idx)} className="text-red-500">✕</button></td>
                          </tr>
                        )) : (
                          <tr><td className="px-3 py-2 text-center text-slate-500" colSpan={7}>Nessuna riga</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-end gap-4 text-sm text-slate-700">
                    <span>Subtotale: {subtotal.toFixed(2)}</span>
                    <span>IVA: {tax.toFixed(2)}</span>
                    <span>Totale: {(subtotal).toFixed(2)}</span>
                  </div>
                </div>
              );
            }

            if (field.type === 'textarea') {
              return (
                <div key={field.name}>
                  <label className="text-sm font-medium text-slate-700 mb-1 block" htmlFor={field.name}>
                    {field.label}
                  </label>
                  <textarea
                    {...common}
                    rows={4}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              );
            }

            return (
              <div key={field.name}>
                <label className="text-sm font-medium text-slate-700 mb-1 block" htmlFor={field.name}>
                  {field.label}
                </label>
                <input {...common} type={field.type || 'text'} />
              </div>
            );
          })}
        </div>
        <div className="flex justify-end gap-2 px-5 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800"
          >
            Annulla
          </button>
          <button
            onClick={onSubmit}
            className="px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm"
          >
            Salva
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;
