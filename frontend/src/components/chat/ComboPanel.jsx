import { useState } from 'react';
import { Soup, Users, DollarSign, Clock, Leaf, Zap } from 'lucide-react';

const MEALS = ['Bữa sáng', 'Bữa trưa', 'Bữa tối', 'Ăn vặt', 'Ăn khuya'];
const GOALS = ['No bụng', 'Giảm cân', 'Tăng cơ', 'Ăn healthy', 'Nhanh gọn'];

const ComboPanel = ({ onSend }) => {
  const [people, setPeople] = useState(1);
  const [budget, setBudget] = useState('');
  const [meal, setMeal] = useState('Bữa trưa');
  const [goal, setGoal] = useState('');
  const [diet, setDiet] = useState('');

  const handleBuild = () => {
    let msg = `🍱 Xây combo ${meal} cho ${people} người`;
    if (budget) msg += `, ngân sách ${budget}k`;
    if (goal) msg += `, mục tiêu: ${goal}`;
    if (diet) msg += `, chế độ ăn: ${diet}`;
    onSend(msg);
  };

  return (
    <div className="p-4 bg-gradient-to-br from-orange-50 to-amber-50 border-t border-orange-100">
      <div className="flex items-center gap-2 mb-3">
        <Soup size={16} className="text-orange-500" />
        <span className="text-sm font-semibold text-orange-700">🍱 Combo Generator</span>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        {/* Bữa ăn */}
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Bữa ăn</label>
          <div className="flex flex-wrap gap-1">
            {MEALS.map(m => (
              <button key={m} onClick={() => setMeal(m)}
                className={`px-2 py-1 text-xs rounded-lg border transition-all ${meal === m ? 'bg-orange-500 text-white border-orange-500' : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300'}`}>
                {m}
              </button>
            ))}
          </div>
        </div>
        {/* Số người */}
        <div>
          <label className="text-xs text-gray-500 mb-1 block flex items-center gap-1"><Users size={11}/> Số người</label>
          <div className="flex items-center gap-2">
            <button onClick={() => setPeople(Math.max(1, people - 1))} className="w-7 h-7 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-orange-50 font-bold">-</button>
            <span className="text-sm font-semibold text-gray-700 w-4 text-center">{people}</span>
            <button onClick={() => setPeople(Math.min(20, people + 1))} className="w-7 h-7 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-orange-50 font-bold">+</button>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <label className="text-xs text-gray-500 mb-1 block flex items-center gap-1"><DollarSign size={11}/> Ngân sách (k)</label>
          <input value={budget} onChange={e => setBudget(e.target.value)} placeholder="VD: 50, 100, 200"
            className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-orange-400 bg-white" />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block flex items-center gap-1"><Leaf size={11}/> Mục tiêu</label>
          <div className="flex flex-wrap gap-1">
            {GOALS.map(g => (
              <button key={g} onClick={() => setGoal(goal === g ? '' : g)}
                className={`px-2 py-1 text-xs rounded-lg border transition-all ${goal === g ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-600 border-gray-200 hover:border-green-300'}`}>
                {g}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1 block">Chế độ ăn / dị ứng (tuỳ chọn)</label>
        <input value={diet} onChange={e => setDiet(e.target.value)} placeholder="VD: chay, không hải sản, ít tinh bột..."
          className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-orange-400 bg-white" />
      </div>
      <button onClick={handleBuild}
        className="w-full py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm font-semibold rounded-xl hover:shadow-md hover:scale-[1.01] transition-all flex items-center justify-center gap-2">
        <Zap size={14} /> Xây combo ngay!
      </button>
    </div>
  );
};

export default ComboPanel;
