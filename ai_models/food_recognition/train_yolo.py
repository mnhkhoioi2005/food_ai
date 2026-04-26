"""
VietFood67 - YOLO Training Script
Train YOLOv8/YOLOv11 model for Vietnamese food detection
Dataset: https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68
"""

import os
import yaml
import argparse
from pathlib import Path
from datetime import datetime

try:
    from ultralytics import YOLO
except ImportError:
    print("Please install ultralytics: pip install ultralytics")
    exit(1)


# =====================================================
# CONFIGURATION
# =====================================================

# VietFood67 Class Names (68 classes including face)
VIETFOOD_CLASSES = [
    "banh_bao", "banh_beo", "banh_bot_loc", "banh_can", "banh_canh",
    "banh_chung", "banh_cuon", "banh_da_lon", "banh_duc", "banh_gio",
    "banh_khot", "banh_mi", "banh_pia", "banh_trang_nuong", "banh_xeo",
    "bo_kho", "bun_bo_hue", "bun_cha", "bun_dau_mam_tom", "bun_mam",
    "bun_moc", "bun_rieu", "bun_thit_nuong", "ca_kho_to", "canh_chua",
    "cao_lau", "chao_long", "che", "com_chay", "com_ga",
    "com_tam", "face", "ga_nuong", "goi_cuon", "goi_ga",
    "hu_tieu", "lau", "mi_quang", "mi_xao", "nem_chua",
    "nem_nuong", "oc", "pho", "rau_muong_xao_toi", "thit_kho",
    "thit_nuong", "xoi", "che_ba_mau", "banh_flan", "sua_chua",
    "sinh_to", "nuoc_mia", "tra_sua", "ca_phe", "nuoc_dua",
    "kem", "xoi_xeo", "xoi_gac", "bap_xao", "khoai_lang_nuong",
    "trung_vit_lon", "chao", "sup", "mi_tom", "com_rang",
    "bun_cha_ca", "banh_trang_tron", "bot_chien"
]


def create_dataset_yaml(data_dir: str, output_path: str = "vietfood67.yaml"):
    """
    Tạo file cấu hình dataset cho YOLO
    
    Args:
        data_dir: Đường dẫn tới thư mục dataset (chứa images/ và labels/)
        output_path: Đường dẫn file yaml output
    """
    data_dir = Path(data_dir)
    
    # Kiểm tra cấu trúc thư mục
    images_dir = data_dir / "images"
    labels_dir = data_dir / "labels"
    
    if not images_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục images: {images_dir}")
    if not labels_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục labels: {labels_dir}")
    
    # Kiểm tra train/val/test
    train_images = images_dir / "train"
    val_images = images_dir / "val"
    test_images = images_dir / "test"
    
    # Dataset config
    dataset_config = {
        'path': str(data_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test' if test_images.exists() else 'images/val',
        'nc': len(VIETFOOD_CLASSES),
        'names': VIETFOOD_CLASSES
    }
    
    # Ghi file yaml
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(dataset_config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ Đã tạo file cấu hình: {output_path}")
    print(f"   - Số lượng classes: {len(VIETFOOD_CLASSES)}")
    print(f"   - Train path: {train_images}")
    print(f"   - Val path: {val_images}")
    
    return output_path


def train_yolo(
    data_yaml: str,
    model_name: str = "yolov8n.pt",
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    device: str = "0",
    project: str = "runs/vietfood",
    name: str = None,
    resume: bool = False,
    pretrained: bool = True,
    patience: int = 50,
    workers: int = 8,
    cache: bool = True,
    optimizer: str = "auto",
    lr0: float = 0.01,
    lrf: float = 0.01,
    momentum: float = 0.937,
    weight_decay: float = 0.0005,
    warmup_epochs: float = 3.0,
    augment: bool = True,
    mixup: float = 0.0,
    copy_paste: float = 0.0,
    mosaic: float = 1.0,
    close_mosaic: int = 10,
    freeze: int = None,
    multi_scale: bool = False,
    cos_lr: bool = False,
    label_smoothing: float = 0.0,
    **kwargs
):
    """
    Train YOLO model trên dataset VietFood67
    
    Args:
        data_yaml: Đường dẫn file cấu hình dataset
        model_name: Tên model YOLO (yolov8n/s/m/l/x.pt hoặc yolo11n/s/m/l/x.pt)
        epochs: Số epoch training
        batch_size: Batch size
        img_size: Kích thước ảnh
        device: GPU device (0, 1, 2... hoặc "cpu")
        project: Thư mục lưu kết quả
        name: Tên run
        resume: Tiếp tục training từ checkpoint
        pretrained: Sử dụng pretrained weights
        patience: Early stopping patience
        workers: Số worker cho dataloader
        cache: Cache images
        optimizer: Optimizer (SGD, Adam, AdamW, auto)
        lr0: Learning rate ban đầu
        lrf: Final learning rate (lr0 * lrf)
        momentum: SGD momentum
        weight_decay: Weight decay
        warmup_epochs: Warmup epochs
        augment: Sử dụng data augmentation
        mixup: Mixup alpha
        copy_paste: Copy-paste augmentation probability
        mosaic: Mosaic augmentation probability
        close_mosaic: Epochs to close mosaic before end
        freeze: Số layers freeze (None = không freeze)
        multi_scale: Multi-scale training
        cos_lr: Cosine learning rate scheduler
        label_smoothing: Label smoothing epsilon
    """
    # Tạo run name
    if name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = Path(model_name).stem
        name = f"{model_type}_{timestamp}"
    
    print("=" * 60)
    print("🍜 VietFood67 YOLO Training")
    print("=" * 60)
    print(f"📁 Dataset: {data_yaml}")
    print(f"🤖 Model: {model_name}")
    print(f"📊 Epochs: {epochs}")
    print(f"📦 Batch size: {batch_size}")
    print(f"📐 Image size: {img_size}")
    print(f"💾 Device: {device}")
    print(f"📂 Output: {project}/{name}")
    print("=" * 60)
    
    # Load model
    if resume:
        # Resume từ checkpoint
        checkpoint_path = Path(project) / name / "weights" / "last.pt"
        if checkpoint_path.exists():
            model = YOLO(str(checkpoint_path))
            print(f"📥 Resuming from: {checkpoint_path}")
        else:
            print(f"⚠️ Checkpoint không tồn tại, bắt đầu training mới")
            model = YOLO(model_name)
    else:
        model = YOLO(model_name)
        print(f"📥 Loaded model: {model_name}")
    
    # Training arguments
    train_args = {
        'data': data_yaml,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'device': device,
        'project': project,
        'name': name,
        'exist_ok': True,
        'pretrained': pretrained,
        'patience': patience,
        'workers': workers,
        'cache': cache,
        'optimizer': optimizer,
        'lr0': lr0,
        'lrf': lrf,
        'momentum': momentum,
        'weight_decay': weight_decay,
        'warmup_epochs': warmup_epochs,
        'augment': augment,
        'mixup': mixup,
        'copy_paste': copy_paste,
        'mosaic': mosaic,
        'close_mosaic': close_mosaic,
        'multi_scale': multi_scale,
        'cos_lr': cos_lr,
        'label_smoothing': label_smoothing,
        # Visualization & Logging
        'plots': True,
        'save': True,
        'save_period': -1,  # Save checkpoint every n epochs (-1 = chỉ best và last)
        'val': True,
        'verbose': True,
    }
    
    # Freeze layers nếu được chỉ định
    if freeze is not None:
        train_args['freeze'] = freeze
    
    # Thêm các kwargs bổ sung
    train_args.update(kwargs)
    
    # Start training
    print("\n🚀 Bắt đầu training...")
    results = model.train(**train_args)
    
    print("\n✅ Training hoàn tất!")
    print(f"📁 Results saved to: {project}/{name}")
    
    return results, model


def validate_model(
    model_path: str,
    data_yaml: str,
    batch_size: int = 16,
    img_size: int = 640,
    device: str = "0",
    conf: float = 0.001,
    iou: float = 0.6,
    split: str = "val"
):
    """
    Validate model trên dataset
    
    Args:
        model_path: Đường dẫn tới model weights
        data_yaml: Đường dẫn file cấu hình dataset
        batch_size: Batch size
        img_size: Kích thước ảnh
        device: GPU device
        conf: Confidence threshold
        iou: IoU threshold cho NMS
        split: Dataset split (val/test)
    """
    print("=" * 60)
    print("🔍 VietFood67 Model Validation")
    print("=" * 60)
    
    model = YOLO(model_path)
    
    results = model.val(
        data=data_yaml,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        conf=conf,
        iou=iou,
        split=split,
        plots=True,
        save_json=True
    )
    
    # Print metrics
    print("\n📊 Validation Results:")
    print(f"   mAP50: {results.box.map50:.4f}")
    print(f"   mAP50-95: {results.box.map:.4f}")
    print(f"   Precision: {results.box.mp:.4f}")
    print(f"   Recall: {results.box.mr:.4f}")
    
    return results


def export_model(
    model_path: str,
    format: str = "onnx",
    img_size: int = 640,
    half: bool = False,
    int8: bool = False,
    dynamic: bool = False,
    simplify: bool = True,
    opset: int = 17,
    device: str = "0"
):
    """
    Export model sang các định dạng khác
    
    Args:
        model_path: Đường dẫn tới model weights
        format: Định dạng export (onnx, torchscript, openvino, tflite, etc.)
        img_size: Kích thước ảnh
        half: FP16 quantization
        int8: INT8 quantization
        dynamic: Dynamic axes
        simplify: Simplify ONNX model
        opset: ONNX opset version
        device: GPU device
    """
    print("=" * 60)
    print(f"📤 Exporting Model to {format.upper()}")
    print("=" * 60)
    
    model = YOLO(model_path)
    
    export_path = model.export(
        format=format,
        imgsz=img_size,
        half=half,
        int8=int8,
        dynamic=dynamic,
        simplify=simplify,
        opset=opset,
        device=device
    )
    
    print(f"\n✅ Exported to: {export_path}")
    
    return export_path


def predict_image(
    model_path: str,
    source: str,
    conf: float = 0.25,
    iou: float = 0.45,
    img_size: int = 640,
    device: str = "0",
    save: bool = True,
    show: bool = False,
    save_txt: bool = False,
    save_crop: bool = False,
    project: str = "runs/predict",
    name: str = "vietfood"
):
    """
    Predict trên ảnh/video
    
    Args:
        model_path: Đường dẫn tới model weights
        source: Đường dẫn ảnh/video hoặc URL
        conf: Confidence threshold
        iou: IoU threshold cho NMS
        img_size: Kích thước ảnh
        device: GPU device
        save: Lưu kết quả
        show: Hiển thị kết quả
        save_txt: Lưu labels
        save_crop: Lưu crops
        project: Thư mục lưu kết quả
        name: Tên run
    """
    model = YOLO(model_path)
    
    results = model.predict(
        source=source,
        conf=conf,
        iou=iou,
        imgsz=img_size,
        device=device,
        save=save,
        show=show,
        save_txt=save_txt,
        save_crop=save_crop,
        project=project,
        name=name
    )
    
    return results


def main():
    parser = argparse.ArgumentParser(description="VietFood67 YOLO Training")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ===== CREATE YAML =====
    yaml_parser = subparsers.add_parser("create-yaml", help="Tạo file cấu hình dataset")
    yaml_parser.add_argument("--data-dir", "-d", type=str, required=True,
                            help="Đường dẫn thư mục dataset")
    yaml_parser.add_argument("--output", "-o", type=str, default="vietfood67.yaml",
                            help="Đường dẫn file yaml output")
    
    # ===== TRAIN =====
    train_parser = subparsers.add_parser("train", help="Train model")
    train_parser.add_argument("--data", "-d", type=str, required=True,
                             help="Đường dẫn file cấu hình dataset (yaml)")
    train_parser.add_argument("--model", "-m", type=str, default="yolov8n.pt",
                             help="Model YOLO (yolov8n/s/m/l/x.pt hoặc yolo11n/s/m/l/x.pt)")
    train_parser.add_argument("--epochs", "-e", type=int, default=100,
                             help="Số epochs")
    train_parser.add_argument("--batch", "-b", type=int, default=16,
                             help="Batch size")
    train_parser.add_argument("--imgsz", "-i", type=int, default=640,
                             help="Image size")
    train_parser.add_argument("--device", type=str, default="0",
                             help="GPU device")
    train_parser.add_argument("--project", type=str, default="runs/vietfood",
                             help="Project directory")
    train_parser.add_argument("--name", type=str, default=None,
                             help="Run name")
    train_parser.add_argument("--resume", action="store_true",
                             help="Resume training")
    train_parser.add_argument("--patience", type=int, default=50,
                             help="Early stopping patience")
    train_parser.add_argument("--workers", type=int, default=8,
                             help="DataLoader workers")
    train_parser.add_argument("--cache", action="store_true",
                             help="Cache images")
    train_parser.add_argument("--optimizer", type=str, default="auto",
                             choices=["SGD", "Adam", "AdamW", "auto"],
                             help="Optimizer")
    train_parser.add_argument("--lr0", type=float, default=0.01,
                             help="Initial learning rate")
    train_parser.add_argument("--freeze", type=int, default=None,
                             help="Number of layers to freeze")
    train_parser.add_argument("--cos-lr", action="store_true",
                             help="Cosine LR scheduler")
    train_parser.add_argument("--mixup", type=float, default=0.0,
                             help="Mixup augmentation")
    train_parser.add_argument("--mosaic", type=float, default=1.0,
                             help="Mosaic augmentation")
    
    # ===== VALIDATE =====
    val_parser = subparsers.add_parser("val", help="Validate model")
    val_parser.add_argument("--model", "-m", type=str, required=True,
                           help="Model weights path")
    val_parser.add_argument("--data", "-d", type=str, required=True,
                           help="Dataset yaml path")
    val_parser.add_argument("--batch", "-b", type=int, default=16,
                           help="Batch size")
    val_parser.add_argument("--imgsz", "-i", type=int, default=640,
                           help="Image size")
    val_parser.add_argument("--device", type=str, default="0",
                           help="GPU device")
    val_parser.add_argument("--conf", type=float, default=0.001,
                           help="Confidence threshold")
    val_parser.add_argument("--iou", type=float, default=0.6,
                           help="IoU threshold")
    val_parser.add_argument("--split", type=str, default="val",
                           choices=["val", "test"],
                           help="Dataset split")
    
    # ===== EXPORT =====
    export_parser = subparsers.add_parser("export", help="Export model")
    export_parser.add_argument("--model", "-m", type=str, required=True,
                              help="Model weights path")
    export_parser.add_argument("--format", "-f", type=str, default="onnx",
                              choices=["onnx", "torchscript", "openvino", "tflite", 
                                      "coreml", "paddle", "ncnn", "engine"],
                              help="Export format")
    export_parser.add_argument("--imgsz", "-i", type=int, default=640,
                              help="Image size")
    export_parser.add_argument("--half", action="store_true",
                              help="FP16 quantization")
    export_parser.add_argument("--int8", action="store_true",
                              help="INT8 quantization")
    export_parser.add_argument("--dynamic", action="store_true",
                              help="Dynamic axes")
    export_parser.add_argument("--simplify", action="store_true", default=True,
                              help="Simplify ONNX model")
    export_parser.add_argument("--device", type=str, default="0",
                              help="GPU device")
    
    # ===== PREDICT =====
    predict_parser = subparsers.add_parser("predict", help="Predict on images")
    predict_parser.add_argument("--model", "-m", type=str, required=True,
                               help="Model weights path")
    predict_parser.add_argument("--source", "-s", type=str, required=True,
                               help="Image/video path or URL")
    predict_parser.add_argument("--conf", type=float, default=0.25,
                               help="Confidence threshold")
    predict_parser.add_argument("--iou", type=float, default=0.45,
                               help="IoU threshold")
    predict_parser.add_argument("--imgsz", "-i", type=int, default=640,
                               help="Image size")
    predict_parser.add_argument("--device", type=str, default="0",
                               help="GPU device")
    predict_parser.add_argument("--save", action="store_true", default=True,
                               help="Save results")
    predict_parser.add_argument("--show", action="store_true",
                               help="Show results")
    predict_parser.add_argument("--save-txt", action="store_true",
                               help="Save labels")
    predict_parser.add_argument("--save-crop", action="store_true",
                               help="Save crops")
    
    args = parser.parse_args()
    
    if args.command == "create-yaml":
        create_dataset_yaml(args.data_dir, args.output)
        
    elif args.command == "train":
        train_yolo(
            data_yaml=args.data,
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.imgsz,
            device=args.device,
            project=args.project,
            name=args.name,
            resume=args.resume,
            patience=args.patience,
            workers=args.workers,
            cache=args.cache,
            optimizer=args.optimizer,
            lr0=args.lr0,
            freeze=args.freeze,
            cos_lr=args.cos_lr,
            mixup=args.mixup,
            mosaic=args.mosaic
        )
        
    elif args.command == "val":
        validate_model(
            model_path=args.model,
            data_yaml=args.data,
            batch_size=args.batch,
            img_size=args.imgsz,
            device=args.device,
            conf=args.conf,
            iou=args.iou,
            split=args.split
        )
        
    elif args.command == "export":
        export_model(
            model_path=args.model,
            format=args.format,
            img_size=args.imgsz,
            half=args.half,
            int8=args.int8,
            dynamic=args.dynamic,
            simplify=args.simplify,
            device=args.device
        )
        
    elif args.command == "predict":
        predict_image(
            model_path=args.model,
            source=args.source,
            conf=args.conf,
            iou=args.iou,
            img_size=args.imgsz,
            device=args.device,
            save=args.save,
            show=args.show,
            save_txt=args.save_txt,
            save_crop=args.save_crop
        )
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
