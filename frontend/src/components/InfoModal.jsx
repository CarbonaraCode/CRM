import React from 'react';
import { X } from 'lucide-react';

const InfoModal = ({ title, data, onClose }) => {
  return (
    <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl border border-slate-200">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>
        <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[70vh] overflow-y-auto">
          {Object.entries(data || {}).map(([key, value]) => (
            <div key={key} className="flex flex-col">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{key}</span>
              <span className="text-sm text-slate-800 break-words">{`${value ?? '-'}`}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-end px-5 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800"
          >
            Chiudi
          </button>
        </div>
      </div>
    </div>
  );
};

export default InfoModal;
