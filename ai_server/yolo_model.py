"""
VietFood YOLO Model Handler
Sử dụng YOLO để detect món ăn Việt Nam
Hỗ trợ ensemble nhiều models
"""
import os
import sys
import json
import numpy as np
from PIL import Image
from typing import List, Dict, Optional, Union
from pathlib import Path
import io

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ai_models" / "food_recognition"))

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    print("[WARNING] ultralytics not installed. Run: pip install ultralytics")

from config import settings

# Import ensemble nếu có
try:
    from ensemble import EnsembleDetector, weighted_boxes_fusion, nms_ensemble
    HAS_ENSEMBLE = True
except ImportError:
    HAS_ENSEMBLE = False


# VietFood67 class ID → slug mapping (theo thứ tự trong vietfood67.yaml)
VIETFOOD_CLASS_NAMES = {
    0: "banh_bao",    1: "banh_beo",         2: "banh_bot_loc",    3: "banh_can",
    4: "banh_canh",  5: "banh_chung",       6: "banh_cuon",       7: "banh_da_lon",
    8: "banh_duc",   9: "banh_gio",        10: "banh_khot",      11: "banh_mi",
   12: "banh_pia",  13: "banh_trang_nuong",14: "banh_xeo",       15: "bo_kho",
   16: "bun_bo_hue",17: "bun_cha",         18: "bun_dau_mam_tom",19: "bun_mam",
   20: "bun_moc",   21: "bun_rieu",        22: "bun_thit_nuong", 23: "ca_kho_to",
   24: "canh_chua", 25: "cao_lau",         26: "chao_long",       27: "che",
   28: "com_chay",  29: "com_ga",          30: "com_tam",         31: "face",
   32: "ga_nuong",  33: "goi_cuon",        34: "goi_ga",          35: "hu_tieu",
   36: "lau",       37: "mi_quang",        38: "mi_xao",          39: "nem_chua",
   40: "nem_nuong", 41: "oc",              42: "pho",             43: "rau_muong_xao_toi",
   44: "thit_kho",  45: "thit_nuong",      46: "xoi",             47: "che_ba_mau",
   48: "banh_flan", 49: "sua_chua",        50: "sinh_to",         51: "nuoc_mia",
   52: "tra_sua",   53: "ca_phe",          54: "nuoc_dua",        55: "kem",
   56: "xoi_xeo",   57: "xoi_gac",         58: "bap_xao",         59: "khoai_lang_nuong",
   60: "trung_vit_lon", 61: "com_rang",     62: "sup",             63: "mi_tom",
   64: "chao",  65: "bun_cha_ca",      66: "banh_trang_tron", 67: "bot_chien",
}

# VietFood67 class names
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
    "bun_cha_ca": "Bún Chả Cá", "banh_trang_tron": "Bánh Tráng Trộn", "bot_chien": "Bột Chiên",
    # Legacy mappings
    "pho_bo": "Phở Bò", "pho_ga": "Phở Gà", "pho_chay": "Phở Chay",
    "lau_thai": "Lẩu Thái"
}


class YOLOFoodDetector:
    """
    YOLO-based food detector với hỗ trợ ensemble
    """
    
    def __init__(self):
        self.models: List[YOLO] = []
        self.model_names: List[str] = []
        self.device = settings.DEVICE
        self.conf_threshold = settings.CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.IOU_THRESHOLD
        self.use_ensemble = settings.USE_ENSEMBLE
        self.ensemble_method = settings.ENSEMBLE_METHOD
        self.ensemble_weights = settings.get_ensemble_weights()
        self.class_names: Dict[int, str] = {}
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load YOLO model(s)"""
        if not HAS_YOLO:
            print("[WARNING] YOLO not available, using mock predictions")
            return

        # Nếu tắt ensemble → chỉ load 1 model tốt nhất (YOLO_MODEL_PATH)
        if not self.use_ensemble:
            single_path = Path(settings.YOLO_MODEL_PATH)
            if single_path.exists():
                model_paths = [str(single_path)]
                print(f"[INFO] Ensemble OFF → Load single model: {single_path.name}")
            else:
                # Fallback: lấy model cuối trong thư mục (thường là tốt nhất)
                all_paths = settings.get_yolo_model_paths()
                model_paths = all_paths[-1:] if all_paths else []
                if model_paths:
                    print(f"[INFO] YOLO_MODEL_PATH not found → Fallback to: {Path(model_paths[0]).name}")
                else:
                    print(f"[WARNING] No model found at {settings.YOLO_MODEL_PATH}")
                    print("   Please train a model or place best.pt in ai_models/trained_weights/")
                    return
        else:
            # Ensemble ON → load tất cả models từ thư mục
            model_paths = settings.get_yolo_model_paths()
            if not model_paths:
                single_path = Path(settings.YOLO_MODEL_PATH)
                if single_path.exists():
                    model_paths = [str(single_path)]
                else:
                    print(f"[WARNING] No model found at {settings.YOLO_MODEL_PATH}")
                    print("   Please train a model or place best.pt in ai_models/trained_weights/")
                    return
        
        print(f"[INFO] Loading {len(model_paths)} YOLO model(s)...")
        
        for path in model_paths:
            try:
                model = YOLO(path)
                self.models.append(model)
                self.model_names.append(Path(path).stem)
                print(f"   [OK] Loaded: {Path(path).name}")
                
                # Get class names from first model, ưu tiên VIETFOOD_CLASS_NAMES
                if not self.class_names:
                    # Nếu model.names là generic (class_0, class_1, ...) thì dùng mapping cứng
                    raw = model.names if hasattr(model, 'names') else {}
                    if raw and not str(list(raw.values())[0]).startswith('class_'):
                        self.class_names = raw
                    else:
                        self.class_names = VIETFOOD_CLASS_NAMES
            except Exception as e:
                print(f"   [ERROR] Failed to load {path}: {e}")
        
        if self.models:
            print(f"\n[OK] Total models loaded: {len(self.models)}")
            if len(self.models) > 1 and self.use_ensemble:
                print(f"   Ensemble enabled: {self.ensemble_method}")
        else:
            print("[WARNING] No models loaded, using mock predictions")
    
    def _make_tta_crops(self, image: Image.Image) -> List[Image.Image]:
        """
        Tạo các biến thể ảnh cho Test Time Augmentation.
        Gồm: ảnh gốc, center crop 80%, 4 corner crop 70%, flip ngang.
        """
        w, h = image.size
        crops = [image]  # 1. Gốc

        # 2. Center crop 80%
        m = 0.10
        crops.append(image.crop((int(w*m), int(h*m), int(w*(1-m)), int(h*(1-m)))))

        # 3. Center crop 65%
        m2 = 0.175
        crops.append(image.crop((int(w*m2), int(h*m2), int(w*(1-m2)), int(h*(1-m2)))))

        # 4–7. Four corner crops 70%
        cw, ch = int(w*0.70), int(h*0.70)
        crops.append(image.crop((0, 0, cw, ch)))
        crops.append(image.crop((w-cw, 0, w, ch)))
        crops.append(image.crop((0, h-ch, cw, h)))
        crops.append(image.crop((w-cw, h-ch, w, h)))

        # 8. Flip ngang của ảnh gốc
        crops.append(image.transpose(Image.FLIP_LEFT_RIGHT))

        return crops

    def _run_model_on_image(self, model: YOLO, img: Image.Image, conf: float) -> Dict[int, float]:
        """
        Chạy 1 model trên 1 ảnh, trả về dict {class_id: max_confidence}.
        """
        results = model.predict(
            source=img,
            conf=conf,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False
        )
        scores: Dict[int, float] = {}
        for result in results:
            for box in result.boxes:
                cid = int(box.cls[0])
                conf_val = float(box.conf[0])
                if conf_val > scores.get(cid, 0):
                    scores[cid] = conf_val
        return scores

    def _get_bboxes_for_classes(self, image: Image.Image, class_ids: List[int]) -> Dict[int, List[float]]:
        """
        Chạy model trên ảnh gốc để lấy bounding box thực cho các class đã vote.
        Trả về dict {class_id: [x1, y1, x2, y2]} (pixel coords).
        """
        best_boxes: Dict[int, tuple] = {}  # cid -> (conf, bbox)
        target_set = set(class_ids)

        for model in self.models:
            results = model.predict(
                source=image,
                conf=max(0.10, self.conf_threshold * 0.3),
                iou=self.iou_threshold,
                device=self.device,
                verbose=False
            )
            for result in results:
                for box in result.boxes:
                    cid = int(box.cls[0])
                    if cid not in target_set:
                        continue
                    conf_val = float(box.conf[0])
                    if cid not in best_boxes or conf_val > best_boxes[cid][0]:
                        bbox = box.xyxy[0].cpu().numpy().tolist()
                        best_boxes[cid] = (conf_val, bbox)

        return {cid: bbox for cid, (_, bbox) in best_boxes.items()}

    def predict(self, image_bytes: bytes) -> Dict:
        """
        Nhận diện món ăn bằng class-level voting ensemble + TTA.
        Trả về predictions kèm bounding box + image dimensions.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            w, h = image.size

            if not self.models:
                return self._mock_predict()

            predictions = self._predict_class_vote(image)

            # Lấy bbox thực cho các class đã vote
            if predictions:
                voted_cids = [p['class_id'] for p in predictions]
                bbox_map = self._get_bboxes_for_classes(image, voted_cids)
                for p in predictions:
                    cid = p['class_id']
                    if cid in bbox_map:
                        p['bbox'] = [round(v, 1) for v in bbox_map[cid]]

            return {
                'success': True,
                'predictions': predictions,
                'num_models': len(self.models),
                'ensemble': True,
                'image_width': w,
                'image_height': h,
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'predictions': []}

    def _predict_class_vote(self, image: Image.Image) -> List[Dict]:
        """
        Class-level voting ensemble + TTA.

        Thuật toán:
          - Tạo N crops (TTA)
          - Chạy tất cả models trên tất cả crops
          - Gom score theo class dùng weighted sum
          - Filter bằng RAW max confidence (không dùng normalized score để filter)
          - Trả top-5 với confidence = raw max confidence từ model thực tế
        """
        crops = self._make_tta_crops(image)
        # crop weight: ảnh gốc quan trọng nhất, corner crop ít hơn
        crop_weights = [1.5, 1.2, 1.0, 0.7, 0.7, 0.7, 0.7, 0.9]

        n_models = len(self.models)
        # Dùng conf thấp để TTA bắt được nhiều tín hiệu
        low_conf = max(0.05, self.conf_threshold * 0.4)

        # Gom tổng score và raw max confidence theo class
        class_score: Dict[int, float] = {}
        class_vote_count: Dict[int, int] = {}
        class_max_conf: Dict[int, float] = {}  # raw max confidence từ model thực tế

        for m_idx, model in enumerate(self.models):
            m_weight = 1.0
            for c_idx, crop in enumerate(crops):
                cw = crop_weights[c_idx] if c_idx < len(crop_weights) else 0.7
                scores = self._run_model_on_image(model, crop, low_conf)
                for cid, conf_val in scores.items():
                    class_score[cid] = class_score.get(cid, 0) + conf_val * cw * m_weight
                    class_vote_count[cid] = class_vote_count.get(cid, 0) + 1
                    # Lưu raw confidence cao nhất (dùng để filter và display)
                    if conf_val > class_max_conf.get(cid, 0):
                        class_max_conf[cid] = conf_val

        if not class_score:
            return []

        # Sắp xếp theo weighted sum score (ranking)
        # Thêm bonus cho class được nhiều crop/model đồng thuận
        max_votes = n_models * len(crops)
        final_score: Dict[int, float] = {}
        for cid, score in class_score.items():
            vote_ratio = class_vote_count[cid] / max_votes
            final_score[cid] = score * (1 + 0.5 * vote_ratio)  # bonus consistency

        sorted_classes = sorted(final_score.items(), key=lambda x: x[1], reverse=True)

        predictions = []
        for rank, (cid, _) in enumerate(sorted_classes[:5], start=1):
            # Dùng RAW max confidence để filter và display - có nghĩa thực tế
            raw_conf = class_max_conf.get(cid, 0)
            if raw_conf < self.conf_threshold:
                break  # cắt những class model không đủ tự tin
            class_name = (VIETFOOD_CLASS_NAMES.get(cid)
                          or self.class_names.get(cid)
                          or f"class_{cid}")
            name_vi = VIETFOOD_NAMES_VI.get(class_name, class_name)
            predictions.append({
                'class_id': cid,
                'label': class_name,
                'name_vi': name_vi,
                'confidence': round(raw_conf, 4),  # raw confidence có nghĩa hơn
                'bbox': [],
                'rank': rank,
                'n_models': class_vote_count.get(cid, 0),
            })

        return predictions

    def _predict_single(self, image: Image.Image, model: YOLO) -> List[Dict]:
        """Dùng khi chỉ có 1 model (không TTA)"""
        scores = self._run_model_on_image(model, image, self.conf_threshold)
        predictions = []
        for rank, (cid, conf_val) in enumerate(
            sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5], start=1
        ):
            class_name = (VIETFOOD_CLASS_NAMES.get(cid)
                          or self.class_names.get(cid)
                          or f"class_{cid}")
            predictions.append({
                'class_id': cid,
                'label': class_name,
                'name_vi': VIETFOOD_NAMES_VI.get(class_name, class_name),
                'confidence': round(conf_val, 4),
                'bbox': [],
                'rank': rank,
            })
        return predictions
    
    def _predict_ensemble(self, image: Image.Image) -> List[Dict]:
        """Predict với ensemble"""
        all_predictions = []
        
        # Get predictions from all models
        for model in self.models:
            results = model.predict(
                source=image,
                conf=self.conf_threshold * 0.5,  # Lower threshold for individual
                iou=self.iou_threshold,
                device=self.device,
                verbose=False
            )
            
            model_preds = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    class_name = (VIETFOOD_CLASS_NAMES.get(class_id)
                                  or self.class_names.get(class_id)
                                  or result.names.get(class_id, f"class_{class_id}"))
                    
                    model_preds.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'name_vi': VIETFOOD_NAMES_VI.get(class_name, class_name),
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            all_predictions.append(model_preds)
        
        # Ensemble
        if HAS_ENSEMBLE:
            if self.ensemble_method == "wbf":
                ensemble_preds = weighted_boxes_fusion(
                    all_predictions, 
                    self.ensemble_weights,
                    self.iou_threshold,
                    self.conf_threshold
                )
            else:
                ensemble_preds = nms_ensemble(
                    all_predictions,
                    self.iou_threshold,
                    self.conf_threshold
                )
        else:
            # Simple NMS if ensemble module not available
            ensemble_preds = self._simple_nms(all_predictions)
        
        # Format output
        predictions = []
        for pred in ensemble_preds:
            predictions.append({
                'class_id': pred['class_id'],
                'label': pred['class_name'],
                'name_vi': pred['name_vi'],
                'confidence': round(pred['confidence'], 4),
                'bbox': [round(x, 2) for x in pred['bbox']],
                'rank': len(predictions) + 1,
                'n_models': pred.get('n_models', 1)
            })
        
        return predictions
    
    def _simple_nms(self, all_predictions: List[List[Dict]]) -> List[Dict]:
        """Simple NMS khi không có ensemble module"""
        # Flatten
        all_boxes = []
        for preds in all_predictions:
            all_boxes.extend(preds)
        
        if not all_boxes:
            return []
        
        # Sort by confidence
        all_boxes.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Simple NMS
        keep = []
        while all_boxes:
            best = all_boxes.pop(0)
            if best['confidence'] >= self.conf_threshold:
                keep.append(best)
            
            # Remove overlapping
            remaining = []
            for box in all_boxes:
                iou = self._compute_iou(best['bbox'], box['bbox'])
                if iou < self.iou_threshold or best['class_id'] != box['class_id']:
                    remaining.append(box)
            all_boxes = remaining
        
        return keep
    
    def _compute_iou(self, box1: List[float], box2: List[float]) -> float:
        """Compute IoU"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _mock_predict(self) -> Dict:
        """Mock prediction khi không có model"""
        import random
        
        sample_foods = [
            ("pho", "Phở"),
            ("banh_mi", "Bánh Mì"),
            ("com_tam", "Cơm Tấm"),
            ("bun_cha", "Bún Chả"),
            ("goi_cuon", "Gỏi Cuốn")
        ]
        
        num_results = random.randint(1, 3)
        selected = random.sample(sample_foods, num_results)
        
        predictions = []
        for i, (label, name_vi) in enumerate(selected):
            confidence = max(0.5, 0.95 - (i * 0.15) + random.uniform(-0.1, 0.1))
            predictions.append({
                'class_id': i,
                'label': label,
                'name_vi': name_vi,
                'confidence': round(confidence, 4),
                'bbox': [100, 100, 400, 400],
                'rank': i + 1
            })
        
        return {
            'success': True,
            'predictions': predictions,
            'note': '[WARNING] Mock prediction - No model loaded. Place best.pt in ai_models/trained_weights/'
        }


# Singleton instance
_detector: Optional[YOLOFoodDetector] = None


def get_yolo_detector() -> YOLOFoodDetector:
    """Get or create YOLO detector instance"""
    global _detector
    if _detector is None:
        _detector = YOLOFoodDetector()
    return _detector
