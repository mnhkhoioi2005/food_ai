import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, Utensils, Users, Plus, Search, Edit, Trash2,
  Loader, AlertCircle, X, Save, LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { foodAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AdminFoods = () => {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();
  
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingFood, setEditingFood] = useState(null);
  const [formData, setFormData] = useState({
    name_vi: '',
    name_en: '',
    description_vi: '',
    region: '',
    is_spicy: false,
    is_vegetarian: false,
    is_soup: false,
    calories: '',
    prep_time: '',
    image_url: '',
  });

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/');
      return;
    }
    loadFoods();
  }, []);

  const loadFoods = async () => {
    setLoading(true);
    try {
      const response = await foodAPI.search({ limit: 100 });
      setFoods(response.data.foods || response.data || []);
    } catch (error) {
      console.error('Error loading foods:', error);
      toast.error('Không thể tải danh sách món ăn');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const openAddModal = () => {
    setEditingFood(null);
    setFormData({
      name_vi: '',
      name_en: '',
      description_vi: '',
      region: '',
      is_spicy: false,
      is_vegetarian: false,
      is_soup: false,
      calories: '',
      prep_time: '',
      image_url: '',
    });
    setShowModal(true);
  };

  const openEditModal = (food) => {
    setEditingFood(food);
    setFormData({
      name_vi: food.name_vi || '',
      name_en: food.name_en || '',
      description_vi: food.description_vi || '',
      region: food.region || '',
      is_spicy: food.is_spicy || false,
      is_vegetarian: food.is_vegetarian || false,
      is_soup: food.is_soup || false,
      calories: food.calories || '',
      prep_time: food.prep_time || '',
      image_url: food.image_url || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name_vi) {
      toast.error('Vui lòng nhập tên món ăn');
      return;
    }

    try {
      const data = {
        ...formData,
        calories: formData.calories ? parseInt(formData.calories) : null,
        prep_time: formData.prep_time ? parseInt(formData.prep_time) : null,
      };

      if (editingFood) {
        await foodAPI.update(editingFood.id, data);
        toast.success('Cập nhật món ăn thành công!');
      } else {
        await foodAPI.create(data);
        toast.success('Thêm món ăn thành công!');
      }
      
      setShowModal(false);
      loadFoods();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (food) => {
    if (!confirm(`Bạn có chắc muốn xóa "${food.name_vi}"?`)) return;
    
    try {
      await foodAPI.delete(food.id);
      toast.success('Đã xóa món ăn');
      loadFoods();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const filteredFoods = foods.filter(food => 
    food.name_vi?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    food.name_en?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const menuItems = [
    { path: '/admin', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/admin/foods', label: 'Quản lý món ăn', icon: <Utensils size={20} />, active: true },
    { path: '/admin/users', label: 'Quản lý người dùng', icon: <Users size={20} /> },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 z-40">
        <div className="h-20 flex items-center px-6 border-b">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🍜</span>
            <span className="text-xl font-bold gradient-text">Admin</span>
          </Link>
        </div>

        <nav className="p-4">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all ${
                item.active
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center font-semibold">
              {user?.full_name?.[0] || 'A'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-800 truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-500">Admin</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-xl"
          >
            <LogOut size={18} />
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Quản lý món ăn</h1>
            <p className="text-gray-600">{foods.length} món ăn</p>
          </div>
          <button
            onClick={openAddModal}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            Thêm món ăn
          </button>
        </div>

        {/* Search */}
        <div className="bg-white rounded-2xl border border-gray-100 p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm món ăn..."
              className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader className="w-8 h-8 text-primary-500 animate-spin" />
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Món ăn</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Vùng miền</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Thuộc tính</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Calories</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-700">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredFoods.map((food) => (
                  <tr key={food.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <img
                          src={food.image_url || food.images?.[0]?.url || 'https://via.placeholder.com/48'}
                          alt={food.name_vi}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div>
                          <p className="font-medium text-gray-800">{food.name_vi}</p>
                          <p className="text-sm text-gray-500">{food.name_en}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{food.region || '-'}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {food.is_spicy && (
                          <span className="px-2 py-1 bg-red-100 text-red-600 rounded text-xs">Cay</span>
                        )}
                        {food.is_vegetarian && (
                          <span className="px-2 py-1 bg-green-100 text-green-600 rounded text-xs">Chay</span>
                        )}
                        {food.is_soup && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs">Nước</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{food.calories || '-'} kcal</td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEditModal(food)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(food)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          
          {!loading && filteredFoods.length === 0 && (
            <div className="text-center py-12">
              <Utensils className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Không tìm thấy món ăn nào</p>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-800">
                {editingFood ? 'Chỉnh sửa món ăn' : 'Thêm món ăn mới'}
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tên tiếng Việt *
                  </label>
                  <input
                    type="text"
                    value={formData.name_vi}
                    onChange={(e) => setFormData({ ...formData, name_vi: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tên tiếng Anh
                  </label>
                  <input
                    type="text"
                    value={formData.name_en}
                    onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mô tả
                </label>
                <textarea
                  value={formData.description_vi}
                  onChange={(e) => setFormData({ ...formData, description_vi: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none resize-none"
                />
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Vùng miền
                  </label>
                  <select
                    value={formData.region}
                    onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                  >
                    <option value="">Chọn vùng miền</option>
                    <option value="Miền Bắc">Miền Bắc</option>
                    <option value="Miền Trung">Miền Trung</option>
                    <option value="Miền Nam">Miền Nam</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Calories
                  </label>
                  <input
                    type="number"
                    value={formData.calories}
                    onChange={(e) => setFormData({ ...formData, calories: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Thời gian (phút)
                  </label>
                  <input
                    type="number"
                    value={formData.prep_time}
                    onChange={(e) => setFormData({ ...formData, prep_time: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL hình ảnh
                </label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                  placeholder="https://..."
                />
              </div>

              <div className="flex flex-wrap gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_spicy}
                    onChange={(e) => setFormData({ ...formData, is_spicy: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary-500"
                  />
                  <span className="text-gray-700">Cay</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_vegetarian}
                    onChange={(e) => setFormData({ ...formData, is_vegetarian: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary-500"
                  />
                  <span className="text-gray-700">Chay</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_soup}
                    onChange={(e) => setFormData({ ...formData, is_soup: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary-500"
                  />
                  <span className="text-gray-700">Món nước</span>
                </label>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-primary flex items-center justify-center gap-2"
                >
                  <Save size={18} />
                  {editingFood ? 'Cập nhật' : 'Thêm mới'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminFoods;
