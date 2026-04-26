import { useState } from 'react';
import { GitCompare, Plus, Trash2, Zap } from 'lucide-react';

const CRITERIA = ['Giá cả', 'Dinh dưỡng', 'Vị ngon', 'Thời gian', 'Phù hợp mục tiêu'];

const ComparePanel = ({ onSend }) => {
  const [items, setItems] = useState(['', '']);
  const [criteria, setCriteria] = useState([]);
  const [context, setContext] = useState('');

  const addItem = () => { if (items.length < 5) setItems([...items, '']); };
  const removeItem = (i) => { if (items.length > 2) setItems(items.filter((_, idx) => idx !== i)); };
  const updateItem = (i, val) => { const u = [...items]; u[i] = val; setItems(u); };
  const toggleCriteria = (c) => setCriteria(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);

  const handleSend = () => {
    const filled = items.filter(x => x.trim());
    if (filled.length < 2) return;
    let msg = `⚖️ So sánh: ${filled.join(' vs ')}`;
    if (criteria.length) msg += `\nTiêu chí: ${criteria.join(', ')}`;
    if (context) msg += `\nBối cảnh: ${context}`;
    msg += '\nMón nào phù hợp hơn và vì sao?';
    onSend(msg);
  };

  const canSend = items.filter(x => x.trim()).length >= 2;

  return (
    <div className="p-4 bg-gradient-to-br from-violet-50 to-fuchsia-50 border-t border-violet-100">
      <div className="flex items-center gap-2 mb-3">
        <GitCompare size={16} className="text-violet-500" />
        <span className="text-sm font-semibold text-violet-700">⚖️ So sánh món ăn</span>
      </div>
      <div className="space-y-2 mb-2">
        {items.map((item, i) => (
          <div key={i} className="flex gap-2 items-center">
            <div className="w-6 h-6 rounded-full bg-violet-500 text-white text-xs flex items-center justify-center font-bold flex-shrink-0">
              {i + 1}
            </div>
            <input value={item} onChange={e => updateItem(i, e.target.value)}
              placeholder={`Món / quán thứ ${i + 1}... (VD: Phở bò, Bún bò)`}
              className="flex-1 px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-violet-400 bg-white" />
            {items.length > 2 && (
              <button onClick={() => removeItem(i)} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={13} /></button>
            )}
          </div>
        ))}
      </div>
      {items.length < 5 && (
        <button onClick={addItem} className="flex items-center gap-1 text-xs text-violet-600 hover:text-violet-700 mb-3 px-1">
          <Plus size={13} /> Thêm món để so sánh
        </button>
      )}
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1.5 block">So sánh theo tiêu chí</label>
        <div className="flex flex-wrap gap-1.5">
          {CRITERIA.map(c => (
            <button key={c} onClick={() => toggleCriteria(c)}
              className={`px-2.5 py-1 text-xs rounded-lg border transition-all font-medium
                ${criteria.includes(c) ? 'bg-violet-500 text-white border-violet-500' : 'bg-white text-gray-600 border-gray-200 hover:border-violet-300'}`}>
              {c}
            </button>
          ))}
        </div>
      </div>
      <input value={context} onChange={e => setContext(e.target.value)}
        placeholder="Bối cảnh: VD: đang giảm cân, ngân sách 50k, ăn trưa..."
        className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-violet-400 bg-white mb-3" />
      <button onClick={handleSend} disabled={!canSend}
        className={`w-full py-2 text-white text-sm font-semibold rounded-xl transition-all flex items-center justify-center gap-2
          ${canSend ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:shadow-md hover:scale-[1.01]' : 'bg-gray-300 cursor-not-allowed'}`}>
        <Zap size={14} /> So sánh ngay!
      </button>
    </div>
  );
};

export default ComparePanel;
