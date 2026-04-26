/**
 * Overpass API utilities – chia sẻ giữa RestaurantMap và RecommendationPage
 */

const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';
const SEARCH_RADIUS = 5000; // mét

// ─── Cache sessionStorage (5 phút) ────────────────────────────────────────
export function getCacheKey(lat, lng, keyword) {
  return 'osm_' + lat.toFixed(3) + '_' + lng.toFixed(3) + '_' + (keyword || '').trim().toLowerCase();
}

export function getCached(key) {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    const { data, ts } = JSON.parse(raw);
    if (Date.now() - ts > 5 * 60 * 1000) { sessionStorage.removeItem(key); return null; }
    return data;
  } catch { return null; }
}

export function setCache(key, data) {
  try { sessionStorage.setItem(key, JSON.stringify({ data, ts: Date.now() })); } catch { /* quota */ }
}

// ─── Fetch nhà hàng từ Overpass API ────────────────────────────────────────
export async function fetchNearbyRestaurants(lat, lng, keyword) {
  const cacheKey = getCacheKey(lat, lng, keyword);
  const cached = getCached(cacheKey);
  if (cached) return cached;

  let nodes;
  if (keyword && keyword.trim()) {
    const kw = keyword.trim().replace(/"/g, '').replace(/\s+/g, '|'); // "phở bò" → "phở|bò"
    // Tìm theo tên VÀ theo cuisine tag, bao phủ nhiều loại hình quán
    const amenities = ['restaurant', 'fast_food', 'cafe', 'food_court', 'bar', 'pub'];
    nodes = amenities.map(a =>
      'node["amenity"="' + a + '"]["name"~"' + kw + '",i](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');\n' +
      'node["amenity"="' + a + '"]["cuisine"~"' + kw + '",i](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');'
    ).join('\n');
  } else {
    nodes =
      'node["amenity"="restaurant"](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');\n' +
      'node["amenity"="fast_food"](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');\n' +
      'node["amenity"="cafe"](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');\n' +
      'node["amenity"="food_court"](around:' + SEARCH_RADIUS + ',' + lat + ',' + lng + ');';
  }

  const query = '[out:json][timeout:20];\n(\n' + nodes + '\n);\nout body;';

  const res = await fetch(OVERPASS_URL, {
    method: 'POST',
    body: query,
    headers: { 'Content-Type': 'text/plain' },
  });
  if (!res.ok) throw new Error('Overpass API lỗi: ' + res.status);
  const json = await res.json();
  const elements = json.elements || [];

  setCache(cacheKey, elements);
  return elements;
}

// ─── Parse opening_hours (OSM format) ──────────────────────────────────────
export function isCurrentlyOpen(oh) {
  if (!oh) return null;
  const s = oh.trim();
  if (s === '24/7') return true;

  const now = new Date();
  const today = now.getDay();
  const curMin = now.getHours() * 60 + now.getMinutes();
  const DAY = { Mo: 1, Tu: 2, We: 3, Th: 4, Fr: 5, Sa: 6, Su: 0 };

  function inRange(d, a, b) { return a <= b ? d >= a && d <= b : d >= a || d <= b; }
  function toMin(t) { const [h, m] = t.split(':').map(Number); return h * 60 + m; }

  let everMatched = false;
  for (const rule of s.split(';').map(r => r.trim()).filter(Boolean)) {
    const timeRx = /(\d{1,2}:\d{2})-(\d{1,2}:\d{2})/g;
    const times = []; let mt;
    while ((mt = timeRx.exec(rule)) !== null) times.push([toMin(mt[1]), toMin(mt[2])]);
    if (!times.length) continue;

    const dayPart = rule.substring(0, rule.search(/\d{1,2}:\d{2}/)).trim();
    let dayOk = !dayPart;
    if (!dayOk) {
      for (const seg of dayPart.split(',').map(d => d.trim()).filter(Boolean)) {
        const rm = seg.match(/^([A-Z][a-z])-([A-Z][a-z])$/);
        if (rm) {
          const a = DAY[rm[1]], b = DAY[rm[2]];
          if (a !== undefined && b !== undefined && inRange(today, a, b)) { dayOk = true; break; }
        } else {
          if (DAY[seg] === today) { dayOk = true; break; }
        }
      }
    }
    if (!dayOk) continue;
    everMatched = true;
    for (const [start, end] of times) { if (curMin >= start && curMin <= end) return true; }
  }
  return everMatched ? false : null;
}

// ─── Parse elements thành danh sách nhà hàng ──────────────────────────────
export function parseRestaurants(elements) {
  return elements
    .filter((el) => el.lat && el.lon && el.tags && el.tags.name)
    .map((el) => ({
      id: el.id,
      name: el.tags.name,
      position: [el.lat, el.lon],
      cuisine: el.tags.cuisine || '',
      openingHours: el.tags.opening_hours || '',
      phone: el.tags.phone || el.tags['contact:phone'] || '',
      website: el.tags.website || el.tags['contact:website'] || '',
      address: [el.tags['addr:housenumber'], el.tags['addr:street'], el.tags['addr:city']]
        .filter(Boolean)
        .join(' '),
      isOpen: isCurrentlyOpen(el.tags.opening_hours || null),
    }))
    .slice(0, 30);
}

// ─── Matching keywords: nhà hàng ↔ món ăn ─────────────────────────────────
const FOOD_KEYWORDS = [
  'phở', 'bún', 'cơm', 'bánh mì', 'bánh cuốn', 'bánh xèo', 'bánh tráng',
  'bánh', 'lẩu', 'hủ tiếu', 'mì', 'xôi', 'gỏi', 'chả', 'nem', 'chè',
  'bò', 'gà', 'vịt', 'heo', 'cá', 'tôm', 'cua', 'chay',
];

/**
 * Khớp danh sách nhà hàng đang mở với danh sách món ăn trong DB.
 * Trả về mảng { food, restaurants[] } – mỗi món có danh sách quán gần bạn bán.
 */
export function matchFoodsToRestaurants(foods, restaurants) {
  const openRestaurants = restaurants.filter((r) => r.isOpen !== false);
  if (!openRestaurants.length || !foods.length) return [];

  const results = [];

  for (const food of foods) {
    const foodName = (food.name || '').toLowerCase();
    const foodCategory = (food.category || '').toLowerCase();
    const text = foodName + ' ' + foodCategory;

    // Tìm keywords xuất hiện trong tên/category món ăn
    const foodKws = FOOD_KEYWORDS.filter((kw) => text.includes(kw));
    if (!foodKws.length) continue;

    // Tìm các quán có tên/cuisine chứa keyword đó
    const matched = openRestaurants.filter((r) => {
      const rText = (r.name + ' ' + r.cuisine).toLowerCase();
      return foodKws.some((kw) => rText.includes(kw));
    });

    if (matched.length > 0) {
      results.push({ food, restaurants: matched });
    }
  }

  return results;
}
