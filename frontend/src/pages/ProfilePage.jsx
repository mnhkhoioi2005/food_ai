import { useState, useEffect } from 'react';
import { 
  User, Mail, Lock, Settings, Heart, History, 
  Camera, Loader, Save, AlertCircle, CheckCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authAPI, recognitionAPI, recommendationAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  
  // Profile state
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    spicy_level: user?.spicy_level || 3,
    prefer_soup: user?.prefer_soup || false,
    is_vegetarian: user?.is_vegetarian || false,
    favorite_regions: user?.favorite_regions || [],
    allergens: user?.allergens || [],
  });
  
  // Password state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  // History state
  const [recognitionHistory, setRecognitionHistory] = useState([]);
  const [interactionHistory, setInteractionHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'history') {
      loadHistory();
    }
  }, [activeTab]);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const [recogRes, interactRes] = await Promise.all([
        recognitionAPI.getHistory(20),
        recommendationAPI.getHistory(20),
      ]);
      setRecognitionHistory(recogRes.data || []);
      setInteractionHistory(interactRes.data || []);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await authAPI.updateMe(profileData);
      updateUser(response.data);
      toast.success('Cập nhật thông tin thành công!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setLoading(false);
    }
  };

  const handlePreferencesUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await authAPI.updateMe(preferences);
      updateUser(response.data);
      toast.success('Cập nhật sở thích thành công!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }
    
    if (passwordData.new_password.length < 6) {
      toast.error('Mật khẩu mới phải có ít nhất 6 ký tự');
      return;
    }
    
    setLoading(true);
    
    try {
      await authAPI.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      toast.success('Đổi mật khẩu thành công!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Mật khẩu hiện tại không đúng');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Thông tin', icon: <User size={18} /> },
    { id: 'preferences', label: 'Sở thích', icon: <Heart size={18} /> },
    { id: 'security', label: 'Bảo mật', icon: <Lock size={18} /> },
    { id: 'history', label: 'Lịch sử', icon: <History size={18} /> },
  ];

  const regions = ['Miền Bắc', 'Miền Trung', 'Miền Nam'];
  const allergens = ['Đậu phộng', 'Hải sản', 'Sữa', 'Trứng', 'Gluten', 'Đậu nành'];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Tài khoản của bạn</h1>
        <p className="text-gray-600">Quản lý thông tin cá nhân và sở thích</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <div className="w-full md:w-64 flex-shrink-0">
          {/* User Card */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 text-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 text-white flex items-center justify-center text-3xl font-bold mx-auto mb-4">
              {user?.full_name?.[0] || user?.email?.[0] || 'U'}
            </div>
            <h3 className="font-semibold text-gray-800">{user?.full_name || 'User'}</h3>
            <p className="text-sm text-gray-500">{user?.email}</p>
            <span className="inline-block mt-2 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium">
              {user?.role === 'admin' ? 'Quản trị viên' : 'Thành viên'}
            </span>
          </div>

          {/* Navigation */}
          <nav className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-600 border-l-4 border-primary-500'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <form onSubmit={handleProfileUpdate} className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <User size={20} />
                  Thông tin cá nhân
                </h2>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Họ và tên
                  </label>
                  <input
                    type="text"
                    value={profileData.full_name}
                    onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={profileData.email}
                    disabled
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Email không thể thay đổi</p>
                </div>
                
                <button 
                  type="submit" 
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                >
                  {loading ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
                  Lưu thay đổi
                </button>
              </form>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <form onSubmit={handlePreferencesUpdate} className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Heart size={20} />
                  Sở thích ẩm thực
                </h2>
                
                {/* Spicy Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Độ cay ưa thích: {preferences.spicy_level}/5
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={preferences.spicy_level}
                    onChange={(e) => setPreferences({ ...preferences, spicy_level: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Không cay</span>
                    <span>Cực cay</span>
                  </div>
                </div>
                
                {/* Toggles */}
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.prefer_soup}
                      onChange={(e) => setPreferences({ ...preferences, prefer_soup: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                    />
                    <span className="text-gray-700">Thích món nước</span>
                  </label>
                  
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.is_vegetarian}
                      onChange={(e) => setPreferences({ ...preferences, is_vegetarian: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                    />
                    <span className="text-gray-700">Ăn chay</span>
                  </label>
                </div>
                
                {/* Favorite Regions */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Vùng miền yêu thích
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {regions.map((region) => (
                      <button
                        key={region}
                        type="button"
                        onClick={() => {
                          const newRegions = preferences.favorite_regions?.includes(region)
                            ? preferences.favorite_regions.filter(r => r !== region)
                            : [...(preferences.favorite_regions || []), region];
                          setPreferences({ ...preferences, favorite_regions: newRegions });
                        }}
                        className={`px-4 py-2 rounded-xl transition-all ${
                          preferences.favorite_regions?.includes(region)
                            ? 'bg-primary-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {region}
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Allergens */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dị ứng thực phẩm
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {allergens.map((allergen) => (
                      <button
                        key={allergen}
                        type="button"
                        onClick={() => {
                          const newAllergens = preferences.allergens?.includes(allergen)
                            ? preferences.allergens.filter(a => a !== allergen)
                            : [...(preferences.allergens || []), allergen];
                          setPreferences({ ...preferences, allergens: newAllergens });
                        }}
                        className={`px-4 py-2 rounded-xl transition-all ${
                          preferences.allergens?.includes(allergen)
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {allergen}
                      </button>
                    ))}
                  </div>
                </div>
                
                <button 
                  type="submit" 
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                >
                  {loading ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
                  Lưu thay đổi
                </button>
              </form>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <form onSubmit={handlePasswordChange} className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Lock size={20} />
                  Đổi mật khẩu
                </h2>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mật khẩu hiện tại
                  </label>
                  <input
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mật khẩu mới
                  </label>
                  <input
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Xác nhận mật khẩu mới
                  </label>
                  <input
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none"
                  />
                </div>
                
                <button 
                  type="submit" 
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                >
                  {loading ? <Loader className="animate-spin" size={18} /> : <Lock size={18} />}
                  Đổi mật khẩu
                </button>
              </form>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <History size={20} />
                  Lịch sử hoạt động
                </h2>
                
                {historyLoading ? (
                  <div className="text-center py-8">
                    <Loader className="w-8 h-8 text-primary-500 animate-spin mx-auto" />
                  </div>
                ) : (
                  <>
                    {/* Recognition History */}
                    <div>
                      <h3 className="font-medium text-gray-700 mb-3 flex items-center gap-2">
                        <Camera size={16} />
                        Nhận diện gần đây
                      </h3>
                      {recognitionHistory.length > 0 ? (
                        <div className="space-y-2">
                          {recognitionHistory.slice(0, 5).map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                              <div>
                                <p className="font-medium text-gray-800">{item.food_name || 'Món ăn'}</p>
                                <p className="text-xs text-gray-500">
                                  {new Date(item.created_at).toLocaleString('vi-VN')}
                                </p>
                              </div>
                              <span className="text-sm text-primary-600">
                                {((item.confidence || 0) * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">Chưa có lịch sử nhận diện</p>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
