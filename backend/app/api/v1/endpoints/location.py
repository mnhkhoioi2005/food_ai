"""
Location Endpoints
- Get nearby restaurants
- Search restaurants by food
"""
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/restaurants/nearby")
async def get_nearby_restaurants(
    latitude: float = Query(..., description="Vĩ độ"),
    longitude: float = Query(..., description="Kinh độ"),
    radius: int = Query(5000, description="Bán kính (m)"),
    food_name: str = Query(None, description="Tên món ăn")
):
    """
    Tìm nhà hàng gần đây có món ăn
    """
    # TODO: Integrate with Google Maps API
    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "radius": radius,
        "food_name": food_name,
        "restaurants": []
    }


@router.get("/restaurants/{restaurant_id}")
async def get_restaurant_detail(restaurant_id: str):
    """
    Lấy thông tin chi tiết nhà hàng
    """
    # TODO: Get from Google Maps API
    return {
        "id": restaurant_id,
        "name": "",
        "address": "",
        "rating": 0,
        "photos": [],
        "menu": []
    }
