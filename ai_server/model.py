"""
Food Classification Model
Sử dụng EfficientNet/MobileNet để nhận diện món ăn Việt Nam
"""
import os
import json
import numpy as np
from PIL import Image
from typing import List, Dict, Tuple, Optional
import io

# Kiểm tra xem có GPU không
try:
    import tensorflow as tf
    # Disable GPU nếu không cần (chạy trên CPU cho demo)
    # tf.config.set_visible_devices([], 'GPU')
    USE_TENSORFLOW = True
except ImportError:
    USE_TENSORFLOW = False

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision import models
    USE_PYTORCH = True
except ImportError:
    USE_PYTORCH = False

from config import settings


class FoodClassifier:
    """
    Food Classification Model
    Hỗ trợ cả TensorFlow và PyTorch
    """
    
    def __init__(self):
        self.model = None
        self.labels: List[str] = []
        self.image_size = settings.IMAGE_SIZE
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
        # Load labels
        self._load_labels()
        
        # Load model
        self._load_model()
    
    def _load_labels(self):
        """Load danh sách nhãn món ăn"""
        labels_path = settings.LABELS_PATH
        
        if os.path.exists(labels_path):
            with open(labels_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.labels = data.get('labels', [])
        else:
            # Default labels cho demo
            self.labels = [
                "pho_bo",
                "pho_ga",
                "pho_chay",
                "banh_mi",
                "bun_cha",
                "bun_bo_hue",
                "com_tam",
                "goi_cuon",
                "banh_xeo",
                "che_ba_mau",
                "lau_thai",
                "mi_quang",
                "cao_lau",
                "banh_cuon",
                "xoi"
            ]
            
            # Tạo file labels
            os.makedirs(os.path.dirname(labels_path), exist_ok=True)
            with open(labels_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'labels': self.labels,
                    'label_names': {
                        'pho_bo': 'Phở Bò',
                        'pho_ga': 'Phở Gà',
                        'pho_chay': 'Phở Chay',
                        'banh_mi': 'Bánh Mì',
                        'bun_cha': 'Bún Chả',
                        'bun_bo_hue': 'Bún Bò Huế',
                        'com_tam': 'Cơm Tấm',
                        'goi_cuon': 'Gỏi Cuốn',
                        'banh_xeo': 'Bánh Xèo',
                        'che_ba_mau': 'Chè Ba Màu',
                        'lau_thai': 'Lẩu Thái',
                        'mi_quang': 'Mì Quảng',
                        'cao_lau': 'Cao Lầu',
                        'banh_cuon': 'Bánh Cuốn',
                        'xoi': 'Xôi'
                    }
                }, f, ensure_ascii=False, indent=2)
        
        print(f"Loaded {len(self.labels)} food labels")
    
    def _load_model(self):
        """Load model nhận diện"""
        model_path = settings.MODEL_PATH
        
        if os.path.exists(model_path):
            # Load pre-trained model
            if USE_TENSORFLOW and model_path.endswith('.h5'):
                self.model = tf.keras.models.load_model(model_path)
                self.framework = 'tensorflow'
                print(f"Loaded TensorFlow model from {model_path}")
            elif USE_PYTORCH and model_path.endswith('.pth'):
                self.model = torch.load(model_path)
                self.model.eval()
                self.framework = 'pytorch'
                print(f"Loaded PyTorch model from {model_path}")
        else:
            # Sử dụng pre-trained model cho demo
            if USE_PYTORCH:
                print("Loading pre-trained EfficientNet (PyTorch) for demo...")
                self.model = models.efficientnet_b0(pretrained=True)
                self.model.eval()
                self.framework = 'pytorch'
            elif USE_TENSORFLOW:
                print("Loading pre-trained EfficientNet (TensorFlow) for demo...")
                self.model = tf.keras.applications.EfficientNetB0(
                    weights='imagenet',
                    include_top=True
                )
                self.framework = 'tensorflow'
            else:
                print("⚠️ No ML framework available. Using mock predictions.")
                self.framework = 'mock'
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Tiền xử lý ảnh trước khi đưa vào model
        """
        # Resize về kích thước chuẩn
        image = image.convert('RGB')
        image = image.resize((self.image_size, self.image_size))
        
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        if self.framework == 'tensorflow':
            # Normalize cho EfficientNet TF
            img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)
        elif self.framework == 'pytorch':
            # Normalize cho PyTorch
            img_array = img_array / 255.0
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img_array = (img_array - mean) / std
            img_array = np.transpose(img_array, (2, 0, 1))
            img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image_bytes: bytes) -> Dict:
        """
        Nhận diện món ăn từ bytes ảnh
        
        Args:
            image_bytes: Ảnh dạng bytes
            
        Returns:
            Dict chứa predictions và thông tin
        """
        try:
            # Load ảnh
            image = Image.open(io.BytesIO(image_bytes))
            
            if self.framework == 'mock':
                # Mock prediction cho demo
                return self._mock_predict()
            
            # Preprocess
            img_array = self.preprocess_image(image)
            
            # Predict
            if self.framework == 'tensorflow':
                predictions = self.model.predict(img_array, verbose=0)[0]
            elif self.framework == 'pytorch':
                with torch.no_grad():
                    tensor = torch.from_numpy(img_array).float()
                    outputs = self.model(tensor)
                    predictions = torch.nn.functional.softmax(outputs, dim=1)[0].numpy()
            
            # Map predictions to labels
            # Với pre-trained ImageNet model, ta mock mapping sang food labels
            # Trong thực tế, cần train model với dataset món ăn Việt
            results = self._map_predictions(predictions)
            
            return {
                'success': True,
                'predictions': results
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions': []
            }
    
    def _map_predictions(self, predictions: np.ndarray) -> List[Dict]:
        """
        Map predictions sang food labels
        Đây là demo, trong thực tế model được train với food dataset
        """
        import random
        
        # Simulate food classification results
        # Random chọn một số labels với confidence ngẫu nhiên
        results = []
        
        # Chọn top food ngẫu nhiên để demo
        num_predictions = min(5, len(self.labels))
        selected_indices = random.sample(range(len(self.labels)), num_predictions)
        
        # Tạo confidence scores giảm dần
        confidences = sorted([random.uniform(0.5, 0.98) for _ in range(num_predictions)], reverse=True)
        
        for i, idx in enumerate(selected_indices):
            label = self.labels[idx]
            confidence = confidences[i]
            
            if confidence >= self.confidence_threshold:
                results.append({
                    'label': label,
                    'confidence': round(confidence, 4),
                    'rank': i + 1
                })
        
        return results
    
    def _mock_predict(self) -> Dict:
        """Mock prediction khi không có ML framework"""
        import random
        
        # Random chọn món ăn
        num_results = random.randint(1, 3)
        selected = random.sample(self.labels, num_results)
        
        results = []
        for i, label in enumerate(selected):
            confidence = max(0.5, 0.95 - (i * 0.15) + random.uniform(-0.1, 0.1))
            results.append({
                'label': label,
                'confidence': round(confidence, 4),
                'rank': i + 1
            })
        
        return {
            'success': True,
            'predictions': results,
            'note': 'Mock prediction - No ML model loaded'
        }


# Singleton instance
_classifier: Optional[FoodClassifier] = None


def get_classifier() -> FoodClassifier:
    """Get or create classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = FoodClassifier()
    return _classifier
