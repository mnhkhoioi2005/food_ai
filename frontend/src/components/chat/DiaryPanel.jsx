import { useState } from 'react';
import { BookOpen, Plus, Trash2, Zap } from 'lucide-react';

const MEAL_TYPES = ['Sáng', 'Trưa', 'Tối', 'Vặt'];

const DiaryPanel = ({ onSend }) => {
  const [entries, setEntries] = useState([{ meal: 'Trưa', food: '', calo: '' }]);
  const [goal, setGoal] = useState('');
  const [askType, setAskType] = useState('log'); // 'log' | 'suggest' | 'analyze'

  const addEntry = () => setEntries([...entries, { meal: 'Tối', food: '', calo: '' }]);
  const removeEntry = (i) => setEntries(entries.filter((_, idx) => idx !== i));
  const updateEntry = (i, field, val) => {
    const updated = [...entries];
    updated[i][field] = val;
    setEntries(updated);
  };

  const handleSend = () => {
    const filled = entries.filter(e => e.food.trim());
    if (askType === 'suggest') {
      let msg = '📔 Hôm nay tôi đã ăn:\n';
      filled.forEach(e => { msg += `- ${e.meal}: ${e.food}${e.calo ? ` (~${e.calo} calo)` : ''}\n`; });
      msg += goal ? `\nMục tiêu: ${goal}. ` : '';
      msg += 'Bữa tiếp theo tôi nên ăn gì để cân bằng dinh dưỡng?';
      onSend(msg);
    } else if (askType === 'analyze') {
      let msg = '📊 Phân tích bữa ăn hôm nay của tôi:\n';
      filled.forEach(e => { msg += `- ${e.meal}: ${e.food}${e.calo ? ` (~${e.calo} calo)` : ''}\n`; });
      msg += goal ? `\nMục tiêu sức khoẻ: ${goal}.` : '';
      onSend(msg);
    } else {
      let msg = '📔 Ghi nhận nhật ký ăn uống hôm nay:\n';
      filled.forEach(e => { msg += `- Bữa ${e.meal}: ${e.food}${e.calo ? ` (~${e.calo} calo)` : ''}\n`; });
      if (goal) msg += `Mục tiêu: ${goal}.`;
      onSend(msg);
    }
  };

  const btnLabels = { log: '📝 Ghi nhật ký', suggest: '💡 Gợi ý bữa tiếp', analyze: '📊 Phân tích' };

  return (
    <div className="p-4 bg-gradient-to-br from-emerald-50 to-teal-50 border-t border-emerald-100">
      <div className="flex items-center gap-2 mb-3">
        <BookOpen size={16} className="text-emerald-500" />
        <span className="text-sm font-semibold text-emerald-700">📔 Food Diary</span>
      </div>
      {/* Action type */}
      <div className="flex gap-1.5 mb-3">
        {Object.entries(btnLabels).map(([key, label]) => (
          <button key={key} onClick={() => setAskType(key)}
            className={`flex-1 py-1.5 text-xs font-medium rounded-lg border transition-all
              ${askType === key ? 'bg-emerald-500 text-white border-emerald-500' : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-300'}`}>
            {label}
          </button>
        ))}
      </div>
      {/* Entries */}
      <div className="space-y-2 mb-2">
        {entries.map((e, i) => (
          <div key={i} className="flex gap-1.5 items-center">
            <select value={e.meal} onChange={ev => updateEntry(i, 'meal', ev.target.value)}
              className="px-1.5 py-1.5 text-xs border border-gray-200 rounded-lg bg-white outline-none w-16">
              {MEAL_TYPES.map(t => <option key={t}>{t}</option>)}
            </select>
            <input value={e.food} onChange={ev => updateEntry(i, 'food', ev.target.value)}
              placeholder="Món đã ăn..." className="flex-1 px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-emerald-400 bg-white" />
            <input value={e.calo} onChange={ev => updateEntry(i, 'calo', ev.target.value)}
              placeholder="calo" className="w-16 px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-emerald-400 bg-white" />
            {entries.length > 1 && (
              <button onClick={() => removeEntry(i)} className="p-1 text-red-400 hover:text-red-600"><Trash2 size={13} /></button>
            )}
          </div>
        ))}
      </div>
      <button onClick={addEntry} className="flex items-center gap-1 text-xs text-emerald-600 hover:text-emerald-700 mb-2 px-1">
        <Plus size={13} /> Thêm bữa
      </button>
      <input value={goal} onChange={e => setGoal(e.target.value)}
        placeholder="Mục tiêu sức khoẻ (VD: giảm cân, tăng cơ, 1800 calo/ngày)..."
        className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-emerald-400 bg-white mb-3" />
      <button onClick={handleSend}
        className="w-full py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm font-semibold rounded-xl hover:shadow-md hover:scale-[1.01] transition-all flex items-center justify-center gap-2">
        <Zap size={14} /> {btnLabels[askType]}
      </button>
    </div>
  );
};

export default DiaryPanel;
