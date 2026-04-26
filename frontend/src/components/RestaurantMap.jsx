/**
 * RestaurantMap – Leaflet + OpenStreetMap (100% miễn phí, không cần API key)
 * Tìm nhà hàng gần đây qua Overpass API (dữ liệu OpenStreetMap).
 *
 * Props:
 *   recommendations – danh sách gợi ý (mỗi phần tử có .food hoặc trực tiếp là food)
 *   userLocation     – { lat, lng } vị trí người dùng
 */
import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Loader, Navigation, ExternalLink, RefreshCw } from 'lucide-react';
import { fetchNearbyRestaurants, parseRestaurants, getCacheKey } from '../utils/overpass';

// ─── Fix Leaflet default icon bị vỡ trong Vite ────────────────────────────
// Dùng DivIcon SVG tự vẽ → không phụ thuộc file ảnh bundled.
const makeIcon = (color, emoji, size) => {
  size = size || 36;
  return L.divIcon({
    className: '',
    html:
      '<div style="position:relative;width:' + size + 'px;height:' + (size * 1.25) + 'px;display:flex;align-items:flex-start;justify-content:center;">' +
      '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + (size * 1.25) + '" viewBox="0 0 40 50">' +
      '<path d="M20 0C9 0 0 9 0 20c0 13.5 20 30 20 30s20-16.5 20-30C40 9 31 0 20 0z" fill="' + color + '" stroke="white" stroke-width="2"/>' +
      '<circle cx="20" cy="20" r="11" fill="white"/>' +
      '<text x="20" y="26" font-size="13" text-anchor="middle">' + emoji + '</text>' +
      '</svg></div>',
    iconSize: [size, size * 1.25],
    iconAnchor: [size / 2, size * 1.25],
    popupAnchor: [0, -(size * 1.25)],
  });
};

const USER_ICON = L.divIcon({
  className: '',
  html: '<div style="width:18px;height:18px;border-radius:50%;background:#3B82F6;border:3px solid white;box-shadow:0 0 0 3px rgba(59,130,246,0.4);"></div>',
  iconSize: [18, 18],
  iconAnchor: [9, 9],
  popupAnchor: [0, -12],
});

const RESTAURANT_ICON        = makeIcon('#EF4444', '🍜', 36); // giờ không rõ
const RESTAURANT_OPEN_ICON   = makeIcon('#15803D', '🍜', 36); // xanh: đang mở cửa
const RESTAURANT_CLOSED_ICON = makeIcon('#9CA3AF', '🍜', 32); // xám:  đã đóng cửa

// ─── Helper: di chuyển map đến vị trí mới ─────────────────────────────────
function FlyToLocation({ position, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (position) map.flyTo(position, zoom || 15, { duration: 1.2 });
  }, [position, zoom, map]);
  return null;
}

// ─── Component chính ───────────────────────────────────────────────────────
/**
 * Props:
 *   recommendations – gợi ý món ăn (dùng ở tab Gần đây của RecommendationPage)
 *   userLocation    – { lat, lng }
 *   dishQuery       – tên món tìm kiếm (VD: "phở") → dùng ở SearchPage
 */
/**
 * Nếu staticRestaurants được truyền vào → dùng luôn, bỏ qua Overpass fetch.
 * Dùng ở màn hình "Dành cho bạn" khi chọn một món để xem quán bán món đó.
 */
const RestaurantMap = ({ recommendations, userLocation, dishQuery, openNowOnly, staticRestaurants }) => {
  recommendations = recommendations || [];
  const isStatic = Array.isArray(staticRestaurants);
  const [restaurants, setRestaurants] = useState(isStatic ? staticRestaurants : []);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [flyTarget, setFlyTarget] = useState(null);
  const lastFetchRef = useRef(null);
  const markerRefs = useRef({});

  const center = userLocation
    ? [userLocation.lat, userLocation.lng]
    : [10.7769, 106.7009];

  const doFetch = (lat, lng, keyword) => {
    setSearching(true);
    setError(null);
    fetchNearbyRestaurants(lat, lng, keyword)
      .then((elements) => setRestaurants(parseRestaurants(elements)))
      .catch(() => setError('Không thể tải dữ liệu nhà hàng. Thử lại sau.'))
      .finally(() => setSearching(false));
  };

  // Khi staticRestaurants thay đổi (người dùng chọn món khác) → cập nhật ngay
  useEffect(() => {
    if (isStatic) { setRestaurants(staticRestaurants); setFlyTarget(null); }
  }, [staticRestaurants]);

  useEffect(() => {
    if (isStatic || !userLocation) return;
    // Key gồm cả từ khóa tìm kiếm để re-fetch khi đổi món
    const key = userLocation.lat.toFixed(4) + ',' + userLocation.lng.toFixed(4) + ':' + (dishQuery || '');
    if (lastFetchRef.current === key) return;
    lastFetchRef.current = key;
    setRestaurants([]);
    doFetch(userLocation.lat, userLocation.lng, dishQuery);
  }, [userLocation, dishQuery]);

  const handleRefresh = () => {
    if (isStatic || !userLocation) return;
    // Xóa cache để fetch mới
    const cacheKey = getCacheKey(userLocation.lat, userLocation.lng, dishQuery);
    try { sessionStorage.removeItem(cacheKey); } catch {}
    lastFetchRef.current = null;
    setRestaurants([]);
    doFetch(userLocation.lat, userLocation.lng, dishQuery);
  };

  if (!userLocation) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-blue-50 rounded-2xl border border-blue-200 text-blue-600 gap-3">
        <Navigation size={32} />
        <p className="font-medium">Chưa có vị trí</p>
        <p className="text-sm text-blue-400">Cho phép truy cập vị trí để xem bản đồ nhà hàng</p>
      </div>
    );
  }

  // Nếu có dishQuery (từ SearchPage) thì dùng nó làm nhãn chính,
  // ngược lại trích từ danh sách recommendations (từ RecommendationPage).
  const dishNames = dishQuery
    ? [dishQuery]
    : [
        ...new Set(
          recommendations
            .slice(0, 5)
            .map((item) => (item.food || item).name_vi || (item.food || item).name_en)
            .filter(Boolean)
        ),
      ];

  // Khi openNowOnly: ẩn quán được xác nhận là đóng cửa; giờ không rõ vẫn hiện
  const visibleRestaurants = openNowOnly
    ? restaurants.filter((r) => r.isOpen !== false)
    : restaurants;
  const openCount    = visibleRestaurants.filter((r) => r.isOpen === true).length;
  const unknownCount = visibleRestaurants.filter((r) => r.isOpen === null).length;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          {searching
            ? 'Đang tải quán ăn...'
            : openNowOnly
              ? 'Tìm thấy ' + visibleRestaurants.length + ' quán (có thể đang mở) trong bán kính 5 km'
              : 'Tìm thấy ' + visibleRestaurants.length + ' nhà hàng trong bán kính 5 km'}
        </p>
        <button
          onClick={handleRefresh}
          disabled={searching}
          className="flex items-center gap-1.5 text-sm text-primary-600 hover:text-primary-800 disabled:opacity-50"
        >
          <RefreshCw size={14} className={searching ? 'animate-spin' : ''} />
          Làm mới
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
      )}

      <div className="relative">
        {searching && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-2 bg-white/95 backdrop-blur-sm px-4 py-2 rounded-full shadow-md text-sm text-gray-600 border border-gray-100">
            <Loader className="animate-spin text-primary-500" size={14} />
            Đang tải dữ liệu từ OpenStreetMap...
          </div>
        )}

        <MapContainer
          center={center}
          zoom={15}
          style={{ height: '480px', width: '100%', borderRadius: '16px', zIndex: 0 }}
          scrollWheelZoom
          preferCanvas
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={20}
          />

          <FlyToLocation position={flyTarget || center} zoom={flyTarget ? 17 : 15} />

          {/* Marker vị trí người dùng */}
          <Marker position={center} icon={USER_ICON}>
            <Popup>
              <span className="font-medium text-blue-600">📍 Vị trí của bạn</span>
            </Popup>
          </Marker>

          {/* Marker nhà hàng */}
          {visibleRestaurants.map((r) => (
            <Marker
              key={r.id}
              position={r.position}
              icon={
                r.isOpen === true  ? RESTAURANT_OPEN_ICON :
                r.isOpen === false ? RESTAURANT_CLOSED_ICON :
                RESTAURANT_ICON
              }
              ref={(ref) => { if (ref) markerRefs.current[r.id] = ref; }}
              eventHandlers={{ click: () => setSelectedId(r.id) }}
            >
              <Popup minWidth={200} maxWidth={260}>
                <div style={{ fontFamily: 'sans-serif', color: '#1f2937' }}>
                  <p style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>{r.name}</p>

                  {/* Trạng thái mở / đóng */}
                  {r.isOpen === true && (
                    <span style={{ display:'inline-block', padding:'2px 8px', background:'#DCFCE7', color:'#15803D', borderRadius:'9999px', fontSize:'11px', marginBottom:'6px' }}>
                      ● Đang mở cửa
                    </span>
                  )}
                  {r.isOpen === false && (
                    <span style={{ display:'inline-block', padding:'2px 8px', background:'#FEE2E2', color:'#B91C1C', borderRadius:'9999px', fontSize:'11px', marginBottom:'6px' }}>
                      ● Đã đóng cửa
                    </span>
                  )}

                  {dishNames.length > 0 && (
                    <div style={{ marginBottom: '4px' }}>
                      {dishNames.slice(0, 2).map((dish) => (
                        <span
                          key={dish}
                          style={{
                            display: 'inline-block',
                            padding: '2px 8px',
                            background: '#FEF3C7',
                            color: '#B45309',
                            borderRadius: '9999px',
                            fontSize: '11px',
                            marginRight: '4px',
                          }}
                        >
                          🍜 {dish}
                        </span>
                      ))}
                    </div>
                  )}

                  {r.cuisine && (
                    <p style={{ fontSize: '12px', color: '#6B7280', margin: '2px 0' }}>
                      🍽️ {r.cuisine.split(';').join(', ')}
                    </p>
                  )}
                  {r.openingHours && (
                    <p style={{ fontSize: '12px', color: '#6B7280', margin: '2px 0' }}>
                      🕐 {r.openingHours}
                    </p>
                  )}
                  {r.address && (
                    <p style={{ fontSize: '12px', color: '#6B7280', margin: '2px 0' }}>
                      📍 {r.address}
                    </p>
                  )}
                  {r.phone && (
                    <p style={{ fontSize: '12px', color: '#6B7280', margin: '2px 0' }}>
                      📞 <a href={'tel:' + r.phone} style={{ color: '#2563EB' }}>{r.phone}</a>
                    </p>
                  )}
                  {r.website && (
                    <a
                      href={r.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#2563EB', marginTop: '4px' }}
                    >
                      🌐 Website
                    </a>
                  )}
                  <a
                    href={'https://www.openstreetmap.org/?mlat=' + r.position[0] + '&mlon=' + r.position[1] + '&zoom=18'}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#9CA3AF', marginTop: '6px' }}
                  >
                    🗺️ Xem trên OpenStreetMap
                  </a>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center flex-wrap gap-x-5 gap-y-2 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-blue-500 block" />
          Vị trí của bạn
        </div>
        {openNowOnly ? (
          <>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-green-700 block" />
              {'Xác nhận mở cửa (' + openCount + ')'}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-400 block" />
              {'Giờ không rõ (' + unknownCount + ')'}
            </div>
          </>
        ) : (
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500 block" />
            {'Nhà hàng (' + visibleRestaurants.length + ')'}
          </div>
        )}
        <span className="ml-auto text-gray-300 text-[10px]">
          Dữ liệu: OpenStreetMap · Overpass API (miễn phí)
        </span>
      </div>

      {visibleRestaurants.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-gray-800 mb-3">
            {openNowOnly ? 'Quán ăn gần bạn' : 'Nhà hàng gần bạn'}
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {visibleRestaurants.map((r) => (
              <button
                key={r.id}
                onClick={() => {
                  setSelectedId(r.id);
                  setFlyTarget([...r.position]);
                  // Mở popup sau khi map bay đến
                  setTimeout(() => {
                    const marker = markerRefs.current[r.id];
                    if (marker) marker.openPopup();
                  }, 1300);
                }}
                className={
                  'text-left p-4 bg-white rounded-xl border transition-all group ' +
                  (selectedId === r.id
                    ? 'border-primary-400 shadow-md'
                    : 'border-gray-100 hover:border-primary-300 hover:shadow-sm')
                }
              >
                <p className="font-medium text-gray-800 text-sm leading-snug group-hover:text-primary-600 line-clamp-1">
                  {r.name}
                </p>
                {r.isOpen === true && (
                  <span className="inline-block px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full mt-1">
                    ● Đang mở cửa
                  </span>
                )}
                {r.isOpen === null && openNowOnly && (
                  <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-400 text-xs rounded-full mt-1">
                    Giờ chưa rõ
                  </span>
                )}
                {r.cuisine && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    🍽️ {r.cuisine.split(';').slice(0, 2).join(', ')}
                  </p>
                )}
                {r.address && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-1">📍 {r.address}</p>
                )}
                {r.openingHours && (
                  <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">🕐 {r.openingHours}</p>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RestaurantMap;
