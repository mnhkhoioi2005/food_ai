-- =====================================================
-- VietFood AI - Database Initialization Script
-- PostgreSQL 14+
-- =====================================================

-- Tạo database (chạy riêng trong psql hoặc pgAdmin)
-- CREATE DATABASE vietfood_db;

-- Kết nối vào database vietfood_db trước khi chạy các lệnh dưới

-- =====================================================
-- EXTENSIONS
-- =====================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLES
-- =====================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'user',
    spicy_level INTEGER DEFAULT 2,
    prefer_soup BOOLEAN DEFAULT TRUE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    allergens JSONB DEFAULT '[]',
    favorite_regions JSONB DEFAULT '[]',
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 2. Foods table
CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    slug VARCHAR(255) UNIQUE,
    description_vi TEXT,
    description_en TEXT,
    region VARCHAR(100),
    is_spicy BOOLEAN DEFAULT FALSE,
    spicy_level INTEGER DEFAULT 0,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_soup BOOLEAN DEFAULT FALSE,
    is_popular BOOLEAN DEFAULT FALSE,
    calories INTEGER,
    prep_time INTEGER,
    difficulty VARCHAR(50),
    serving_size VARCHAR(100),
    image_url VARCHAR(500),
    nutrition JSONB,
    average_rating DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 3. Ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Food-Ingredients relationship
CREATE TABLE IF NOT EXISTS food_ingredients (
    id SERIAL PRIMARY KEY,
    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity VARCHAR(100),
    is_main BOOLEAN DEFAULT FALSE,
    UNIQUE(food_id, ingredient_id)
);

-- 5. Allergies table
CREATE TABLE IF NOT EXISTS allergies (
    id SERIAL PRIMARY KEY,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Food-Allergies relationship
CREATE TABLE IF NOT EXISTS food_allergies (
    id SERIAL PRIMARY KEY,
    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
    allergy_id INTEGER REFERENCES allergies(id) ON DELETE CASCADE,
    UNIQUE(food_id, allergy_id)
);

-- 7. Food Images table
CREATE TABLE IF NOT EXISTS food_images (
    id SERIAL PRIMARY KEY,
    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Recognition History table
CREATE TABLE IF NOT EXISTS recognition_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    image_url VARCHAR(500) NOT NULL,
    predicted_food_id INTEGER REFERENCES foods(id) ON DELETE SET NULL,
    predicted_food_name VARCHAR(255),
    confidence VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
    score DECIMAL(5,4),
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Search Logs table
CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    query VARCHAR(500),
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_foods_name_vi ON foods(name_vi);
CREATE INDEX IF NOT EXISTS idx_foods_slug ON foods(slug);
CREATE INDEX IF NOT EXISTS idx_foods_region ON foods(region);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_food_id ON interactions(food_id);
CREATE INDEX IF NOT EXISTS idx_recognition_history_user_id ON recognition_history(user_id);

-- =====================================================
-- SEED DATA - Allergies
-- =====================================================
INSERT INTO allergies (name_vi, name_en, description) VALUES
('Hải sản', 'Seafood', 'Dị ứng với hải sản như tôm, cua, cá'),
('Đậu phộng', 'Peanuts', 'Dị ứng với đậu phộng và các sản phẩm từ đậu phộng'),
('Sữa', 'Dairy', 'Dị ứng với sữa và các sản phẩm từ sữa'),
('Trứng', 'Eggs', 'Dị ứng với trứng'),
('Gluten', 'Gluten', 'Dị ứng với gluten trong lúa mì'),
('Đậu nành', 'Soy', 'Dị ứng với đậu nành'),
('Hạt cây', 'Tree nuts', 'Dị ứng với các loại hạt')
ON CONFLICT DO NOTHING;

-- =====================================================
-- SEED DATA - Ingredients
-- =====================================================
INSERT INTO ingredients (name_vi, name_en, category) VALUES
('Thịt bò', 'Beef', 'Thịt'),
('Thịt heo', 'Pork', 'Thịt'),
('Thịt gà', 'Chicken', 'Thịt'),
('Tôm', 'Shrimp', 'Hải sản'),
('Cá', 'Fish', 'Hải sản'),
('Mực', 'Squid', 'Hải sản'),
('Bánh phở', 'Pho noodles', 'Tinh bột'),
('Bún', 'Rice vermicelli', 'Tinh bột'),
('Mì', 'Noodles', 'Tinh bột'),
('Cơm', 'Rice', 'Tinh bột'),
('Rau muống', 'Water spinach', 'Rau củ'),
('Giá đỗ', 'Bean sprouts', 'Rau củ'),
('Hành lá', 'Green onion', 'Rau củ'),
('Rau thơm', 'Herbs', 'Rau củ'),
('Ớt', 'Chili', 'Gia vị'),
('Tỏi', 'Garlic', 'Gia vị'),
('Nước mắm', 'Fish sauce', 'Gia vị'),
('Đường', 'Sugar', 'Gia vị'),
('Chanh', 'Lime', 'Gia vị'),
('Trứng', 'Egg', 'Khác'),
('Đậu phụ', 'Tofu', 'Khác'),
('Bánh mì', 'Bread', 'Tinh bột'),
('Bơ', 'Butter', 'Khác'),
('Pate', 'Pate', 'Khác'),
('Dưa leo', 'Cucumber', 'Rau củ'),
('Cà rốt', 'Carrot', 'Rau củ'),
('Đồ chua', 'Pickled vegetables', 'Rau củ')
ON CONFLICT DO NOTHING;

-- =====================================================
-- SEED DATA - Foods
-- =====================================================
INSERT INTO foods (name_vi, name_en, slug, description_vi, region, is_spicy, is_vegetarian, is_soup, is_popular, calories, prep_time, difficulty, image_url) VALUES
('Phở bò', 'Beef Pho', 'pho-bo', 'Phở bò là món ăn truyền thống nổi tiếng của Việt Nam với nước dùng trong, thơm ngon từ xương bò ninh nhừ, bánh phở mềm và thịt bò tái hoặc chín.', 'Miền Bắc', FALSE, FALSE, TRUE, TRUE, 450, 30, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Bún chả', 'Bun Cha', 'bun-cha', 'Bún chả Hà Nội với thịt nướng thơm lừng, bún tươi và nước chấm chua ngọt đặc trưng.', 'Miền Bắc', FALSE, FALSE, FALSE, TRUE, 550, 45, 'Trung bình', 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=600'),

('Bánh mì', 'Banh Mi', 'banh-mi', 'Bánh mì Việt Nam với vỏ giòn, nhân đa dạng từ pate, thịt nguội, rau sống đến trứng ốp la.', 'Miền Nam', FALSE, FALSE, FALSE, TRUE, 350, 10, 'Dễ', 'https://images.unsplash.com/photo-1600688640154-9619e002df30?w=600'),

('Cơm tấm', 'Broken Rice', 'com-tam', 'Cơm tấm Sài Gòn với sườn nướng, bì, chả, trứng ốp la và nước mắm pha đặc trưng miền Nam.', 'Miền Nam', FALSE, FALSE, FALSE, TRUE, 650, 25, 'Trung bình', 'https://images.unsplash.com/photo-1569058242567-93de6f36f8eb?w=600'),

('Bún bò Huế', 'Hue Beef Noodle Soup', 'bun-bo-hue', 'Bún bò Huế cay nồng với nước dùng đậm đà, thịt bò, giò heo và mắm ruốc đặc trưng xứ Huế.', 'Miền Trung', TRUE, FALSE, TRUE, TRUE, 520, 60, 'Khó', 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=600'),

('Mì Quảng', 'Quang Noodles', 'mi-quang', 'Mì Quảng với sợi mì vàng, nước dùng ít, tôm thịt và đậu phộng rang giòn.', 'Miền Trung', FALSE, FALSE, FALSE, TRUE, 480, 40, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Hủ tiếu', 'Hu Tieu', 'hu-tieu', 'Hủ tiếu Nam Vang với nước dùng trong, sợi hủ tiếu dai, thịt, tôm và rau sống.', 'Miền Nam', FALSE, FALSE, TRUE, TRUE, 400, 30, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Gỏi cuốn', 'Spring Rolls', 'goi-cuon', 'Gỏi cuốn tươi mát với tôm, thịt, bún, rau sống cuốn trong bánh tráng.', 'Miền Nam', FALSE, FALSE, FALSE, TRUE, 150, 20, 'Dễ', 'https://images.unsplash.com/photo-1553621042-f6e147245754?w=600'),

('Bánh xèo', 'Vietnamese Crepe', 'banh-xeo', 'Bánh xèo giòn rụm với nhân tôm thịt, giá đỗ, ăn kèm rau sống và nước mắm chua ngọt.', 'Miền Nam', FALSE, FALSE, FALSE, TRUE, 450, 35, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Chả giò', 'Fried Spring Rolls', 'cha-gio', 'Chả giò chiên giòn với nhân thịt heo, miến, nấm mèo, cà rốt thơm ngon.', 'Miền Nam', FALSE, FALSE, FALSE, TRUE, 300, 45, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Bò kho', 'Beef Stew', 'bo-kho', 'Bò kho thơm lừng với thịt bò mềm, cà rốt, ăn kèm bánh mì hoặc bún.', 'Miền Nam', TRUE, FALSE, TRUE, FALSE, 480, 90, 'Khó', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Cao lầu', 'Cao Lau', 'cao-lau', 'Cao lầu Hội An với sợi mì đặc biệt, thịt xá xíu, rau sống và bánh tráng giòn.', 'Miền Trung', FALSE, FALSE, FALSE, FALSE, 420, 40, 'Khó', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Bún riêu', 'Crab Noodle Soup', 'bun-rieu', 'Bún riêu cua với nước dùng chua thanh, riêu cua thơm ngon, đậu phụ chiên.', 'Miền Bắc', FALSE, FALSE, TRUE, FALSE, 380, 50, 'Khó', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Bánh cuốn', 'Steamed Rice Rolls', 'banh-cuon', 'Bánh cuốn Thanh Trì mỏng mềm với nhân thịt, mộc nhĩ, ăn kèm chả quế.', 'Miền Bắc', FALSE, FALSE, FALSE, FALSE, 280, 30, 'Khó', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600'),

('Xôi', 'Sticky Rice', 'xoi', 'Xôi với nhiều loại: xôi gấc, xôi đậu xanh, xôi lạc... dẻo thơm.', 'Miền Bắc', FALSE, TRUE, FALSE, FALSE, 350, 40, 'Trung bình', 'https://images.unsplash.com/photo-1555126634-323283e090fa?w=600')
ON CONFLICT (slug) DO NOTHING;

-- =====================================================
-- SEED DATA - Admin User (password: admin123)
-- =====================================================
-- Hash được tạo bởi bcrypt với password: admin123
INSERT INTO users (email, hashed_password, full_name, role) VALUES
('admin@vietfood.ai', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin VietFood', 'admin')
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- DONE
-- =====================================================
SELECT 'Database initialized successfully!' as status;
