"""
Food Search & CRUD Endpoints
- Search by keyword
- Filter by criteria
- CRUD operations
"""
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import re

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.models.food import Food, Ingredient, FoodIngredient, Allergy, FoodImage
from app.models.interaction import Interaction
from app.schemas.food import (
    FoodResponse, FoodDetailResponse, FoodCreate, FoodUpdate, 
    FoodListResponse, IngredientResponse, AllergyResponse
)

router = APIRouter()


def create_slug(name: str) -> str:
    """Tạo slug từ tên món ăn"""
    # Chuyển về lowercase và thay khoảng trắng bằng dấu gạch ngang
    slug = name.lower().strip()
    slug = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', slug)
    slug = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', slug)
    slug = re.sub(r'[ìíịỉĩ]', 'i', slug)
    slug = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', slug)
    slug = re.sub(r'[ùúụủũưừứựửữ]', 'u', slug)
    slug = re.sub(r'[ỳýỵỷỹ]', 'y', slug)
    slug = re.sub(r'đ', 'd', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug


# ==================== Public Endpoints ====================

@router.get("/", response_model=FoodListResponse)
async def search_foods(
    q: Optional[str] = Query(None, min_length=1, description="Từ khóa tìm kiếm"),
    region: Optional[str] = Query(None, description="Vùng miền: bac, trung, nam"),
    food_type: Optional[str] = Query(None, description="Loại: mon_nuoc, mon_kho"),
    category: Optional[str] = Query(None, description="Danh mục: pho, bun, com, banh"),
    is_vegetarian: Optional[bool] = Query(None, description="Món chay"),
    is_vegan: Optional[bool] = Query(None, description="Món thuần chay"),
    spicy_level_min: Optional[int] = Query(None, ge=0, le=5),
    spicy_level_max: Optional[int] = Query(None, ge=0, le=5),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm món ăn theo từ khóa và bộ lọc
    """
    query = db.query(Food).filter(Food.is_active == True)
    
    # Tìm theo từ khóa
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Food.name.ilike(search_term),
                Food.name_en.ilike(search_term),
                Food.description.ilike(search_term)
            )
        )
    
    # Filter theo vùng miền
    if region:
        query = query.filter(Food.region == region)
    
    # Filter theo loại món
    if food_type:
        query = query.filter(Food.food_type == food_type)
    
    # Filter theo danh mục
    if category:
        query = query.filter(Food.category == category)
    
    # Filter món chay
    if is_vegetarian is not None:
        query = query.filter(Food.is_vegetarian == is_vegetarian)
    
    if is_vegan is not None:
        query = query.filter(Food.is_vegan == is_vegan)
    
    # Filter theo độ cay
    if spicy_level_min is not None:
        query = query.filter(Food.spicy_level >= spicy_level_min)
    if spicy_level_max is not None:
        query = query.filter(Food.spicy_level <= spicy_level_max)
    
    # Đếm tổng số kết quả
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    # Phân trang
    foods = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return FoodListResponse(
        items=[FoodResponse.model_validate(f) for f in foods],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/filters")
async def get_available_filters(db: Session = Depends(get_db)):
    """
    Lấy danh sách các bộ lọc có sẵn
    """
    return {
        "regions": [
            {"value": "bac", "label": "Miền Bắc", "label_en": "Northern"},
            {"value": "trung", "label": "Miền Trung", "label_en": "Central"},
            {"value": "nam", "label": "Miền Nam", "label_en": "Southern"}
        ],
        "food_types": [
            {"value": "mon_nuoc", "label": "Món nước", "label_en": "Soup dishes"},
            {"value": "mon_kho", "label": "Món khô", "label_en": "Dry dishes"},
            {"value": "mon_xao", "label": "Món xào", "label_en": "Stir-fried"},
            {"value": "mon_nuong", "label": "Món nướng", "label_en": "Grilled"},
            {"value": "mon_hap", "label": "Món hấp", "label_en": "Steamed"},
            {"value": "do_uong", "label": "Đồ uống", "label_en": "Beverages"},
            {"value": "trang_mieng", "label": "Tráng miệng", "label_en": "Desserts"}
        ],
        "categories": [
            {"value": "pho", "label": "Phở"},
            {"value": "bun", "label": "Bún"},
            {"value": "com", "label": "Cơm"},
            {"value": "banh", "label": "Bánh"},
            {"value": "che", "label": "Chè"},
            {"value": "goi", "label": "Gỏi/Salad"},
            {"value": "lau", "label": "Lẩu/Hotpot"}
        ],
        "spicy_levels": [
            {"value": 0, "label": "Không cay", "label_en": "Not spicy"},
            {"value": 1, "label": "Ít cay", "label_en": "Mild"},
            {"value": 2, "label": "Cay vừa", "label_en": "Medium"},
            {"value": 3, "label": "Cay", "label_en": "Spicy"},
            {"value": 4, "label": "Rất cay", "label_en": "Very spicy"},
            {"value": 5, "label": "Siêu cay", "label_en": "Extremely spicy"}
        ]
    }


@router.get("/popular")
async def get_popular_foods(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách món ăn phổ biến (theo view count)
    """
    foods = db.query(Food)\
        .filter(Food.is_active == True)\
        .order_by(Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    return [FoodResponse.model_validate(f) for f in foods]


@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_all_ingredients(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách nguyên liệu
    """
    query = db.query(Ingredient)
    if category:
        query = query.filter(Ingredient.category == category)
    ingredients = query.all()
    return [IngredientResponse.model_validate(i) for i in ingredients]


@router.get("/allergies", response_model=List[AllergyResponse])
async def get_all_allergies(db: Session = Depends(get_db)):
    """
    Lấy danh sách chất gây dị ứng
    """
    allergies = db.query(Allergy).all()
    return [AllergyResponse.model_validate(a) for a in allergies]


@router.get("/{food_id}", response_model=FoodDetailResponse)
async def get_food_detail(
    food_id: int,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết món ăn
    """
    food = db.query(Food).filter(Food.id == food_id, Food.is_active == True).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    # Tăng view count
    food.view_count += 1
    db.commit()
    
    return FoodDetailResponse.model_validate(food)


@router.get("/slug/{slug}", response_model=FoodDetailResponse)
async def get_food_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin món ăn theo slug
    """
    food = db.query(Food).filter(Food.slug == slug, Food.is_active == True).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    food.view_count += 1
    db.commit()
    
    return FoodDetailResponse.model_validate(food)


# ==================== Admin Endpoints ====================

@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(
    food_data: FoodCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Tạo món ăn mới
    """
    # Tạo slug
    slug = create_slug(food_data.name)
    base_slug = slug
    counter = 1
    while db.query(Food).filter(Food.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Tạo food
    food_dict = food_data.model_dump(exclude={'ingredient_ids', 'allergy_ids'})
    food = Food(**food_dict, slug=slug)
    
    db.add(food)
    db.commit()
    db.refresh(food)
    
    # Thêm allergies
    if food_data.allergy_ids:
        allergies = db.query(Allergy).filter(Allergy.id.in_(food_data.allergy_ids)).all()
        food.allergies = allergies
        db.commit()
    
    return FoodResponse.model_validate(food)


@router.put("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Cập nhật món ăn
    """
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    update_data = food_data.model_dump(exclude_unset=True)
    
    # Nếu đổi tên, cập nhật slug
    if 'name' in update_data:
        slug = create_slug(update_data['name'])
        base_slug = slug
        counter = 1
        while db.query(Food).filter(Food.slug == slug, Food.id != food_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        update_data['slug'] = slug
    
    for field, value in update_data.items():
        setattr(food, field, value)
    
    db.commit()
    db.refresh(food)
    
    return FoodResponse.model_validate(food)


@router.delete("/{food_id}")
async def delete_food(
    food_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Xóa món ăn (soft delete)
    """
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy món ăn"
        )
    
    food.is_active = False
    db.commit()
    
    return {"message": "Đã xóa món ăn thành công"}


@router.get("/admin/all", response_model=FoodListResponse)
async def get_all_foods_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_inactive: bool = Query(False),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Lấy tất cả món ăn kể cả inactive
    """
    query = db.query(Food)
    if not include_inactive:
        query = query.filter(Food.is_active == True)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    foods = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return FoodListResponse(
        items=[FoodResponse.model_validate(f) for f in foods],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/admin/count")
async def get_foods_count(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Thống kê số lượng món ăn
    """
    total = db.query(Food).count()
    active = db.query(Food).filter(Food.is_active == True).count()
    
    by_region = {}
    for region in ['bac', 'trung', 'nam']:
        by_region[region] = db.query(Food).filter(
            Food.region == region, 
            Food.is_active == True
        ).count()
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "by_region": by_region
    }
