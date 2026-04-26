import { Link } from 'react-router-dom';
import { Facebook, Instagram, Youtube, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <span className="text-3xl">🍜</span>
              <span className="text-2xl font-bold text-primary-500">VietFood AI</span>
            </Link>
            <p className="text-gray-400 mb-4">
              Hệ thống nhận diện và gợi ý món ăn Việt Nam bằng trí tuệ nhân tạo.
            </p>
            <div className="flex gap-3">
              <a href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center hover:bg-primary-500 transition-all">
                <Facebook size={18} />
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center hover:bg-primary-500 transition-all">
                <Instagram size={18} />
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center hover:bg-primary-500 transition-all">
                <Youtube size={18} />
              </a>
            </div>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Tính năng</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/recognition" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Nhận diện món ăn
                </Link>
              </li>
              <li>
                <Link to="/search" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Tìm kiếm
                </Link>
              </li>
              <li>
                <Link to="/recommendations" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Gợi ý thông minh
                </Link>
              </li>
              <li>
                <Link to="/profile" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Tài khoản
                </Link>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Về chúng tôi</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Giới thiệu
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Điều khoản sử dụng
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Chính sách bảo mật
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-primary-500 transition-colors">
                  Liên hệ
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Liên hệ</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-gray-400">
                <Mail size={18} />
                <span>contact@vietfoodai.com</span>
              </li>
              <li className="flex items-center gap-3 text-gray-400">
                <Phone size={18} />
                <span>+84 123 456 789</span>
              </li>
              <li className="flex items-center gap-3 text-gray-400">
                <MapPin size={18} />
                <span>TP. Hồ Chí Minh, Việt Nam</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500">
          <p>&copy; 2026 VietFood AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
