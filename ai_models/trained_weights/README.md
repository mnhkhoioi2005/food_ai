# Trained Weights Directory

Đặt các file model đã train vào thư mục này.

## 📁 Cấu trúc đặt tên

### Nếu có 1 model:
```
trained_weights/
└── best.pt
```

### Nếu có nhiều models (train nhiều lần):
```
trained_weights/
├── best_part1.pt      # Model train lần 1
├── best_part2.pt      # Model train lần 2
├── best_part3.pt      # Model train lần 3
├── best_part4.pt      # Model train lần 4
└── best_part5.pt      # Model train lần 5
```

Hoặc đặt tên theo epoch/checkpoint:
```
trained_weights/
├── yolov8m_epoch50.pt
├── yolov8m_epoch100.pt
├── yolov8m_epoch150.pt
└── yolov8m_final.pt
```

## 🔧 Cách server sử dụng models

Server sẽ **tự động** tìm tất cả file `.pt` trong thư mục này và:

1. **Nếu có 1 model** → Sử dụng model đó trực tiếp
2. **Nếu có nhiều models** → Tự động ensemble (kết hợp) các models

### Cấu hình Ensemble (trong `.env` hoặc `config.py`):

```env
# Bật/tắt ensemble
USE_ENSEMBLE=true

# Phương pháp ensemble
# - wbf: Weighted Boxes Fusion (recommended)
# - nms: Non-Maximum Suppression
# - voting: Voting ensemble
ENSEMBLE_METHOD=wbf

# Trọng số cho mỗi model (optional)
# Để trống = equal weights
# Ví dụ: model 1 có trọng số 1.0, model 2 có 0.8, model 3 có 1.2
ENSEMBLE_WEIGHTS=1.0,0.8,1.2
```

## 🚀 Sau khi train xong

### Copy từ output folder:
```powershell
# Windows PowerShell
copy "ai_models\food_recognition\runs\vietfood\train1\weights\best.pt" "ai_models\trained_weights\best_part1.pt"
copy "ai_models\food_recognition\runs\vietfood\train2\weights\best.pt" "ai_models\trained_weights\best_part2.pt"
# ... tiếp tục với các lần train khác
```

```bash
# Linux/Mac
cp ai_models/food_recognition/runs/vietfood/train1/weights/best.pt ai_models/trained_weights/best_part1.pt
cp ai_models/food_recognition/runs/vietfood/train2/weights/best.pt ai_models/trained_weights/best_part2.pt
```

## 📊 Test ensemble

```bash
cd ai_models/food_recognition

# Liệt kê các models
python ensemble.py list -d ../trained_weights

# Test predict
python ensemble.py predict -d ../trained_weights -s path/to/image.jpg --method wbf
```

## ⚠️ Lưu ý

- **Không đặt** các file classification model (efficientnet, resnet, vit) vào đây nếu bạn dùng YOLO
- Đặt classification models với tên có chứa `classification_`, ví dụ: `classification_best.pt`
- Server sẽ tự động phân biệt YOLO và classification models dựa trên tên file

## 📈 Tips để ensemble tốt hơn

1. **Train với các hyperparameters khác nhau**: lr, augmentation, image size
2. **Train với các subset khác nhau**: shuffle data khác nhau mỗi lần
3. **Train với các model khác nhau**: YOLOv8n, YOLOv8s, YOLOv8m
4. **Đặt trọng số cao hơn cho model có accuracy cao hơn**
