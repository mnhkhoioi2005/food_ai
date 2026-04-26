"""
Recommendation Endpoints
- Location-based recommendations
- Personalized recommendations (Content-based & Collaborative filtering)
- Taste-based recommendations
"""
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
import random

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.food import Food
from app.models.interaction import Interaction, Recommendation
from app.schemas.recommendation import (
    RecommendationRequest, RecommendedFood, RecommendationResponse,
    InteractionCreate, InteractionResponse, UserHistoryResponse
)

router = APIRouter()


def calculate_content_based_score(food: Food, user: User) -> tuple[float, str]:
    """
    Tính điểm gợi ý dựa trên content-based filtering
    So sánh đặc điểm món ăn với preferences của user
    """
    score = 0.5  # Base score
    reasons = []
    
    # Match độ cay
    spicy_diff = abs(food.spicy_level - (user.spicy_level or 2))
    if spicy_diff <= 1:
        score += 0.15
        reasons.append("phù hợp độ cay")
    
    # Match món nước/khô
    if user.prefer_soup and food.food_type == "mon_nuoc":
        score += 0.15
        reasons.append("bạn thích món nước")
    elif not user.prefer_soup and food.food_type == "mon_kho":
        score += 0.15
        reasons.append("bạn thích món khô")
    
    # Match vegetarian
    if user.is_vegetarian and food.is_vegetarian:
        score += 0.2
        reasons.append("món chay")
    
    # Match vùng miền yêu thích
    if user.favorite_regions and food.region in (user.favorite_regions or []):
        score += 0.1
        reasons.append(f"vùng miền yêu thích ({food.region})")
    
    # Penalty nếu có allergen
    if user.allergens:
        for allergy in food.allergies:
            if allergy.name in user.allergens:
                score -= 0.3
                reasons.append(f"⚠️ chứa {allergy.name}")
    
    score = max(0, min(1, score))  # Clamp 0-1
    reason = "Phù hợp với " + ", ".join(reasons) if reasons else "Gợi ý phổ biến"
    
    return score, reason


def get_collaborative_recommendations(user_id: int, db: Session, limit: int = 10) -> List[Food]:
    """
    Collaborative Filtering đơn giản:
    Tìm user có cùng sở thích và gợi ý món họ đã thích
    """
    # Lấy danh sách food_id mà user hiện tại đã tương tác
    user_foods = db.query(Interaction.food_id).filter(
        Interaction.user_id == user_id
    ).distinct().all()
    user_food_ids = [f[0] for f in user_foods]
    
    if not user_food_ids:
        return []
    
    # Tìm users khác đã tương tác với cùng món ăn
    similar_users = db.query(Interaction.user_id).filter(
        and_(
            Interaction.food_id.in_(user_food_ids),
            Interaction.user_id != user_id
        )
    ).distinct().limit(50).all()
    similar_user_ids = [u[0] for u in similar_users]
    
    if not similar_user_ids:
        return []
    
    # Lấy món ăn mà similar users đã thích nhưng user hiện tại chưa xem
    recommended = db.query(Food).join(Interaction).filter(
        and_(
            Interaction.user_id.in_(similar_user_ids),
            ~Food.id.in_(user_food_ids),
            Food.is_active == True
        )
    ).group_by(Food.id).order_by(
        func.count(Interaction.id).desc()
    ).limit(limit).all()
    
    return recommended


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy gợi ý món ăn thông minh
    Kết hợp Content-based và Collaborative filtering
    """
    recommendations = []
    
    # 1. Content-based filtering (nếu có user)
    if current_user:
        # Lấy tất cả món ăn active
        foods = db.query(Food).filter(Food.is_active == True).limit(100).all()
        
        for food in foods:
            score, reason = calculate_content_based_score(food, current_user)
            if score >= 0.5:
                recommendations.append(RecommendedFood(
                    id=food.id,
                    name=food.name,
                    name_en=food.name_en,
                    description=food.description,
                    region=food.region,
                    food_type=food.food_type,
                    spicy_level=food.spicy_level,
                    is_vegetarian=food.is_vegetarian,
                    image_url=food.image_url,
                    score=score,
                    recommendation_type="content_based",
                    reason=reason
                ))
        
        # 2. Collaborative filtering
        collab_foods = get_collaborative_recommendations(current_user.id, db, 5)
        for food in collab_foods:
            # Kiểm tra xem đã có trong recommendations chưa
            existing = next((r for r in recommendations if r.id == food.id), None)
            if not existing:
                recommendations.append(RecommendedFood(
                    id=food.id,
                    name=food.name,
                    name_en=food.name_en,
                    description=food.description,
                    region=food.region,
                    food_type=food.food_type,
                    spicy_level=food.spicy_level,
                    is_vegetarian=food.is_vegetarian,
                    image_url=food.image_url,
                    score=0.7,
                    recommendation_type="collaborative",
                    reason="Người dùng tương tự cũng thích"
                ))
    
    # 3. Trending/Popular (fallback)
    if len(recommendations) < request.limit:
        popular_foods = db.query(Food)\
            .filter(Food.is_active == True)\
            .order_by(Food.view_count.desc())\
            .limit(request.limit - len(recommendations))\
            .all()
        
        for food in popular_foods:
            existing = next((r for r in recommendations if r.id == food.id), None)
            if not existing:
                recommendations.append(RecommendedFood(
                    id=food.id,
                    name=food.name,
                    name_en=food.name_en,
                    description=food.description,
                    region=food.region,
                    food_type=food.food_type,
                    spicy_level=food.spicy_level,
                    is_vegetarian=food.is_vegetarian,
                    image_url=food.image_url,
                    score=0.5,
                    recommendation_type="trending",
                    reason="Đang được nhiều người quan tâm"
                ))
    
    # Sort theo score và limit
    recommendations.sort(key=lambda x: x.score, reverse=True)
    recommendations = recommendations[:request.limit]
    
    return RecommendationResponse(
        success=True,
        recommendations=recommendations,
        total=len(recommendations),
        message=f"Đã tìm thấy {len(recommendations)} gợi ý phù hợp"
    )


@router.get("/nearby", response_model=RecommendationResponse)
async def get_nearby_recommendations(
    latitude: float = Query(..., description="Vĩ độ"),
    longitude: float = Query(..., description="Kinh độ"),
    radius: int = Query(5000, description="Bán kính (m)"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Gợi ý món ăn theo vị trí hiện tại
    Gợi ý món ăn đặc trưng của vùng miền gần nhất
    """
    # Xác định vùng miền dựa trên vĩ độ
    # (Đây là logic đơn giản, trong production nên dùng Google Maps API)
    if latitude >= 19:
        region = "bac"
        region_name = "Miền Bắc"
    elif latitude >= 14:
        region = "trung"
        region_name = "Miền Trung"
    else:
        region = "nam"
        region_name = "Miền Nam"
    
    # Lấy món ăn theo vùng miền
    foods = db.query(Food)\
        .filter(Food.region == region, Food.is_active == True)\
        .order_by(Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    recommendations = []
    for food in foods:
        recommendations.append(RecommendedFood(
            id=food.id,
            name=food.name,
            name_en=food.name_en,
            description=food.description,
            region=food.region,
            food_type=food.food_type,
            spicy_level=food.spicy_level,
            is_vegetarian=food.is_vegetarian,
            image_url=food.image_url,
            score=0.8,
            recommendation_type="location_based",
            reason=f"Đặc sản {region_name}"
        ))
    
    return RecommendationResponse(
        success=True,
        recommendations=recommendations,
        total=len(recommendations),
        message=f"Gợi ý món ăn {region_name}"
    )


@router.get("/personalized", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gợi ý món ăn cá nhân hóa dựa trên lịch sử tương tác
    """
    request = RecommendationRequest(limit=limit)
    return await get_recommendations(request, current_user, db)


@router.get("/by-taste", response_model=RecommendationResponse)
async def get_recommendations_by_taste(
    spicy_level: Optional[int] = Query(None, ge=0, le=5, description="Độ cay ưa thích"),
    prefer_soup: Optional[bool] = Query(None, description="Thích món nước"),
    is_vegetarian: Optional[bool] = Query(None, description="Ăn chay"),
    region: Optional[str] = Query(None, description="Vùng miền: bac, trung, nam"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Gợi ý món ăn theo khẩu vị (không cần đăng nhập)
    """
    query = db.query(Food).filter(Food.is_active == True)
    
    if spicy_level is not None:
        # Lấy món có độ cay trong khoảng ±1
        query = query.filter(
            Food.spicy_level.between(max(0, spicy_level - 1), min(5, spicy_level + 1))
        )
    
    if prefer_soup is not None:
        food_type = "mon_nuoc" if prefer_soup else "mon_kho"
        query = query.filter(Food.food_type == food_type)
    
    if is_vegetarian:
        query = query.filter(Food.is_vegetarian == True)
    
    if region:
        query = query.filter(Food.region == region)
    
    foods = query.order_by(Food.view_count.desc()).limit(limit).all()
    
    recommendations = []
    for food in foods:
        reasons = []
        if spicy_level is not None:
            reasons.append(f"độ cay {food.spicy_level}/5")
        if is_vegetarian:
            reasons.append("món chay")
        if region:
            reasons.append(f"vùng {region}")
        
        recommendations.append(RecommendedFood(
            id=food.id,
            name=food.name,
            name_en=food.name_en,
            description=food.description,
            region=food.region,
            food_type=food.food_type,
            spicy_level=food.spicy_level,
            is_vegetarian=food.is_vegetarian,
            image_url=food.image_url,
            score=0.75,
            recommendation_type="content_based",
            reason=", ".join(reasons) if reasons else "Phù hợp khẩu vị"
        ))
    
    return RecommendationResponse(
        success=True,
        recommendations=recommendations,
        total=len(recommendations)
    )


@router.get("/similar/{food_id}", response_model=RecommendationResponse)
async def get_similar_foods(
    food_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Gợi ý món ăn tương tự
    Dựa trên vùng miền, loại món, độ cay
    """
    # Lấy thông tin món ăn gốc
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    # Tìm món tương tự
    similar = db.query(Food).filter(
        and_(
            Food.id != food_id,
            Food.is_active == True,
            # Cùng vùng miền HOẶC cùng loại món HOẶC cùng độ cay
            (Food.region == food.region) | 
            (Food.food_type == food.food_type) |
            (Food.spicy_level == food.spicy_level)
        )
    ).order_by(Food.view_count.desc()).limit(limit).all()
    
    recommendations = []
    for f in similar:
        similarities = []
        if f.region == food.region:
            similarities.append(f"cùng vùng {f.region}")
        if f.food_type == food.food_type:
            similarities.append("cùng loại")
        if f.spicy_level == food.spicy_level:
            similarities.append(f"cùng độ cay")
        
        score = len(similarities) * 0.3 + 0.1
        
        recommendations.append(RecommendedFood(
            id=f.id,
            name=f.name,
            name_en=f.name_en,
            description=f.description,
            region=f.region,
            food_type=f.food_type,
            spicy_level=f.spicy_level,
            is_vegetarian=f.is_vegetarian,
            image_url=f.image_url,
            score=min(1, score),
            recommendation_type="content_based",
            reason=f"Tương tự vì {', '.join(similarities)}" if similarities else "Gợi ý tương tự"
        ))
    
    return RecommendationResponse(
        success=True,
        recommendations=recommendations,
        total=len(recommendations)
    )


# ==================== Interaction Endpoints ====================

@router.post("/interaction", response_model=InteractionResponse)
async def record_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ghi lại tương tác của người dùng
    Dùng cho recommendation engine
    """
    # Kiểm tra food tồn tại
    food = db.query(Food).filter(Food.id == interaction.food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    # Tạo interaction
    new_interaction = Interaction(
        user_id=current_user.id,
        food_id=interaction.food_id,
        interaction_type=interaction.interaction_type,
        rating=interaction.rating
    )
    
    db.add(new_interaction)
    
    # Cập nhật view count nếu là view
    if interaction.interaction_type == "view":
        food.view_count += 1
    
    db.commit()
    db.refresh(new_interaction)
    
    return InteractionResponse.model_validate(new_interaction)


@router.get("/history", response_model=UserHistoryResponse)
async def get_user_history(
    limit: int = Query(50, ge=1, le=200),
    interaction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử tương tác của user
    """
    query = db.query(Interaction).filter(Interaction.user_id == current_user.id)
    
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)
    
    interactions = query.order_by(Interaction.created_at.desc()).limit(limit).all()
    
    return UserHistoryResponse(
        interactions=[InteractionResponse.model_validate(i) for i in interactions],
        total=len(interactions)
    )
