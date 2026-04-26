import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Menu, X, Search, Camera, Utensils, MapPin, 
  User, LogOut, Settings, ChevronDown, MessageCircle
} from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, isAdmin } = useAuth();

  const navItems = [
    { path: '/', label: 'Trang chủ', icon: <Utensils size={18} /> },
    { path: '/recognition', label: 'Nhận diện', icon: <Camera size={18} /> },
    { path: '/search', label: 'Tìm kiếm', icon: <Search size={18} /> },
    { path: '/recommendations', label: 'Gợi ý', icon: <MapPin size={18} /> },
    { path: '/chat', label: 'AI Chat', icon: <MessageCircle size={18} />, badge: 'AI' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsDropdownOpen(false);
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="h-20 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-3xl">🍜</span>
            <span className="text-2xl font-bold gradient-text">VietFood AI</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all relative
                  ${location.pathname === item.path
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white'
                    : 'text-gray-600 hover:bg-primary-50 hover:text-primary-600'
                  }`}
              >
                {item.icon}
                <span>{item.label}</span>
                {item.badge && (
                  <span className="absolute -top-1 -right-1 text-[9px] font-bold bg-red-500 text-white px-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            ))}
          </nav>

          {/* Auth Section */}
          <div className="hidden md:flex items-center gap-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-50 text-primary-600 hover:bg-primary-100 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm font-semibold">
                    {user?.full_name?.[0] || user?.email?.[0] || 'U'}
                  </div>
                  <span className="font-medium">{user?.full_name || 'User'}</span>
                  <ChevronDown size={16} />
                </button>
                
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border animate-fadeIn">
                    <div className="p-3 border-b">
                      <p className="font-medium text-gray-800">{user?.full_name}</p>
                      <p className="text-sm text-gray-500">{user?.email}</p>
                    </div>
                    <div className="py-2">
                      <Link
                        to="/profile"
                        onClick={() => setIsDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50"
                      >
                        <User size={18} />
                        <span>Tài khoản</span>
                      </Link>
                      {isAdmin() && (
                        <Link
                          to="/admin"
                          onClick={() => setIsDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50"
                        >
                          <Settings size={18} />
                          <span>Quản trị</span>
                        </Link>
                      )}
                      <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 w-full"
                      >
                        <LogOut size={18} />
                        <span>Đăng xuất</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="px-4 py-2 text-gray-600 font-medium hover:text-primary-600 transition-all"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium hover:from-primary-600 hover:to-primary-700 transition-all"
                >
                  Đăng ký
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-gray-600"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t animate-slideIn">
            <nav className="flex flex-col gap-2">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium
                    ${location.pathname === item.path
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
              
              <div className="border-t my-2 pt-2">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/profile"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-gray-700"
                    >
                      <User size={18} />
                      <span>Tài khoản</span>
                    </Link>
                    {isAdmin() && (
                      <Link
                        to="/admin"
                        onClick={() => setIsMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-3 text-gray-700"
                      >
                        <Settings size={18} />
                        <span>Quản trị</span>
                      </Link>
                    )}
                    <button
                      onClick={() => { handleLogout(); setIsMenuOpen(false); }}
                      className="flex items-center gap-3 px-4 py-3 text-red-600 w-full"
                    >
                      <LogOut size={18} />
                      <span>Đăng xuất</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setIsMenuOpen(false)}
                      className="block px-4 py-3 text-gray-700 font-medium"
                    >
                      Đăng nhập
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setIsMenuOpen(false)}
                      className="block px-4 py-3 text-primary-600 font-medium"
                    >
                      Đăng ký
                    </Link>
                  </>
                )}
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
