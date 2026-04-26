import { useState } from 'react';
import { Heart, Zap } from 'lucide-react';

const MOODS = [
  { emoji: '😊', label: 'Vui vẻ', color: 'yellow' },
  { emoji: '😔', label: 'Buồn', color: 'blue' },
  { emoji: '😤', label: 'Stress', color: 'red' },
  { emoji: '😴', label: 'Mệt mỏi', color: 'purple' },
  { emoji: '🥰', label: 'Lãng mạn', color: 'pink' },
  { emoji: '💪', label: 'Năng lượng', color: 'green' },
  { emoji: '🤒', label: 'Ốm/mệt', color: 'gray' },
  { emoji: '🎉', label: 'Kỷ niệm', color: 'orange' },
];

const WEATHER = ['☀️ Nắng nóng', '🌧️ Mưa lạnh', '🌤️ Dễ chịu', '🌬️ Gió lạnh'];

const colorMap = {
  yellow: 'bg-yellow-100 border-yellow-400 text-yellow-700',
  blue: 'bg-blue-100 border-blue-400 text-blue-700',
  red: 'bg-red-100 border-red-400 text-red-700',
  purple: 'bg-purple-100 border-purple-400 text-purple-700',
  pink: 'bg-pink-100 border-pink-400 text-pink-700',
  green: 'bg-green-100 border-green-400 text-green-700',
  gray: 'bg-gray-100 border-gray-400 text-gray-700',
  orange: 'bg-orange-100 border-orange-400 text-orange-700',
};

const MoodPanel = ({ onSend }) => {
  const [mood, setMood] = useState(null);
  const [weather, setWeather] = useState('');
  const [extra, setExtra] = useState('');

  const handleSend = () => {
    if (!mood) return;
    let msg = `🎭 Tôi đang cảm thấy ${mood.emoji} ${mood.label}`;
    if (weather) msg += `, thời tiết: ${weather}`;
    if (extra) msg += `. ${extra}`;
    msg += '. Gợi ý món ăn phù hợp với tâm trạng của tôi!';
    onSend(msg);
  };

  return (
    <div className="p-4 bg-gradient-to-br from-pink-50 to-purple-50 border-t border-pink-100">
      <div className="flex items-center gap-2 mb-3">
        <Heart size={16} className="text-pink-500" />
        <span className="text-sm font-semibold text-pink-700">🎭 Gợi ý theo tâm trạng</span>
      </div>
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-2 block">Bạn đang cảm thấy thế nào?</label>
        <div className="grid grid-cols-4 gap-1.5">
          {MOODS.map(m => (
            <button key={m.label} onClick={() => setMood(m)}
              className={`flex flex-col items-center gap-1 p-2 rounded-xl border-2 transition-all text-xs font-medium
                ${mood?.label === m.label ? colorMap[m.color] + ' border-2 scale-105' : 'bg-white border-gray-100 text-gray-600 hover:border-gray-300'}`}>
              <span className="text-xl">{m.emoji}</span>
              <span>{m.label}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1 block">Thời tiết hiện tại (tuỳ chọn)</label>
        <div className="flex flex-wrap gap-1.5">
          {WEATHER.map(w => (
            <button key={w} onClick={() => setWeather(weather === w ? '' : w)}
              className={`px-2 py-1 text-xs rounded-lg border transition-all ${weather === w ? 'bg-blue-500 text-white border-blue-500' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'}`}>
              {w}
            </button>
          ))}
        </div>
      </div>
      <div className="mb-3">
        <input value={extra} onChange={e => setExtra(e.target.value)}
          placeholder="Thêm gì không? VD: ngân sách 50k, gần quận 1..."
          className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-pink-400 bg-white" />
      </div>
      <button onClick={handleSend} disabled={!mood}
        className={`w-full py-2 text-white text-sm font-semibold rounded-xl transition-all flex items-center justify-center gap-2
          ${mood ? 'bg-gradient-to-r from-pink-500 to-purple-500 hover:shadow-md hover:scale-[1.01]' : 'bg-gray-300 cursor-not-allowed'}`}>
        <Zap size={14} /> Gợi ý theo tâm trạng!
      </button>
    </div>
  );
};

export default MoodPanel;
