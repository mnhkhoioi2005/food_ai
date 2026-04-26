import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Search, Filter, X, ChevronDown, SlidersHorizontal, 
  MapPin, Flame, Leaf, Soup, Loader, Navigation
} from 'lucide-react';
import { foodAPI } from '../services/api';
import FoodCard from '../components/FoodCard';
import RestaurantMap from '../components/RestaurantMap';

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Search state
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searched, setSearched] = useState(false);
  
  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    region: searchParams.get('region') || '',
    is_spicy: searchParams.get('is_spicy') === 'true',
    is_vegetarian: searchParams.get('is_vegetarian') === 'true',
    is_soup: searchParams.get('is_soup') === 'true',
    min_calories: searchParams.get('min_calories') || '',
    max_calories: searchParams.get('max_calories') || '',
  });
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    regions: [],
    ingredients: [],
  });

  // Vị trí người dùng (dùng cho bản đồ quán gần đây)
  const [userLocation, setUserLocation] = useState(null);
  const [locationDenied, setLocationDenied] = useState(false);

  const getUserLocation = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => setLocationDenied(true),
      { timeout: 8000 }
    );
  };

  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    // Chỉ tự động tìm khi có query từ URL
    const q = searchParams.get('q');
    if (q) {
      setPage(1);
      setFoods([]);
      setSearched(true);
      searchFoods(1);
    }
  }, []);

  const loadFilterOptions = async () => {
    try {
      const response = await foodAPI.getFilters();
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const searchFoods = async (pageNum = 1) => {
    setLoading(true);
    try {
      const params = {
        q: query || undefined,
        region: filters.region || undefined,
        spicy_level_min: filters.is_spicy ? 1 : undefined,
        is_vegetarian: filters.is_vegetarian || undefined,
        food_type: filters.is_soup ? 'mon_nuoc' : undefined,
        page: pageNum,
        page_size: 12,
      };
      
      // Remove undefined values
      Object.keys(params).forEach(key => 
        params[key] === undefined && delete params[key]
      );
      
      const response = await foodAPI.search(params);
      const newFoods = response.data.items || response.data.foods || [];
      
      if (pageNum === 1) {
        setFoods(newFoods);
      } else {
        setFoods(prev => [...prev, ...newFoods]);
      }
      
      setTotalCount(response.data.total || newFoods.length);
      setHasMore(newFoods.length === 12);
      setPage(pageNum);
    } catch (error) {
      console.error('Error searching foods:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams({ q: query, ...filters });
    setPage(1);
    setFoods([]);
    setSearched(true);
    searchFoods(1);
    // Tự động xin vị trí khi người dùng search lần đầu
    if (!userLocation && !locationDenied) getUserLocation();
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    const params = { q: query };
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) params[k] = v.toString();
    });
    setSearchParams(params);
  };

  // Re-search khi filter thay đổi (chỉ khi đã search trước đó)
  useEffect(() => {
    if (searched) {
      setPage(1);
      setFoods([]);
      searchFoods(1);
    }
  }, [filters]);

  const clearFilters = () => {
    setFilters({
      region: '',
      is_spicy: false,
      is_vegetarian: false,
      is_soup: false,
      min_calories: '',
      max_calories: '',
    });
    setSearchParams({ q: query });
  };

  const activeFilterCount = Object.values(filters).filter(v => v).length;

  const regions = filterOptions.regions?.length > 0 
    ? filterOptions.regions 
    : ['Miền Bắc', 'Miền Trung', 'Miền Nam'];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
          <Search className="inline-block mr-2 text-primary-500" />
          Tìm kiếm món ăn
        </h1>
        <p className="text-gray-600">
          Tìm kiếm hơn 100 món ăn Việt Nam theo tên, nguyên liệu hoặc vùng miền
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative max-w-3xl mx-auto">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm kiếm món ăn... (VD: phở, bún, bánh mì)"
            className="w-full px-6 py-4 pr-32 text-lg rounded-2xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2">
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`p-3 rounded-xl transition-all ${
                showFilters || activeFilterCount > 0
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <SlidersHorizontal size={20} />
              {activeFilterCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
            </button>
            <button
              type="submit"
              className="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-all flex items-center gap-2"
            >
              <Search size={20} />
              <span className="hidden sm:inline">Tìm</span>
            </button>
          </div>
        </div>
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <div className="max-w-3xl mx-auto mb-8 bg-white rounded-2xl border border-gray-100 p-6 animate-fadeIn">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <Filter size={18} />
              Bộ lọc
            </h3>
            {activeFilterCount > 0 && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Xóa tất cả
              </button>
            )}
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {/* Region */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin size={14} className="inline mr-1" />
                Vùng miền
              </label>
              <select
                value={filters.region}
                onChange={(e) => handleFilterChange('region', e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
              >
                <option value="">Tất cả</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>

            {/* Calories Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Calories
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Từ"
                  value={filters.min_calories}
                  onChange={(e) => handleFilterChange('min_calories', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="Đến"
                  value={filters.max_calories}
                  onChange={(e) => handleFilterChange('max_calories', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                />
              </div>
            </div>
          </div>

          {/* Quick Filters */}
          <div className="flex flex-wrap gap-3 mt-4">
            <button
              onClick={() => handleFilterChange('is_spicy', !filters.is_spicy)}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                filters.is_spicy
                  ? 'bg-red-500 text-white'
                  : 'bg-red-50 text-red-600 hover:bg-red-100'
              }`}
            >
              <Flame size={16} />
              Cay
            </button>
            <button
              onClick={() => handleFilterChange('is_vegetarian', !filters.is_vegetarian)}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                filters.is_vegetarian
                  ? 'bg-green-500 text-white'
                  : 'bg-green-50 text-green-600 hover:bg-green-100'
              }`}
            >
              <Leaf size={16} />
              Chay
            </button>
            <button
              onClick={() => handleFilterChange('is_soup', !filters.is_soup)}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
                filters.is_soup
                  ? 'bg-blue-500 text-white'
                  : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              }`}
            >
              <Soup size={16} />
              Món nước
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      <div>
        {/* Results header */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-600">
            {loading && page === 1 
              ? 'Đang tìm kiếm...' 
              : searched ? `Tìm thấy ${totalCount} món ăn` : 'Nhập từ khóa để tìm kiếm'}
          </p>
        </div>

        {/* Loading */}
        {loading && page === 1 && (
          <div className="text-center py-20">
            <Loader className="w-10 h-10 mx-auto text-primary-500 animate-spin mb-4" />
            <p className="text-gray-500">Đang tìm kiếm...</p>
          </div>
        )}

        {/* Results Grid */}
        {!loading || page > 1 ? (
          <>
            {foods.length > 0 ? (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {foods.map(food => (
                  <FoodCard key={food.id} food={food} />
                ))}
              </div>
            ) : (
              !loading && (
                <div className="text-center py-20">
                  <Search className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    Không tìm thấy kết quả
                  </h3>
                  <p className="text-gray-500">
                    Thử thay đổi từ khóa hoặc bộ lọc
                  </p>
                </div>
              )
            )}

            {/* Load more */}
            {hasMore && foods.length > 0 && (
              <div className="text-center mt-8">
                <button
                  onClick={() => searchFoods(page + 1)}
                  disabled={loading}
                  className="btn-secondary inline-flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader className="animate-spin" size={18} />
                      Đang tải...
                    </>
                  ) : (
                    <>
                      <ChevronDown size={18} />
                      Xem thêm
                    </>
                  )}
                </button>
              </div>
            )}
          </>
        ) : null}
      </div>

      {/* ── Bản đồ quán gần đây ── */}
      {query.trim() && (
        <div className="mt-12">
          <div className="flex items-center gap-3 mb-5">
            <MapPin className="text-primary-500" size={22} />
            <h2 className="text-xl font-bold text-gray-800">
              Quán <span className="text-primary-500">{query.trim()}</span> gần bạn
            </h2>
            <span className="ml-auto text-xs text-gray-400">Bán kính 5 km</span>
          </div>

          {/* Prompt xin vị trí nếu chưa có */}
          {!userLocation && !locationDenied && (
            <div className="flex items-center gap-4 p-5 bg-blue-50 border border-blue-200 rounded-2xl mb-4">
              <Navigation className="text-blue-500 flex-shrink-0" size={24} />
              <div className="flex-1">
                <p className="font-medium text-gray-800">Cho phép truy cập vị trí</p>
                <p className="text-sm text-gray-500">để xem quán phục vụ <strong>{query}</strong> gần bạn</p>
              </div>
              <button
                onClick={getUserLocation}
                className="px-4 py-2 bg-blue-500 text-white text-sm rounded-xl hover:bg-blue-600 transition-all"
              >
                Cho phép
              </button>
            </div>
          )}

          {locationDenied && (
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-2xl mb-4 text-sm text-gray-500">
              📍 Bạn đã từ chối quyền truy cập vị trí. Hãy bật lại trong cài đặt trình duyệt để xem bản đồ.
            </div>
          )}

          <RestaurantMap
            userLocation={userLocation}
            dishQuery={query.trim()}
          />
        </div>
      )}
    </div>
  );
};

export default SearchPage;
