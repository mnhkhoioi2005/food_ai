"""
Food Recognition Endpoints
- Upload image
- Camera capture recognition
- Recognition history
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User, RecognitionHistory
from app.models.food import Food
from app.models.interaction import Interaction
from app.schemas.food import RecognitionResponse, RecognitionResult, RecognitionHistoryResponse

router = APIRouter()

# Thư mục lưu ảnh upload
UPLOAD_DIR = "uploads/recognition"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_upload_file(file: UploadFile) -> str:
    """Lưu file upload và trả về đường dẫn"""
    # Tạo tên file unique
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Lưu file
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    
    return f"/uploads/recognition/{filename}"


async def call_ai_server(image_path: str) -> dict:
    """
    Gọi AI Server để nhận diện món ăn
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Đọc file ảnh
            with open(image_path.replace('/uploads/', 'uploads/'), 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                response = await client.post(
                    f"{settings.AI_SERVER_URL}/predict",
                    files=files
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        print(f"AI Server error: {e}")
        return None


@router.post("/upload", response_model=RecognitionResponse)
async def recognize_from_upload(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Nhận diện món ăn từ hình ảnh upload
    - Hỗ trợ: JPG, PNG, WEBP
    - Max size: 10MB
    """
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="File phải là hình ảnh (JPG, PNG, WEBP)"
        )
    
    # Check file size (10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File quá lớn. Tối đa 10MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Lưu file
    image_url = await save_upload_file(file)
    
    # Gọi AI Server
    ai_result = await call_ai_server(image_url)
    
    predictions = []
    top_prediction = None
    image_width = None
    image_height = None
    
    if ai_result and ai_result.get('success'):
        image_width = ai_result.get('image_width')
        image_height = ai_result.get('image_height')
        # Lấy predictions từ AI
        for pred in ai_result.get('predictions', []):
            # Tìm food trong database
            food = db.query(Food).filter(
                Food.ai_label == pred.get('label')
            ).first()
            
            if food:
                result = RecognitionResult(
                    food_id=food.id,
                    food_name=food.name,
                    food_name_en=food.name_en,
                    confidence=pred.get('confidence', 0),
                    region=food.region,
                    description=food.description,
                    image_url=food.image_url,
                    bbox=pred.get('bbox')
                )
                predictions.append(result)
        
        if predictions:
            top_prediction = predictions[0]
    else:
        # AI Server không phản hồi hoặc lỗi - trả về rỗng, không dùng mock
        pass
    
    # Lưu lịch sử nhận diện
    if current_user:
        history = RecognitionHistory(
            user_id=current_user.id,
            image_url=image_url,
            predicted_food_id=top_prediction.food_id if top_prediction else None,
            predicted_food_name=top_prediction.food_name if top_prediction else None,
            confidence=str(top_prediction.confidence) if top_prediction else None
        )
        db.add(history)
        
        # Lưu interaction
        if top_prediction:
            interaction = Interaction(
                user_id=current_user.id,
                food_id=top_prediction.food_id,
                interaction_type="recognize"
            )
            db.add(interaction)
        
        db.commit()
    
    return RecognitionResponse(
        success=True,
        predictions=predictions,
        top_prediction=top_prediction,
        message="Nhận diện thành công" if predictions else "Không thể nhận diện món ăn",
        image_width=image_width,
        image_height=image_height
    )


@router.post("/camera", response_model=RecognitionResponse)
async def recognize_from_camera(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Nhận diện món ăn từ camera capture
    - Tương tự upload nhưng dành cho ảnh chụp từ camera
    """
    # Sử dụng cùng logic với upload
    return await recognize_from_upload(file, current_user, db)


@router.get("/history", response_model=List[RecognitionHistoryResponse])
async def get_recognition_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử nhận diện của user hiện tại
    """
    history = db.query(RecognitionHistory)\
        .filter(RecognitionHistory.user_id == current_user.id)\
        .order_by(RecognitionHistory.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [RecognitionHistoryResponse.model_validate(h) for h in history]


@router.get("/admin/stats")
async def get_recognition_stats(
    current_admin: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [Admin] Thống kê lượt nhận diện
    """
    if current_admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    total = db.query(RecognitionHistory).count()
    
    # Thống kê theo ngày (7 ngày gần nhất)
    from sqlalchemy import func
    daily_stats = db.query(
        func.date(RecognitionHistory.created_at).label('date'),
        func.count(RecognitionHistory.id).label('count')
    ).group_by(
        func.date(RecognitionHistory.created_at)
    ).order_by(
        func.date(RecognitionHistory.created_at).desc()
    ).limit(7).all()
    
    return {
        "total_recognitions": total,
        "daily_stats": [{"date": str(d.date), "count": d.count} for d in daily_stats]
    }
