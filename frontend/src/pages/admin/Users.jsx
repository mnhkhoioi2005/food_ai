import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, Utensils, Users, Search, Edit, Trash2,
  Loader, X, Save, LogOut, Shield, User as UserIcon
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { userAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AdminUsers = () => {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();
  
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    role: 'user',
    is_active: true,
  });

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/');
      return;
    }
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await userAPI.getAll({ limit: 100 });
      setUsers(response.data.users || response.data || []);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Không thể tải danh sách người dùng');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const openEditModal = (userItem) => {
    setEditingUser(userItem);
    setFormData({
      full_name: userItem.full_name || '',
      email: userItem.email || '',
      role: userItem.role || 'user',
      is_active: userItem.is_active !== false,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await userAPI.update(editingUser.id, formData);
      toast.success('Cập nhật người dùng thành công!');
      setShowModal(false);
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const handleDelete = async (userItem) => {
    if (userItem.id === user?.id) {
      toast.error('Không thể xóa tài khoản của chính bạn');
      return;
    }
    
    if (!confirm(`Bạn có chắc muốn xóa người dùng "${userItem.full_name || userItem.email}"?`)) return;
    
    try {
      await userAPI.delete(userItem.id);
      toast.success('Đã xóa người dùng');
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  const filteredUsers = users.filter(u => 
    u.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const menuItems = [
    { path: '/admin', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/admin/foods', label: 'Quản lý món ăn', icon: <Utensils size={20} /> },
    { path: '/admin/users', label: 'Quản lý người dùng', icon: <Users size={20} />, active: true },
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
            <h1 className="text-2xl font-bold text-gray-800">Quản lý người dùng</h1>
            <p className="text-gray-600">{users.length} người dùng</p>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-2xl border border-gray-100 p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm người dùng..."
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
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Người dùng</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Email</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Vai trò</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Trạng thái</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">Ngày tạo</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-700">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredUsers.map((userItem) => (
                  <tr key={userItem.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center font-semibold">
                          {userItem.full_name?.[0] || userItem.email?.[0] || '?'}
                        </div>
                        <span className="font-medium text-gray-800">
                          {userItem.full_name || 'No name'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{userItem.email}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        userItem.role === 'admin'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {userItem.role === 'admin' ? <Shield size={12} /> : <UserIcon size={12} />}
                        {userItem.role === 'admin' ? 'Admin' : 'User'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        userItem.is_active !== false
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {userItem.is_active !== false ? 'Hoạt động' : 'Bị khóa'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {userItem.created_at 
                        ? new Date(userItem.created_at).toLocaleDateString('vi-VN')
                        : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEditModal(userItem)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(userItem)}
                          disabled={userItem.id === user?.id}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
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
          
          {!loading && filteredUsers.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Không tìm thấy người dùng nào</p>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && editingUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-800">
                Chỉnh sửa người dùng
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Họ và tên
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  disabled
                  className="w-full px-4 py-2 border border-gray-200 rounded-xl bg-gray-50 text-gray-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vai trò
                </label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:border-primary-500 outline-none"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-5 h-5 rounded border-gray-300 text-primary-500"
                  />
                  <span className="text-gray-700">Tài khoản hoạt động</span>
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
                  Cập nhật
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;
