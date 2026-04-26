"""
AI Server Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


# Base paths
BASE_DIR = Path(__file__).parent
AI_MODELS_DIR = BASE_DIR.parent / "ai_models"
TRAINED_WEIGHTS_DIR = AI_MODELS_DIR / "trained_weights"


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    
    # Model
    MODEL_TYPE: str = "yolo"  # yolo, ensemble, efficientnet, mobilenet, resnet
    
    # YOLO model paths - hỗ trợ nhiều models
    # Đặt các file best.pt với tên: best_1.pt, best_2.pt, ... hoặc model_part1.pt, model_part2.pt
    YOLO_MODELS_DIR: str = str(TRAINED_WEIGHTS_DIR)
    
    # Model chính (nếu chỉ dùng 1 model)
    YOLO_MODEL_PATH: str = str(TRAINED_WEIGHTS_DIR / "best.pt")
    
    # Ensemble settings
    USE_ENSEMBLE: bool = True  # Tự động ensemble nếu có nhiều models
    ENSEMBLE_METHOD: str = "wbf"  # nms, wbf, voting
    ENSEMBLE_WEIGHTS: str = ""  # Comma-separated weights, vd: "1.0,1.0,0.8" (empty = equal)
    
    # Classification model path (fallback)
    CLASSIFICATION_MODEL_PATH: str = str(TRAINED_WEIGHTS_DIR / "classification_best.pt")
    
    # Legacy paths
    MODEL_PATH: str = "models/food_classifier.h5"
    LABELS_PATH: str = "models/labels.json"
    
    # Image
    IMAGE_SIZE: int = 640  # 640 for YOLO, 224 for classification
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    
    # Device
    DEVICE: str = "cpu"  # cuda or cpu (auto-detect below)
    
    class Config:
        env_file = ".env"
    
    def get_yolo_model_paths(self) -> list:
        """Lấy danh sách tất cả model paths"""
        models_dir = Path(self.YOLO_MODELS_DIR)
        if not models_dir.exists():
            return []
        
        # Tìm tất cả file .pt
        model_files = list(models_dir.glob("*.pt"))
        
        # Loại bỏ các file không phải YOLO model (classification, etc.)
        yolo_models = [
            str(f) for f in model_files 
            if not any(x in f.stem.lower() for x in ['classification', 'efficientnet', 'resnet', 'vit'])
        ]
        
        return sorted(yolo_models)
    
    def get_ensemble_weights(self) -> list:
        """Parse ensemble weights từ string"""
        if not self.ENSEMBLE_WEIGHTS:
            return None
        try:
            return [float(w.strip()) for w in self.ENSEMBLE_WEIGHTS.split(",")]
        except:
            return None


settings = Settings()
