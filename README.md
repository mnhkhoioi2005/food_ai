<div align="center">

# 🍜 VietFood AI

### Hệ thống Nhận diện & Gợi ý Món ăn Việt Nam bằng AI

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF69B4?style=flat-square)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

*Nhận diện món ăn Việt Nam qua ảnh, gợi ý nhà hàng theo vị trí, và trò chuyện với AI về ẩm thực.*

</div>

---

## 📌 Giới thiệu

**VietFood AI** là ứng dụng web kết hợp Computer Vision và AI để:

- 📸 **Nhận diện món ăn** từ ảnh chụp hoặc camera trực tiếp (67 loại món Việt Nam)
- 🗺️ **Gợi ý nhà hàng** gần vị trí người dùng thông qua Google Maps
- 🤖 **Trò chuyện với AI** (Gemini) về ẩm thực Việt Nam
- 🔍 **Tìm kiếm & khám phá** món ăn theo khẩu vị, vùng miền, nguyên liệu
- 👤 **Hệ thống tài khoản** với lịch sử tương tác và gợi ý cá nhân hóa

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)             │
│           Leaflet Maps │ Gemini Chat │ Camera UI          │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API
┌───────────────────────▼─────────────────────────────────┐
│                   Backend (FastAPI)                       │
│     Auth │ Food Search │ Recommendation │ Location       │
└──────────┬────────────────────────┬────────────────────--┘
           │                        │
    ┌──────▼──────┐         ┌───────▼──────┐
    │  PostgreSQL  │         │  AI Server   │
    │  (Database)  │         │  (YOLOv8 +  │
    └─────────────┘         │  EfficientNet)│
                             └──────────────┘
```

---

## 🛠️ Công nghệ sử dụng

| Tầng | Công nghệ |
|------|-----------|
| **Frontend** | React 18, Vite, TailwindCSS, Leaflet.js, Lucide Icons |
| **Backend** | FastAPI, SQLAlchemy, Alembic, Pydantic v2, JWT |
| **AI Server** | YOLOv8 (Ultralytics), EfficientNet, Ensemble Model |
| **AI Chat** | Google Gemini API (`google-genai`) |
| **Database** | PostgreSQL 16 |
| **Maps** | Google Maps Platform, Leaflet.js + OpenStreetMap |
| **Auth** | JWT (python-jose), bcrypt |

---

## 📁 Cấu trúc dự án

```
food_ai_predict/
├── 📂 frontend/               # React + Vite app
│   ├── src/
│   │   ├── components/        # UI components (Map, Chat, Camera...)
│   │   ├── pages/             # Trang chính (Home, Map, Chat, Profile)
│   │   ├── services/          # API calls (api.js)
│   │   ├── context/           # React Context (Auth...)
│   │   └── hooks/             # Custom hooks
│   └── package.json
│
├── 📂 backend/                # FastAPI REST API
│   ├── app/
│   │   ├── api/v1/endpoints/  # auth, food_search, recognition, chat...
│   │   ├── models/            # SQLAlchemy models (User, Food, Rating...)
│   │   ├── schemas/           # Pydantic schemas
│   │   └── core/              # Config, DB connection, security
│   ├── .env.example           # Mẫu biến môi trường
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📂 ai_server/              # AI inference server (YOLOv8 + EfficientNet)
│   ├── main.py                # FastAPI AI server entry point
│   ├── yolo_model.py          # YOLOv8 inference logic
│   ├── model.py               # EfficientNet/MobileNet inference
│   ├── models/labels.json     # Nhãn 67 món ăn Việt Nam
│   ├── .env.example
│   └── requirements.txt
│
├── 📂 ai_models/              # Tài nguyên model AI
│   ├── food_recognition/      # Script huấn luyện (train_yolo.py, train_classification.py...)
│   ├── trained_weights/       # File .pt weights (không commit lên git)
│   └── exports/               # Model đã export (ONNX, TFLite...)
│
└── 📂 database/
    ├── init.sql               # Khởi tạo schema database
    └── commands.sql           # Các lệnh SQL tiện ích
```

---

## 🚀 Hướng dẫn cài đặt

### Yêu cầu

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- GPU (khuyến nghị) hoặc CPU cho inference

### 1. Clone repository

```bash
git clone https://github.com/<your-username>/food_ai_predict.git
cd food_ai_predict
```

### 2. Cài đặt Backend

```bash
cd backend

# Tạo và kích hoạt virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Cài dependencies
pip install -r requirements.txt

# Sao chép và cấu hình biến môi trường
copy .env.example .env
# Chỉnh sửa .env với thông tin database, API keys của bạn
```

### 3. Cài đặt AI Server

```bash
cd ai_server

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
# Chỉnh sửa .env, trỏ MODEL_PATH đến file weights của bạn
```

> ⚠️ **Lưu ý:** File model weights (`.pt`) không được lưu trong repository do kích thước lớn. Tải về tại [Releases](../../releases) hoặc tự huấn luyện theo hướng dẫn trong `ai_models/food_recognition/README.md`.

### 4. Cài đặt Frontend

```bash
cd frontend

npm install

copy .env.example .env
# Thêm VITE_GOOGLE_MAPS_API_KEY nếu cần
```

### 5. Khởi tạo Database

```bash
# Tạo database PostgreSQL
psql -U postgres -c "CREATE DATABASE vietfood_db;"

# Chạy schema khởi tạo
psql -U postgres -d vietfood_db -f database/init.sql
```

### 6. Chạy ứng dụng

Mở **3 terminal** riêng biệt:

```bash
# Terminal 1 — Backend API (port 8000)
cd backend && venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — AI Server (port 8001)
cd ai_server && venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 3 — Frontend (port 5173)
cd frontend
npm run dev
```

Truy cập: **http://localhost:5173**

---

## ⚙️ Biến môi trường

### `backend/.env`

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/vietfood_db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

AI_SERVER_URL=http://localhost:8001
GOOGLE_MAPS_API_KEY=your-google-maps-key
GEMINI_API_KEY=your-gemini-api-key

HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### `ai_server/.env`

```env
HOST=0.0.0.0
PORT=8001
MODEL_TYPE=yolo           # yolo | efficientnet
MODEL_PATH=../ai_models/trained_weights/best_part1.pt
LABELS_PATH=models/labels.json
CONFIDENCE_THRESHOLD=0.5
```

### `frontend/.env`

```env
VITE_API_URL=http://localhost:8000
VITE_AI_SERVER_URL=http://localhost:8001
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
```

---

## 🎯 Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| 📸 **Nhận diện qua ảnh** | Upload ảnh món ăn, AI trả về tên và thông tin chi tiết |
| 📹 **Camera trực tiếp** | Mở webcam, nhận diện real-time |
| 🗺️ **Bản đồ nhà hàng** | Hiển thị nhà hàng gần vị trí với popup tương tác |
| 💬 **AI Chat** | Hỏi đáp về ẩm thực Việt Nam với Gemini AI |
| 🔍 **Tìm kiếm món ăn** | Tìm theo tên, vùng miền, nguyên liệu |
| ⭐ **Yêu thích & Lịch sử** | Lưu món ăn, xem lịch sử tương tác |
| 👤 **Tài khoản** | Đăng ký, đăng nhập, quản lý profile |

---

## 🤖 Mô hình AI

Hệ thống sử dụng **Ensemble Model** kết hợp:
- **YOLOv8** — phát hiện và định vị món ăn trong ảnh
- **EfficientNet-B3** — phân loại chi tiết 67 món ăn Việt Nam

Dataset: **VietFood-67** — 67 loại món ăn Việt Nam từ 3 miền Bắc, Trung, Nam.

Để tự huấn luyện, xem hướng dẫn tại [`ai_models/food_recognition/README.md`](ai_models/food_recognition/README.md).

---

## 📖 API Documentation

Sau khi chạy backend, xem tài liệu API tại:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🤝 Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/ten-tinh-nang`
3. Commit thay đổi: `git commit -m 'feat: thêm tính năng X'`
4. Push lên branch: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

---

## 📄 License

Dự án này được phân phối dưới [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ for Vietnamese Cuisine

</div>
