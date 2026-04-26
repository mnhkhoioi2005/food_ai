# VietFood67 Training Guide
## Vietnamese Food Detection & Classification
Dataset: https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68

## 📁 Cấu trúc thư mục

```
ai_models/food_recognition/
├── train_yolo.py           # Train YOLO detection model
├── train_classification.py # Train classification model (EfficientNet, ViT, etc.)
├── dataset_utils.py        # Dataset utilities (convert, split, analyze)
├── vietfood67.yaml         # Dataset config cho YOLO
├── requirements.txt        # Dependencies
└── README.md               # Guide này
```

## 🚀 Quick Start

### 1. Cài đặt dependencies

```bash
cd ai_models/food_recognition
pip install -r requirements.txt
```

### 2. Download dataset từ Kaggle

```bash
# Cài đặt Kaggle CLI
pip install kaggle

# Download dataset (cần setup Kaggle API key trước)
kaggle datasets download -d thomasnguyen6868/vietfood68
unzip vietfood68.zip -d D:/datasets/vietfood67
```

Hoặc download thủ công từ: https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68

### 3. Cấu trúc dataset sau khi download

```
D:/datasets/vietfood67/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   └── ...
│   ├── val/
│   │   └── ...
│   └── test/
│       └── ...
└── labels/
    ├── train/
    │   ├── image1.txt  # YOLO format: class_id x_center y_center width height
    │   └── ...
    ├── val/
    │   └── ...
    └── test/
        └── ...
```

## 🎯 Option 1: Train YOLO Detection Model

### Tạo file config dataset

```bash
# Tự động tạo file vietfood67.yaml
python train_yolo.py create-yaml -d D:/datasets/vietfood67 -o vietfood67.yaml
```

### Train model

```bash
# YOLOv8 nano (nhẹ, nhanh)
python train_yolo.py train -d vietfood67.yaml -m yolov8n.pt -e 100 -b 16 --device 0

# YOLOv8 small (cân bằng)
python train_yolo.py train -d vietfood67.yaml -m yolov8s.pt -e 100 -b 16 --device 0

# YOLOv8 medium (chính xác hơn)
python train_yolo.py train -d vietfood67.yaml -m yolov8m.pt -e 100 -b 8 --device 0

# YOLOv8 large (best accuracy)
python train_yolo.py train -d vietfood67.yaml -m yolov8l.pt -e 100 -b 4 --device 0

# YOLO11 (newest)
python train_yolo.py train -d vietfood67.yaml -m yolo11n.pt -e 100 -b 16 --device 0
```

### Training với các tùy chọn nâng cao

```bash
python train_yolo.py train \
    -d vietfood67.yaml \
    -m yolov8m.pt \
    -e 150 \
    -b 16 \
    --imgsz 640 \
    --device 0 \
    --patience 50 \
    --workers 8 \
    --cache \
    --optimizer AdamW \
    --lr0 0.01 \
    --cos-lr \
    --mosaic 1.0 \
    --mixup 0.1 \
    --name vietfood_yolov8m
```

### Validate model

```bash
python train_yolo.py val -m runs/vietfood/vietfood_yolov8m/weights/best.pt -d vietfood67.yaml
```

### Export model

```bash
# Export sang ONNX
python train_yolo.py export -m runs/vietfood/vietfood_yolov8m/weights/best.pt -f onnx

# Export sang TensorRT (NVIDIA)
python train_yolo.py export -m runs/vietfood/vietfood_yolov8m/weights/best.pt -f engine

# Export sang OpenVINO
python train_yolo.py export -m runs/vietfood/vietfood_yolov8m/weights/best.pt -f openvino
```

### Predict

```bash
python train_yolo.py predict \
    -m runs/vietfood/vietfood_yolov8m/weights/best.pt \
    -s path/to/image.jpg \
    --conf 0.25 \
    --save
```

## 🎯 Option 2: Train Classification Model

Nếu bạn muốn train classification model (chỉ phân loại, không detect bounding box):

### Convert YOLO dataset sang Classification format

```bash
# Crop bounding boxes thành images riêng lẻ
python dataset_utils.py convert -i D:/datasets/vietfood67 -o D:/datasets/vietfood67_cls

# Không crop, chỉ copy ảnh gốc
python dataset_utils.py convert -i D:/datasets/vietfood67 -o D:/datasets/vietfood67_cls --no-crop
```

### Train classification

```bash
# EfficientNet-B0 (nhẹ, nhanh)
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m efficientnet_b0 \
    -e 100 \
    -b 32 \
    --img-size 224

# EfficientNet-B3 (cân bằng)
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m efficientnet_b3 \
    -e 100 \
    -b 16 \
    --img-size 300

# ResNet-50
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m resnet50 \
    -e 100 \
    -b 32 \
    --img-size 224

# Vision Transformer (cần timm)
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m vit_base_patch16_224 \
    -e 100 \
    -b 16 \
    --img-size 224

# ConvNeXt
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m convnext_tiny \
    -e 100 \
    -b 32 \
    --img-size 224
```

### Training với đầy đủ options

```bash
python train_classification.py \
    -d D:/datasets/vietfood67_cls \
    -m efficientnet_b2 \
    -e 100 \
    -b 32 \
    --img-size 260 \
    --lr 0.001 \
    --weight-decay 1e-4 \
    --optimizer adamw \
    --scheduler cosine \
    --dropout 0.3 \
    --label-smoothing 0.1 \
    --patience 20 \
    --auto-augment randaugment \
    --device cuda \
    --project runs/classify \
    --name efficientnet_b2_vietfood
```

## 🔧 Dataset Utilities

### Phân tích dataset

```bash
python dataset_utils.py analyze -i D:/datasets/vietfood67
```

### Split dataset (nếu cần)

```bash
python dataset_utils.py split -i D:/datasets/vietfood67_cls --train 0.8 --val 0.1 --test 0.1
```

### Verify dataset (kiểm tra ảnh lỗi)

```bash
# Chỉ kiểm tra
python dataset_utils.py verify -i D:/datasets/vietfood67

# Kiểm tra và xóa ảnh lỗi
python dataset_utils.py verify -i D:/datasets/vietfood67 --fix
```

## 📊 Recommended Settings

### Cho GPU RTX 3060/3070/3080 (8-12GB VRAM)

| Model | Image Size | Batch Size | Epochs |
|-------|------------|------------|--------|
| YOLOv8n | 640 | 32 | 100 |
| YOLOv8s | 640 | 16 | 100 |
| YOLOv8m | 640 | 8 | 100 |
| EfficientNet-B0 | 224 | 64 | 100 |
| EfficientNet-B3 | 300 | 32 | 100 |
| ViT-Base | 224 | 16 | 100 |

### Cho GPU RTX 4090 / A100 (24GB+ VRAM)

| Model | Image Size | Batch Size | Epochs |
|-------|------------|------------|--------|
| YOLOv8l | 640 | 16 | 150 |
| YOLOv8x | 640 | 8 | 150 |
| EfficientNet-B4 | 380 | 32 | 100 |
| ViT-Large | 224 | 32 | 100 |

## 🎯 Tips để training tốt hơn

1. **Sử dụng cache**: Thêm `--cache` để cache dataset vào RAM
2. **Mixed precision**: Mặc định đã bật AMP, giúp train nhanh hơn
3. **Data augmentation**: Mosaic và MixUp giúp tăng accuracy
4. **Learning rate**: Bắt đầu với lr=0.01, dùng cosine scheduler
5. **Early stopping**: patience=50 để tránh overfitting
6. **Pretrained weights**: Luôn dùng pretrained từ ImageNet

## 📈 Expected Results

Với dataset VietFood67 (~33,000 images, 68 classes):

- YOLOv8n: mAP50 ~75-80%
- YOLOv8m: mAP50 ~82-87%
- YOLOv8l: mAP50 ~85-90%

Classification:
- EfficientNet-B0: Accuracy ~85-88%
- EfficientNet-B3: Accuracy ~88-92%
- ViT-Base: Accuracy ~87-91%

## 🔗 References

- [VietFood67 Dataset](https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [timm Models](https://huggingface.co/docs/timm/index)
- [PyTorch](https://pytorch.org/docs/stable/index.html)
