import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, Star, Clock, Utensils, MapPin, Heart, Share2,
  Flame, Leaf, ChefHat, Users, Loader, AlertCircle
} from 'lucide-react';
import { foodAPI, recommendationAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import FoodCard from '../components/FoodCard';
import toast from 'react-hot-toast';

const FoodDetailPage = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  
  const [food, setFood] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [similarFoods, setSimilarFoods] = useState([]);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    loadFood();
  }, [id]);

  const loadFood = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await foodAPI.getById(id);
      setFood(response.data);
      
      // Load similar foods
      try {
        const similarResponse = await recommendationAPI.getSimilar(id, 4);
        setSimilarFoods(similarResponse.data);
      } catch (err) {
        console.error('Error loading similar foods:', err);
      }
      
      // Record interaction
      if (isAuthenticated) {
        try {
          await recommendationAPI.recordInteraction({
            food_id: parseInt(id),
            interaction_type: 'view'
          });
        } catch (err) {
          console.error('Error recording interaction:', err);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Không tìm thấy món ăn');
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = async () => {
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để thêm vào yêu thích');
      return;
    }
    
    try {
      await recommendationAPI.recordInteraction({
        food_id: parseInt(id),
        interaction_type: isFavorite ? 'unfavorite' : 'favorite'
      });
      setIsFavorite(!isFavorite);
      toast.success(isFavorite ? 'Đã xóa khỏi yêu thích' : 'Đã thêm vào yêu thích');
    } catch (err) {
      toast.error('Có lỗi xảy ra');
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: food.name_vi,
        text: food.description_vi,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Đã sao chép link');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader className="w-10 h-10 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">Oops!</h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <Link to="/search" className="btn-primary">
          Quay lại tìm kiếm
        </Link>
      </div>
    );
  }

  if (!food) return null;

  const images = food.images?.length > 0 
    ? food.images 
    : [{ url: food.image_url || `https://source.unsplash.com/800x600/?vietnamese,food,${food.name_vi}` }];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Back button */}
      <Link 
        to="/search" 
        className="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6"
      >
        <ArrowLeft size={20} />
        Quay lại
      </Link>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Images */}
        <div>
          <div className="relative aspect-[4/3] rounded-3xl overflow-hidden mb-4">
            <img 
              src={images[activeImageIndex]?.url}
              alt={food.name_vi}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/800x600?text=No+Image';
              }}
            />
            
            {/* Actions */}
            <div className="absolute top-4 right-4 flex gap-2">
              <button
                onClick={handleFavorite}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                  isFavorite 
                    ? 'bg-red-500 text-white' 
                    : 'bg-white/90 text-gray-600 hover:bg-red-500 hover:text-white'
                }`}
              >
                <Heart size={20} fill={isFavorite ? 'currentColor' : 'none'} />
              </button>
              <button
                onClick={handleShare}
                className="w-10 h-10 rounded-full bg-white/90 text-gray-600 flex items-center justify-center hover:bg-primary-500 hover:text-white transition-all"
              >
                <Share2 size={20} />
              </button>
            </div>

            {/* Tags */}
            <div className="absolute bottom-4 left-4 flex gap-2">
              {food.is_spicy && (
                <span className="px-3 py-1 bg-red-500 text-white rounded-full text-sm flex items-center gap-1">
                  <Flame size={14} />
                  Cay
                </span>
              )}
              {food.is_vegetarian && (
                <span className="px-3 py-1 bg-green-500 text-white rounded-full text-sm flex items-center gap-1">
                  <Leaf size={14} />
                  Chay
                </span>
              )}
              {food.is_soup && (
                <span className="px-3 py-1 bg-blue-500 text-white rounded-full text-sm">
                  🍜 Món nước
                </span>
              )}
            </div>
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex gap-3 overflow-x-auto pb-2">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveImageIndex(idx)}
                  className={`flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden border-2 transition-all ${
                    activeImageIndex === idx 
                      ? 'border-primary-500' 
                      : 'border-transparent hover:border-gray-300'
                  }`}
                >
                  <img 
                    src={img.url}
                    alt={`${food.name_vi} ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          {/* Header */}
          <div className="mb-6">
            {food.region && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm mb-3">
                <MapPin size={14} />
                {food.region}
              </span>
            )}
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
              {food.name_vi}
            </h1>
            {food.name_en && (
              <p className="text-xl text-gray-500">{food.name_en}</p>
            )}
          </div>

          {/* Rating & Stats */}
          <div className="flex flex-wrap gap-6 mb-6">
            <div className="flex items-center gap-2">
              <div className="flex text-yellow-500">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    size={20} 
                    fill={i < Math.round(food.average_rating || 4.5) ? 'currentColor' : 'none'}
                  />
                ))}
              </div>
              <span className="text-gray-700 font-medium">
                {(food.average_rating || 4.5).toFixed(1)}
              </span>
              <span className="text-gray-500">
                ({food.rating_count || 0} đánh giá)
              </span>
            </div>
          </div>

          {/* Quick Info */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            {food.prep_time && (
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Clock className="w-6 h-6 text-primary-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Thời gian</p>
                <p className="font-semibold">{food.prep_time} phút</p>
              </div>
            )}
            {food.calories && (
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Utensils className="w-6 h-6 text-primary-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Calories</p>
                <p className="font-semibold">{food.calories} kcal</p>
              </div>
            )}
            {food.difficulty && (
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <ChefHat className="w-6 h-6 text-primary-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Độ khó</p>
                <p className="font-semibold">{food.difficulty}</p>
              </div>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Giới thiệu</h3>
            <p className="text-gray-600 leading-relaxed">
              {food.description_vi || 'Một món ăn truyền thống Việt Nam với hương vị đặc trưng.'}
            </p>
          </div>

          {/* Ingredients */}
          {food.ingredients && food.ingredients.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Nguyên liệu</h3>
              <div className="flex flex-wrap gap-2">
                {food.ingredients.map((ing, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {ing.name_vi || ing.name || ing}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Allergies */}
          {food.allergies && food.allergies.length > 0 && (
            <div className="mb-6 p-4 bg-yellow-50 rounded-xl">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Lưu ý dị ứng</h3>
              <div className="flex flex-wrap gap-2">
                {food.allergies.map((allergy, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-yellow-200 text-yellow-800 rounded-full text-sm"
                  >
                    {allergy.name_vi || allergy.name || allergy}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Nutrition Info */}
          {food.nutrition && (
            <div className="p-4 bg-green-50 rounded-xl">
              <h3 className="text-lg font-semibold text-green-800 mb-3">Thông tin dinh dưỡng</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-600">{food.nutrition.protein || 0}g</p>
                  <p className="text-sm text-gray-600">Protein</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">{food.nutrition.carbs || 0}g</p>
                  <p className="text-sm text-gray-600">Carbs</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">{food.nutrition.fat || 0}g</p>
                  <p className="text-sm text-gray-600">Chất béo</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">{food.nutrition.fiber || 0}g</p>
                  <p className="text-sm text-gray-600">Chất xơ</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Similar Foods */}
      {similarFoods.length > 0 && (
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Món ăn tương tự
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {similarFoods.map((item) => (
              <FoodCard key={item.id} food={item.food || item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FoodDetailPage;
