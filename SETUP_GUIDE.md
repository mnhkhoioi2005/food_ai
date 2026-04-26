# 🍜 VietFood AI - Hệ thống Nhận diện và Gợi ý Món ăn Việt Nam

Hệ thống sử dụng AI để nhận diện món ăn Việt Nam qua hình ảnh và gợi ý món ăn phù hợp với khẩu vị người dùng.

## 📁 Cấu trúc dự án

```
food_ai_predict/
├── backend/           # FastAPI Backend Server
├── frontend/          # React + Vite Frontend
├── ai_server/         # AI Model Server (TensorFlow/PyTorch)
└── README.md
```

## 🚀 Hướng dẫn cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

---

## 1️⃣ Backend (FastAPI)

### Cài đặt

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (Linux/Mac)
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Cấu hình

Tạo file `.env` trong thư mục `backend/`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/vietfood_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
AI_SERVER_URL=http://localhost:8001
```

### Tạo Database

```sql
-- Chạy trong PostgreSQL
CREATE DATABASE vietfood_db;
```

### Chạy Backend

```bash
cd backend

# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc
python -m uvicorn app.main:app --reload
```

Backend sẽ chạy tại: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Seed dữ liệu mẫu

```bash
cd backend
python -m app.seed_data
```

---

## 2️⃣ AI Server (TensorFlow/PyTorch)

### Cài đặt

```bash
cd ai_server

# Tạo virtual environment
python -m venv venv

# Kích hoạt
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt
```

### Cấu hình

Tạo file `.env` trong thư mục `ai_server/`:

```env
MODEL_PATH=models/food_classifier.h5
LABELS_PATH=models/labels.json
MODEL_TYPE=tensorflow
CONFIDENCE_THRESHOLD=0.5
```

### Chạy AI Server

```bash
cd ai_server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

AI Server sẽ chạy tại: http://localhost:8001
- Health check: http://localhost:8001/health
- Predict: POST http://localhost:8001/predict

---

## 3️⃣ Frontend (React + Vite)

### Cài đặt

```bash
cd frontend

# Cài đặt dependencies
npm install
```

### Cấu hình

Tạo file `.env` trong thư mục `frontend/`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Chạy Frontend

```bash
cd frontend

# Development
npm run dev

# Build production
npm run build

# Preview production build
npm run preview
```

Frontend sẽ chạy tại: http://localhost:3000

---

## 📖 Tính năng chính

### 👤 Người dùng
- Đăng ký / Đăng nhập (JWT Authentication)
- Quản lý thông tin cá nhân
- Thiết lập sở thích ẩm thực
- Lịch sử nhận diện và tương tác

### 📷 Nhận diện món ăn
- Upload hình ảnh
- Chụp trực tiếp từ camera
- Nhận kết quả với độ tin cậy
- Xem thông tin chi tiết món ăn

### 🔍 Tìm kiếm
- Tìm theo tên món ăn
- Lọc theo vùng miền (Bắc, Trung, Nam)
- Lọc theo thuộc tính (cay, chay, món nước)
- Lọc theo calories

### ✨ Gợi ý thông minh
- Gợi ý cá nhân hóa
- Gợi ý theo xu hướng
- Gợi ý theo vị trí
- Gợi ý theo khẩu vị

### 👨‍💼 Admin
- Quản lý món ăn (CRUD)
- Quản lý người dùng
- Thống kê hệ thống

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Authentication:** JWT (python-jose)
- **Password:** bcrypt

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite 5
- **Styling:** TailwindCSS
- **Routing:** React Router 6
- **HTTP Client:** Axios
- **Camera:** react-webcam
- **Icons:** Lucide React
- **Notifications:** react-hot-toast

### AI Server
- **Deep Learning:** TensorFlow / PyTorch
- **Model:** EfficientNet / MobileNet
- **API:** FastAPI
- **Inference:** ONNX Runtime (optional)

---

## 📝 API Endpoints

### Auth
- `POST /api/v1/auth/register` - Đăng ký
- `POST /api/v1/auth/login/json` - Đăng nhập
- `GET /api/v1/auth/me` - Thông tin user hiện tại
- `PUT /api/v1/auth/me` - Cập nhật thông tin
- `POST /api/v1/auth/change-password` - Đổi mật khẩu

### Foods
- `GET /api/v1/foods` - Danh sách món ăn
- `GET /api/v1/foods/{id}` - Chi tiết món ăn
- `GET /api/v1/foods/popular` - Món phổ biến
- `GET /api/v1/foods/filters` - Bộ lọc
- `POST /api/v1/foods` - Thêm món ăn (Admin)
- `PUT /api/v1/foods/{id}` - Sửa món ăn (Admin)
- `DELETE /api/v1/foods/{id}` - Xóa món ăn (Admin)

### Recognition
- `POST /api/v1/recognition/upload` - Nhận diện từ file upload
- `POST /api/v1/recognition/camera` - Nhận diện từ camera
- `GET /api/v1/recognition/history` - Lịch sử nhận diện

### Recommendations
- `POST /api/v1/recommendations` - Lấy gợi ý
- `GET /api/v1/recommendations/personalized` - Gợi ý cá nhân
- `GET /api/v1/recommendations/nearby` - Gợi ý gần đây
- `GET /api/v1/recommendations/by-taste` - Gợi ý theo khẩu vị
- `GET /api/v1/recommendations/similar/{food_id}` - Món tương tự

### Users (Admin)
- `GET /api/v1/users` - Danh sách users
- `GET /api/v1/users/{id}` - Chi tiết user
- `PUT /api/v1/users/{id}` - Cập nhật user
- `DELETE /api/v1/users/{id}` - Xóa user

---

## 🎨 Giao diện

### Màu sắc chính
- **Primary (Orange):** #f97316
- **Secondary (Green):** #22c55e

### Responsive
- Mobile-first design
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)

---

## 👥 Tài khoản mặc định

Sau khi chạy seed data:

**Admin:**
- Email: admin@vietfood.ai
- Password: admin123

**User:**
- Email: user@example.com  
- Password: user123

---

## 📄 License

MIT License - Free to use for educational purposes.

---

## 🤝 Đóng góp

Pull requests are welcome. For major changes, please open an issue first.

---

Made with ❤️ for Vietnamese Cuisine 🇻🇳
