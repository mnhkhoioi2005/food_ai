"""
AI Server - Vietnamese Food Recognition
FastAPI server để serve AI model nhận diện món ăn
Hỗ trợ YOLO detection với ensemble nhiều models
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from config import settings

# Import model handlers
if settings.MODEL_TYPE in ["yolo", "ensemble"]:
    from yolo_model import get_yolo_detector as get_model
    USE_YOLO = True
else:
    from model import get_classifier as get_model
    USE_YOLO = False


# Pydantic models for response
class PredictionItem(BaseModel):
    label: str
    confidence: float
    rank: int
    name_vi: Optional[str] = None
    bbox: Optional[List[float]] = None
    n_models: Optional[int] = None


class PredictionResponse(BaseModel):
    success: bool
    predictions: List[PredictionItem]
    message: Optional[str] = None
    note: Optional[str] = None
    num_models: Optional[int] = None
    ensemble: Optional[bool] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: str
    num_models: int
    labels_count: int


# Create FastAPI app
app = FastAPI(
    title="Vietnamese Food Recognition AI",
    description="AI API để nhận diện món ăn Việt Nam từ hình ảnh. Hỗ trợ YOLO detection với ensemble nhiều models.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load model khi server start"""
    print("🚀 Starting AI Server...")
    model = get_model()
    
    if USE_YOLO:
        num_models = len(model.models)
        print(f"✓ YOLO models loaded: {num_models}")
        if num_models > 1:
            print(f"✓ Ensemble enabled: {model.ensemble_method}")
    else:
        print(f"✓ Model loaded: {model.framework}")
        print(f"✓ Labels: {len(model.labels)}")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Vietnamese Food Recognition AI Server",
        "version": "2.0.0",
        "model_type": settings.MODEL_TYPE,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model = get_model()
    
    if USE_YOLO:
        return HealthResponse(
            status="healthy",
            model_loaded=len(model.models) > 0,
            model_type="yolo",
            num_models=len(model.models),
            labels_count=len(model.class_names)
        )
    else:
        return HealthResponse(
            status="healthy",
            model_loaded=model.model is not None or model.framework == 'mock',
            model_type=model.framework,
            num_models=1,
            labels_count=len(model.labels)
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Nhận diện món ăn từ hình ảnh
    
    - **file**: File hình ảnh (JPG, PNG, WEBP)
    
    Returns:
        Danh sách predictions với label, confidence, bbox (nếu dùng YOLO)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File phải là hình ảnh (JPG, PNG, WEBP)"
        )
    
    # Read file
    contents = await file.read()
    
    # Check file size (max 10MB)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File quá lớn. Tối đa 10MB"
        )
    
    # Get prediction
    model = get_model()
    result = model.predict(contents)
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result.get('error', 'Prediction failed')
        )
    
    # Build predictions list
    predictions = []
    for pred in result['predictions']:
        predictions.append(PredictionItem(
            label=pred.get('label', pred.get('class_name', '')),
            confidence=pred['confidence'],
            rank=pred.get('rank', 0),
            name_vi=pred.get('name_vi'),
            bbox=pred.get('bbox'),
            n_models=pred.get('n_models')
        ))
    
    return PredictionResponse(
        success=True,
        predictions=predictions,
        message=f"Đã nhận diện {len(predictions)} món ăn",
        note=result.get('note'),
        num_models=result.get('num_models'),
        ensemble=result.get('ensemble'),
        image_width=result.get('image_width'),
        image_height=result.get('image_height'),
    )


@app.get("/labels")
async def get_labels():
    """
    Lấy danh sách các nhãn món ăn model có thể nhận diện
    """
    model = get_model()
    
    if USE_YOLO:
        return {
            "total": len(model.class_names),
            "labels": list(model.class_names.values()) if model.class_names else []
        }
    else:
        return {
            "total": len(model.labels),
            "labels": model.labels
        }


@app.get("/models")
async def get_models():
    """
    Lấy thông tin về các models đang được load
    """
    model = get_model()
    
    if USE_YOLO:
        return {
            "model_type": "yolo",
            "num_models": len(model.models),
            "model_names": model.model_names,
            "ensemble_enabled": model.use_ensemble and len(model.models) > 1,
            "ensemble_method": model.ensemble_method if len(model.models) > 1 else None,
            "device": model.device,
            "conf_threshold": model.conf_threshold,
            "iou_threshold": model.iou_threshold
        }
    else:
        return {
            "model_type": model.framework,
            "num_models": 1,
            "model_names": ["default"],
            "ensemble_enabled": False
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
