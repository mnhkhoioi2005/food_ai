/**
 * MiniMapPopup – dùng iframe OpenStreetMap embed (không cần Leaflet).
 * Luôn hoạt động trong Portal, không bị lỗi invalidateSize.
 * Props:
 *   restaurantPosition – [lat, lng]
 *   restaurantName     – tên quán
 *   userLocation       – { lat, lng } vị trí người dùng
 */
const MiniMapPopup = ({ restaurantPosition, restaurantName, userLocation }) => {
  if (!restaurantPosition) return null;

  const [rLat, rLng] = restaurantPosition;

  // Tính khoảng cách (Haversine)
  let distText = null;
  if (userLocation) {
    const R = 6371;
    const dLat = (rLat - userLocation.lat) * Math.PI / 180;
    const dLon = (rLng - userLocation.lng) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(userLocation.lat * Math.PI / 180) * Math.cos(rLat * Math.PI / 180) *
      Math.sin(dLon / 2) ** 2;
    const d = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    distText = d < 1 ? Math.round(d * 1000) + ' m' : d.toFixed(1) + ' km';
  }

  // Tính bbox cho iframe (center ở nhà hàng, ±0.006 độ ≈ 600m)
  const delta = 0.006;
  const bbox = `${rLng - delta},${rLat - delta},${rLng + delta},${rLat + delta}`;
  const iframeSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${rLat},${rLng}`;

  return (
    <div style={{
      width: 270,
      borderRadius: 14,
      overflow: 'hidden',
      boxShadow: '0 16px 40px rgba(0,0,0,0.25), 0 2px 10px rgba(0,0,0,0.12)',
      border: '1.5px solid #e5e7eb',
      background: 'white',
      pointerEvents: 'none',
    }}>
      {/* Map iframe */}
      <div style={{ position: 'relative', height: 170, background: '#f3f4f6' }}>
        <iframe
          title={restaurantName}
          src={iframeSrc}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            display: 'block',
          }}
          loading="lazy"
          referrerPolicy="no-referrer"
        />
        {/* Overlay gradient phía dưới để footer đẹp hơn */}
        <div style={{
          position: 'absolute',
          bottom: 0, left: 0, right: 0, height: 24,
          background: 'linear-gradient(transparent, rgba(255,255,255,0.6))',
          pointerEvents: 'none',
        }} />
      </div>

      {/* Footer info */}
      <div style={{ padding: '8px 12px', background: 'white', borderTop: '1px solid #f3f4f6' }}>
        <p style={{
          margin: 0, fontSize: 12, fontWeight: 700, color: '#1f2937',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          🍜 {restaurantName}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
          {userLocation && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#3B82F6', flexShrink: 0 }} />
              <span style={{ fontSize: 10, color: '#9ca3af' }}>Vị trí của bạn</span>
            </div>
          )}
          {distText && (
            <span style={{
              fontSize: 10, fontWeight: 700,
              color: '#059669', background: '#d1fae5',
              padding: '2px 8px', borderRadius: 999,
            }}>
              📍 {distText}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MiniMapPopup;
