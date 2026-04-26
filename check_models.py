"""
Script kiểm tra thông tin training của các model .pt
"""
import os
import sys

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics chưa được cài. Chạy: pip install ultralytics")
    sys.exit(1)

weights_dir = os.path.join(os.path.dirname(__file__), "ai_models", "trained_weights")
files = sorted([f for f in os.listdir(weights_dir) if f.endswith(".pt")])

if not files:
    print("Không tìm thấy file .pt nào trong trained_weights/")
    sys.exit(0)

print("=" * 60)
print("KIỂM TRA THÔNG TIN CÁC MODEL ĐÃ TRAIN")
print("=" * 60)

for fname in files:
    path = os.path.join(weights_dir, fname)
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"\n>>> {fname}  ({size_mb:.1f} MB)")
    print("-" * 40)

    try:
        model = YOLO(path)

        # Số class và tên
        nc = model.model.nc if hasattr(model.model, "nc") else "?"
        names = list(model.names.values()) if model.names else []
        print(f"  Số classes    : {nc}")
        print(f"  Class names   : {names[:5]}{'...' if len(names) > 5 else ''}")

        # Kiến trúc model
        arch = type(model.model).__name__
        print(f"  Architecture  : {arch}")

        # Thông tin từ checkpoint
        ckpt = model.ckpt if hasattr(model, "ckpt") else {}

        if ckpt:
            epoch = ckpt.get("epoch", "not found")
            print(f"  Epoch cuối    : {epoch}")

            best_fitness = ckpt.get("best_fitness", None)
            if best_fitness is not None:
                print(f"  Best fitness  : {best_fitness:.4f}  (mAP50-95)")

            train_args = ckpt.get("train_args", None)
            if train_args:
                def get(key):
                    v = train_args.get(key, "?")
                    return v

                print(f"  --- Training args ---")
                print(f"  Base model    : {get('model')}")
                print(f"  Image size    : {get('imgsz')}")
                print(f"  Batch size    : {get('batch')}")
                print(f"  Optimizer     : {get('optimizer')}")
                print(f"  LR0           : {get('lr0')}")
                print(f"  LRf           : {get('lrf')}")
                print(f"  Momentum      : {get('momentum')}")
                print(f"  Weight decay  : {get('weight_decay')}")
                print(f"  Warmup epochs : {get('warmup_epochs')}")
                print(f"  Mosaic        : {get('mosaic')}")
                print(f"  Mixup         : {get('mixup')}")
                print(f"  Copy-paste    : {get('copy_paste')}")
                print(f"  Augment       : {get('augment')}")
                print(f"  Label smooth  : {get('label_smoothing')}")
                print(f"  Cos LR        : {get('cos_lr')}")
                print(f"  Patience      : {get('patience')}")
                print(f"  Device        : {get('device')}")
                print(f"  Data yaml     : {get('data')}")
                print(f"  Project       : {get('project')}")
                print(f"  Name          : {get('name')}")
            else:
                print("  [train_args không có trong checkpoint]")

            # Kích thước model
            model_info = ckpt.get("model", None)
            if model_info and hasattr(model_info, "args"):
                print(f"  Model args    : {model_info.args}")
        else:
            print("  [Không đọc được checkpoint metadata]")

    except Exception as e:
        print(f"  LỖI: {e}")

print("\n" + "=" * 60)
print("XONG")
print("=" * 60)
