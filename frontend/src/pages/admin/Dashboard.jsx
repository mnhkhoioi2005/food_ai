import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, Utensils, Users, Camera, TrendingUp,
  Settings, LogOut, ChevronRight, Loader
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { foodAPI, userAPI, recognitionAPI } from '../../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();
  
  const [stats, setStats] = useState({
    totalFoods: 0,
    totalUsers: 0,
    totalRecognitions: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/');
      return;
    }
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [foodsRes, usersRes, recogRes] = await Promise.allSettled([
        foodAPI.getCount(),
        userAPI.getCount(),
        recognitionAPI.getStats(),
      ]);
      
      setStats({
        totalFoods: foodsRes.status === 'fulfilled' ? foodsRes.value?.data?.count || 0 : 0,
        totalUsers: usersRes.status === 'fulfilled' ? usersRes.value?.data?.count || 0 : 0,
        totalRecognitions: recogRes.status === 'fulfilled' ? recogRes.value?.data?.total || 0 : 0,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const menuItems = [
    { path: '/admin', label: 'Dashboard', icon: <LayoutDashboard size={20} />, active: true },
    { path: '/admin/foods', label: 'Quản lý món ăn', icon: <Utensils size={20} /> },
    { path: '/admin/users', label: 'Quản lý người dùng', icon: <Users size={20} /> },
  ];

  const statCards = [
    { 
      label: 'Tổng món ăn', 
      value: stats.totalFoods, 
      icon: <Utensils className="text-primary-500" size={24} />,
      color: 'bg-primary-50',
      link: '/admin/foods'
    },
    { 
      label: 'Người dùng', 
      value: stats.totalUsers, 
      icon: <Users className="text-blue-500" size={24} />,
      color: 'bg-blue-50',
      link: '/admin/users'
    },
    { 
      label: 'Lượt nhận diện', 
      value: stats.totalRecognitions, 
      icon: <Camera className="text-green-500" size={24} />,
      color: 'bg-green-50',
      link: '#'
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 z-40">
        {/* Logo */}
        <div className="h-20 flex items-center px-6 border-b">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🍜</span>
            <span className="text-xl font-bold gradient-text">Admin</span>
          </Link>
        </div>

        {/* Menu */}
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

        {/* User Section */}
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
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-xl transition-all"
          >
            <LogOut size={18} />
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-600">Tổng quan hệ thống VietFood AI</p>
        </div>

        {/* Stats */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader className="w-8 h-8 text-primary-500 animate-spin" />
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {statCards.map((stat, idx) => (
              <Link
                key={idx}
                to={stat.link}
                className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                    {stat.icon}
                  </div>
                  <ChevronRight className="text-gray-400" size={20} />
                </div>
                <p className="text-3xl font-bold text-gray-800 mb-1">{stat.value}</p>
                <p className="text-gray-500">{stat.label}</p>
              </Link>
            ))}
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Thao tác nhanh</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Link 
              to="/admin/foods"
              className="p-4 bg-primary-50 rounded-xl hover:bg-primary-100 transition-all"
            >
              <Utensils className="text-primary-500 mb-2" size={24} />
              <p className="font-medium text-gray-800">Thêm món ăn mới</p>
              <p className="text-sm text-gray-500">Thêm món ăn vào cơ sở dữ liệu</p>
            </Link>
            <Link 
              to="/admin/users"
              className="p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-all"
            >
              <Users className="text-blue-500 mb-2" size={24} />
              <p className="font-medium text-gray-800">Quản lý người dùng</p>
              <p className="text-sm text-gray-500">Xem và quản lý tài khoản</p>
            </Link>
            <Link 
              to="/"
              className="p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-all"
            >
              <TrendingUp className="text-green-500 mb-2" size={24} />
              <p className="font-medium text-gray-800">Xem trang chính</p>
              <p className="text-sm text-gray-500">Quay lại giao diện người dùng</p>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
