import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Camera, Search, Utensils, Star, TrendingUp, MapPin, ArrowRight, Sparkles } from 'lucide-react';
import { foodAPI } from '../services/api';
import FoodCard from '../components/FoodCard';

const HomePage = () => {
  const [popularFoods, setPopularFoods] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPopularFoods();
  }, []);

  const loadPopularFoods = async () => {
    try {
      const response = await foodAPI.getPopular(8);
      setPopularFoods(response.data);
    } catch (error) {
      console.error('Error loading popular foods:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <Camera className="w-8 h-8" />,
      title: 'Nhận diện AI',
      description: 'Chụp ảnh món ăn và AI sẽ nhận diện ngay lập tức',
      link: '/recognition',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: <Search className="w-8 h-8" />,
      title: 'Tìm kiếm thông minh',
      description: 'Tìm món ăn theo tên, nguyên liệu hoặc vùng miền',
      link: '/search',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: 'Gợi ý cá nhân',
      description: 'Gợi ý món ăn phù hợp với khẩu vị của bạn',
      link: '/recommendations',
      color: 'from-primary-500 to-primary-600',
    },
    {
      icon: <MapPin className="w-8 h-8" />,
      title: 'Món gần đây',
      description: 'Tìm quán ăn và món ngon gần vị trí của bạn',
      link: '/recommendations',
      color: 'from-green-500 to-green-600',
    },
  ];

  const regions = [
    { name: 'Miền Bắc', image: '🍜', dishes: 'Phở, Bún chả, Bánh cuốn' },
    { name: 'Miền Trung', image: '🍲', dishes: 'Bún bò Huế, Mì Quảng, Bánh bèo' },
    { name: 'Miền Nam', image: '🥘', dishes: 'Hủ tiếu, Bánh mì, Cơm tấm' },
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50" />
        <div className="absolute top-20 right-0 w-[600px] h-[600px] bg-primary-200 rounded-full opacity-30 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-secondary-200 rounded-full opacity-30 blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 py-20 grid md:grid-cols-2 gap-12 items-center">
          <div className="animate-fadeIn">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-full mb-6">
              <Sparkles size={16} />
              <span className="text-sm font-medium">Powered by AI</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-6 leading-tight">
              Khám phá ẩm thực<br />
              <span className="gradient-text">Việt Nam</span> cùng AI
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Nhận diện món ăn qua hình ảnh, tìm kiếm thông minh và nhận gợi ý 
              phù hợp với khẩu vị của bạn.
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Link to="/recognition" className="btn-primary inline-flex items-center gap-2">
                <Camera size={20} />
                Nhận diện ngay
              </Link>
              <Link to="/search" className="btn-secondary inline-flex items-center gap-2">
                <Search size={20} />
                Tìm món ăn
              </Link>
            </div>
            
            <div className="flex items-center gap-6 mt-10">
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-600">100+</p>
                <p className="text-sm text-gray-500">Món ăn</p>
              </div>
              <div className="w-px h-10 bg-gray-200" />
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-600">95%</p>
                <p className="text-sm text-gray-500">Độ chính xác</p>
              </div>
              <div className="w-px h-10 bg-gray-200" />
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-600">3</p>
                <p className="text-sm text-gray-500">Vùng miền</p>
              </div>
            </div>
          </div>
          
          <div className="relative animate-slideIn hidden md:block">
            <div className="relative z-10">
              <img 
                src="https://images.unsplash.com/photo-1555126634-323283e090fa?w=600" 
                alt="Vietnamese Food"
                className="rounded-3xl shadow-2xl"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 w-48 h-48 bg-white rounded-2xl shadow-xl p-4 animate-pulse">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <Camera className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Đã nhận diện</p>
                  <p className="text-xs text-gray-500">Phở bò</p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-yellow-500">
                <Star size={14} fill="currentColor" />
                <Star size={14} fill="currentColor" />
                <Star size={14} fill="currentColor" />
                <Star size={14} fill="currentColor" />
                <Star size={14} fill="currentColor" />
                <span className="text-xs text-gray-500 ml-1">4.9/5</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              Tính năng nổi bật
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Khám phá các tính năng thông minh giúp bạn tìm và thưởng thức món ăn Việt Nam
            </p>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Link
                key={index}
                to={feature.link}
                className="group p-6 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-xl transition-all duration-300"
              >
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.color} text-white flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {feature.description}
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                  Khám phá <ArrowRight size={16} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Regions Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              Ẩm thực ba miền
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Khám phá hương vị đặc trưng của từng vùng miền Việt Nam
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {regions.map((region, index) => (
              <Link
                key={index}
                to={`/search?region=${encodeURIComponent(region.name)}`}
                className="group p-8 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-xl transition-all text-center"
              >
                <span className="text-6xl mb-4 block">{region.image}</span>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  {region.name}
                </h3>
                <p className="text-gray-600">
                  {region.dishes}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Foods Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
                <TrendingUp className="inline-block mr-2 text-primary-500" />
                Món ăn phổ biến
              </h2>
              <p className="text-gray-600">
                Những món ăn được yêu thích nhất
              </p>
            </div>
            <Link 
              to="/search" 
              className="hidden md:inline-flex items-center gap-2 text-primary-600 font-medium hover:gap-3 transition-all"
            >
              Xem tất cả <ArrowRight size={18} />
            </Link>
          </div>
          
          {loading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-48 rounded-2xl mb-4" />
                  <div className="bg-gray-200 h-4 w-3/4 rounded mb-2" />
                  <div className="bg-gray-200 h-3 w-1/2 rounded" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {popularFoods.map((food) => (
                <FoodCard key={food.id} food={food} />
              ))}
            </div>
          )}
          
          <div className="text-center mt-8 md:hidden">
            <Link 
              to="/search" 
              className="btn-primary inline-flex items-center gap-2"
            >
              Xem tất cả <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-500 to-primary-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Bắt đầu khám phá ngay!
          </h2>
          <p className="text-white/90 text-lg mb-8">
            Chụp ảnh món ăn và để AI giúp bạn nhận diện, tìm hiểu thông tin và gợi ý món phù hợp
          </p>
          <Link 
            to="/recognition" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-600 rounded-xl font-semibold hover:bg-gray-100 transition-all"
          >
            <Camera size={24} />
            Nhận diện món ăn
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
