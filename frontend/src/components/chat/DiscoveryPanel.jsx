import { useState } from 'react';
import { Compass, MapPin, Zap } from 'lucide-react';

const CATEGORIES = ['Món Việt', 'Châu Á', 'Âu Mỹ', 'Chay', 'Hải sản', 'Đồ nướng', 'Ăn vặt', 'Tráng miệng'];
const VIBES = ['Mới lạ chưa thử', 'Đang trend', 'Ít người biết', 'Đặc sản vùng miền', 'Fusion sáng tạo'];

const DiscoveryPanel = ({ onSend }) => {
  const [category, setCategory] = useState('');
  const [vibe, setVibe] = useState('');
  const [location, setLocation] = useState('');
  const [budget, setBudget] = useState('');
  const [avoid, setAvoid] = useState('');

  const handleSend = () => {
    let msg = '🌟 Tôi muốn khám phá món ăn mới';
    if (category) msg += ` thuộc loại ${category}`;
    if (vibe) msg += `, phong cách ${vibe}`;
    if (location) msg += `, ở ${location}`;
    if (budget) msg += `, ngân sách ${budget}k`;
    if (avoid) msg += `. Tôi không ăn được: ${avoid}`;
    msg += '. Gợi ý món gì đặc biệt, thú vị mà tôi chưa từng thử!';
    onSend(msg);
  };

  return (
    <div className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 border-t border-indigo-100">
      <div className="flex items-center gap-2 mb-3">
        <Compass size={16} className="text-indigo-500" />
        <span className="text-sm font-semibold text-indigo-700">🌟 Khám phá món mới</span>
      </div>
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1.5 block">Loại ẩm thực yêu thích</label>
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(category === c ? '' : c)}
              className={`px-2.5 py-1 text-xs rounded-lg border transition-all font-medium
                ${category === c ? 'bg-indigo-500 text-white border-indigo-500' : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'}`}>
              {c}
            </button>
          ))}
        </div>
      </div>
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1.5 block">Phong cách khám phá</label>
        <div className="flex flex-wrap gap-1.5">
          {VIBES.map(v => (
            <button key={v} onClick={() => setVibe(vibe === v ? '' : v)}
              className={`px-2.5 py-1 text-xs rounded-lg border transition-all font-medium
                ${vibe === v ? 'bg-purple-500 text-white border-purple-500' : 'bg-white text-gray-600 border-gray-200 hover:border-purple-300'}`}>
              {v}
            </button>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <label className="text-xs text-gray-500 mb-1 block flex items-center gap-1"><MapPin size={10}/> Khu vực</label>
          <input value={location} onChange={e => setLocation(e.target.value)}
            placeholder="VD: Hà Nội, Quận 1..." className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-indigo-400 bg-white" />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Ngân sách (k)</label>
          <input value={budget} onChange={e => setBudget(e.target.value)}
            placeholder="VD: 50, 100..." className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-indigo-400 bg-white" />
        </div>
      </div>
      <input value={avoid} onChange={e => setAvoid(e.target.value)}
        placeholder="Không ăn được / dị ứng... (tuỳ chọn)"
        className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-indigo-400 bg-white mb-3" />
      <button onClick={handleSend}
        className="w-full py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-semibold rounded-xl hover:shadow-md hover:scale-[1.01] transition-all flex items-center justify-center gap-2">
        <Zap size={14} /> Khám phá ngay!
      </button>
    </div>
  );
};

export default DiscoveryPanel;
