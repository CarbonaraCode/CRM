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
