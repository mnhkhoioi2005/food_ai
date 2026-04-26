"""
VietFood67 - Dataset Utilities
Các công cụ để xử lý dataset VietFood67
- Convert từ YOLO format sang Classification format
- Split dataset
- Analyze dataset
"""

import os
import shutil
import random
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional
import argparse

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kwargs: x


# VietFood67 Classes
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


def yolo_to_classification(
    yolo_dir: str,
    output_dir: str,
    class_names: List[str] = None,
    crop_bbox: bool = True,
    min_crop_size: int = 32,
    single_object_only: bool = False
):
    """
    Convert dataset từ YOLO format sang Classification format
    
    YOLO format:
        images/train/image1.jpg
        labels/train/image1.txt (class_id x_center y_center width height)
    
    Classification format:
        train/class_name/image1.jpg
    
    Args:
        yolo_dir: Thư mục YOLO dataset (chứa images/ và labels/)
        output_dir: Thư mục output
        class_names: Danh sách tên class
        crop_bbox: Crop ảnh theo bounding box
        min_crop_size: Kích thước tối thiểu của crop
        single_object_only: Chỉ lấy ảnh có 1 object
    """
    if Image is None:
        raise ImportError("PIL is required. Install with: pip install Pillow")
    
    yolo_dir = Path(yolo_dir)
    output_dir = Path(output_dir)
    class_names = class_names or VIETFOOD_CLASSES
    
    images_dir = yolo_dir / "images"
    labels_dir = yolo_dir / "labels"
    
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    if not labels_dir.exists():
        raise FileNotFoundError(f"Labels directory not found: {labels_dir}")
    
    print("=" * 60)
    print("🔄 Converting YOLO to Classification format")
    print("=" * 60)
    print(f"📂 Input: {yolo_dir}")
    print(f"📂 Output: {output_dir}")
    print(f"✂️ Crop bbox: {crop_bbox}")
    print("=" * 60)
    
    stats = {'total': 0, 'success': 0, 'skipped': 0, 'error': 0}
    class_counts = Counter()
    
    # Process each split (train, val, test)
    for split in ['train', 'val', 'test']:
        split_images = images_dir / split
        split_labels = labels_dir / split
        
        if not split_images.exists():
            continue
        
        print(f"\n📁 Processing {split}...")
        
        # Get all image files
        image_files = list(split_images.glob("*.[jp][pn][g]")) + \
                      list(split_images.glob("*.jpeg")) + \
                      list(split_images.glob("*.webp"))
        
        for img_path in tqdm(image_files, desc=f"  {split}"):
            stats['total'] += 1
            
            # Find corresponding label file
            label_path = split_labels / f"{img_path.stem}.txt"
            
            if not label_path.exists():
                stats['skipped'] += 1
                continue
            
            try:
                # Read label file
                with open(label_path, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    stats['skipped'] += 1
                    continue
                
                # Parse labels
                bboxes = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        x_center, y_center, width, height = map(float, parts[1:5])
                        bboxes.append((class_id, x_center, y_center, width, height))
                
                if not bboxes:
                    stats['skipped'] += 1
                    continue
                
                if single_object_only and len(bboxes) > 1:
                    stats['skipped'] += 1
                    continue
                
                # Load image
                img = Image.open(img_path).convert('RGB')
                img_w, img_h = img.size
                
                # Process each bbox
                for idx, (class_id, x_center, y_center, w, h) in enumerate(bboxes):
                    if class_id >= len(class_names):
                        continue
                    
                    class_name = class_names[class_id]
                    
                    # Create output directory
                    out_class_dir = output_dir / split / class_name
                    out_class_dir.mkdir(parents=True, exist_ok=True)
                    
                    if crop_bbox:
                        # Convert normalized coords to pixel coords
                        x1 = int((x_center - w / 2) * img_w)
                        y1 = int((y_center - h / 2) * img_h)
                        x2 = int((x_center + w / 2) * img_w)
                        y2 = int((y_center + h / 2) * img_h)
                        
                        # Add padding (10%)
                        pad_w = int((x2 - x1) * 0.1)
                        pad_h = int((y2 - y1) * 0.1)
                        x1 = max(0, x1 - pad_w)
                        y1 = max(0, y1 - pad_h)
                        x2 = min(img_w, x2 + pad_w)
                        y2 = min(img_h, y2 + pad_h)
                        
                        # Check minimum size
                        if (x2 - x1) < min_crop_size or (y2 - y1) < min_crop_size:
                            continue
                        
                        # Crop image
                        cropped = img.crop((x1, y1, x2, y2))
                        
                        # Save cropped image
                        out_name = f"{img_path.stem}_{idx}.jpg"
                        out_path = out_class_dir / out_name
                        cropped.save(out_path, quality=95)
                    else:
                        # Copy original image
                        out_name = f"{img_path.stem}.jpg"
                        out_path = out_class_dir / out_name
                        
                        if not out_path.exists():
                            img.save(out_path, quality=95)
                    
                    class_counts[class_name] += 1
                
                stats['success'] += 1
                
            except Exception as e:
                stats['error'] += 1
                print(f"\n⚠️ Error processing {img_path}: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Conversion Summary")
    print("=" * 60)
    print(f"   Total images: {stats['total']}")
    print(f"   Processed: {stats['success']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['error']}")
    
    print("\n📊 Class distribution:")
    for class_name, count in sorted(class_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"   {class_name}: {count}")
    
    if len(class_counts) > 20:
        print(f"   ... and {len(class_counts) - 20} more classes")
    
    return stats, class_counts


def split_dataset(
    data_dir: str,
    output_dir: str = None,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
    copy: bool = True
):
    """
    Split dataset thành train/val/test
    
    Args:
        data_dir: Thư mục chứa ảnh (cấu trúc: data_dir/class_name/images)
        output_dir: Thư mục output (None = ghi đè)
        train_ratio: Tỷ lệ train
        val_ratio: Tỷ lệ validation
        test_ratio: Tỷ lệ test
        seed: Random seed
        copy: Copy file (True) hoặc move file (False)
    """
    data_dir = Path(data_dir)
    output_dir = Path(output_dir) if output_dir else data_dir
    
    random.seed(seed)
    
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"
    
    print("=" * 60)
    print("✂️ Splitting Dataset")
    print("=" * 60)
    print(f"📂 Input: {data_dir}")
    print(f"📂 Output: {output_dir}")
    print(f"📊 Split: {train_ratio:.0%} train / {val_ratio:.0%} val / {test_ratio:.0%} test")
    print("=" * 60)
    
    # Get all class directories
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name not in ['train', 'val', 'test']]
    
    if not class_dirs:
        # Check if already split
        if (data_dir / 'train').exists():
            print("⚠️ Dataset appears to already be split")
            return
        raise FileNotFoundError("No class directories found")
    
    stats = {'train': 0, 'val': 0, 'test': 0}
    
    for class_dir in tqdm(class_dirs, desc="Processing classes"):
        class_name = class_dir.name
        
        # Get all images
        images = list(class_dir.glob("*.[jp][pn][g]")) + \
                 list(class_dir.glob("*.jpeg")) + \
                 list(class_dir.glob("*.webp"))
        
        if not images:
            continue
        
        # Shuffle
        random.shuffle(images)
        
        # Calculate split sizes
        n = len(images)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        # Split
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]
        
        # Copy/move files
        for split_name, split_images in [('train', train_images), 
                                          ('val', val_images), 
                                          ('test', test_images)]:
            if not split_images:
                continue
            
            split_dir = output_dir / split_name / class_name
            split_dir.mkdir(parents=True, exist_ok=True)
            
            for img_path in split_images:
                dest_path = split_dir / img_path.name
                
                if copy:
                    shutil.copy2(img_path, dest_path)
                else:
                    shutil.move(img_path, dest_path)
                
                stats[split_name] += 1
    
    print("\n📊 Split Statistics:")
    print(f"   Train: {stats['train']} images")
    print(f"   Val: {stats['val']} images")
    print(f"   Test: {stats['test']} images")
    
    return stats


def analyze_dataset(data_dir: str):
    """
    Phân tích dataset
    
    Args:
        data_dir: Thư mục dataset
    """
    data_dir = Path(data_dir)
    
    print("=" * 60)
    print("📊 Dataset Analysis")
    print("=" * 60)
    
    stats = {
        'total_images': 0,
        'splits': {},
        'classes': {},
        'image_sizes': [],
        'formats': Counter()
    }
    
    # Check structure
    splits = ['train', 'val', 'test']
    has_splits = any((data_dir / s).exists() for s in splits)
    
    if has_splits:
        for split in splits:
            split_dir = data_dir / split
            if not split_dir.exists():
                continue
            
            split_stats = {'total': 0, 'classes': {}}
            
            for class_dir in split_dir.iterdir():
                if not class_dir.is_dir():
                    continue
                
                class_name = class_dir.name
                images = list(class_dir.glob("*"))
                n_images = len([f for f in images if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
                
                split_stats['classes'][class_name] = n_images
                split_stats['total'] += n_images
                stats['total_images'] += n_images
                
                # Count formats
                for img in images:
                    stats['formats'][img.suffix.lower()] += 1
            
            stats['splits'][split] = split_stats
    else:
        # Single directory structure
        for class_dir in data_dir.iterdir():
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            images = list(class_dir.glob("*"))
            n_images = len([f for f in images if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
            
            stats['classes'][class_name] = n_images
            stats['total_images'] += n_images
            
            for img in images:
                stats['formats'][img.suffix.lower()] += 1
    
    # Print results
    print(f"\n📁 Dataset path: {data_dir}")
    print(f"📷 Total images: {stats['total_images']}")
    print(f"📁 Structure: {'Split (train/val/test)' if has_splits else 'Single directory'}")
    
    if has_splits:
        print("\n📊 Split distribution:")
        for split, split_stats in stats['splits'].items():
            n_classes = len(split_stats['classes'])
            print(f"   {split}: {split_stats['total']} images, {n_classes} classes")
    
    print("\n📊 Image formats:")
    for fmt, count in stats['formats'].most_common():
        print(f"   {fmt}: {count}")
    
    # Class distribution
    all_classes = {}
    if has_splits:
        for split_stats in stats['splits'].values():
            for class_name, count in split_stats['classes'].items():
                all_classes[class_name] = all_classes.get(class_name, 0) + count
    else:
        all_classes = stats['classes']
    
    if all_classes:
        print(f"\n📊 Class distribution ({len(all_classes)} classes):")
        sorted_classes = sorted(all_classes.items(), key=lambda x: -x[1])
        
        # Top 10
        print("   Top 10:")
        for class_name, count in sorted_classes[:10]:
            print(f"      {class_name}: {count}")
        
        # Bottom 5
        if len(sorted_classes) > 15:
            print("   ...")
            print("   Bottom 5:")
            for class_name, count in sorted_classes[-5:]:
                print(f"      {class_name}: {count}")
        
        # Statistics
        counts = list(all_classes.values())
        print(f"\n   Min: {min(counts)}, Max: {max(counts)}, Avg: {sum(counts)/len(counts):.1f}")
    
    return stats


def verify_dataset(data_dir: str, fix: bool = False):
    """
    Kiểm tra và sửa lỗi dataset
    
    Args:
        data_dir: Thư mục dataset
        fix: Tự động sửa lỗi
    """
    if Image is None:
        raise ImportError("PIL is required")
    
    data_dir = Path(data_dir)
    
    print("=" * 60)
    print("🔍 Verifying Dataset")
    print("=" * 60)
    
    issues = {
        'corrupt': [],
        'empty': [],
        'small': [],
        'wrong_format': []
    }
    
    # Get all images
    all_images = []
    for ext in ['jpg', 'jpeg', 'png', 'webp', 'bmp']:
        all_images.extend(data_dir.rglob(f"*.{ext}"))
        all_images.extend(data_dir.rglob(f"*.{ext.upper()}"))
    
    print(f"📷 Found {len(all_images)} images")
    
    for img_path in tqdm(all_images, desc="Verifying"):
        try:
            img = Image.open(img_path)
            img.verify()
            
            # Check size
            img = Image.open(img_path)  # Need to reopen after verify
            w, h = img.size
            
            if w == 0 or h == 0:
                issues['empty'].append(img_path)
            elif w < 32 or h < 32:
                issues['small'].append(img_path)
                
        except Exception as e:
            issues['corrupt'].append((img_path, str(e)))
    
    # Print results
    print("\n📊 Verification Results:")
    print(f"   Corrupt: {len(issues['corrupt'])}")
    print(f"   Empty: {len(issues['empty'])}")
    print(f"   Small (<32px): {len(issues['small'])}")
    
    if issues['corrupt']:
        print("\n⚠️ Corrupt images:")
        for path, error in issues['corrupt'][:10]:
            print(f"   {path}: {error}")
        if len(issues['corrupt']) > 10:
            print(f"   ... and {len(issues['corrupt']) - 10} more")
    
    if fix:
        print("\n🔧 Fixing issues...")
        removed = 0
        
        for path, _ in issues['corrupt']:
            path.unlink()
            removed += 1
        
        for path in issues['empty']:
            path.unlink()
            removed += 1
        
        print(f"   Removed {removed} problematic files")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="VietFood67 Dataset Utilities")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Convert
    convert_parser = subparsers.add_parser("convert", help="Convert YOLO to Classification format")
    convert_parser.add_argument("--input", "-i", type=str, required=True,
                               help="YOLO dataset directory")
    convert_parser.add_argument("--output", "-o", type=str, required=True,
                               help="Output directory")
    convert_parser.add_argument("--no-crop", action="store_true",
                               help="Don't crop bounding boxes")
    convert_parser.add_argument("--min-size", type=int, default=32,
                               help="Minimum crop size")
    convert_parser.add_argument("--single-object", action="store_true",
                               help="Only images with single object")
    
    # Split
    split_parser = subparsers.add_parser("split", help="Split dataset into train/val/test")
    split_parser.add_argument("--input", "-i", type=str, required=True,
                             help="Dataset directory")
    split_parser.add_argument("--output", "-o", type=str, default=None,
                             help="Output directory (default: same as input)")
    split_parser.add_argument("--train", type=float, default=0.8,
                             help="Train ratio")
    split_parser.add_argument("--val", type=float, default=0.1,
                             help="Validation ratio")
    split_parser.add_argument("--test", type=float, default=0.1,
                             help="Test ratio")
    split_parser.add_argument("--seed", type=int, default=42,
                             help="Random seed")
    split_parser.add_argument("--move", action="store_true",
                             help="Move files instead of copy")
    
    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze dataset")
    analyze_parser.add_argument("--input", "-i", type=str, required=True,
                               help="Dataset directory")
    
    # Verify
    verify_parser = subparsers.add_parser("verify", help="Verify dataset integrity")
    verify_parser.add_argument("--input", "-i", type=str, required=True,
                              help="Dataset directory")
    verify_parser.add_argument("--fix", action="store_true",
                              help="Auto-fix issues")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        yolo_to_classification(
            yolo_dir=args.input,
            output_dir=args.output,
            crop_bbox=not args.no_crop,
            min_crop_size=args.min_size,
            single_object_only=args.single_object
        )
    
    elif args.command == "split":
        split_dataset(
            data_dir=args.input,
            output_dir=args.output,
            train_ratio=args.train,
            val_ratio=args.val,
            test_ratio=args.test,
            seed=args.seed,
            copy=not args.move
        )
    
    elif args.command == "analyze":
        analyze_dataset(args.input)
    
    elif args.command == "verify":
        verify_dataset(args.input, fix=args.fix)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
