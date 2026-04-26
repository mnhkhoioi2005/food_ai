import { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, MapPin, Flame, Heart, TrendingUp, 
  RefreshCw, Loader, AlertCircle, ChevronRight, Store
} from 'lucide-react';
import { recommendationAPI, foodAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import FoodCard from '../components/FoodCard';
import RestaurantMap from '../components/RestaurantMap';
import { fetchNearbyRestaurants, parseRestaurants, matchFoodsToRestaurants } from '../utils/overpass';
import { Link, useSearchParams } from 'react-router-dom';

const RecommendationPage = () => {
  const { user, isAuthenticated } = useAuth();
  const [searchParams] = useSearchParams();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('personalized');
  const [mapDishQuery, setMapDishQuery] = useState(''); // từ khóa từ AI chat
  const [location, setLocation] = useState(null);
  const [nearbyMatches, setNearbyMatches] = useState([]); // { food, restaurants[] }[]
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null); // món được chọn → hiện map
  const nearbyFetchedRef = useRef(false);
  const mapRef = useRef(null);

  // User preferences for recommendation
  const [preferences, setPreferences] = useState({
    prefer_spicy: false,
    prefer_soup: false,
    is_vegetarian: false,
    region: '',
    exclude_allergens: [],
  });

  // Đọc URL params (?tab=nearby&q=phở) khi navigate từ AI chat
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    const qParam = searchParams.get('q');
    if (tabParam === 'nearby') {
      setActiveTab('nearby');
      getUserLocation();
    }
    if (qParam) setMapDishQuery(qParam);
  }, [searchParams]);

  useEffect(() => {
    loadRecommendations();
  }, [activeTab, user]);

  // Lấy vị trí ngay khi mount
  useEffect(() => {
    getUserLocation();
  }, []);

  // Khi có vị trí → tìm quán gần bạn đang mở → khớp với món ăn trong DB
  useEffect(() => {
    if (!location || nearbyFetchedRef.current) return;
    nearbyFetchedRef.current = true;
    setNearbyLoading(true);
    Promise.all([
      fetchNearbyRestaurants(location.lat, location.lng),
      foodAPI.search({ page_size: 100 }),
    ])
      .then(([elements, foodRes]) => {
        const restaurants = parseRestaurants(elements);
        const foods = foodRes.data.items || foodRes.data || [];
        const matches = matchFoodsToRestaurants(foods, restaurants);
        setNearbyMatches(matches);
      })
      .catch(() => {})
      .finally(() => setNearbyLoading(false));
  }, [location]);

  // Get user location (lưu vào sessionStorage để AI chat dùng lại)
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setLocation(loc);
          try { sessionStorage.setItem('vfa_user_location', JSON.stringify(loc)); } catch {}
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  const loadRecommendations = async () => {
    // Tab Gần đây dùng bản đồ trực tiếp, không cần gọi API gợi ý
    if (activeTab === 'nearby') { getUserLocation(); return; }
    setLoading(true);
    setError(null);
    
    try {
      let response;
      
      switch (activeTab) {
        case 'personalized':
          if (isAuthenticated) {
            response = await recommendationAPI.getPersonalized(12);
          } else {
            response = await recommendationAPI.getByTaste({ limit: 12 });
          }
          break;
          
        case 'nearby':
          if (location) {
            response = await recommendationAPI.getNearby(location.lat, location.lng, 12);
          } else {
            getUserLocation();
            response = await recommendationAPI.getByTaste({ limit: 12 });
          }
          break;
          
        case 'trending':
          response = await recommendationAPI.get({ 
            filter_type: 'popular',
            limit: 12 
          });
          break;
          
        case 'taste':
          response = await recommendationAPI.getByTaste({
            ...preferences,
            limit: 12,
          });
          break;
          
        default:
          response = await recommendationAPI.get({ limit: 12 });
      }
      
      setRecommendations(response.data.recommendations || response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'personalized', label: 'Dành cho bạn', icon: <Sparkles size={18} /> },
    { id: 'trending', label: 'Xu hướng', icon: <TrendingUp size={18} /> },
    { id: 'nearby', label: 'Gần đây', icon: <MapPin size={18} /> },
    { id: 'taste', label: 'Theo khẩu vị', icon: <Heart size={18} /> },
  ];

  const regions = ['Miền Bắc', 'Miền Trung', 'Miền Nam'];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
          <Sparkles className="inline-block mr-2 text-primary-500" />
          Gợi ý món ăn
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          {isAuthenticated 
            ? `Xin chào ${user?.full_name}! Dưới đây là những món ăn được gợi ý dành riêng cho bạn.`
            : 'Khám phá những món ăn phù hợp với khẩu vị của bạn.'}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto gap-2 mb-8 pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl whitespace-nowrap font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-primary-500 text-white shadow-lg'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-primary-300'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Taste Preferences (when taste tab is active) */}
      {activeTab === 'taste' && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-8 animate-fadeIn">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Tùy chọn khẩu vị
          </h3>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Region */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vùng miền
              </label>
              <select
                value={preferences.region}
                onChange={(e) => setPreferences({ ...preferences, region: e.target.value })}
                className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
              >
                <option value="">Tất cả</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 mb-4">
            <button
              onClick={() => setPreferences({ ...preferences, prefer_spicy: !preferences.prefer_spicy })}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                preferences.prefer_spicy
                  ? 'bg-red-500 text-white'
                  : 'bg-red-50 text-red-600 hover:bg-red-100'
              }`}
            >
              <Flame size={16} />
              Thích cay
            </button>
            <button
              onClick={() => setPreferences({ ...preferences, prefer_soup: !preferences.prefer_soup })}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                preferences.prefer_soup
                  ? 'bg-blue-500 text-white'
                  : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              }`}
            >
              🍜 Món nước
            </button>
            <button
              onClick={() => setPreferences({ ...preferences, is_vegetarian: !preferences.is_vegetarian })}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                preferences.is_vegetarian
                  ? 'bg-green-500 text-white'
                  : 'bg-green-50 text-green-600 hover:bg-green-100'
              }`}
            >
              🥬 Ăn chay
            </button>
          </div>

          <button
            onClick={loadRecommendations}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            {loading ? (
              <Loader className="animate-spin" size={18} />
            ) : (
              <RefreshCw size={18} />
            )}
            Cập nhật gợi ý
          </button>
        </div>
      )}

      {/* Nearby notice đã được chuyển vào phần bản đồ bên dưới */}

      {/* Error */}
      {error && (
        <div className="mb-8 p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-3">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && activeTab !== 'nearby' && (
        <div className="text-center py-20">
          <Loader className="w-10 h-10 mx-auto text-primary-500 animate-spin mb-4" />
          <p className="text-gray-500">Đang tải gợi ý...</p>
        </div>
      )}

      {/* Tab Gần đây – Bản đồ quán đang mở cửa */}
      {activeTab === 'nearby' && (
        <div>
          {!location && (
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mb-6 flex items-center gap-4">
              <MapPin className="text-blue-500 flex-shrink-0" size={24} />
              <div className="flex-1">
                <h4 className="font-medium text-gray-800">Cho phép truy cập vị trí</h4>
                <p className="text-sm text-gray-600">Dể xem quán ăn đang mở cửa gần bạn trên bản đồ</p>
              </div>
              <button onClick={getUserLocation} className="btn-primary">
                Cho phép
              </button>
            </div>
          )}
          {mapDishQuery && (
            <div className="flex items-center gap-2 mb-4 px-1">
              <span className="text-sm text-gray-600">Tìm quán bán:</span>
              <span className="px-3 py-1 bg-orange-100 text-orange-700 text-sm font-semibold rounded-full">
                🍜 {mapDishQuery}
              </span>
              <button
                onClick={() => setMapDishQuery('')}
                className="text-xs text-gray-400 hover:text-gray-600 ml-1"
              >
                × Xóa bộ lọc
              </button>
            </div>
          )}
          <RestaurantMap userLocation={location} dishQuery={mapDishQuery || undefined} openNowOnly />
        </div>
      )}

      {/* Recommendations Grid – chỉ hiện cho các tab khác */}
      {activeTab === 'personalized' && nearbyMatches.length > 0 && !loading && (
        <div className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <Store className="text-green-600" size={20} />
            <h3 className="text-lg font-semibold text-gray-800">
              Quán gần bạn đang bán
            </h3>
            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full font-medium">
              {nearbyMatches.length} món
            </span>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {nearbyMatches.map(({ food, restaurants }) => {
              const isSelected = selectedMatch?.food?.id === food.id;
              return (
                <button
                  key={food.id}
                  className={`relative text-left rounded-2xl transition-all ring-2 ${
                    isSelected ? 'ring-green-500 shadow-lg' : 'ring-transparent hover:ring-green-300'
                  }`}
                  onClick={() => {
                    setSelectedMatch(isSelected ? null : { food, restaurants });
                    if (!isSelected) setTimeout(() => mapRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
                  }}
                >
                  <FoodCard food={food} />
                  <div className="absolute top-3 right-3 px-2 py-1 bg-green-500/90 backdrop-blur-sm rounded-full text-xs font-medium text-white flex items-center gap-1">
                    <Store size={10} />
                    {restaurants.length} quán gần bạn
                  </div>
                  {isSelected && (
                    <div className="absolute inset-0 rounded-2xl bg-green-500/10 pointer-events-none" />
                  )}
                  <div className="mt-1 px-1">
                    {restaurants.slice(0, 2).map((r) => (
                      <span key={r.id} className="inline-flex items-center gap-1 text-[11px] text-green-700 bg-green-50 px-2 py-0.5 rounded-full mr-1 mb-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
                        {r.name}
                      </span>
                    ))}
                    {restaurants.length > 2 && (
                      <span className="text-[11px] text-gray-400">+{restaurants.length - 2} quán khác</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Bản đồ quán bán món được chọn */}
      {activeTab === 'personalized' && selectedMatch && (
        <div ref={mapRef} className="mt-6">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="text-green-600" size={18} />
            <h3 className="text-base font-semibold text-gray-800">
              Quán đang bán <span className="text-green-600">«{selectedMatch.food.name || selectedMatch.food.name_en}»</span> gần bạn
            </h3>
            <button onClick={() => setSelectedMatch(null)} className="ml-auto text-xs text-gray-400 hover:text-gray-600">✕ Đóng</button>
          </div>
          <RestaurantMap
            userLocation={location}
            staticRestaurants={selectedMatch.restaurants}
          />
        </div>
      )}

      {activeTab === 'personalized' && nearbyLoading && (
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
          <Loader className="animate-spin" size={14} />
          Đang tìm quán ăn gần bạn...
        </div>
      )}

      {activeTab !== 'nearby' && activeTab !== 'personalized' && !loading && recommendations.length > 0 && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {recommendations.map((item, index) => (
            <div key={item.id || index} className="relative">
              <FoodCard food={item.food || item} />
              {item.score && (
                <div className="absolute top-3 right-3 px-2 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-medium text-primary-600">
                  {(item.score * 100).toFixed(0)}% phù hợp
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty state – chỉ cho tab khác (không phải nearby và personalized) */}
      {activeTab !== 'nearby' && activeTab !== 'personalized' && !loading && recommendations.length === 0 && (
        <div className="text-center py-20">
          <Sparkles className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">
            Chưa có gợi ý
          </h3>
          <p className="text-gray-500 mb-4">
            {isAuthenticated
              ? 'Hãy tương tác nhiều hơn để nhận được gợi ý tốt hơn.'
              : 'Đăng nhập để nhận gợi ý cá nhân hóa.'}
          </p>
          {!isAuthenticated && (
            <Link to="/login" className="btn-primary inline-flex items-center gap-2">
              Đăng nhập
              <ChevronRight size={18} />
            </Link>
          )}
        </div>
      )}

      {/* Refresh – chỉ cho tab khác ngoài personalized và nearby */}
      {activeTab !== 'nearby' && activeTab !== 'personalized' && !loading && recommendations.length > 0 && (
        <div className="text-center mt-8">
          <button
            onClick={loadRecommendations}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw size={18} />
            Làm mới gợi ý
          </button>
        </div>
      )}
    </div>
  );
};

export default RecommendationPage;
