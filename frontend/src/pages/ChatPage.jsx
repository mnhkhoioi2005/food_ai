import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import ReactDOM from 'react-dom';
import { Send, User, Trash2, Loader2, Copy, Check, ThumbsUp, ThumbsDown, ChefHat, X, Save } from 'lucide-react';
import { chatAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import ComboPanel from '../components/chat/ComboPanel';
import MoodPanel from '../components/chat/MoodPanel';
import DiaryPanel from '../components/chat/DiaryPanel';
import DiscoveryPanel from '../components/chat/DiscoveryPanel';
import ComparePanel from '../components/chat/ComparePanel';
import NearbyRestaurantsCard from '../components/chat/NearbyRestaurantsCard';
import MiniMapPopup from '../components/MiniMapPopup';
import { fetchNearbyRestaurants, parseRestaurants } from '../utils/overpass';

// ── localStorage helpers theo user ─────────────────────────────────────────
const storageKey   = (uid) => uid ? `vfa_chat_msgs_${uid}`  : null;
const historyKey   = (uid) => uid ? `vfa_chat_hist_${uid}`  : null;

function loadMessages(uid) {
  const key = storageKey(uid);
  if (!key) return null;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch { return null; }
}

function saveMessages(uid, messages) {
  const key = storageKey(uid);
  if (!key) return;
  try {
    // Loại bỏ onViewMap (function) trước khi serialize
    const toSave = messages.map(({ onViewMap, ...rest }) => rest);
    localStorage.setItem(key, JSON.stringify(toSave));
  } catch { /* quota exceeded – bỏ qua */ }
}

function loadHistory(uid) {
  const key = historyKey(uid);
  if (!key) return [];
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveHistory(uid, history) {
  const key = historyKey(uid);
  if (!key) return;
  try { localStorage.setItem(key, JSON.stringify(history)); } catch { }
}


const MODES = [
  { id: 'ai', emoji: '🤖', label: 'AI Decision', desc: 'Ăn gì hôm nay?', color: '#f97316', isPopup: false },
  { id: 'combo', emoji: '🍱', label: 'Combo', desc: 'Xây bữa ăn', color: '#f59e0b', isPopup: true },
  { id: 'discovery', emoji: '🌟', label: 'Khám phá', desc: 'Thử món mới', color: '#6366f1', isPopup: true },
  { id: 'compare', emoji: '⚖️', label: 'So sánh', desc: 'Chọn món nào?', color: '#8b5cf6', isPopup: true },
  { id: 'mood', emoji: '🎭', label: 'Tâm trạng', desc: 'Gợi ý theo mood', color: '#ec4899', isPopup: true },
  { id: 'diary', emoji: '📔', label: 'Nhật ký', desc: 'Food diary', color: '#10b981', isPopup: true },
];

const POPUP_TITLES = {
  combo: { emoji: '🍱', label: 'Combo Generator', sub: 'Xây bữa ăn hoàn chỉnh theo nhu cầu' },
  discovery: { emoji: '🌟', label: 'Khám phá món mới', sub: 'Tìm món lạ, đặc sản, đang trend' },
  compare: { emoji: '⚖️', label: 'So sánh món ăn', sub: 'Chọn giữa các món dễ dàng hơn' },
  mood: { emoji: '🎭', label: 'Gợi ý theo tâm trạng', sub: 'AI hiểu cảm xúc và gợi ý phù hợp' },
  diary: { emoji: '📔', label: 'Nhật ký ăn uống', sub: 'Ghi lại, phân tích bữa ăn của bạn' },
};

const AI_PROMPTS = [
  { text: 'Ăn gì hôm nay dưới 50k ở Hà Nội?', label: 'Ăn gì hôm nay?' },
  { text: 'Tôi muốn ăn healthy, đang giảm cân', label: 'Ăn healthy' },
  { text: 'Cần ăn nhanh trong 15 phút gần văn phòng', label: 'Ăn nhanh' },
  { text: 'Gợi ý ăn khuya ngon, không quá nặng', label: 'Ăn khuya' },
];

// ── Extract food keyword from AI response ──────────────────────────────────
const FOOD_LIST = [
  'phở bò', 'phở gà', 'phở', 'bún bò huế', 'bún bò', 'bún riêu', 'bún mắm', 'bún',
  'cơm tấm', 'cơm gà', 'cơm chiên', 'cơm rang', 'cơm', 'bánh mì', 'bánh cuốn',
  'bánh xèo', 'bánh tráng', 'bánh', 'lẩu', 'hủ tiếu', 'mì quảng', 'mì', 'xôi',
  'gỏi cuốn', 'chả giò', 'nem', 'chè', 'bún chả', 'bún đậu', 'bún thịt nướng',
  'pizza', 'burger', 'sushi', 'ramen',
];

function extractFoodKeyword(text) {
  const best = text.match(/Đề xuất tốt nhất[^:]*:\s*\*?\*?([^—\n*~]+)/i);
  if (best) return best[1].trim();
  const main = text.match(/Món chính[^:]*:\s*([^~\n]+)/i);
  if (main) return main[1].trim().split('~')[0].trim();
  const lower = text.toLowerCase();
  for (const f of FOOD_LIST) if (lower.includes(f)) return f;
  return null;
}

// Trích xuất từ khóa từ câu hỏi của user ("quán phở gần đây", "tìm phở", v.v.)
function extractMapKeyword(text) {
  const lower = text.toLowerCase();
  // Pattern: "quán/nhà hàng/tiệm + tên món"
  const m = lower.match(/(?:quán|tìm quán|các quán|nhà hàng|tiệm|chỗ bán)\s+([\wÀ-ỹ]{2,}(?:\s+[\wÀ-ỹ]{2,})?)/iu);
  if (m) return m[1].trim();
  // Fallback: tìm tên món trong câu hỏi
  for (const f of FOOD_LIST) if (lower.includes(f)) return f;
  return null;
}

// Kiểm tra xem câu hỏi có đang hỏi về quán gần đây không
function isNearbyQuery(text) {
  const lower = text.toLowerCase();
  return (
    lower.includes('gần đây') || lower.includes('gần mình') || lower.includes('gần tôi') ||
    lower.includes('gần nhà') || lower.includes('gần chỗ') || lower.includes('gần nơi') ||
    lower.includes('quán nào') || lower.includes('ở đâu') || lower.includes('tìm quán') ||
    lower.includes('quán ăn') || lower.includes('nhà hàng')
  );
}

// ── Geocoding quán ăn (Nominatim OpenStreetMap) ─────────────────────────────
const geocodeCache = new Map();
let lastGeoTime = 0;

async function geocodeRestaurant(name, addr) {
  const key = `${name}|${addr}`;
  if (geocodeCache.has(key)) return geocodeCache.get(key);

  // Nominatim rate-limit: max 1 req/s
  const now = Date.now();
  if (now - lastGeoTime < 1100) await new Promise(r => setTimeout(r, 1100 - (now - lastGeoTime)));
  lastGeoTime = Date.now();

  // Có địa chỉ → tìm chính xác; không có → tìm theo tên quán + thành phố
  const queries = addr
    ? [`${name}, ${addr}, Việt Nam`, `${addr}, Việt Nam`]
    : [
        `${name}, Thành phố Hồ Chí Minh`,
        `${name}, Hà Nội`,
        `${name}, Việt Nam`,
      ];

  for (const q of queries) {
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1&countrycodes=vn`,
        { headers: { 'Accept-Language': 'vi' } }
      );
      const data = await res.json();
      if (data[0]) {
        const pos = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
        geocodeCache.set(key, pos);
        return pos;
      }
    } catch { }
  }
  geocodeCache.set(key, null);
  return null;
}

// Kiểm tra chuỗi có phải địa chỉ Việt Nam không (tránh lần với giá tiền, mô tả )
function isVietAddress(s) {
  if (s.length < 5) return false;
  // Chứa tên quận/phường phổ biến
  if (/\b(quận|qu\.|phường|p\.|h\.|bình thạnh|tân bình|phú nhuận|gò vấp|tân phú|bình tân|thủ đức|hóc môn|nhà bè|bình chánh|cần giờ|củ chi|hà đông|hoàn kiếm|đống đa|hai bà|cầu giấy|tây hồ|long biên|sóng|sa đéc|niênh|mỹ tho)/i.test(s)) return true;
  // Có dấu phẩy & chữ in hoa đầu từ sau phẩy (VD: "Nguyễn Trọng Tuyến, Phú Nhuận")
  if (/,\s*[A-ZĐĂÂÔƠƯẠ-ỹ]/u.test(s)) return true;
  // Có số nhà + tên đường (VD: "123 Lê Lợi")
  if (/^\d+\s+[A-Z]/u.test(s.trim())) return true;
  return false;
}

// ── Typing Indicator ───────────────────────────────────────────
const TypingIndicator = () => (
  <div className="flex items-end gap-3 mb-5">
    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center flex-shrink-0">
      <ChefHat size={15} className="text-white" />
    </div>
    <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-sm border border-gray-100">
      <div className="flex gap-1.5 items-center">
        {[0, 1, 2].map(i => (
          <span key={i} className="w-2 h-2 rounded-full bg-orange-400"
            style={{ animation: `db 1.4s ease-in-out ${i * 0.2}s infinite` }} />
        ))}
      </div>
    </div>
  </div>
);

// ── Message Bubble ──────────────────────────────────────────
const MessageBubble = ({ msg, onFeedback, userLocation }) => {
  const [copied, setCopied] = useState(false);
  const [popup, setPopup] = useState(null); // { pos, name, addr, pos2D }
  const msgBodyRef = useRef(null);
  const hoverTimerRef = useRef(null);
  const isBot = msg.role === 'model';

  // Hàm tạo span highlight cho tên quán
  const makeRestSpan = (inner, cleanName, addr) => {
    const encN = encodeURIComponent(cleanName);
    const encA = encodeURIComponent(addr || '');
    return `<span class="rest-hover" data-rn="${encN}" data-ra="${encA}" style="color:#065f46;border-bottom:1.5px dotted #10b981;cursor:default;font-weight:600" title="Hover để xem vị trí">${inner}</span>`;
  };

  const fmt = (text) => {
    // Bước 1: Phát hiện tên quán trong numbered list TRƯỚC khi convert bold
    // Yêu cầu: bắt đầu bằng "N." hoặc "N)" + tên + tùy chọn (ghi chú) + dấu —/–
    text = text.replace(
      /^(\d+[.)]\s+)(\*\*)?([^*\n—–(){~]{2,55}?)(\*\*)?\s*(\([^)\n]{0,100}\))?\s*(?=—|–)/gmu,
      (match, num, b1, name, b2, paren) => {
        const cleanName = name.trim();
        if (cleanName.length < 3) return match;
        // Bỏ qua tiêu đề section, giá tiền
        if (/^(mode|feedback|đề xuất|lựa chọn|combo|tổng|tổng cộng|khi nào|lý do|món chính|món phụ|đồ uống)/i.test(cleanName)) return match;

        const cleanParen = paren ? paren.slice(1, -1).trim() : '';
        const addr = isVietAddress(cleanParen) ? cleanParen : '';
        const inner = b1 ? `<strong>${cleanName}</strong>` : cleanName;
        const span = makeRestSpan(inner, cleanName, addr);
        return `${num}${span}${paren ? ` ${paren}` : ''}`;
      }
    );

    // Bước 2: Bold các **text** còn lại chưa được xử lý
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Bước 3: Headings
    text = text.replace(/^### (.+)$/gm, '<p class="font-bold text-orange-700 text-sm mt-3 mb-1">$1</p>');
    text = text.replace(/^## (.+)$/gm, '<p class="font-semibold text-gray-800 mt-2 mb-1">$1</p>');

    // Bước 4: Phát hiện thêm các mẫu "Tên quán (địa chỉ VN)" chưa được đánh dấu
    text = text.replace(
      /(?<!data-rn[^>]{0,200})(<strong>[^<]{2,50}<\/strong>|[A-ZĐĂẠ-ỹ][^\n<(~—]{2,50}?)\s*\(([^)\n]{5,80})\)/gu,
      (match, name, addr) => {
        if (match.includes('rest-hover')) return match;
        if (!isVietAddress(addr)) return match;
        const cleanName = name.replace(/<[^>]+>/g, '').trim();
        return `${makeRestSpan(name, cleanName, addr)} (${addr})`;
      }
    );

    // Bước 5: Newlines
    text = text.replace(/\n/g, '<br/>');
    return text;
  };

  // Event delegation: hover vào span.rest-hover → geocode → hiện popup
  useEffect(() => {
    const el = msgBodyRef.current;
    if (!el || !isBot) return;

    const show = async (e) => {
      const span = e.target.closest('.rest-hover');
      if (!span) return;
      const capturedSpan = span;
      clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = setTimeout(async () => {
        const rect = capturedSpan.getBoundingClientRect();
        const name = decodeURIComponent(capturedSpan.dataset.rn || '');
        const addr = decodeURIComponent(capturedSpan.dataset.ra || '');
        const vw = window.innerWidth;
        const popupW = 270;
        let left = rect.right + 12;
        if (left + popupW > vw - 12) left = rect.left - popupW - 12;
        let top = rect.top - 10;
        const popupH = 230;
        if (top + popupH > window.innerHeight - 12) top = window.innerHeight - popupH - 12;
        // Hiện popup ngay với trạng thái loading
        setPopup({ pos: { left: Math.max(8, left), top: Math.max(8, top) }, name, addr, pos2D: null, loading: true });
        // Geocode bất đồng bộ
        const pos2D = await geocodeRestaurant(name, addr);
        setPopup(p => p ? { ...p, pos2D, loading: false } : null);
      }, 250);
    };

    const hide = (e) => {
      if (e.target.closest('.rest-hover')) return; // đang rời khỏi span này
      clearTimeout(hoverTimerRef.current);
      setPopup(null);
    };

    el.addEventListener('mouseover', show);
    el.addEventListener('mouseout', hide);
    return () => {
      el.removeEventListener('mouseover', show);
      el.removeEventListener('mouseout', hide);
      clearTimeout(hoverTimerRef.current);
    };
  }, [isBot, msg.content]);

  return (
    <div className={`flex items-end gap-3 mb-5 group ${isBot ? '' : 'flex-row-reverse'}`}>
      {popup && ReactDOM.createPortal(
        <div style={{
          position: 'fixed',
          left: popup.pos.left,
          top: popup.pos.top,
          zIndex: 999999,
          pointerEvents: 'none',
        }}>
          {popup.loading ? (
            <div style={{
              width: 270, background: 'white', borderRadius: 14,
              boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
              border: '1.5px solid #e5e7eb', padding: '14px 16px',
              display: 'flex', alignItems: 'center', gap: 10,
            }}>
              <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2.5px solid #10b981', borderTopColor: 'transparent', animation: 'spin 0.8s linear infinite', flexShrink: 0 }} />
              <div>
                <p style={{ margin: 0, fontSize: 12, fontWeight: 700, color: '#065f46' }}>{popup.name}</p>
                <p style={{ margin: '2px 0 0', fontSize: 11, color: '#9ca3af' }}>Đang tìm vị trí...</p>
              </div>
            </div>
          ) : popup.pos2D ? (
            <MiniMapPopup
              restaurantPosition={popup.pos2D}
              restaurantName={popup.name}
              userLocation={userLocation}
            />
          ) : (
            <div style={{
              width: 270, background: 'white', borderRadius: 14,
              boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
              border: '1.5px solid #e5e7eb', padding: '14px 16px',
            }}>
              <p style={{ margin: 0, fontSize: 12, fontWeight: 700, color: '#374151' }}>{popup.name}</p>
              <p style={{ margin: '4px 0 0', fontSize: 11, color: '#ef4444' }}>⚠️ Không tìm được vị trí trên bản đồ</p>
              <p style={{ margin: '2px 0 0', fontSize: 10, color: '#9ca3af' }}>{popup.addr}</p>
            </div>
          )}
        </div>,
        document.body
      )}
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm
        ${isBot ? 'bg-gradient-to-br from-orange-400 to-red-500' : 'bg-gradient-to-br from-blue-500 to-indigo-600'}`}>
        {isBot ? <ChefHat size={15} className="text-white" /> : <User size={15} className="text-white" />}
      </div>
      <div className="max-w-[76%]">
        {isBot && msg.mode && (
          <span className="inline-block text-[10px] text-orange-600 bg-orange-50 border border-orange-200 px-2 py-0.5 rounded-full mb-1.5 font-medium">
            {msg.mode}
          </span>
        )}
        <div
          ref={msgBodyRef}
          className={`px-4 py-3 text-sm leading-relaxed shadow-sm
            ${isBot
              ? 'bg-white rounded-2xl rounded-bl-none border border-gray-100 text-gray-700'
              : 'bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl rounded-br-none text-white'}`}
        >
          <div dangerouslySetInnerHTML={{ __html: fmt(msg.content) }} />
        </div>
        <div className="flex items-center gap-1.5 mt-1.5 px-1">
          <span className="text-[10px] text-gray-400">
            {new Date(msg.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
          </span>
          {isBot && (
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button onClick={() => { navigator.clipboard.writeText(msg.content); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
                className="p-1 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                {copied ? <Check size={11} className="text-green-500" /> : <Copy size={11} />}
              </button>
              <button onClick={() => onFeedback(msg.id, 'like')}
                className={`p-1 rounded-md hover:bg-gray-100 ${msg.feedback === 'like' ? 'text-green-500' : 'text-gray-400 hover:text-green-500'}`}>
                <ThumbsUp size={11} />
              </button>
              <button onClick={() => onFeedback(msg.id, 'dislike')}
                className={`p-1 rounded-md hover:bg-gray-100 ${msg.feedback === 'dislike' ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}>
                <ThumbsDown size={11} />
              </button>
            </div>
          )}
        </div>
        {/* Nearby restaurants – hiện sau tin nhắn AI Decision */}
        {isBot && msg.nearbyRestaurants && (
          <NearbyRestaurantsCard
            restaurants={msg.nearbyRestaurants}
            foodName={msg.foodKeyword}
            onViewMap={msg.onViewMap}
            userLocation={msg.userLocation}
          />
        )}
      </div>
    </div>
  );
};

// ── Modal Popup ────────────────────────────────────────────────
const ModeModal = ({ modeId, color, onClose, onSend }) => {
  const info = POPUP_TITLES[modeId];
  if (!info) return null;

  const handleSend = (text) => {
    onSend(text);
    onClose();
  };

  // Close on backdrop click
  const handleBackdrop = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)' }}
      onClick={handleBackdrop}>
      <div
        className="w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden"
        style={{ animation: 'modalIn .25s cubic-bezier(.34,1.56,.64,1)' }}>
        {/* Modal header */}
        <div className="px-5 py-4 flex items-center justify-between"
          style={{ background: `linear-gradient(135deg, ${color}22, ${color}11)`, borderBottom: `2px solid ${color}33` }}>
          <div>
            <h3 className="font-bold text-gray-800 text-base flex items-center gap-2">
              <span>{info.emoji}</span> {info.label}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">{info.sub}</p>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all">
            <X size={16} />
          </button>
        </div>
        {/* Panel content */}
        <div className="max-h-[70vh] overflow-y-auto">
          {modeId === 'combo' && <ComboPanel onSend={handleSend} />}
          {modeId === 'discovery' && <DiscoveryPanel onSend={handleSend} />}
          {modeId === 'compare' && <ComparePanel onSend={handleSend} />}
          {modeId === 'mood' && <MoodPanel onSend={handleSend} />}
          {modeId === 'diary' && <DiaryPanel onSend={handleSend} />}
        </div>
      </div>
    </div>
  );
};

// ── Main Page ──────────────────────────────────────────────────
const ChatPage = () => {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [openModal, setOpenModal] = useState(null);
  const [userLocation, setUserLocation] = useState(null);

  // Welcome message chuẩn
  const welcomeMsg = useMemo(() => ({
    id: 'welcome',
    role: 'model',
    timestamp: new Date().toISOString(),
    content: `Xin chào${user?.full_name ? ' **' + user.full_name + '**' : ''}! Tôi là **Food AI Assistant**.\n\nHỏi trực tiếp bên dưới, hoặc chọn một chế độ từ sidebar để nhận gợi ý chi tiết hơn! 😊`,
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [user?.id]);

  const [messages, setMessages] = useState(() => [welcomeMsg]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const msgsRef = useRef(null);
  const inputRef = useRef(null);
  const chatHistory = useRef([]);
  const hasRestoredRef = useRef(false); // tránh restore 2 lần

  // ── Khôi phục chat từ localStorage khi user đã xác định ────────────────
  useEffect(() => {
    if (authLoading) return; // chờ auth load xong
    if (hasRestoredRef.current) return;
    hasRestoredRef.current = true;

    const uid = user?.id ?? 'guest';
    const saved = loadMessages(uid);
    if (saved && saved.length > 0) {
      // Gắn lại onViewMap cho các tin có nearbyRestaurants (function không serialize được)
      const restored = saved.map(m =>
        m.nearbyRestaurants && m.foodKeyword
          ? { ...m, onViewMap: () => navigate(`/recommendations?tab=nearby${m.foodKeyword ? '&q=' + encodeURIComponent(m.foodKeyword) : ''}`) }
          : m
      );
      setMessages(restored);
      chatHistory.current = loadHistory(uid);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, user?.id]);

  // ── Lưu messages vào localStorage mỗi khi thay đổi ─────────────────────
  useEffect(() => {
    if (authLoading) return;
    const uid = user?.id ?? 'guest';
    saveMessages(uid, messages);
  }, [messages, user?.id, authLoading]);

  // Lấy vị trí: ưu tiên sessionStorage (chia sẻ từ tab Gần đây), fallback geolocation
  useEffect(() => {
    const syncLocation = () => {
      try {
        const cached = sessionStorage.getItem('vfa_user_location');
        if (cached) { setUserLocation(JSON.parse(cached)); return; }
      } catch { }
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            setUserLocation(loc);
            try { sessionStorage.setItem('vfa_user_location', JSON.stringify(loc)); } catch { }
          },
          () => { }
        );
      }
    };
    syncLocation();
    // Đồng bộ lại khi cửa sổ focus
    window.addEventListener('focus', syncLocation);
    return () => window.removeEventListener('focus', syncLocation);
  }, []);

  useEffect(() => {
    if (msgsRef.current)
      msgsRef.current.scrollTo({ top: msgsRef.current.scrollHeight, behavior: messages.length <= 1 ? 'auto' : 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => { window.scrollTo(0, 0); inputRef.current?.focus(); }, []);

  const onFeedback = useCallback((id, type) => {
    setMessages(p => p.map(m => m.id === id ? { ...m, feedback: type } : m));
  }, []);

  const sendMessage = async (text) => {
    const trimmed = (text || inputValue).trim();
    if (!trimmed || isTyping) return;
    const userMsg = { id: `u-${Date.now()}`, role: 'user', content: trimmed, timestamp: new Date().toISOString() };
    setMessages(p => [...p, userMsg]);
    setInputValue('');
    setIsTyping(true);
    // Refresh vị trí từ sessionStorage trước khi gửi (sync với tab Map)
    let currentLocation = userLocation;
    try {
      const cached = sessionStorage.getItem('vfa_user_location');
      if (cached) { currentLocation = JSON.parse(cached); setUserLocation(currentLocation); }
    } catch { }

    try {
      const res = await chatAPI.send({
        message: trimmed,
        history: chatHistory.current,
        user_context: {
          ...(user ? { name: user.full_name } : {}),
          ...(currentLocation
            ? { location: `${currentLocation.lat.toFixed(5)},${currentLocation.lng.toFixed(5)} (khu vực gần đây)` }
            : {}),
        } || null,
      });
      const msgId = `b-${Date.now()}`;
      const isAIDecision = res.data.mode_detected?.includes('AI Decision');
      const isMapExplorer = res.data.mode_detected?.includes('Food Map Explorer');
      const botMsg = {
        id: msgId,
        role: 'model',
        content: res.data.reply,
        mode: res.data.mode_detected,
        timestamp: new Date().toISOString(),
      };
      setMessages(p => [...p, botMsg]);
      chatHistory.current = [...chatHistory.current,
        { role: 'user', content: trimmed },
        { role: 'model', content: res.data.reply },
      ];
      // L\u01b0u history (Gemini context) \u0111\u1ec3 gi\u1eef multi-turn khi chuy\u1ec3n tab
      saveHistory(user?.id ?? 'guest', chatHistory.current);

      // Tìm quán gần đây:
      // - AI Decision + câu hỏi có đề cập quán/gần đây → dùng keyword từ câu hỏi
      // - AI Decision bình thường → dùng keyword từ câu trả lời AI
      // - Food Map Explorer → dùng keyword từ câu hỏi
      const shouldSearch =
        (isAIDecision || isMapExplorer) && currentLocation;

      if (shouldSearch) {
        let keyword;
        if (isMapExplorer) {
          keyword = extractMapKeyword(trimmed);
        } else if (isAIDecision && isNearbyQuery(trimmed)) {
          // User hỏi trực tiếp về quán → extract từ câu hỏi
          keyword = extractMapKeyword(trimmed) || extractFoodKeyword(res.data.reply);
        } else {
          // AI gợi ý món → extract từ câu trả lời
          keyword = extractFoodKeyword(res.data.reply);
        }

        const locSnap = currentLocation;
        fetchNearbyRestaurants(locSnap.lat, locSnap.lng, keyword || '')
          .then(elements => {
            const restaurants = parseRestaurants(elements);
            if (restaurants.length > 0) {
              setMessages(p => p.map(m =>
                m.id === msgId
                  ? {
                    ...m,
                    nearbyRestaurants: restaurants,
                    foodKeyword: keyword,
                    userLocation: locSnap,
                    onViewMap: () => navigate(
                      `/recommendations?tab=nearby${keyword ? '&q=' + encodeURIComponent(keyword) : ''}`
                    ),
                  }
                  : m
              ));
            }
          })
          .catch(() => { });
      }
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail || '';
      let txt = '❌ Có lỗi xảy ra. Vui lòng thử lại!';
      if (status === 503 || detail.includes('API key')) txt = '⚙️ AI chưa được cấu hình.';
      else if (status === 429) txt = '⏳ Quá nhiều yêu cầu, chờ vài giây rồi thử lại!';
      else if (!err.response) txt = '🌐 Không kết nối được backend.';
      setMessages(p => [...p, { id: `e-${Date.now()}`, role: 'model', content: txt, timestamp: new Date().toISOString() }]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    if (!window.confirm('Xóa toàn bộ lịch sử chat? Thao tác này không thể hoàn tác.')) return;
    const uid = user?.id ?? 'guest';
    chatHistory.current = [];
    saveHistory(uid, []);
    const newWelcome = { id: `w-${Date.now()}`, role: 'model', content: 'Cuộc trò chuyện mới! Tôi có thể giúp gì? 😊', timestamp: new Date().toISOString() };
    setMessages([newWelcome]);
    saveMessages(uid, [newWelcome]);
  };

  const activeModalMode = MODES.find(m => m.id === openModal);

  return (
    <div className="min-h-screen bg-gray-50">
      <style>{`
        @keyframes db{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-7px)}}
        @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        @keyframes modalIn{from{opacity:0;transform:translateY(24px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes spin{to{transform:rotate(360deg)}}
        .msg-in{animation:fadeUp .22s ease-out}
      `}</style>

      {/* Modal */}
      {openModal && activeModalMode && (
        <ModeModal
          modeId={openModal}
          color={activeModalMode.color}
          onClose={() => setOpenModal(null)}
          onSend={sendMessage}
        />
      )}

      <div className="max-w-6xl mx-auto px-4 py-6 h-[calc(100vh-80px)] flex gap-4">

        {/* ── Sidebar ───────────────────────────── */}
        <aside className="hidden lg:flex flex-col gap-3 w-56 flex-shrink-0">
          {/* Brand */}
          <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl p-4 text-white shadow-lg shadow-orange-200/50">
            <div className="flex items-center gap-2.5 mb-2">
              <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
                <ChefHat size={18} className="text-white" />
              </div>
              <div>
                <p className="font-bold text-sm">Food AI</p>
                <p className="text-orange-100 text-[11px]">Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 bg-white/15 rounded-lg px-2 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-300 animate-pulse" />
              <span className="text-[11px] text-white/90">Đang hoạt động</span>
            </div>
          </div>

          {/* Mode nav */}
          <div className="bg-white rounded-2xl p-3 shadow-sm border border-gray-100">
            <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2 px-1">Chế độ</p>
            <nav className="space-y-0.5">
              {MODES.map(m => (
                <button key={m.id}
                  onClick={() => m.isPopup ? setOpenModal(m.id) : null}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left transition-all hover:bg-gray-50 group relative"
                  title={m.isPopup ? 'Mở form nhập liệu' : ''}>
                  <span className="text-base">{m.emoji}</span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-gray-700 leading-tight">{m.label}</p>
                    <p className="text-[10px] text-gray-400 leading-tight truncate">{m.desc}</p>
                  </div>
                  {m.isPopup && (
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-md text-white opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      style={{ backgroundColor: m.color }}>
                      Mở
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Mode shortcuts (popup buttons) */}
          <div className="bg-white rounded-2xl p-3 shadow-sm border border-gray-100">
            <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2 px-1">Truy cập nhanh</p>
            <div className="grid grid-cols-2 gap-1.5">
              {MODES.filter(m => m.isPopup).map(m => (
                <button key={m.id} onClick={() => setOpenModal(m.id)}
                  className="flex flex-col items-center gap-1 p-2.5 rounded-xl border-2 border-transparent hover:border-opacity-50 transition-all text-center"
                  style={{ backgroundColor: m.color + '15' }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = m.color + '60'}
                  onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}>
                  <span className="text-xl">{m.emoji}</span>
                  <span className="text-[10px] font-semibold leading-tight" style={{ color: m.color }}>{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white rounded-2xl p-3 shadow-sm border border-gray-100">
            <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2 px-1">Phiên này</p>
            <div className="px-1 space-y-1.5">
              <div className="flex justify-between">
                <span className="text-xs text-gray-500">Tin nhắn</span>
                <span className="text-xs font-bold text-gray-700">{messages.length}</span>
              </div>
            </div>
          </div>
        </aside>

        {/* ── Main Chat ─────────────────────────── */}
        <div className="flex-1 flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

          {/* Header */}
          <div className="px-5 py-3.5 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-3">
              <span className="font-semibold text-gray-800 text-sm">Food AI Assistant</span>
              <span className="text-xs text-gray-400 hidden sm:block">Powered by Google Gemini</span>
              {/* Badge lưu chat */}
              {messages.length > 1 && user && (
                <span className="hidden sm:flex items-center gap-1 text-[10px] text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">
                  <Save size={9} /> Đã lưu · {messages.length - 1} tin nhắn
                </span>
              )}
            </div>
            {/* Mobile mode buttons */}
            <div className="flex lg:hidden gap-1 overflow-x-auto" style={{ scrollbarWidth: 'none' }}>
              {MODES.filter(m => m.isPopup).map(m => (
                <button key={m.id} onClick={() => setOpenModal(m.id)}
                  className="flex-shrink-0 px-2.5 py-1 rounded-lg text-xs font-semibold text-white transition-all hover:opacity-90"
                  style={{ backgroundColor: m.color }}>
                  {m.emoji}
                </button>
              ))}
            </div>
            <button onClick={clearChat}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-red-500 hover:bg-red-50 px-2.5 py-1.5 rounded-lg transition-all flex-shrink-0 ml-2">
              <Trash2 size={13} /> <span className="hidden sm:inline">Xóa</span>
            </button>
          </div>

          {/* Messages */}
          <div ref={msgsRef} className="flex-1 overflow-y-auto px-5 py-5 min-h-0">
            {messages.map(msg => (
              <div key={msg.id} className="msg-in">
                <MessageBubble msg={msg} onFeedback={onFeedback} userLocation={userLocation} />
              </div>
            ))}
            {isTyping && <TypingIndicator />}
          </div>

          {/* Mode shortcut chips — above input */}
          <div className="px-5 pt-3 pb-1 flex-shrink-0 flex gap-2 flex-wrap">
            {MODES.filter(m => m.isPopup).map(m => (
              <button key={m.id} onClick={() => setOpenModal(m.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border-2 transition-all hover:scale-105"
                style={{ borderColor: m.color + '60', color: m.color, backgroundColor: m.color + '12' }}>
                {m.emoji} {m.label}
              </button>
            ))}
          </div>

          {/* Input area (always AI Decision style) */}
          <div className="px-5 pb-4 pt-2 flex-shrink-0">
            {messages.length <= 2 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {AI_PROMPTS.map((p, i) => (
                  <button key={i} onClick={() => sendMessage(p.text)}
                    className="px-3 py-1.5 text-xs font-medium bg-orange-50 hover:bg-orange-100 text-orange-700 border border-orange-200 hover:border-orange-400 rounded-full transition-all">
                    {p.label}
                  </button>
                ))}
              </div>
            )}
            <div className="flex items-end gap-2">
              <div className="flex-1 bg-gray-50 rounded-xl border border-gray-200 focus-within:border-orange-400 focus-within:ring-2 focus-within:ring-orange-100 transition-all px-4 py-3">
                <textarea ref={inputRef} id="chat-page-input" value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Hỏi Food AI bất cứ điều gì... hoặc chọn chế độ bên trên"
                  className="w-full bg-transparent text-sm text-gray-700 resize-none outline-none max-h-28 min-h-[36px] placeholder-gray-400"
                  rows={1} disabled={isTyping} />
              </div>
              <button id="chat-page-send" onClick={() => sendMessage()} disabled={!inputValue.trim() || isTyping}
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all
                  ${inputValue.trim() && !isTyping
                    ? 'bg-gradient-to-br from-orange-500 to-red-500 text-white hover:shadow-md hover:shadow-orange-200 hover:scale-105'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}>
                {isTyping ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </div>
            <p className="text-center text-[10px] text-gray-400 mt-2">Enter gửi · Shift+Enter xuống dòng</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
