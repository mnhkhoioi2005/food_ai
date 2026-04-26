import { Link } from 'react-router-dom';
import { Star, MapPin, Clock, Utensils } from 'lucide-react';

const FoodCard = ({ food }) => {
  const imageUrl = food.images?.[0]?.url || 
    food.image_url || 
    `https://source.unsplash.com/400x300/?vietnamese,food,${food.name_vi}`;

  return (
    <Link 
      to={`/food/${food.id}`}
      className="group block bg-white rounded-2xl overflow-hidden border border-gray-100 hover:border-primary-200 hover:shadow-xl transition-all duration-300"
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <img 
          src={imageUrl}
          alt={food.name_vi}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
          }}
        />
        {food.region && (
          <span className="absolute top-3 left-3 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-medium text-gray-700">
            <MapPin size={12} className="inline-block mr-1" />
            {food.region}
          </span>
        )}
        {food.is_popular && (
          <span className="absolute top-3 right-3 px-3 py-1 bg-primary-500 text-white rounded-full text-xs font-medium">
            Phổ biến
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 group-hover:text-primary-600 transition-colors mb-1">
          {food.name_vi}
        </h3>
        {food.name_en && (
          <p className="text-sm text-gray-500 mb-2">{food.name_en}</p>
        )}

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {food.is_spicy && (
            <span className="px-2 py-0.5 bg-red-100 text-red-600 rounded text-xs">
              🌶️ Cay
            </span>
          )}
          {food.is_vegetarian && (
            <span className="px-2 py-0.5 bg-green-100 text-green-600 rounded text-xs">
              🥬 Chay
            </span>
          )}
          {food.is_soup && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded text-xs">
              🍜 Nước
            </span>
          )}
        </div>

        {/* Info */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-1 text-yellow-500">
            <Star size={14} fill="currentColor" />
            <span className="text-gray-700">{food.average_rating?.toFixed(1) || '4.5'}</span>
          </div>
          {food.prep_time && (
            <div className="flex items-center gap-1 text-gray-500">
              <Clock size={14} />
              <span>{food.prep_time} phút</span>
            </div>
          )}
          {food.calories && (
            <div className="flex items-center gap-1 text-gray-500">
              <Utensils size={14} />
              <span>{food.calories} kcal</span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
};

export default FoodCard;
