"""
Database Seed Script
Tạo dữ liệu mẫu cho database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.food import Food, Ingredient, FoodIngredient, Allergy
from app.models.interaction import Interaction
from app.core.security import get_password_hash


def create_tables():
    """Tạo tất cả tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Đã tạo tables")


def seed_users(db: Session):
    """Tạo users mẫu"""
    users = [
        {
            "email": "admin@vietfood.ai",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin VietFood",
            "role": "admin",
            "spicy_level": 3,
            "prefer_soup": True,
            "is_vegetarian": False
        },
        {
            "email": "user@vietfood.ai",
            "hashed_password": get_password_hash("user123"),
            "full_name": "Nguyễn Văn A",
            "role": "user",
            "spicy_level": 2,
            "prefer_soup": True,
            "is_vegetarian": False,
            "favorite_regions": ["bac", "nam"]
        },
        {
            "email": "veggie@vietfood.ai",
            "hashed_password": get_password_hash("user123"),
            "full_name": "Trần Thị B",
            "role": "user",
            "spicy_level": 1,
            "prefer_soup": False,
            "is_vegetarian": True
        }
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
    
    db.commit()
    print(f"✓ Đã tạo {len(users)} users")


def seed_allergies(db: Session):
    """Tạo danh sách dị ứng"""
    allergies = [
        {"name": "Gluten", "name_en": "Gluten", "description": "Có trong lúa mì, bánh phở, bánh mì", "severity": "high"},
        {"name": "Đậu phộng", "name_en": "Peanut", "description": "Có trong nhiều món xào, gỏi", "severity": "high"},
        {"name": "Hải sản", "name_en": "Seafood", "description": "Tôm, cua, mực, cá", "severity": "high"},
        {"name": "Trứng", "name_en": "Egg", "description": "Trứng gà, trứng vịt", "severity": "medium"},
        {"name": "Sữa", "name_en": "Milk/Dairy", "description": "Sữa và các sản phẩm từ sữa", "severity": "medium"},
        {"name": "Đậu nành", "name_en": "Soy", "description": "Đậu hũ, nước tương, đậu nành", "severity": "low"},
        {"name": "MSG", "name_en": "MSG", "description": "Bột ngọt", "severity": "low"},
    ]
    
    for allergy_data in allergies:
        existing = db.query(Allergy).filter(Allergy.name == allergy_data["name"]).first()
        if not existing:
            allergy = Allergy(**allergy_data)
            db.add(allergy)
    
    db.commit()
    print(f"✓ Đã tạo {len(allergies)} allergies")


def seed_ingredients(db: Session):
    """Tạo danh sách nguyên liệu"""
    ingredients = [
        # Thịt
        {"name": "Thịt bò", "name_en": "Beef", "category": "Thịt"},
        {"name": "Thịt heo", "name_en": "Pork", "category": "Thịt"},
        {"name": "Thịt gà", "name_en": "Chicken", "category": "Thịt"},
        {"name": "Giò heo", "name_en": "Pork leg", "category": "Thịt"},
        
        # Hải sản
        {"name": "Tôm", "name_en": "Shrimp", "category": "Hải sản", "is_allergen": True},
        {"name": "Mực", "name_en": "Squid", "category": "Hải sản", "is_allergen": True},
        {"name": "Cá", "name_en": "Fish", "category": "Hải sản", "is_allergen": True},
        
        # Rau củ
        {"name": "Hành tây", "name_en": "Onion", "category": "Rau củ"},
        {"name": "Hành lá", "name_en": "Green onion", "category": "Rau củ"},
        {"name": "Rau mùi", "name_en": "Cilantro", "category": "Rau củ"},
        {"name": "Giá đỗ", "name_en": "Bean sprouts", "category": "Rau củ"},
        {"name": "Xà lách", "name_en": "Lettuce", "category": "Rau củ"},
        {"name": "Húng quế", "name_en": "Thai basil", "category": "Rau củ"},
        {"name": "Cà rốt", "name_en": "Carrot", "category": "Rau củ"},
        {"name": "Dưa leo", "name_en": "Cucumber", "category": "Rau củ"},
        
        # Tinh bột
        {"name": "Bánh phở", "name_en": "Pho noodles", "category": "Tinh bột", "is_allergen": True},
        {"name": "Bún", "name_en": "Rice vermicelli", "category": "Tinh bột"},
        {"name": "Bánh mì", "name_en": "Bread", "category": "Tinh bột", "is_allergen": True},
        {"name": "Cơm", "name_en": "Rice", "category": "Tinh bột"},
        {"name": "Bánh tráng", "name_en": "Rice paper", "category": "Tinh bột"},
        
        # Gia vị
        {"name": "Nước mắm", "name_en": "Fish sauce", "category": "Gia vị"},
        {"name": "Tương ớt", "name_en": "Chili sauce", "category": "Gia vị"},
        {"name": "Tương đen", "name_en": "Hoisin sauce", "category": "Gia vị"},
        {"name": "Chanh", "name_en": "Lime", "category": "Gia vị"},
        {"name": "Ớt", "name_en": "Chili", "category": "Gia vị"},
        {"name": "Gừng", "name_en": "Ginger", "category": "Gia vị"},
        {"name": "Sả", "name_en": "Lemongrass", "category": "Gia vị"},
    ]
    
    for ing_data in ingredients:
        existing = db.query(Ingredient).filter(Ingredient.name == ing_data["name"]).first()
        if not existing:
            ingredient = Ingredient(**ing_data)
            db.add(ingredient)
    
    db.commit()
    print(f"✓ Đã tạo {len(ingredients)} ingredients")


def seed_foods(db: Session):
    """Tạo danh sách món ăn mẫu"""
    foods = [
        {
            "name": "Phở Bò",
            "name_en": "Beef Pho",
            "slug": "pho-bo",
            "description": "Phở là món ăn truyền thống nổi tiếng của Việt Nam, với nước dùng trong veo từ xương bò ninh nhừ, bánh phở mềm và thịt bò tái hoặc chín.",
            "description_en": "Pho is a famous traditional Vietnamese dish with clear broth from simmered beef bones, soft pho noodles and rare or well-done beef.",
            "region": "bac",
            "food_type": "mon_nuoc",
            "category": "pho",
            "spicy_level": 1,
            "is_vegetarian": False,
            "calories": 450,
            "protein": 25,
            "carbs": 50,
            "fat": 15,
            "how_to_eat": "Ăn nóng kèm giá đỗ, rau thơm (húng quế, ngò gai), vắt chanh, thêm tương ớt và tương đen tùy khẩu vị. Có thể thêm quẩy để chấm nước.",
            "how_to_eat_en": "Eat hot with bean sprouts, herbs (Thai basil, culantro), squeeze lime, add chili sauce and hoisin sauce to taste.",
            "image_url": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800",
            "ai_label": "pho_bo",
            "view_count": 1000
        },
        {
            "name": "Bánh Mì",
            "name_en": "Vietnamese Baguette",
            "slug": "banh-mi",
            "description": "Bánh mì Việt Nam là sự kết hợp hoàn hảo giữa vỏ bánh giòn tan và nhân đa dạng: pate, chả lụa, thịt nguội, rau mùi, đồ chua.",
            "description_en": "Vietnamese baguette is a perfect combination of crispy crust and diverse fillings: pate, Vietnamese ham, cold cuts, cilantro, pickled vegetables.",
            "region": "nam",
            "food_type": "mon_kho",
            "category": "banh",
            "spicy_level": 2,
            "is_vegetarian": False,
            "calories": 350,
            "protein": 15,
            "carbs": 45,
            "fat": 12,
            "how_to_eat": "Ăn nguyên ổ, có thể yêu cầu thêm hoặc bớt ớt, bớt rau. Ăn kèm xíu mại hoặc nước ngọt.",
            "how_to_eat_en": "Eat whole, can request more or less chili, less vegetables. Eat with meatballs or soft drinks.",
            "image_url": "https://images.unsplash.com/photo-1600688640154-9619e002df30?w=800",
            "ai_label": "banh_mi",
            "view_count": 850
        },
        {
            "name": "Bún Chả",
            "name_en": "Grilled Pork with Noodles",
            "slug": "bun-cha",
            "description": "Bún chả Hà Nội gồm bún tươi, chả thịt nướng thơm lừng, nước mắm pha chua ngọt và rau sống. Món ăn đặc trưng của ẩm thực Hà Thành.",
            "description_en": "Hanoi bun cha consists of fresh vermicelli, fragrant grilled pork, sweet and sour fish sauce and fresh vegetables. A typical dish of Hanoi cuisine.",
            "region": "bac",
            "food_type": "mon_kho",
            "category": "bun",
            "spicy_level": 2,
            "is_vegetarian": False,
            "calories": 500,
            "protein": 30,
            "carbs": 55,
            "fat": 18,
            "how_to_eat": "Gắp bún và chả vào bát nước mắm, ăn kèm rau sống. Có thể thêm ớt, tỏi băm tùy khẩu vị.",
            "how_to_eat_en": "Pick up vermicelli and grilled meat into fish sauce bowl, eat with fresh vegetables. Can add chili, minced garlic to taste.",
            "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800",
            "ai_label": "bun_cha",
            "view_count": 750
        },
        {
            "name": "Cơm Tấm",
            "name_en": "Broken Rice",
            "slug": "com-tam",
            "description": "Cơm tấm Sài Gòn với gạo tấm dẻo thơm, sườn nướng đậm đà, bì heo giòn sần sật, chả trứng béo ngậy và nước mắm pha đặc trưng.",
            "description_en": "Saigon broken rice with fragrant soft broken rice, savory grilled ribs, crispy shredded pork skin, rich egg meatloaf and special fish sauce.",
            "region": "nam",
            "food_type": "mon_kho",
            "category": "com",
            "spicy_level": 1,
            "is_vegetarian": False,
            "calories": 600,
            "protein": 35,
            "carbs": 65,
            "fat": 22,
            "how_to_eat": "Rưới nước mắm lên cơm và thịt, ăn kèm dưa leo, cà chua. Trộn đều để nước mắm thấm vào cơm.",
            "how_to_eat_en": "Pour fish sauce over rice and meat, eat with cucumber, tomato. Mix well to let fish sauce soak into rice.",
            "image_url": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800",
            "ai_label": "com_tam",
            "view_count": 680
        },
        {
            "name": "Bún Bò Huế",
            "name_en": "Hue Beef Noodle Soup",
            "slug": "bun-bo-hue",
            "description": "Bún bò Huế đặc trưng với nước dùng đậm đà từ xương heo, sả, mắm ruốc. Bún sợi to ăn kèm thịt bò, giò heo, chả cua và rau sống.",
            "description_en": "Hue beef noodle soup is characterized by rich broth from pork bones, lemongrass, shrimp paste. Thick noodles served with beef, pork leg, crab cake and fresh vegetables.",
            "region": "trung",
            "food_type": "mon_nuoc",
            "category": "bun",
            "spicy_level": 4,
            "is_vegetarian": False,
            "calories": 550,
            "protein": 28,
            "carbs": 52,
            "fat": 20,
            "how_to_eat": "Ăn nóng, thêm rau muống bào, bắp chuối, chanh, ớt sa tế. Vắt chanh và thêm mắm ruốc nếu thích.",
            "how_to_eat_en": "Eat hot, add shredded water spinach, banana blossom, lime, satay chili. Squeeze lime and add shrimp paste if you like.",
            "image_url": "https://images.unsplash.com/photo-1576577445504-6af96477db52?w=800",
            "ai_label": "bun_bo_hue",
            "view_count": 600
        },
        {
            "name": "Gỏi Cuốn",
            "name_en": "Fresh Spring Rolls",
            "slug": "goi-cuon",
            "description": "Gỏi cuốn tươi mát với bánh tráng mềm cuốn tôm, thịt heo, bún, rau sống. Chấm cùng nước mắm pha hoặc tương đậu phộng.",
            "description_en": "Fresh spring rolls with soft rice paper wrapped with shrimp, pork, vermicelli, fresh vegetables. Dip with fish sauce or peanut sauce.",
            "region": "nam",
            "food_type": "mon_kho",
            "category": "goi",
            "spicy_level": 0,
            "is_vegetarian": False,
            "calories": 150,
            "protein": 12,
            "carbs": 18,
            "fat": 4,
            "how_to_eat": "Cầm cuốn, chấm vào nước mắm hoặc tương đậu phộng rồi ăn. Không nên cắt nhỏ để giữ nguyên vẹn cuốn.",
            "how_to_eat_en": "Hold the roll, dip into fish sauce or peanut sauce then eat. Do not cut small to keep the roll intact.",
            "image_url": "https://images.unsplash.com/photo-1562967916-eb82221dfb44?w=800",
            "ai_label": "goi_cuon",
            "view_count": 520
        },
        {
            "name": "Bánh Xèo",
            "name_en": "Vietnamese Sizzling Crepe",
            "slug": "banh-xeo",
            "description": "Bánh xèo giòn rụm với vỏ bột gạo nghệ vàng ươm, nhân tôm, thịt, giá đỗ. Cuốn với rau sống và chấm nước mắm chua ngọt.",
            "description_en": "Crispy Vietnamese crepe with golden turmeric rice flour shell, filled with shrimp, pork, bean sprouts. Wrapped with fresh vegetables and dipped in sweet and sour fish sauce.",
            "region": "trung",
            "food_type": "mon_kho",
            "category": "banh",
            "spicy_level": 1,
            "is_vegetarian": False,
            "calories": 400,
            "protein": 18,
            "carbs": 42,
            "fat": 16,
            "how_to_eat": "Bẻ miếng bánh, đặt lên rau sống (xà lách, rau thơm), cuộn lại rồi chấm nước mắm pha.",
            "how_to_eat_en": "Break a piece of crepe, place on fresh vegetables (lettuce, herbs), roll up and dip in fish sauce.",
            "image_url": "https://images.unsplash.com/photo-1562967916-eb82221dfb44?w=800",
            "ai_label": "banh_xeo",
            "view_count": 480
        },
        {
            "name": "Phở Chay",
            "name_en": "Vegetarian Pho",
            "slug": "pho-chay",
            "description": "Phở chay thanh đạm với nước dùng từ rau củ, nấm đông cô, đậu hũ và các loại rau xanh. Phù hợp cho người ăn chay.",
            "description_en": "Light vegetarian pho with vegetable broth, shiitake mushrooms, tofu and green vegetables. Suitable for vegetarians.",
            "region": "bac",
            "food_type": "mon_nuoc",
            "category": "pho",
            "spicy_level": 0,
            "is_vegetarian": True,
            "is_vegan": True,
            "calories": 300,
            "protein": 12,
            "carbs": 48,
            "fat": 6,
            "how_to_eat": "Ăn nóng kèm giá đỗ, rau thơm, chanh. Có thể thêm tương ớt chay.",
            "how_to_eat_en": "Eat hot with bean sprouts, herbs, lime. Can add vegetarian chili sauce.",
            "image_url": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800",
            "ai_label": "pho_chay",
            "view_count": 320
        },
        {
            "name": "Chè Ba Màu",
            "name_en": "Three Color Dessert",
            "slug": "che-ba-mau",
            "description": "Chè ba màu mát lạnh với đậu xanh, đậu đỏ, thạch và nước cốt dừa. Món tráng miệng phổ biến của miền Nam.",
            "description_en": "Cool three color dessert with mung beans, red beans, jelly and coconut milk. A popular Southern Vietnamese dessert.",
            "region": "nam",
            "food_type": "trang_mieng",
            "category": "che",
            "spicy_level": 0,
            "is_vegetarian": True,
            "calories": 250,
            "protein": 6,
            "carbs": 45,
            "fat": 8,
            "how_to_eat": "Khuấy đều các lớp đậu, thạch với nước cốt dừa và đá bào. Ăn bằng muỗng.",
            "how_to_eat_en": "Stir the layers of beans, jelly with coconut milk and shaved ice. Eat with a spoon.",
            "image_url": "https://images.unsplash.com/photo-1555126634-323283e090fa?w=800",
            "ai_label": "che_ba_mau",
            "view_count": 400
        },
        {
            "name": "Lẩu Thái",
            "name_en": "Thai Hotpot",
            "slug": "lau-thai",
            "description": "Lẩu Thái chua cay đậm đà với nước dùng Tom Yum, hải sản tươi sống, rau củ và mì. Phù hợp ăn nhóm.",
            "description_en": "Spicy and sour Thai hotpot with Tom Yum broth, fresh seafood, vegetables and noodles. Suitable for group dining.",
            "region": "nam",
            "food_type": "mon_nuoc",
            "category": "lau",
            "spicy_level": 5,
            "is_vegetarian": False,
            "calories": 450,
            "protein": 32,
            "carbs": 35,
            "fat": 18,
            "how_to_eat": "Nhúng các nguyên liệu vào nồi lẩu đang sôi, chờ chín rồi vớt ra chấm nước mắm hoặc sa tế.",
            "how_to_eat_en": "Dip ingredients into boiling hotpot, wait until cooked then pick up and dip in fish sauce or satay.",
            "image_url": "https://images.unsplash.com/photo-1555126634-323283e090fa?w=800",
            "ai_label": "lau_thai",
            "view_count": 550
        }
    ]
    
    for food_data in foods:
        existing = db.query(Food).filter(Food.slug == food_data["slug"]).first()
        if not existing:
            food = Food(**food_data)
            db.add(food)
    
    db.commit()
    print(f"✓ Đã tạo {len(foods)} foods")


def seed_all():
    """Chạy tất cả seed functions"""
    print("🌱 Bắt đầu seed database...\n")
    
    db = SessionLocal()
    try:
        create_tables()
        seed_allergies(db)
        seed_ingredients(db)
        seed_users(db)
        seed_foods(db)
        
        print("\n✅ Seed database hoàn tất!")
        print("\n📝 Thông tin đăng nhập:")
        print("  Admin: admin@vietfood.ai / admin123")
        print("  User: user@vietfood.ai / user123")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
