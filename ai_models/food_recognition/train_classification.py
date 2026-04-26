"""
VietFood67 - Classification Training Script
Train EfficientNet/ResNet/ViT models for Vietnamese food classification
Dataset: https://www.kaggle.com/datasets/thomasnguyen6868/vietfood68

Script này dùng để train model classification (phân loại ảnh)
Nếu dataset của bạn ở dạng YOLO (có bounding box), 
cần chuyển đổi sang format classification trước
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.optim.lr_scheduler import CosineAnnealingLR, OneCycleLR, StepLR
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
from PIL import Image
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kwargs: x  # fallback

try:
    import timm
    HAS_TIMM = True
except ImportError:
    HAS_TIMM = False
    print("⚠️ timm not installed. Install with: pip install timm")

try:
    from torch.cuda.amp import autocast, GradScaler
    HAS_AMP = True
except ImportError:
    HAS_AMP = False


# =====================================================
# CONFIGURATION
# =====================================================

VIETFOOD_CLASSES = [
    "banh_bao", "banh_beo", "banh_bot_loc", "banh_can", "banh_canh",
    "banh_chung", "banh_cuon", "banh_da_lon", "banh_duc", "banh_gio",
    "banh_khot", "banh_mi", "banh_pia", "banh_trang_nuong", "banh_xeo",
    "bo_kho", "bun_bo_hue", "bun_cha", "bun_dau_mam_tom", "bun_mam",
    "bun_moc", "bun_rieu", "bun_thit_nuong", "ca_kho_to", "canh_chua",
    "cao_lau", "chao_long", "che", "com_chay", "com_ga",
    "com_tam", "ga_nuong", "goi_cuon", "goi_ga", "hu_tieu",
    "lau", "mi_quang", "mi_xao", "nem_chua", "nem_nuong",
    "oc", "pho", "rau_muong_xao_toi", "thit_kho", "thit_nuong",
    "xoi", "che_ba_mau", "banh_flan", "sua_chua", "sinh_to",
    "nuoc_mia", "tra_sua", "ca_phe", "nuoc_dua", "kem",
    "xoi_xeo", "xoi_gac", "bap_xao", "khoai_lang_nuong", "trung_vit_lon",
    "chao", "sup", "mi_tom", "com_rang", "bun_cha_ca",
    "banh_trang_tron", "bot_chien"
]

# Tên tiếng Việt cho các class
VIETFOOD_NAMES_VI = {
    "banh_bao": "Bánh Bao",
    "banh_beo": "Bánh Bèo",
    "banh_bot_loc": "Bánh Bột Lọc",
    "banh_can": "Bánh Căn",
    "banh_canh": "Bánh Canh",
    "banh_chung": "Bánh Chưng",
    "banh_cuon": "Bánh Cuốn",
    "banh_da_lon": "Bánh Da Lợn",
    "banh_duc": "Bánh Đúc",
    "banh_gio": "Bánh Giò",
    "banh_khot": "Bánh Khọt",
    "banh_mi": "Bánh Mì",
    "banh_pia": "Bánh Pía",
    "banh_trang_nuong": "Bánh Tráng Nướng",
    "banh_xeo": "Bánh Xèo",
    "bo_kho": "Bò Kho",
    "bun_bo_hue": "Bún Bò Huế",
    "bun_cha": "Bún Chả",
    "bun_dau_mam_tom": "Bún Đậu Mắm Tôm",
    "bun_mam": "Bún Mắm",
    "bun_moc": "Bún Mọc",
    "bun_rieu": "Bún Riêu",
    "bun_thit_nuong": "Bún Thịt Nướng",
    "ca_kho_to": "Cá Kho Tộ",
    "canh_chua": "Canh Chua",
    "cao_lau": "Cao Lầu",
    "chao_long": "Cháo Lòng",
    "che": "Chè",
    "com_chay": "Cơm Cháy",
    "com_ga": "Cơm Gà",
    "com_tam": "Cơm Tấm",
    "ga_nuong": "Gà Nướng",
    "goi_cuon": "Gỏi Cuốn",
    "goi_ga": "Gỏi Gà",
    "hu_tieu": "Hủ Tiếu",
    "lau": "Lẩu",
    "mi_quang": "Mì Quảng",
    "mi_xao": "Mì Xào",
    "nem_chua": "Nem Chua",
    "nem_nuong": "Nem Nướng",
    "oc": "Ốc",
    "pho": "Phở",
    "rau_muong_xao_toi": "Rau Muống Xào Tỏi",
    "thit_kho": "Thịt Kho",
    "thit_nuong": "Thịt Nướng",
    "xoi": "Xôi",
    "che_ba_mau": "Chè Ba Màu",
    "banh_flan": "Bánh Flan",
    "sua_chua": "Sữa Chua",
    "sinh_to": "Sinh Tố",
    "nuoc_mia": "Nước Mía",
    "tra_sua": "Trà Sữa",
    "ca_phe": "Cà Phê",
    "nuoc_dua": "Nước Dừa",
    "kem": "Kem",
    "xoi_xeo": "Xôi Xéo",
    "xoi_gac": "Xôi Gấc",
    "bap_xao": "Bắp Xào",
    "khoai_lang_nuong": "Khoai Lang Nướng",
    "trung_vit_lon": "Trứng Vịt Lộn",
    "chao": "Cháo",
    "sup": "Súp",
    "mi_tom": "Mì Tôm",
    "com_rang": "Cơm Rang",
    "bun_cha_ca": "Bún Chả Cá",
    "banh_trang_tron": "Bánh Tráng Trộn",
    "bot_chien": "Bột Chiên"
}


# =====================================================
# DATA AUGMENTATION
# =====================================================

def get_transforms(
    img_size: int = 224,
    mode: str = "train",
    auto_augment: str = "randaugment"
):
    """
    Lấy transforms cho training/validation
    
    Args:
        img_size: Kích thước ảnh
        mode: "train" hoặc "val"
        auto_augment: "randaugment", "autoaugment", hoặc "trivialaugment"
    """
    # ImageNet normalization
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    
    if mode == "train":
        transform_list = [
            transforms.RandomResizedCrop(img_size, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(
                brightness=0.3,
                contrast=0.3,
                saturation=0.3,
                hue=0.1
            ),
        ]
        
        # Auto augmentation
        if auto_augment == "randaugment":
            transform_list.append(transforms.RandAugment(num_ops=2, magnitude=9))
        elif auto_augment == "autoaugment":
            transform_list.append(transforms.AutoAugment(transforms.AutoAugmentPolicy.IMAGENET))
        elif auto_augment == "trivialaugment":
            transform_list.append(transforms.TrivialAugmentWide())
        
        transform_list.extend([
            transforms.ToTensor(),
            normalize,
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.2)),
        ])
        
    else:  # val/test
        transform_list = [
            transforms.Resize(int(img_size * 1.14)),  # 256 for 224
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            normalize,
        ]
    
    return transforms.Compose(transform_list)


# =====================================================
# DATASET
# =====================================================

class VietFoodDataset(Dataset):
    """
    Custom dataset cho VietFood
    Hỗ trợ cả ImageFolder structure và custom structure
    """
    
    def __init__(
        self,
        root_dir: str,
        transform=None,
        class_names: List[str] = None
    ):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.class_names = class_names or VIETFOOD_CLASSES
        self.class_to_idx = {name: idx for idx, name in enumerate(self.class_names)}
        
        # Collect samples
        self.samples = []
        self._load_samples()
    
    def _load_samples(self):
        """Load tất cả samples từ thư mục"""
        for class_name in self.class_names:
            class_dir = self.root_dir / class_name
            if class_dir.exists():
                for img_path in class_dir.glob("*"):
                    if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                        self.samples.append((str(img_path), self.class_to_idx[class_name]))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


# =====================================================
# MODEL
# =====================================================

def create_model(
    model_name: str = "efficientnet_b0",
    num_classes: int = 67,
    pretrained: bool = True,
    dropout: float = 0.2
) -> nn.Module:
    """
    Tạo model cho classification
    
    Args:
        model_name: Tên model (efficientnet_b0, resnet50, vit_base_patch16_224, etc.)
        num_classes: Số classes
        pretrained: Sử dụng pretrained weights
        dropout: Dropout rate
    """
    print(f"📦 Creating model: {model_name}")
    
    # Sử dụng timm nếu có
    if HAS_TIMM:
        model = timm.create_model(
            model_name,
            pretrained=pretrained,
            num_classes=num_classes,
            drop_rate=dropout
        )
        return model
    
    # Fallback to torchvision
    if "efficientnet" in model_name:
        if model_name == "efficientnet_b0":
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "efficientnet_b1":
            model = models.efficientnet_b1(
                weights=models.EfficientNet_B1_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "efficientnet_b2":
            model = models.efficientnet_b2(
                weights=models.EfficientNet_B2_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "efficientnet_b3":
            model = models.efficientnet_b3(
                weights=models.EfficientNet_B3_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "efficientnet_b4":
            model = models.efficientnet_b4(
                weights=models.EfficientNet_B4_Weights.DEFAULT if pretrained else None
            )
        else:
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            )
        
        # Replace classifier
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, num_classes)
        )
        
    elif "resnet" in model_name:
        if model_name == "resnet50":
            model = models.resnet50(
                weights=models.ResNet50_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "resnet101":
            model = models.resnet101(
                weights=models.ResNet101_Weights.DEFAULT if pretrained else None
            )
        elif model_name == "resnet152":
            model = models.resnet152(
                weights=models.ResNet152_Weights.DEFAULT if pretrained else None
            )
        else:
            model = models.resnet50(
                weights=models.ResNet50_Weights.DEFAULT if pretrained else None
            )
        
        # Replace fc
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes)
        )
        
    elif "mobilenet" in model_name:
        model = models.mobilenet_v3_large(
            weights=models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        )
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, num_classes)
        
    elif "convnext" in model_name:
        model = models.convnext_tiny(
            weights=models.ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None
        )
        in_features = model.classifier[2].in_features
        model.classifier[2] = nn.Linear(in_features, num_classes)
        
    else:
        raise ValueError(f"Unknown model: {model_name}. Install timm for more models.")
    
    return model


# =====================================================
# TRAINING
# =====================================================

class Trainer:
    """
    Trainer class cho VietFood classification
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: optim.Optimizer,
        scheduler,
        device: torch.device,
        num_classes: int,
        project_dir: str = "runs/classify",
        run_name: str = None,
        use_amp: bool = True,
        grad_clip: float = 1.0
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.num_classes = num_classes
        self.use_amp = use_amp and HAS_AMP
        self.grad_clip = grad_clip
        
        # Setup directories
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_name = run_name or f"run_{timestamp}"
        self.project_dir = Path(project_dir) / self.run_name
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # AMP scaler
        self.scaler = GradScaler() if self.use_amp else None
        
        # Best metrics
        self.best_acc = 0.0
        self.best_loss = float('inf')
        
        # History
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'lr': []
        }
    
    def train_epoch(self, epoch: int) -> Tuple[float, float]:
        """Train một epoch"""
        self.model.train()
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch} [Train]")
        
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                
                # Backward pass với scaling
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                if self.grad_clip > 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
                
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                
                if self.grad_clip > 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
                
                self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{total_loss / (batch_idx + 1):.4f}',
                'acc': f'{100. * correct / total:.2f}%'
            })
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    @torch.no_grad()
    def validate(self, epoch: int) -> Tuple[float, float]:
        """Validate model"""
        self.model.eval()
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.val_loader, desc=f"Epoch {epoch} [Val]")
        
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                'loss': f'{total_loss / (total // labels.size(0)):.4f}',
                'acc': f'{100. * correct / total:.2f}%'
            })
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """Lưu checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_acc': self.best_acc,
            'history': self.history
        }
        
        # Save last
        torch.save(checkpoint, self.project_dir / 'last.pt')
        
        # Save best
        if is_best:
            torch.save(checkpoint, self.project_dir / 'best.pt')
            
            # Export model only
            torch.save(self.model.state_dict(), self.project_dir / 'best_weights.pt')
    
    def train(self, epochs: int, early_stop_patience: int = 20):
        """
        Full training loop
        
        Args:
            epochs: Số epochs
            early_stop_patience: Early stopping patience
        """
        print("=" * 60)
        print("🍜 VietFood67 Classification Training")
        print("=" * 60)
        print(f"📂 Output: {self.project_dir}")
        print(f"📊 Epochs: {epochs}")
        print(f"🔢 Num classes: {self.num_classes}")
        print(f"⚡ AMP: {self.use_amp}")
        print("=" * 60)
        
        patience_counter = 0
        
        for epoch in range(1, epochs + 1):
            # Train
            train_loss, train_acc = self.train_epoch(epoch)
            
            # Validate
            val_loss, val_acc = self.validate(epoch)
            
            # Get current LR
            current_lr = self.optimizer.param_groups[0]['lr']
            
            # Update scheduler
            if self.scheduler:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            self.history['lr'].append(current_lr)
            
            # Check best
            is_best = val_acc > self.best_acc
            if is_best:
                self.best_acc = val_acc
                self.best_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
            
            # Save checkpoint
            self.save_checkpoint(epoch, is_best)
            
            # Print summary
            print(f"\n📊 Epoch {epoch}/{epochs}")
            print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            print(f"   Best Acc: {self.best_acc:.2f}% | LR: {current_lr:.6f}")
            
            if is_best:
                print(f"   ✨ New best model saved!")
            
            # Early stopping
            if patience_counter >= early_stop_patience:
                print(f"\n⚠️ Early stopping at epoch {epoch}")
                break
        
        # Save history
        with open(self.project_dir / 'history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
        
        # Save class names
        with open(self.project_dir / 'classes.json', 'w', encoding='utf-8') as f:
            json.dump({
                'class_names': VIETFOOD_CLASSES,
                'class_names_vi': VIETFOOD_NAMES_VI
            }, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Training complete!")
        print(f"   Best accuracy: {self.best_acc:.2f}%")
        print(f"   Weights saved: {self.project_dir / 'best.pt'}")
        
        return self.history


# =====================================================
# MAIN FUNCTIONS
# =====================================================

def train_classification(
    data_dir: str,
    model_name: str = "efficientnet_b0",
    epochs: int = 100,
    batch_size: int = 32,
    img_size: int = 224,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    optimizer_name: str = "adamw",
    scheduler_name: str = "cosine",
    dropout: float = 0.2,
    num_workers: int = 4,
    device: str = "cuda",
    project: str = "runs/classify",
    name: str = None,
    pretrained: bool = True,
    use_amp: bool = True,
    label_smoothing: float = 0.1,
    early_stop_patience: int = 20,
    grad_clip: float = 1.0,
    auto_augment: str = "randaugment"
):
    """
    Train classification model
    
    Args:
        data_dir: Thư mục dataset (cấu trúc: data_dir/train/class_name/images)
        model_name: Tên model
        epochs: Số epochs
        batch_size: Batch size
        img_size: Kích thước ảnh
        lr: Learning rate
        weight_decay: Weight decay
        optimizer_name: Optimizer (adamw, adam, sgd)
        scheduler_name: Scheduler (cosine, step, onecycle)
        dropout: Dropout rate
        num_workers: Số workers cho DataLoader
        device: Device (cuda, cpu)
        project: Thư mục project
        name: Tên run
        pretrained: Sử dụng pretrained
        use_amp: Sử dụng AMP
        label_smoothing: Label smoothing
        early_stop_patience: Early stopping patience
        grad_clip: Gradient clipping
        auto_augment: Auto augmentation strategy
    """
    # Setup device
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Device: {device}")
    
    # Prepare data
    data_dir = Path(data_dir)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    
    if not train_dir.exists():
        raise FileNotFoundError(f"Train directory not found: {train_dir}")
    
    # Transforms
    train_transform = get_transforms(img_size, "train", auto_augment)
    val_transform = get_transforms(img_size, "val")
    
    # Datasets
    train_dataset = ImageFolder(str(train_dir), transform=train_transform)
    
    if val_dir.exists():
        val_dataset = ImageFolder(str(val_dir), transform=val_transform)
    else:
        # Split từ train nếu không có val
        from torch.utils.data import random_split
        train_size = int(0.9 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])
    
    num_classes = len(train_dataset.classes) if hasattr(train_dataset, 'classes') else 67
    
    print(f"📊 Dataset:")
    print(f"   Train: {len(train_dataset)} images")
    print(f"   Val: {len(val_dataset)} images")
    print(f"   Classes: {num_classes}")
    
    # DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    # Model
    model = create_model(model_name, num_classes, pretrained, dropout)
    model = model.to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📦 Model: {model_name}")
    print(f"   Total params: {total_params:,}")
    print(f"   Trainable params: {trainable_params:,}")
    
    # Loss function
    criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)
    
    # Optimizer
    if optimizer_name.lower() == "adamw":
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name.lower() == "adam":
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name.lower() == "sgd":
        optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, 
                             weight_decay=weight_decay, nesterov=True)
    else:
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # Scheduler
    if scheduler_name.lower() == "cosine":
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.01)
    elif scheduler_name.lower() == "step":
        scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
    elif scheduler_name.lower() == "onecycle":
        scheduler = OneCycleLR(
            optimizer, 
            max_lr=lr * 10,
            epochs=epochs,
            steps_per_epoch=len(train_loader)
        )
    else:
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
    
    # Run name
    if name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{model_name}_{timestamp}"
    
    # Trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        num_classes=num_classes,
        project_dir=project,
        run_name=name,
        use_amp=use_amp,
        grad_clip=grad_clip
    )
    
    # Train
    history = trainer.train(epochs, early_stop_patience)
    
    return history, trainer.project_dir


def main():
    parser = argparse.ArgumentParser(description="VietFood67 Classification Training")
    
    parser.add_argument("--data", "-d", type=str, required=True,
                       help="Data directory (với train/ và val/ subfolders)")
    parser.add_argument("--model", "-m", type=str, default="efficientnet_b0",
                       help="Model name (efficientnet_b0, resnet50, vit_base_patch16_224, etc.)")
    parser.add_argument("--epochs", "-e", type=int, default=100,
                       help="Number of epochs")
    parser.add_argument("--batch", "-b", type=int, default=32,
                       help="Batch size")
    parser.add_argument("--img-size", type=int, default=224,
                       help="Image size")
    parser.add_argument("--lr", type=float, default=1e-3,
                       help="Learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4,
                       help="Weight decay")
    parser.add_argument("--optimizer", type=str, default="adamw",
                       choices=["adamw", "adam", "sgd"],
                       help="Optimizer")
    parser.add_argument("--scheduler", type=str, default="cosine",
                       choices=["cosine", "step", "onecycle"],
                       help="Learning rate scheduler")
    parser.add_argument("--dropout", type=float, default=0.2,
                       help="Dropout rate")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of data loading workers")
    parser.add_argument("--device", type=str, default="cuda",
                       help="Device (cuda or cpu)")
    parser.add_argument("--project", type=str, default="runs/classify",
                       help="Project directory")
    parser.add_argument("--name", type=str, default=None,
                       help="Run name")
    parser.add_argument("--no-pretrained", action="store_true",
                       help="Don't use pretrained weights")
    parser.add_argument("--no-amp", action="store_true",
                       help="Don't use AMP")
    parser.add_argument("--label-smoothing", type=float, default=0.1,
                       help="Label smoothing")
    parser.add_argument("--patience", type=int, default=20,
                       help="Early stopping patience")
    parser.add_argument("--grad-clip", type=float, default=1.0,
                       help="Gradient clipping value")
    parser.add_argument("--auto-augment", type=str, default="randaugment",
                       choices=["randaugment", "autoaugment", "trivialaugment", "none"],
                       help="Auto augmentation strategy")
    
    args = parser.parse_args()
    
    train_classification(
        data_dir=args.data,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.img_size,
        lr=args.lr,
        weight_decay=args.weight_decay,
        optimizer_name=args.optimizer,
        scheduler_name=args.scheduler,
        dropout=args.dropout,
        num_workers=args.workers,
        device=args.device,
        project=args.project,
        name=args.name,
        pretrained=not args.no_pretrained,
        use_amp=not args.no_amp,
        label_smoothing=args.label_smoothing,
        early_stop_patience=args.patience,
        grad_clip=args.grad_clip,
        auto_augment=args.auto_augment if args.auto_augment != "none" else None
    )


if __name__ == "__main__":
    main()
