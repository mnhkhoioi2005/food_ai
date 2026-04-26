# 🎯 Hướng Dẫn Cải Thiện Độ Chính Xác Nhận Diện Món Ăn

## 📊 Bước 0: Chẩn đoán vấn đề trước

Trước khi làm bất cứ điều gì, hãy kiểm tra mAP của model hiện tại:

```powershell
cd D:\Code\food_ai_predict\ai_models\food_recognition

python train_yolo.py val `
  --model ../../ai_models/trained_weights/best_part1.pt `
  --data vietfood67.yaml `
  --device cpu `
  --split val
```

**Đọc kết quả:**
| mAP50 | Đánh giá | Hành động |
|---|---|---|
| < 0.40 | Kém | Cần train lại từ đầu với nhiều dữ liệu hơn |
| 0.40 – 0.60 | Trung bình | Fine-tune thêm, tăng augmentation |
| 0.60 – 0.75 | Khá | Chỉ cần điều chỉnh threshold |
| > 0.75 | Tốt | Vấn đề là ở inference/camera, không phải model |

---

## 🔴 Vấn Đề 1: Chọn Model Part Tốt Nhất (Làm Ngay)

Hiện tại bạn có 5 model parts. Server đang ensemble tất cả, nhưng các model kém sẽ làm giảm độ chính xác.

### Cách xác định model tốt nhất:

```powershell
# Validate từng model, xem mAP50 của cái nào cao nhất
cd D:\Code\food_ai_predict\ai_models\food_recognition

foreach ($i in 1..5) {
  Write-Host "=== Testing best_part$i.pt ===" -ForegroundColor Yellow
  python train_yolo.py val `
    --model "../../ai_models/trained_weights/best_part$i.pt" `
    --data vietfood67.yaml `
    --device cpu `
    --split val
}
```

### Sau khi biết model tốt nhất:

```powershell
# Ví dụ: best_part3.pt có mAP cao nhất → copy thành best.pt
copy D:\Code\food_ai_predict\ai_models\trained_weights\best_part3.pt `
     D:\Code\food_ai_predict\ai_models\trained_weights\best.pt
```

Rồi cập nhật `.env` trong `ai_server`:
```env
# Chỉ dùng 1 model tốt nhất (tắt ensemble với model kém)
USE_ENSEMBLE=false
YOLO_MODEL_PATH=../ai_models/trained_weights/best.pt
```

---

## 🔴 Vấn Đề 2: Train Lại Với Model Lớn Hơn

Script train hiện tại dùng `yolov8n` (nano). Với 68 class phức tạp, cần ít nhất `yolov8s` hoặc `yolov8m`.

### So sánh model sizes:

| Model | Parameters | mAP (COCO) | Tốc độ | Phù hợp |
|---|---|---|---|---|
| yolov8n | 3.2M | 37.3 | Nhanh nhất | Không đủ cho 68 class |
| yolov8s | 11.2M | 44.9 | Nhanh | ✅ Tối thiểu nên dùng |
| **yolov8m** | **25.9M** | **50.2** | **Vừa** | ✅ **Khuyến nghị** |
| yolov8l | 43.7M | 52.9 | Chậm | Nếu có GPU mạnh |

### Lệnh train với model lớn hơn:

```powershell
cd D:\Code\food_ai_predict\ai_models\food_recognition

# Train với YOLOv8s (nhẹ hơn, nhanh hơn)
python train_yolo.py train `
  --data vietfood67.yaml `
  --model yolov8s.pt `
  --epochs 150 `
  --batch 16 `
  --imgsz 640 `
  --device 0 `
  --optimizer AdamW `
  --lr0 0.001 `
  --cos-lr `
  --mosaic 1.0 `
  --mixup 0.1

# Hoặc train với YOLOv8m (khuyến nghị nếu có đủ RAM/GPU)
python train_yolo.py train `
  --data vietfood67.yaml `
  --model yolov8m.pt `
  --epochs 200 `
  --batch 8 `
  --imgsz 640 `
  --device 0 `
  --optimizer AdamW `
  --lr0 0.001 `
  --cos-lr `
  --patience 30
```

---

## 🔴 Vấn Đề 3: Tăng Chất Lượng Dữ Liệu

### 3a. Kiểm tra số lượng ảnh hiện tại:

```powershell
# Đếm ảnh theo từng split
$dataDir = "D:\datasets\vietfood67\images"
Write-Host "Train: $((Get-ChildItem "$dataDir\train" -File).Count) ảnh"
Write-Host "Val:   $((Get-ChildItem "$dataDir\val"   -File).Count) ảnh"
Write-Host "Test:  $((Get-ChildItem "$dataDir\test"  -File -ErrorAction SilentlyContinue).Count) ảnh"
```

**Tiêu chuẩn tối thiểu:** Mỗi class cần ít nhất **100–200 ảnh** trong tập train.

### 3b. Thêm ảnh không đủ class:

Tải thêm ảnh từ:
- **Kaggle**: [VietFood68 dataset](https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68)
- **Google Images** + label thủ công bằng [Label Studio](https://labelstud.io/) hoặc [Roboflow](https://roboflow.com/)
- **Chụp thêm** ảnh thực tế từ điện thoại (giống điều kiện camera)

### 3c. Thêm ảnh từ camera thực tế (giải quyết domain gap):

```
Vấn đề: Model train trên ảnh đẹp từ internet, nhưng camera cho ảnh mờ/góc nghiêng
Giải pháp: Thu thập thêm ảnh từ camera thực dưới nhiều điều kiện khác nhau
```

Chụp ảnh với:
- ✅ Góc nhìn từ trên xuống (như chụp món ăn trên bàn)
- ✅ Ánh sáng đèn trong nhà (không phải studio)
- ✅ Background thực tế (khăn trải bàn, đĩa, đũa)
- ✅ Multiple góc chụp (thẳng, 45 độ)
- ❌ Tránh ảnh chỉ là sản phẩm trắng background

---

## 🟡 Vấn Đề 4: Điều Chỉnh Thresholds

Sửa file `ai_server/.env`:

```env
# Confidence threshold:
# - Cao hơn (0.4-0.5) = ít kết quả hơn nhưng chính xác hơn
# - Thấp hơn (0.15-0.2) = nhiều kết quả hơn nhưng có thể sai
CONFIDENCE_THRESHOLD=0.35

# IOU threshold:
# - Thấp hơn = merge boxes tích cực hơn
IOU_THRESHOLD=0.45
```

**Gợi ý theo tình huống:**

| Tình huống | CONFIDENCE_THRESHOLD |
|---|---|
| Thường xuyên nhận diện sai (false positive) | Tăng lên 0.40–0.50 |
| Thường xuyên không nhận diện được | Giảm xuống 0.20–0.25 |
| Cân bằng (khuyến nghị) | 0.30–0.35 |

---

## 🟡 Vấn Đề 5: Cải Thiện Augmentation Khi Train Lại

Thêm augmentation để model quen với điều kiện camera:

```python
# Trong train_yolo.py, hoặc tạo file train_improved.py
model.train(
    data="vietfood67.yaml",
    model="yolov8m.pt",
    epochs=200,
    imgsz=640,
    
    # Augmentation mạnh hơn để giống camera thực
    hsv_h=0.015,      # Color jitter (hue)
    hsv_s=0.7,        # Color jitter (saturation)  
    hsv_v=0.4,        # Brightness variation (giống ánh sáng thực)
    degrees=10,        # Rotation nhẹ
    translate=0.1,     # Translation
    scale=0.5,         # Scale variation
    shear=2.0,         # Shear
    perspective=0.001, # Perspective (giống góc nhìn camera)
    flipud=0.0,        # Không lật dọc
    fliplr=0.5,        # Lật ngang
    mosaic=1.0,        # Mosaic
    mixup=0.15,        # Mixup giúp giảm overfitting
    copy_paste=0.1,    # Copy-paste augmentation
    blur=0.01,         # Blur nhẹ (giống camera mờ)
    
    # Optimizer
    optimizer="AdamW",
    lr0=0.001,
    lrf=0.01,
    cos_lr=True,
    warmup_epochs=3,
    weight_decay=0.0005,
    label_smoothing=0.1,  # Giảm overconfidence
)
```

---

## 🟢 Vấn Đề 6: Cải Thiện Inference (Không Cần Train Lại)

Sửa `ai_server/yolo_model.py` — giảm số crops TTA để nhanh hơn và ổn định hơn:

```python
# Trong _make_tta_crops, giảm từ 8 crops xuống 3 crops
def _make_tta_crops(self, image):
    w, h = image.size
    crops = [image]  # 1. Ảnh gốc (quan trọng nhất)
    
    # 2. Center crop nhẹ
    m = 0.05
    crops.append(image.crop((int(w*m), int(h*m), int(w*(1-m)), int(h*(1-m)))))
    
    # 3. Flip ngang
    crops.append(image.transpose(Image.FLIP_LEFT_RIGHT))
    
    return crops
```

---

## 📋 Tóm Tắt Thứ Tự Ưu Tiên

```
1. ✅ [Ngay] Validate từng model part → chọn model tốt nhất
2. ✅ [Ngay] Điều chỉnh CONFIDENCE_THRESHOLD=0.35 trong .env
3. ⚙️  [Ngắn hạn] Train lại với yolov8m thay vì yolov8n
4. ⚙️  [Ngắn hạn] Thu thập thêm ảnh thực tế từ camera
5. 📈 [Dài hạn] Dataset augmentation mạnh hơn
```

---

## 🐛 Debug: Khi Camera Chụp Không Nhận Diện Được

Kiểm tra xem ảnh từ camera có vấn đề gì:

```python
# Chạy script debug này
from PIL import Image
import requests, io

# Lấy ảnh từ camera → lưu → test với model trực tiếp
# Hoặc test với YOLO CLI:
# python -m ultralytics predict model=best_part1.pt source=test_image.jpg conf=0.1
```

Nếu confidence của kết quả đúng < 0.25 → vấn đề là domain gap (cần thêm ảnh camera).
Nếu model predict sai class hoàn toàn → vấn đề là model quality (cần train lại).
