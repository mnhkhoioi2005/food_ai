import { useState, useRef, useEffect, useCallback } from 'react';
import {
  MessageCircle, X, Send, Bot, User, Minimize2, Maximize2,
  Trash2, ChevronDown, Sparkles, Loader2, Volume2, Copy, Check,
  RefreshCw, ThumbsUp, ThumbsDown, ChefHat
} from 'lucide-react';
import { chatAPI } from '../services/api';
import { fetchNearbyRestaurants, parseRestaurants } from '../utils/overpass';
import NearbyRestaurantsCard from './chat/NearbyRestaurantsCard';

// ==================== Helpers ====================
function extractFoodKeyword(text) {
  const best = text.match(/Đề xuất tốt nhất[^:]*:\s*\*?\*?([^—\n*~]+)/i);
  if (best) return best[1].trim();
  const main = text.match(/Món chính[^:]*:\s*([^~\n]+)/i);
  if (main) return main[1].trim().split('~')[0].trim();
  const foods = ['phở bò', 'phở gà', 'phở', 'bún bò', 'bún riêu', 'bún', 'cơm tấm', 'cơm gà', 'cơm', 'bánh mì', 'bánh cuốn', 'bánh xèo', 'lẩu', 'hủ tiếu', 'mì quảng', 'mì', 'xôi', 'gỏi cuốn', 'chả giò', 'nem', 'chè'];
  const lower = text.toLowerCase();
  for (const f of foods) if (lower.includes(f)) return f;
  return null;
}

// Trích xuất từ khóa món ăn từ câu hỏi tìm quán của user
function extractMapKeyword(text) {
  // Khớp pattern: "quán phở", "tìm quán bún bò", "các quán cơm tấm", v.v.
  const m = text.match(/(?:quán|tìm quán|các quán|nhà hàng|tiệm)\s+([^\s,?.!]{2,}(?:\s+[^\s,?.!]{2,})?)/i);
  if (m) return m[1].trim();
  // Fallback: dùng lại extractFoodKeyword
  return extractFoodKeyword(text);
}

// ==================== Typing Indicator ====================
const TypingIndicator = () => (
  <div className="flex items-end gap-2 mb-4 animate-fadeIn">
    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center flex-shrink-0 shadow-md">
      <ChefHat size={16} className="text-white" />
    </div>
    <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-sm border border-orange-100">
      <div className="flex gap-1 items-center h-5">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-2 h-2 rounded-full bg-orange-400"
            style={{ animation: `bounce 1.4s ease-in-out ${i * 0.2}s infinite` }}
          />
        ))}
      </div>
    </div>
  </div>
);

// ==================== Message Bubble ====================
const MessageBubble = ({ msg, onFeedback }) => {
  const [copied, setCopied] = useState(false);
  const isBot = msg.role === 'model';

  const handleCopy = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Render markdown-like formatting
  const formatContent = (text) => {
    // Bold **text**
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Line breaks
    text = text.replace(/\n/g, '<br/>');
    // Headers ##
    text = text.replace(/^##\s(.+)$/gm, '<h3 class="font-bold text-orange-700 text-sm mt-2 mb-1">$1</h3>');
    return text;
  };

  return (
    <div className={`flex items-end gap-2 mb-4 animate-fadeIn ${isBot ? '' : 'flex-row-reverse'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-md
        ${isBot
          ? 'bg-gradient-to-br from-orange-400 to-red-500'
          : 'bg-gradient-to-br from-blue-400 to-indigo-500'}`}>
        {isBot
          ? <ChefHat size={16} className="text-white" />
          : <User size={16} className="text-white" />}
      </div>

      {/* Bubble */}
      <div className={`group max-w-[80%] ${isBot ? '' : ''}`}>
        {/* Mode badge */}
        {isBot && msg.mode && (
          <div className="flex items-center gap-1 mb-1">
            <span className="text-xs text-orange-500 font-medium bg-orange-50 px-2 py-0.5 rounded-full border border-orange-100">
              {msg.mode}
            </span>
          </div>
        )}

        <div className={`relative px-4 py-3 shadow-sm text-sm leading-relaxed
          ${isBot
            ? 'bg-white rounded-2xl rounded-bl-none border border-orange-100 text-gray-700'
            : 'bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl rounded-br-none text-white'}`}>
          <div
            dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
            className="chat-content"
          />
        </div>

        {/* Actions for bot messages */}
        {isBot && (
          <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
              title="Sao chép"
            >
              {copied ? <Check size={13} className="text-green-500" /> : <Copy size={13} />}
            </button>
            <button
              onClick={() => onFeedback(msg.id, 'like')}
              className={`p-1 hover:bg-gray-100 rounded-lg transition-colors ${msg.feedback === 'like' ? 'text-green-500' : 'text-gray-400 hover:text-green-500'}`}
              title="Hợp lý"
            >
              <ThumbsUp size={13} />
            </button>
            <button
              onClick={() => onFeedback(msg.id, 'dislike')}
              className={`p-1 hover:bg-gray-100 rounded-lg transition-colors ${msg.feedback === 'dislike' ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
              title="Không hợp"
            >
              <ThumbsDown size={13} />
            </button>
          </div>
        )}

        <span className="text-[10px] text-gray-400 mt-0.5 block px-1">
          {new Date(msg.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
        </span>
        {/* Nearby restaurants card */}
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

// ==================== Quick Prompts ====================
const QUICK_PROMPTS = [
  { emoji: '🤔', text: 'Ăn gì hôm nay?', label: 'Ăn gì?' },
  { emoji: '💰', text: 'Gợi ý món ngon dưới 50k', label: 'Dưới 50k' },
  { emoji: '🥗', text: 'Tôi muốn ăn healthy, ít calo', label: 'Healthy' },
  { emoji: '🍱', text: 'Xây combo bữa trưa đủ chất', label: 'Combo bữa trưa' },
  { emoji: '😴', text: 'Tôi đang mệt và muốn ăn gì đó nhẹ', label: 'Nhẹ bụng' },
  { emoji: '👥', text: 'Đi ăn nhóm 5 người, ngân sách 500k', label: 'Nhóm 5 người' },
];

// ==================== Main Chat Widget ====================
const AIChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'model',
      content: '🍜 Chào bạn! Tôi là **Food AI Assistant** — trợ lý ẩm thực thông minh của bạn!\n\nTôi có thể giúp bạn:\n- 🤖 Quyết định **ăn gì hôm nay**\n- 🍱 Tạo **combo bữa ăn** hoàn chỉnh\n- 💰 Gợi ý **theo ngân sách**\n- 🎭 Gợi ý theo **tâm trạng**\n- 📔 Theo dõi **nhật ký ăn uống**\n\nBạn đang đói không? Hãy nói cho tôi biết bạn cần gì! 😊',
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatHistory = useRef([]);

  // Lấy vị trí: ưu tiên sessionStorage (chia sẻ từ RecommendationPage)
  useEffect(() => {
    const syncLocation = () => {
      try {
        const cached = sessionStorage.getItem('vfa_user_location');
        if (cached) {
          setUserLocation(JSON.parse(cached));
          return;
        }
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
    // Đồng bộ lại khi cửa sổ focus (người dùng có thể đã vào trang Gần đây)
    window.addEventListener('focus', syncLocation);
    return () => window.removeEventListener('focus', syncLocation);
  }, []);

  const scrollToBottom = useCallback((behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  }, []);

  // Scroll xuống ngay khi mở widget (instant, không animation)
  useEffect(() => {
    if (isOpen) {
      setHasNewMessage(false);
      // Dùng setTimeout để đảm bảo DOM đã render trước khi scroll
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'instant' });
        inputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Scroll smooth khi có tin nhắn mới
  useEffect(() => {
    if (isOpen) {
      scrollToBottom('smooth');
    }
  }, [messages, isTyping, scrollToBottom, isOpen]);

  const handleFeedback = useCallback((msgId, type) => {
    setMessages(prev => prev.map(m =>
      m.id === msgId ? { ...m, feedback: type } : m
    ));
  }, []);

  const sendMessage = async (text) => {
    const trimmed = (text || inputValue).trim();
    if (!trimmed || isTyping) return;

    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      const res = await chatAPI.send({
        message: trimmed,
        history: chatHistory.current,
        user_context: userLocation
          ? { location: `${userLocation.lat.toFixed(5)},${userLocation.lng.toFixed(5)} (TP.HCM khu vực gần đây)` }
          : undefined,
      });

      const msgId = `b-${Date.now()}`;
      const isAIDecision = res.data.mode_detected?.includes('AI Decision');
      const botMsg = {
        id: msgId,
        role: 'model',
        content: res.data.reply,
        mode: res.data.mode_detected,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, botMsg]);

      // Cập nhật lịch sử cho multi-turn
      chatHistory.current = [
        ...chatHistory.current,
        { role: 'user', content: trimmed },
        { role: 'model', content: res.data.reply },
      ];

      if (!isOpen) setHasNewMessage(true);

      // Tìm quán gần đây sau AI Decision hoặc Food Map Explorer (không chặn UI)
      const isMapExplorer = res.data.mode_detected?.includes('Food Map Explorer');
      if ((isAIDecision || isMapExplorer) && userLocation) {
        // Với Map Explorer: dùng trực tiếp từ khóa trong tin nhắn user
        const keyword = isMapExplorer
          ? extractMapKeyword(trimmed)
          : extractFoodKeyword(res.data.reply);
        const locSnap = userLocation;
        fetchNearbyRestaurants(locSnap.lat, locSnap.lng, keyword || '')
          .then(elements => {
            const restaurants = parseRestaurants(elements);
            if (restaurants.length > 0) {
              setMessages(prev => prev.map(m =>
                m.id === msgId
                  ? {
                    ...m,
                    nearbyRestaurants: restaurants,
                    foodKeyword: keyword,
                    userLocation: locSnap,
                    onViewMap: () => {
                      window.location.href = `/recommendations?tab=nearby${keyword ? '&q=' + encodeURIComponent(keyword) : ''}`;
                    },
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
      let errContent = '❌ Xin lỗi, có lỗi xảy ra khi kết nối với AI. Vui lòng thử lại sau!';
      if (status === 503 || detail.includes('API key')) {
        errContent = '⚙️ AI chưa được cấu hình. Vui lòng liên hệ quản trị viên!';
      } else if (status === 429) {
        errContent = '⏳ Bạn đang gửi quá nhiều yêu cầu. Vui lòng chờ vài giây rồi thử lại!';
      } else if (status === 401) {
        errContent = '🔑 Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!';
      } else if (!err.response) {
        errContent = '🌐 Không thể kết nối đến máy chủ. Vui lòng kiểm tra backend đã chạy chưa!';
      }
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'model',
        content: errContent,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    chatHistory.current = [];
    setMessages([{
      id: 'welcome-new',
      role: 'model',
      content: '🔄 Cuộc trò chuyện mới bắt đầu! Tôi có thể giúp gì cho bạn? 😊',
      timestamp: new Date().toISOString(),
    }]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Bounce animation keyframes */}
      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-8px); }
        }
        @keyframes wiggle {
          0%, 100% { transform: rotate(-3deg); }
          50% { transform: rotate(3deg); }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .chat-widget-enter {
          animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .chat-content strong { font-weight: 700; }
        .chat-content em { font-style: italic; }
      `}</style>

      {/* Floating Button */}
      {!isOpen && (
        <button
          id="ai-chat-fab"
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-16 h-16 rounded-full shadow-2xl 
            bg-gradient-to-br from-orange-400 via-orange-500 to-red-500
            flex items-center justify-center text-white
            hover:scale-110 active:scale-95 transition-all duration-300
            hover:shadow-orange-300/60 hover:shadow-2xl"
          title="Mở Food AI Chat"
        >
          <div className="relative">
            <ChefHat size={26} />
            {hasNewMessage && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white" />
            )}
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          className={`fixed z-50 bottom-6 right-6 
            bg-white rounded-3xl shadow-2xl border border-orange-100
            flex flex-col overflow-hidden chat-widget-enter
            transition-all duration-300
            ${isExpanded
              ? 'w-[420px] h-[700px]'
              : 'w-[370px] h-[580px]'}`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 via-orange-400 to-red-500 px-4 py-3 flex items-center gap-3 flex-shrink-0">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <ChefHat size={22} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-white text-sm">Food AI Assistant</p>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-300 animate-pulse" />
                <p className="text-orange-100 text-xs">Đang hoạt động • Gemini AI</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={clearChat}
                className="p-1.5 text-white/70 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                title="Xóa lịch sử"
              >
                <Trash2 size={15} />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 text-white/70 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                title={isExpanded ? 'Thu nhỏ' : 'Phóng to'}
              >
                {isExpanded ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-white/70 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                title="Đóng"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-0 bg-gradient-to-b from-orange-50/50 to-white">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                msg={msg}
                onFeedback={handleFeedback}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          {messages.length <= 2 && !isTyping && (
            <div className="px-3 pb-2 flex-shrink-0">
              <p className="text-xs text-gray-400 mb-2 px-1">💡 Gợi ý nhanh:</p>
              <div className="flex gap-1.5 flex-wrap">
                {QUICK_PROMPTS.slice(0, 4).map((p, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(p.text)}
                    className="px-3 py-1.5 text-xs bg-orange-50 hover:bg-orange-100 text-orange-700 
                      border border-orange-200 rounded-full transition-all hover:border-orange-400
                      flex items-center gap-1 font-medium"
                  >
                    {p.emoji} {p.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="px-3 pb-3 pt-2 border-t border-gray-100 flex-shrink-0 bg-white">
            <div className="flex items-end gap-2 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-orange-400 focus-within:ring-2 focus-within:ring-orange-100 transition-all px-3 py-2">
              <textarea
                ref={inputRef}
                id="chat-input"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Hỏi AI về món ăn... (Enter để gửi)"
                className="flex-1 bg-transparent text-sm text-gray-700 resize-none outline-none max-h-24 min-h-[36px] placeholder-gray-400"
                rows={1}
                disabled={isTyping}
              />
              <button
                id="chat-send-btn"
                onClick={() => sendMessage()}
                disabled={!inputValue.trim() || isTyping}
                className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all
                  ${inputValue.trim() && !isTyping
                    ? 'bg-gradient-to-br from-orange-500 to-red-500 text-white hover:shadow-lg hover:scale-105'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              >
                {isTyping
                  ? <Loader2 size={16} className="animate-spin" />
                  : <Send size={16} />}
              </button>
            </div>
            <p className="text-center text-[10px] text-gray-400 mt-1.5">
              Powered by Google Gemini • Shift+Enter xuống dòng
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export default AIChatWidget;
