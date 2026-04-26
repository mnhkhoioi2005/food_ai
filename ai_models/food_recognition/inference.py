"""
VietFood67 - Inference Script
Nhận diện món ăn Việt Nam từ ảnh
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import time

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

try:
    import timm
    HAS_TIMM = True
except ImportError:
    HAS_TIMM = False


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
    "com_tam", "face", "ga_nuong", "goi_cuon", "goi_ga",
    "hu_tieu", "lau", "mi_quang", "mi_xao", "nem_chua",
    "nem_nuong", "oc", "pho", "rau_muong_xao_toi", "thit_kho",
    "thit_nuong", "xoi", "che_ba_mau", "banh_flan", "sua_chua",
    "sinh_to", "nuoc_mia", "tra_sua", "ca_phe", "nuoc_dua",
    "kem", "xoi_xeo", "xoi_gac", "bap_xao", "khoai_lang_nuong",
    "trung_vit_lon", "chao", "sup", "mi_tom", "com_rang",
    "bun_cha_ca", "banh_trang_tron", "bot_chien"
]

VIETFOOD_NAMES_VI = {
    "banh_bao": "Bánh Bao", "banh_beo": "Bánh Bèo", "banh_bot_loc": "Bánh Bột Lọc",
    "banh_can": "Bánh Căn", "banh_canh": "Bánh Canh", "banh_chung": "Bánh Chưng",
    "banh_cuon": "Bánh Cuốn", "banh_da_lon": "Bánh Da Lợn", "banh_duc": "Bánh Đúc",
    "banh_gio": "Bánh Giò", "banh_khot": "Bánh Khọt", "banh_mi": "Bánh Mì",
    "banh_pia": "Bánh Pía", "banh_trang_nuong": "Bánh Tráng Nướng", "banh_xeo": "Bánh Xèo",
    "bo_kho": "Bò Kho", "bun_bo_hue": "Bún Bò Huế", "bun_cha": "Bún Chả",
    "bun_dau_mam_tom": "Bún Đậu Mắm Tôm", "bun_mam": "Bún Mắm", "bun_moc": "Bún Mọc",
    "bun_rieu": "Bún Riêu", "bun_thit_nuong": "Bún Thịt Nướng", "ca_kho_to": "Cá Kho Tộ",
    "canh_chua": "Canh Chua", "cao_lau": "Cao Lầu", "chao_long": "Cháo Lòng",
    "che": "Chè", "com_chay": "Cơm Cháy", "com_ga": "Cơm Gà", "com_tam": "Cơm Tấm",
    "face": "Khuôn Mặt", "ga_nuong": "Gà Nướng", "goi_cuon": "Gỏi Cuốn",
    "goi_ga": "Gỏi Gà", "hu_tieu": "Hủ Tiếu", "lau": "Lẩu", "mi_quang": "Mì Quảng",
    "mi_xao": "Mì Xào", "nem_chua": "Nem Chua", "nem_nuong": "Nem Nướng",
    "oc": "Ốc", "pho": "Phở", "rau_muong_xao_toi": "Rau Muống Xào Tỏi",
    "thit_kho": "Thịt Kho", "thit_nuong": "Thịt Nướng", "xoi": "Xôi",
    "che_ba_mau": "Chè Ba Màu", "banh_flan": "Bánh Flan", "sua_chua": "Sữa Chua",
    "sinh_to": "Sinh Tố", "nuoc_mia": "Nước Mía", "tra_sua": "Trà Sữa",
    "ca_phe": "Cà Phê", "nuoc_dua": "Nước Dừa", "kem": "Kem",
    "xoi_xeo": "Xôi Xéo", "xoi_gac": "Xôi Gấc", "bap_xao": "Bắp Xào",
    "khoai_lang_nuong": "Khoai Lang Nướng", "trung_vit_lon": "Trứng Vịt Lộn",
    "chao": "Cháo", "sup": "Súp", "mi_tom": "Mì Tôm", "com_rang": "Cơm Rang",
    "bun_cha_ca": "Bún Chả Cá", "banh_trang_tron": "Bánh Tráng Trộn", "bot_chien": "Bột Chiên"
}


# =====================================================
# YOLO DETECTOR
# =====================================================

class YOLODetector:
    """
    YOLO-based food detector
    """
    
    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ):
        if not HAS_YOLO:
            raise ImportError("ultralytics not installed. Run: pip install ultralytics")
        
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Load model
        self.model = YOLO(model_path)
        print(f"✅ Loaded YOLO model: {model_path}")
    
    def predict(
        self,
        image: Union[str, np.ndarray, Image.Image],
        conf: float = None,
        iou: float = None
    ) -> List[Dict]:
        """
        Predict trên một ảnh
        
        Args:
            image: Đường dẫn ảnh hoặc numpy array hoặc PIL Image
            conf: Confidence threshold
            iou: IoU threshold
            
        Returns:
            List of predictions với keys: class_id, class_name, name_vi, confidence, bbox
        """
        conf = conf or self.conf_threshold
        iou = iou or self.iou_threshold
        
        # Run inference
        results = self.model.predict(
            source=image,
            conf=conf,
            iou=iou,
            device=self.device,
            verbose=False
        )
        
        # Parse results
        predictions = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
                
                # Get class names
                class_name = VIETFOOD_CLASSES[class_id] if class_id < len(VIETFOOD_CLASSES) else f"class_{class_id}"
                name_vi = VIETFOOD_NAMES_VI.get(class_name, class_name)
                
                predictions.append({
                    'class_id': class_id,
                    'class_name': class_name,
                    'name_vi': name_vi,
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        return predictions
    
    def predict_batch(
        self,
        images: List[Union[str, np.ndarray]],
        conf: float = None,
        iou: float = None
    ) -> List[List[Dict]]:
        """Predict trên nhiều ảnh"""
        return [self.predict(img, conf, iou) for img in images]


# =====================================================
# CLASSIFICATION MODEL
# =====================================================

class FoodClassifier:
    """
    Food classification model (EfficientNet, ResNet, ViT, etc.)
    """
    
    def __init__(
        self,
        model_path: str,
        model_name: str = None,
        device: str = "cuda",
        num_classes: int = 67,
        img_size: int = 224
    ):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.img_size = img_size
        self.num_classes = num_classes
        
        # Load model
        self.model = self._load_model(model_path, model_name)
        self.model.eval()
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize(int(img_size * 1.14)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Load class names
        self._load_class_names(model_path)
        
        print(f"✅ Loaded classification model on {self.device}")
    
    def _load_model(self, model_path: str, model_name: str = None):
        """Load model từ checkpoint"""
        checkpoint_path = Path(model_path)
        
        # Check if it's a checkpoint or just weights
        if checkpoint_path.suffix == '.pt':
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                # Full checkpoint
                state_dict = checkpoint['model_state_dict']
            else:
                # Just state dict
                state_dict = checkpoint
            
            # Infer model architecture from state dict
            if model_name is None:
                model_name = self._infer_model_name(state_dict)
            
            # Create model
            if HAS_TIMM:
                model = timm.create_model(model_name, pretrained=False, num_classes=self.num_classes)
            else:
                from torchvision import models
                if 'efficientnet' in model_name:
                    model = models.efficientnet_b0(weights=None)
                    in_features = model.classifier[1].in_features
                    model.classifier[1] = torch.nn.Linear(in_features, self.num_classes)
                elif 'resnet' in model_name:
                    model = models.resnet50(weights=None)
                    in_features = model.fc.in_features
                    model.fc = torch.nn.Linear(in_features, self.num_classes)
                else:
                    raise ValueError(f"Unknown model: {model_name}")
            
            model.load_state_dict(state_dict, strict=False)
        else:
            raise ValueError(f"Unknown model format: {checkpoint_path.suffix}")
        
        return model.to(self.device)
    
    def _infer_model_name(self, state_dict: dict) -> str:
        """Infer model name từ state dict"""
        keys = list(state_dict.keys())
        
        if any('efficientnet' in k for k in keys) or any('_fc' in k for k in keys):
            return 'efficientnet_b0'
        elif any('layer4' in k for k in keys):
            return 'resnet50'
        elif any('blocks' in k for k in keys):
            return 'vit_base_patch16_224'
        else:
            return 'efficientnet_b0'  # default
    
    def _load_class_names(self, model_path: str):
        """Load class names từ file"""
        model_dir = Path(model_path).parent
        classes_file = model_dir / 'classes.json'
        
        if classes_file.exists():
            with open(classes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.class_names = data.get('class_names', VIETFOOD_CLASSES)
                self.class_names_vi = data.get('class_names_vi', VIETFOOD_NAMES_VI)
        else:
            self.class_names = VIETFOOD_CLASSES
            self.class_names_vi = VIETFOOD_NAMES_VI
    
    def predict(
        self,
        image: Union[str, np.ndarray, Image.Image],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Predict trên một ảnh
        
        Args:
            image: Đường dẫn ảnh hoặc numpy array hoặc PIL Image
            top_k: Số lượng predictions trả về
            
        Returns:
            List of top-k predictions với keys: class_id, class_name, name_vi, confidence
        """
        # Load image
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image).convert('RGB')
        else:
            img = image.convert('RGB')
        
        # Transform
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probabilities = F.softmax(outputs, dim=1)
        
        # Get top-k
        top_probs, top_indices = torch.topk(probabilities[0], top_k)
        
        predictions = []
        for prob, idx in zip(top_probs.cpu().numpy(), top_indices.cpu().numpy()):
            class_name = self.class_names[idx] if idx < len(self.class_names) else f"class_{idx}"
            name_vi = self.class_names_vi.get(class_name, class_name)
            
            predictions.append({
                'class_id': int(idx),
                'class_name': class_name,
                'name_vi': name_vi,
                'confidence': float(prob)
            })
        
        return predictions
    
    def predict_batch(
        self,
        images: List[Union[str, np.ndarray, Image.Image]],
        top_k: int = 5
    ) -> List[List[Dict]]:
        """Predict trên nhiều ảnh"""
        return [self.predict(img, top_k) for img in images]


# =====================================================
# UNIFIED PREDICTOR
# =====================================================

class VietFoodPredictor:
    """
    Unified predictor hỗ trợ cả YOLO detection và classification
    """
    
    def __init__(
        self,
        model_path: str,
        model_type: str = "auto",  # "yolo", "classification", "auto"
        device: str = "cuda",
        **kwargs
    ):
        self.model_type = model_type
        self.device = device
        
        # Auto detect model type
        if model_type == "auto":
            self.model_type = self._detect_model_type(model_path)
        
        # Load model
        if self.model_type == "yolo":
            self.model = YOLODetector(model_path, device, **kwargs)
        else:
            self.model = FoodClassifier(model_path, device=device, **kwargs)
        
        print(f"✅ VietFood Predictor ready (type: {self.model_type})")
    
    def _detect_model_type(self, model_path: str) -> str:
        """Auto detect model type từ file"""
        model_path = Path(model_path)
        
        # Check filename
        if 'yolo' in model_path.stem.lower():
            return 'yolo'
        
        # Check file content (YOLO models have specific structure)
        try:
            checkpoint = torch.load(model_path, map_location='cpu')
            if isinstance(checkpoint, dict):
                if 'model' in checkpoint and hasattr(checkpoint['model'], 'yaml'):
                    return 'yolo'
        except:
            pass
        
        return 'classification'
    
    def predict(self, image: Union[str, np.ndarray, Image.Image], **kwargs):
        """
        Predict trên một ảnh
        """
        return self.model.predict(image, **kwargs)
    
    def predict_batch(self, images: List, **kwargs):
        """
        Predict trên nhiều ảnh
        """
        return self.model.predict_batch(images, **kwargs)


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="VietFood67 Inference")
    parser.add_argument("--model", "-m", type=str, required=True,
                       help="Path to model weights")
    parser.add_argument("--source", "-s", type=str, required=True,
                       help="Image path or directory")
    parser.add_argument("--type", "-t", type=str, default="auto",
                       choices=["auto", "yolo", "classification"],
                       help="Model type")
    parser.add_argument("--conf", type=float, default=0.25,
                       help="Confidence threshold")
    parser.add_argument("--device", type=str, default="cuda",
                       help="Device (cuda or cpu)")
    parser.add_argument("--top-k", type=int, default=5,
                       help="Top-k predictions (for classification)")
    parser.add_argument("--output", "-o", type=str, default=None,
                       help="Output JSON file")
    
    args = parser.parse_args()
    
    # Load predictor
    predictor = VietFoodPredictor(
        model_path=args.model,
        model_type=args.type,
        device=args.device,
        conf_threshold=args.conf
    )
    
    # Get images
    source = Path(args.source)
    if source.is_dir():
        images = list(source.glob("*.jpg")) + list(source.glob("*.png")) + list(source.glob("*.jpeg"))
    else:
        images = [source]
    
    print(f"\n📷 Processing {len(images)} images...")
    
    # Predict
    all_results = []
    
    for img_path in images:
        print(f"\n🔍 {img_path.name}")
        
        start_time = time.time()
        
        if predictor.model_type == "yolo":
            predictions = predictor.predict(str(img_path), conf=args.conf)
        else:
            predictions = predictor.predict(str(img_path), top_k=args.top_k)
        
        elapsed = time.time() - start_time
        
        # Print results
        for pred in predictions:
            conf = pred['confidence'] * 100
            print(f"   {pred['name_vi']} ({pred['class_name']}): {conf:.1f}%")
            if 'bbox' in pred:
                print(f"      BBox: {pred['bbox']}")
        
        print(f"   ⏱️ {elapsed*1000:.1f}ms")
        
        all_results.append({
            'image': str(img_path),
            'predictions': predictions
        })
    
    # Save results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {args.output}")


if __name__ == "__main__":
    main()
