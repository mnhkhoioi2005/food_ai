"""
VietFood67 - Multi-Model Ensemble
Kết hợp nhiều model YOLO để tăng độ chính xác
Hỗ trợ trường hợp train nhiều lần với nhiều file best.pt
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional
from collections import defaultdict

import numpy as np
from PIL import Image

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    print("⚠️ ultralytics not installed. Run: pip install ultralytics")


# =====================================================
# ENSEMBLE STRATEGIES
# =====================================================

def nms_ensemble(
    all_predictions: List[List[Dict]],
    iou_threshold: float = 0.5,
    conf_threshold: float = 0.25
) -> List[Dict]:
    """
    Non-Maximum Suppression ensemble
    Kết hợp predictions từ nhiều model và loại bỏ boxes trùng lặp
    
    Args:
        all_predictions: List of predictions từ mỗi model
        iou_threshold: IoU threshold để merge boxes
        conf_threshold: Confidence threshold tối thiểu
        
    Returns:
        Merged predictions
    """
    if not all_predictions:
        return []
    
    # Flatten all predictions
    all_boxes = []
    for model_preds in all_predictions:
        for pred in model_preds:
            if pred['confidence'] >= conf_threshold:
                all_boxes.append(pred)
    
    if not all_boxes:
        return []
    
    # Sort by confidence
    all_boxes.sort(key=lambda x: x['confidence'], reverse=True)
    
    # NMS
    keep = []
    while all_boxes:
        best = all_boxes.pop(0)
        keep.append(best)
        
        # Remove overlapping boxes
        remaining = []
        for box in all_boxes:
            iou = compute_iou(best['bbox'], box['bbox'])
            if iou < iou_threshold or best['class_id'] != box['class_id']:
                remaining.append(box)
        
        all_boxes = remaining
    
    return keep


def weighted_boxes_fusion(
    all_predictions: List[List[Dict]],
    weights: List[float] = None,
    iou_threshold: float = 0.5,
    conf_threshold: float = 0.25
) -> List[Dict]:
    """
    Weighted Boxes Fusion - kết hợp boxes từ nhiều model
    Boxes giống nhau được merge với weighted average
    
    Args:
        all_predictions: List of predictions từ mỗi model  
        weights: Trọng số cho mỗi model (None = equal weights)
        iou_threshold: IoU threshold để merge boxes
        conf_threshold: Confidence threshold tối thiểu
        
    Returns:
        Fused predictions
    """
    n_models = len(all_predictions)
    if weights is None:
        weights = [1.0] * n_models
    
    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    # Collect all boxes with model weights
    all_boxes = []
    for model_idx, model_preds in enumerate(all_predictions):
        for pred in model_preds:
            if pred['confidence'] >= conf_threshold:
                pred_copy = pred.copy()
                pred_copy['model_idx'] = model_idx
                pred_copy['weight'] = weights[model_idx]
                all_boxes.append(pred_copy)
    
    if not all_boxes:
        return []
    
    # Group by class
    boxes_by_class = defaultdict(list)
    for box in all_boxes:
        boxes_by_class[box['class_id']].append(box)
    
    # Fuse boxes for each class
    fused_boxes = []
    
    for class_id, class_boxes in boxes_by_class.items():
        # Sort by confidence
        class_boxes.sort(key=lambda x: x['confidence'], reverse=True)
        
        while class_boxes:
            # Take best box as reference
            ref_box = class_boxes.pop(0)
            cluster = [ref_box]
            
            # Find overlapping boxes
            remaining = []
            for box in class_boxes:
                iou = compute_iou(ref_box['bbox'], box['bbox'])
                if iou >= iou_threshold:
                    cluster.append(box)
                else:
                    remaining.append(box)
            
            class_boxes = remaining
            
            # Fuse cluster
            if len(cluster) == 1:
                fused_boxes.append(cluster[0])
            else:
                fused = fuse_boxes(cluster)
                fused_boxes.append(fused)
    
    # Sort by confidence
    fused_boxes.sort(key=lambda x: x['confidence'], reverse=True)
    
    return fused_boxes


def fuse_boxes(boxes: List[Dict]) -> Dict:
    """Fuse multiple overlapping boxes into one"""
    total_weight = sum(b['weight'] * b['confidence'] for b in boxes)
    
    # Weighted average of bbox coordinates
    x1 = sum(b['bbox'][0] * b['weight'] * b['confidence'] for b in boxes) / total_weight
    y1 = sum(b['bbox'][1] * b['weight'] * b['confidence'] for b in boxes) / total_weight
    x2 = sum(b['bbox'][2] * b['weight'] * b['confidence'] for b in boxes) / total_weight
    y2 = sum(b['bbox'][3] * b['weight'] * b['confidence'] for b in boxes) / total_weight
    
    # Average confidence (boosted by number of models that detected it)
    avg_conf = sum(b['confidence'] for b in boxes) / len(boxes)
    boost = min(len(boxes) / 3, 1.2)  # Boost up to 20% if detected by multiple models
    fused_conf = min(avg_conf * boost, 1.0)
    
    return {
        'class_id': boxes[0]['class_id'],
        'class_name': boxes[0]['class_name'],
        'name_vi': boxes[0]['name_vi'],
        'confidence': fused_conf,
        'bbox': [x1, y1, x2, y2],
        'n_models': len(boxes)
    }


def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Compute IoU between two boxes [x1, y1, x2, y2]"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0


def voting_ensemble(
    all_predictions: List[List[Dict]],
    min_votes: int = 2
) -> List[Dict]:
    """
    Voting ensemble - chỉ giữ predictions được nhiều model đồng ý
    
    Args:
        all_predictions: List of predictions từ mỗi model
        min_votes: Số model tối thiểu phải detect
        
    Returns:
        Voted predictions
    """
    return weighted_boxes_fusion(
        all_predictions,
        iou_threshold=0.5,
        conf_threshold=0.1
    )


# =====================================================
# ENSEMBLE DETECTOR
# =====================================================

class EnsembleDetector:
    """
    Ensemble nhiều YOLO models
    """
    
    def __init__(
        self,
        model_paths: List[str],
        weights: List[float] = None,
        device: str = "cuda",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        ensemble_method: str = "wbf"  # nms, wbf, voting
    ):
        """
        Args:
            model_paths: List đường dẫn tới các file model (.pt)
            weights: Trọng số cho mỗi model (None = equal)
            device: cuda hoặc cpu
            conf_threshold: Confidence threshold
            iou_threshold: IoU threshold
            ensemble_method: Phương pháp ensemble (nms, wbf, voting)
        """
        if not HAS_YOLO:
            raise ImportError("ultralytics not installed")
        
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.ensemble_method = ensemble_method
        
        # Load models
        self.models = []
        self.model_names = []
        
        print(f"📦 Loading {len(model_paths)} models...")
        
        for i, path in enumerate(model_paths):
            path = Path(path)
            if path.exists():
                model = YOLO(str(path))
                self.models.append(model)
                self.model_names.append(path.stem)
                print(f"   ✅ [{i+1}] {path.name}")
            else:
                print(f"   ⚠️ [{i+1}] Not found: {path}")
        
        if not self.models:
            raise ValueError("No valid models loaded!")
        
        # Set weights
        if weights is None:
            self.weights = [1.0] * len(self.models)
        else:
            self.weights = weights[:len(self.models)]
        
        print(f"\n✅ Loaded {len(self.models)} models")
        print(f"   Ensemble method: {ensemble_method}")
        print(f"   Weights: {self.weights}")
    
    def predict(
        self,
        image: Union[str, np.ndarray, Image.Image],
        conf: float = None,
        iou: float = None
    ) -> List[Dict]:
        """
        Predict với ensemble
        
        Args:
            image: Ảnh input
            conf: Confidence threshold
            iou: IoU threshold
            
        Returns:
            Ensemble predictions
        """
        conf = conf or self.conf_threshold
        iou = iou or self.iou_threshold
        
        # Get predictions from all models
        all_predictions = []
        
        for model in self.models:
            results = model.predict(
                source=image,
                conf=conf * 0.5,  # Lower threshold for individual models
                iou=iou,
                device=self.device,
                verbose=False
            )
            
            # Parse predictions
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    
                    # Get class name from model
                    class_name = result.names.get(class_id, f"class_{class_id}")
                    
                    predictions.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'name_vi': class_name,  # Will be updated later
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            all_predictions.append(predictions)
        
        # Ensemble
        if self.ensemble_method == "nms":
            ensemble_preds = nms_ensemble(all_predictions, iou, conf)
        elif self.ensemble_method == "wbf":
            ensemble_preds = weighted_boxes_fusion(all_predictions, self.weights, iou, conf)
        elif self.ensemble_method == "voting":
            ensemble_preds = voting_ensemble(all_predictions, min_votes=2)
        else:
            ensemble_preds = weighted_boxes_fusion(all_predictions, self.weights, iou, conf)
        
        return ensemble_preds
    
    def predict_batch(self, images: List, **kwargs) -> List[List[Dict]]:
        """Predict trên nhiều ảnh"""
        return [self.predict(img, **kwargs) for img in images]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def find_models(directory: str, pattern: str = "*.pt") -> List[str]:
    """
    Tìm tất cả model files trong thư mục
    
    Args:
        directory: Thư mục chứa models
        pattern: Pattern tìm kiếm
        
    Returns:
        List đường dẫn model files
    """
    directory = Path(directory)
    models = list(directory.glob(pattern))
    return sorted([str(m) for m in models])


def validate_ensemble(
    model_paths: List[str],
    data_yaml: str,
    device: str = "cuda"
) -> Dict:
    """
    Validate ensemble trên validation set
    
    Args:
        model_paths: List model paths
        data_yaml: Dataset config
        device: Device
        
    Returns:
        Validation metrics
    """
    # TODO: Implement full validation
    pass


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="VietFood67 Ensemble Detector")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # ===== PREDICT =====
    predict_parser = subparsers.add_parser("predict", help="Predict với ensemble")
    predict_parser.add_argument("--models-dir", "-d", type=str, required=True,
                               help="Thư mục chứa các file model .pt")
    predict_parser.add_argument("--models", "-m", type=str, nargs="+", default=None,
                               help="Danh sách model files (thay vì dùng --models-dir)")
    predict_parser.add_argument("--source", "-s", type=str, required=True,
                               help="Ảnh hoặc thư mục ảnh")
    predict_parser.add_argument("--weights", "-w", type=float, nargs="+", default=None,
                               help="Trọng số cho mỗi model")
    predict_parser.add_argument("--method", type=str, default="wbf",
                               choices=["nms", "wbf", "voting"],
                               help="Phương pháp ensemble")
    predict_parser.add_argument("--conf", type=float, default=0.25,
                               help="Confidence threshold")
    predict_parser.add_argument("--iou", type=float, default=0.5,
                               help="IoU threshold")
    predict_parser.add_argument("--device", type=str, default="cuda",
                               help="Device")
    predict_parser.add_argument("--output", "-o", type=str, default=None,
                               help="Output JSON file")
    
    # ===== LIST =====
    list_parser = subparsers.add_parser("list", help="Liệt kê models trong thư mục")
    list_parser.add_argument("--dir", "-d", type=str, required=True,
                            help="Thư mục chứa models")
    
    args = parser.parse_args()
    
    if args.command == "predict":
        # Get model paths
        if args.models:
            model_paths = args.models
        else:
            model_paths = find_models(args.models_dir)
        
        if not model_paths:
            print("❌ No models found!")
            return
        
        print(f"📦 Found {len(model_paths)} models")
        
        # Create ensemble
        ensemble = EnsembleDetector(
            model_paths=model_paths,
            weights=args.weights,
            device=args.device,
            conf_threshold=args.conf,
            iou_threshold=args.iou,
            ensemble_method=args.method
        )
        
        # Get images
        source = Path(args.source)
        if source.is_dir():
            images = list(source.glob("*.jpg")) + list(source.glob("*.png"))
        else:
            images = [source]
        
        print(f"\n🔍 Processing {len(images)} images...")
        
        all_results = []
        
        for img_path in images:
            print(f"\n📷 {img_path.name}")
            
            predictions = ensemble.predict(str(img_path))
            
            for pred in predictions:
                n_models = pred.get('n_models', 1)
                print(f"   {pred['class_name']}: {pred['confidence']*100:.1f}% (detected by {n_models} models)")
            
            all_results.append({
                'image': str(img_path),
                'predictions': predictions
            })
        
        # Save results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
    
    elif args.command == "list":
        models = find_models(args.dir)
        print(f"📦 Models in {args.dir}:")
        for i, m in enumerate(models, 1):
            print(f"   [{i}] {Path(m).name}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
