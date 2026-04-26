"""
Script để sửa ai_label và thêm món ăn mới khớp với YOLO model
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.food import Food

db = SessionLocal()

print("🔧 Fixing ai_labels to match YOLO model...")

# Fix existing ai_labels to match YOLO model
updates = {
    'pho_bo': 'pho',
    'pho_chay': 'pho', 
    'lau_thai': 'lau'
}

for old, new in updates.items():
    food = db.query(Food).filter(Food.ai_label == old).first()
    if food:
        print(f"  Updating {food.name}: {old} -> {new}")
        food.ai_label = new

db.commit()

print("\n📝 Adding new foods with correct ai_labels...")

# Add new foods with correct ai_labels matching VietFood67
new_foods = [
    {'name': 'Phở', 'name_en': 'Pho', 'slug': 'pho-general', 'ai_label': 'pho', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Món phở truyền thống Việt Nam với nước dùng thơm ngon, bánh phở mềm.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bánh Bao', 'name_en': 'Steamed Bun', 'slug': 'banh-bao', 'ai_label': 'banh_bao', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bánh bao nhân thịt hấp mềm mịn, thơm ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Bèo', 'name_en': 'Water Fern Cake', 'slug': 'banh-beo', 'ai_label': 'banh_beo', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Bánh bèo Huế mềm mịn với tôm chấy, mỡ hành.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Bột Lọc', 'name_en': 'Tapioca Dumpling', 'slug': 'banh-bot-loc', 'ai_label': 'banh_bot_loc', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Bánh bột lọc Huế trong suốt, nhân tôm thịt.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Căn', 'name_en': 'Mini Savory Pancake', 'slug': 'banh-can', 'ai_label': 'banh_can', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Bánh căn Nha Trang giòn thơm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Canh', 'name_en': 'Thick Noodle Soup', 'slug': 'banh-canh', 'ai_label': 'banh_canh', 'region': 'trung', 'food_type': 'mon_nuoc', 'description': 'Bánh canh sợi to với nước dùng đậm đà.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bánh Chưng', 'name_en': 'Square Sticky Rice Cake', 'slug': 'banh-chung', 'ai_label': 'banh_chung', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bánh chưng truyền thống ngày Tết.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Cuốn', 'name_en': 'Steamed Rice Rolls', 'slug': 'banh-cuon', 'ai_label': 'banh_cuon', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bánh cuốn mỏng mềm với nhân thịt băm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Da Lợn', 'name_en': 'Layer Cake', 'slug': 'banh-da-lon', 'ai_label': 'banh_da_lon', 'region': 'nam', 'food_type': 'trang_mieng', 'description': 'Bánh da lợn nhiều lớp màu sắc.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Đúc', 'name_en': 'Plain Rice Flan', 'slug': 'banh-duc', 'ai_label': 'banh_duc', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bánh đúc mềm mịn ăn kèm mắm tôm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Giò', 'name_en': 'Pyramid Rice Dumpling', 'slug': 'banh-gio', 'ai_label': 'banh_gio', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bánh giò nhân thịt mộc nhĩ.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Khọt', 'name_en': 'Mini Savory Cakes', 'slug': 'banh-khot', 'ai_label': 'banh_khot', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bánh khọt giòn với tôm tươi.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Pía', 'name_en': 'Pia Cake', 'slug': 'banh-pia', 'ai_label': 'banh_pia', 'region': 'nam', 'food_type': 'trang_mieng', 'description': 'Bánh pía Sóc Trăng thơm ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Tráng Nướng', 'name_en': 'Grilled Rice Paper', 'slug': 'banh-trang-nuong', 'ai_label': 'banh_trang_nuong', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bánh tráng nướng Đà Lạt giòn rụm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bò Kho', 'name_en': 'Beef Stew', 'slug': 'bo-kho', 'ai_label': 'bo_kho', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Bò kho đậm đà ăn với bánh mì hoặc bún.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bún Đậu Mắm Tôm', 'name_en': 'Noodles with Tofu & Shrimp Paste', 'slug': 'bun-dau-mam-tom', 'ai_label': 'bun_dau_mam_tom', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Bún đậu chấm mắm tôm đặc trưng Hà Nội.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bún Mắm', 'name_en': 'Fermented Fish Noodle Soup', 'slug': 'bun-mam', 'ai_label': 'bun_mam', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Bún mắm miền Tây đậm đà hương vị.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bún Mọc', 'name_en': 'Pork Ball Noodle Soup', 'slug': 'bun-moc', 'ai_label': 'bun_moc', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Bún mọc thanh đạm với mộc nhĩ.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bún Riêu', 'name_en': 'Crab Noodle Soup', 'slug': 'bun-rieu', 'ai_label': 'bun_rieu', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Bún riêu cua chua thanh ngọt.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Bún Thịt Nướng', 'name_en': 'Grilled Pork Noodles', 'slug': 'bun-thit-nuong', 'ai_label': 'bun_thit_nuong', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bún thịt nướng thơm lừng.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bún Chả Cá', 'name_en': 'Fish Cake Noodles', 'slug': 'bun-cha-ca', 'ai_label': 'bun_cha_ca', 'region': 'trung', 'food_type': 'mon_nuoc', 'description': 'Bún chả cá Đà Nẵng nổi tiếng.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Cá Kho Tộ', 'name_en': 'Caramelized Fish', 'slug': 'ca-kho-to', 'ai_label': 'ca_kho_to', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Cá kho tộ đậm đà trong nồi đất.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Canh Chua', 'name_en': 'Sour Soup', 'slug': 'canh-chua', 'ai_label': 'canh_chua', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Canh chua Nam Bộ chua ngọt thanh mát.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Cao Lầu', 'name_en': 'Cao Lau', 'slug': 'cao-lau', 'ai_label': 'cao_lau', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Cao lầu Hội An đặc sản.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Cháo Lòng', 'name_en': 'Organ Congee', 'slug': 'chao-long', 'ai_label': 'chao_long', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Cháo lòng nóng hổi bổ dưỡng.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Chè', 'name_en': 'Sweet Soup', 'slug': 'che', 'ai_label': 'che', 'region': 'nam', 'food_type': 'trang_mieng', 'description': 'Chè ngọt mát giải nhiệt.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Cơm Cháy', 'name_en': 'Crispy Rice', 'slug': 'com-chay', 'ai_label': 'com_chay', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Cơm cháy Ninh Bình giòn rụm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Cơm Gà', 'name_en': 'Chicken Rice', 'slug': 'com-ga', 'ai_label': 'com_ga', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Cơm gà Hội An thơm ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Gà Nướng', 'name_en': 'Grilled Chicken', 'slug': 'ga-nuong', 'ai_label': 'ga_nuong', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Gà nướng thơm lừng hấp dẫn.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Gỏi Gà', 'name_en': 'Chicken Salad', 'slug': 'goi-ga', 'ai_label': 'goi_ga', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Gỏi gà bắp cải tươi mát.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Hủ Tiếu', 'name_en': 'Hu Tieu', 'slug': 'hu-tieu', 'ai_label': 'hu_tieu', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Hủ tiếu Nam Vang đậm đà.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Lẩu', 'name_en': 'Hot Pot', 'slug': 'lau', 'ai_label': 'lau', 'region': 'nam', 'food_type': 'mon_nuoc', 'description': 'Lẩu nóng hổi ăn cùng bạn bè.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Mì Quảng', 'name_en': 'Quang Noodles', 'slug': 'mi-quang', 'ai_label': 'mi_quang', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Mì Quảng đặc sản miền Trung.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Mì Xào', 'name_en': 'Stir-fried Noodles', 'slug': 'mi-xao', 'ai_label': 'mi_xao', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Mì xào giòn ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Nem Chua', 'name_en': 'Fermented Pork Roll', 'slug': 'nem-chua', 'ai_label': 'nem_chua', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Nem chua Thanh Hóa chua cay.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Nem Nướng', 'name_en': 'Grilled Pork Sausage', 'slug': 'nem-nuong', 'ai_label': 'nem_nuong', 'region': 'trung', 'food_type': 'mon_kho', 'description': 'Nem nướng Nha Trang nổi tiếng.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Ốc', 'name_en': 'Snails', 'slug': 'oc', 'ai_label': 'oc', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Ốc hấp, ốc xào đa dạng món.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Rau Muống Xào Tỏi', 'name_en': 'Stir-fried Water Spinach', 'slug': 'rau-muong-xao-toi', 'ai_label': 'rau_muong_xao_toi', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Rau muống xào tỏi giòn ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Thịt Kho', 'name_en': 'Braised Pork', 'slug': 'thit-kho', 'ai_label': 'thit_kho', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Thịt kho tàu đậm đà ngày Tết.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Thịt Nướng', 'name_en': 'Grilled Meat', 'slug': 'thit-nuong', 'ai_label': 'thit_nuong', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Thịt nướng thơm lừng hấp dẫn.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Xôi', 'name_en': 'Sticky Rice', 'slug': 'xoi', 'ai_label': 'xoi', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Xôi nóng dẻo thơm đủ loại.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Xôi Xéo', 'name_en': 'Yellow Sticky Rice', 'slug': 'xoi-xeo', 'ai_label': 'xoi_xeo', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Xôi xéo Hà Nội vàng ươm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Xôi Gấc', 'name_en': 'Red Sticky Rice', 'slug': 'xoi-gac', 'ai_label': 'xoi_gac', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Xôi gấc đỏ tươi may mắn.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Flan', 'name_en': 'Flan', 'slug': 'banh-flan', 'ai_label': 'banh_flan', 'region': 'nam', 'food_type': 'trang_mieng', 'description': 'Bánh flan mềm mịn béo ngậy.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Sữa Chua', 'name_en': 'Yogurt', 'slug': 'sua-chua', 'ai_label': 'sua_chua', 'region': 'bac', 'food_type': 'trang_mieng', 'description': 'Sữa chua mát lạnh bổ dưỡng.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Sinh Tố', 'name_en': 'Smoothie', 'slug': 'sinh-to', 'ai_label': 'sinh_to', 'region': 'nam', 'food_type': 'do_uong', 'description': 'Sinh tố trái cây tươi mát.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Nước Mía', 'name_en': 'Sugarcane Juice', 'slug': 'nuoc-mia', 'ai_label': 'nuoc_mia', 'region': 'nam', 'food_type': 'do_uong', 'description': 'Nước mía tươi mát ngọt thanh.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Trà Sữa', 'name_en': 'Milk Tea', 'slug': 'tra-sua', 'ai_label': 'tra_sua', 'region': 'nam', 'food_type': 'do_uong', 'description': 'Trà sữa trân châu ngọt ngào.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Cà Phê', 'name_en': 'Vietnamese Coffee', 'slug': 'ca-phe', 'ai_label': 'ca_phe', 'region': 'nam', 'food_type': 'do_uong', 'description': 'Cà phê Việt Nam đậm đà.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Nước Dừa', 'name_en': 'Coconut Water', 'slug': 'nuoc-dua', 'ai_label': 'nuoc_dua', 'region': 'nam', 'food_type': 'do_uong', 'description': 'Nước dừa tươi mát lành.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Kem', 'name_en': 'Ice Cream', 'slug': 'kem', 'ai_label': 'kem', 'region': 'nam', 'food_type': 'trang_mieng', 'description': 'Kem mát lạnh đủ vị.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bắp Xào', 'name_en': 'Stir-fried Corn', 'slug': 'bap-xao', 'ai_label': 'bap_xao', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bắp xào bơ thơm ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Khoai Lang Nướng', 'name_en': 'Grilled Sweet Potato', 'slug': 'khoai-lang-nuong', 'ai_label': 'khoai_lang_nuong', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Khoai lang nướng ngọt bùi.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Trứng Vịt Lộn', 'name_en': 'Balut', 'slug': 'trung-vit-lon', 'ai_label': 'trung_vit_lon', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Trứng vịt lộn bổ dưỡng.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Cháo', 'name_en': 'Congee', 'slug': 'chao', 'ai_label': 'chao', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Cháo nóng dễ tiêu hóa.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Súp', 'name_en': 'Soup', 'slug': 'sup', 'ai_label': 'sup', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Súp nóng bổ dưỡng.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Mì Tôm', 'name_en': 'Instant Noodles', 'slug': 'mi-tom', 'ai_label': 'mi_tom', 'region': 'bac', 'food_type': 'mon_nuoc', 'description': 'Mì tôm ăn liền tiện lợi.', 'image_url': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800'},
    {'name': 'Cơm Rang', 'name_en': 'Fried Rice', 'slug': 'com-rang', 'ai_label': 'com_rang', 'region': 'bac', 'food_type': 'mon_kho', 'description': 'Cơm rang dương châu thơm ngon.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bánh Tráng Trộn', 'name_en': 'Mixed Rice Paper', 'slug': 'banh-trang-tron', 'ai_label': 'banh_trang_tron', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bánh tráng trộn Sài Gòn.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
    {'name': 'Bột Chiên', 'name_en': 'Fried Rice Flour Cake', 'slug': 'bot-chien', 'ai_label': 'bot_chien', 'region': 'nam', 'food_type': 'mon_kho', 'description': 'Bột chiên Sài Gòn giòn thơm.', 'image_url': 'https://images.unsplash.com/photo-1529042410-8d99f9e9c077?w=800'},
]

added = 0
for food_data in new_foods:
    food_data['is_active'] = True
    existing = db.query(Food).filter(Food.ai_label == food_data['ai_label']).first()
    if not existing:
        food = Food(**food_data)
        db.add(food)
        print(f"  Added: {food_data['name']} ({food_data['ai_label']})")
        added += 1
    else:
        print(f"  Exists: {food_data['name']}")

db.commit()
db.close()

print(f"\n✅ Done! Added {added} new foods.")
print("🔄 Restart Backend to apply changes.")
