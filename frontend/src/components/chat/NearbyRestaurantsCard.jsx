import { useState, useRef } from 'react';
import ReactDOM from 'react-dom';
import { MapPin, ExternalLink, Map, Navigation } from 'lucide-react';
import MiniMapPopup from '../MiniMapPopup';

/**
 * NearbyRestaurantsCard – hiện sau tin nhắn AI Decision.
 * Props:
 *   restaurants   – mảng quán ăn từ Overpass
 *   foodName      – tên món ăn (hiển thị label)
 *   onViewMap     – callback khi bấm "Xem bản đồ"
 *   userLocation  – { lat, lng } vị trí người dùng
 */
const NearbyRestaurantsCard = ({ restaurants, foodName, onViewMap, userLocation }) => {
  const [hoveredId, setHoveredId] = useState(null);
  const [popupPos, setPopupPos] = useState({ left: 0, top: 0 });
  const [showAll, setShowAll] = useState(false);
  const timerRef = useRef(null);

  if (!restaurants?.length) return null;

  const displayList = showAll ? restaurants : restaurants.slice(0, 5);
  const hoveredRestaurant = restaurants.find(r => r.id === hoveredId);

  // Tính khoảng cách (Haversine, km hoặc m)
  const distKm = (pos) => {
    if (!userLocation || !pos) return null;
    const R = 6371;
    const dLat = (pos[0] - userLocation.lat) * Math.PI / 180;
    const dLon = (pos[1] - userLocation.lng) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(userLocation.lat * Math.PI / 180) *
      Math.cos(pos[0] * Math.PI / 180) *
      Math.sin(dLon / 2) ** 2;
    const d = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return d < 1 ? Math.round(d * 1000) + ' m' : d.toFixed(1) + ' km';
  };

  const handleMouseEnter = (e, id) => {
    // *** FIX: lưu element reference TRƯỚC khi vào setTimeout ***
    // e.currentTarget bị React xóa sau khi event handler kết thúc
    const el = e.currentTarget;
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      const rect = el.getBoundingClientRect();
      const popupW = 270;
      const popupH = 230;
      const vw = window.innerWidth;
      const vh = window.innerHeight;

      // ưu tiên bên phải, nếu tràn → bên trái
      let left = rect.right + 12;
      if (left + popupW > vw - 12) left = rect.left - popupW - 12;

      // Tránh cắt ở đáy
      let top = rect.top;
      if (top + popupH > vh - 12) top = Math.max(8, vh - popupH - 12);

      setPopupPos({ left: Math.max(8, left), top: Math.max(8, top) });
      setHoveredId(id);
    }, 200);
  };

  const handleMouseLeave = () => {
    clearTimeout(timerRef.current);
    setHoveredId(null);
  };

  return (
    <div className="mt-2.5 border border-emerald-100 bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-3">

      {/* Header */}
      <div className="flex items-center justify-between mb-2.5">
        <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1.5">
          <MapPin size={12} className="text-emerald-500" />
          {restaurants.length} quán gần bạn{foodName ? ` · 🍜 ${foodName}` : ''}
        </span>
        <button
          onClick={onViewMap}
          className="text-[11px] text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 hover:underline"
        >
          Xem bản đồ <ExternalLink size={9} />
        </button>
      </div>

      {/* Danh sách quán */}
      <div className="space-y-1.5">
        {displayList.map(r => {
          const dist = distKm(r.position);
          const isHovered = r.id === hoveredId;
          return (
            <a
              key={r.id}
              href={`https://www.google.com/maps/search/?api=1&query=${r.position[0]},${r.position[1]}`}
              target="_blank"
              rel="noopener noreferrer"
              onMouseEnter={(e) => handleMouseEnter(e, r.id)}
              onMouseLeave={handleMouseLeave}
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-all group border ${
                isHovered
                  ? 'bg-white border-emerald-300 shadow-md'
                  : 'bg-white/80 hover:bg-white border-transparent hover:border-emerald-200 hover:shadow-sm'
              }`}
            >
              <div className="min-w-0 flex-1">
                <p className={`text-xs font-medium truncate ${isHovered ? 'text-emerald-700' : 'text-gray-800 group-hover:text-emerald-700'}`}>
                  {r.name}
                </p>
                {r.address && <p className="text-[10px] text-gray-400 truncate mt-0.5">{r.address}</p>}
              </div>
              <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                {dist && (
                  <span className="text-[9px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                    <Navigation size={7} /> {dist}
                  </span>
                )}
                {r.isOpen === true && (
                  <span className="text-[9px] bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full font-medium">● Mở</span>
                )}
                {r.isOpen === false && (
                  <span className="text-[9px] bg-red-50 text-red-400 px-1.5 py-0.5 rounded-full font-medium">Đóng</span>
                )}
                <Map
                  size={11}
                  className={`transition-colors ${isHovered ? 'text-emerald-500' : 'text-gray-300 group-hover:text-emerald-500'}`}
                />
              </div>
            </a>
          );
        })}

        {restaurants.length > 5 && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="w-full text-center text-[11px] text-emerald-600 hover:text-emerald-800 font-medium py-1.5 hover:underline"
          >
            +{restaurants.length - 5} quán khác → Hiện tất cả
          </button>
        )}
        {showAll && restaurants.length > 5 && (
          <button
            onClick={onViewMap}
            className="w-full text-center text-[11px] text-blue-600 hover:text-blue-800 font-medium py-1.5 hover:underline"
          >
            Xem tất cả {restaurants.length} quán trên bản đồ →
          </button>
        )}
      </div>

      {/* MiniMap Popup — dùng Portal render ở document.body để tránh bị clip bởi overflow/transform */}
      {hoveredRestaurant && ReactDOM.createPortal(
        <div
          style={{
            position: 'fixed',
            left: popupPos.left,
            top: popupPos.top,
            zIndex: 999999,
            pointerEvents: 'none',
            animation: 'nearbyMapIn .18s cubic-bezier(.34,1.56,.64,1)',
          }}
        >
          <style>{`@keyframes nearbyMapIn{from{opacity:0;transform:scale(.9) translateY(6px)}to{opacity:1;transform:scale(1) translateY(0)}}`}</style>
          <MiniMapPopup
            restaurantPosition={hoveredRestaurant.position}
            restaurantName={hoveredRestaurant.name}
            userLocation={userLocation}
          />
        </div>,
        document.body
      )}
    </div>
  );
};

export default NearbyRestaurantsCard;
