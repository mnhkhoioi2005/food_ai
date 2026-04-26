-- =====================================================
-- Các lệnh PostgreSQL cơ bản
-- Chạy trong psql hoặc pgAdmin Query Tool
-- =====================================================

-- =====================================================
-- 1. TẠO DATABASE
-- =====================================================
CREATE DATABASE vietfood_db;

-- Hoặc với encoding UTF-8
CREATE DATABASE vietfood_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- =====================================================
-- 2. KẾT NỐI VÀO DATABASE
-- =====================================================
\c vietfood_db

-- =====================================================
-- 3. XEM DANH SÁCH TABLES
-- =====================================================
\dt

-- Hoặc SQL thuần:
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- =====================================================
-- 4. XEM CẤU TRÚC TABLE
-- =====================================================
\d users
\d foods

-- Hoặc SQL thuần:
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';

-- =====================================================
-- 5. ĐẾM RECORDS
-- =====================================================
SELECT 
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM foods) as foods_count,
    (SELECT COUNT(*) FROM ingredients) as ingredients_count,
    (SELECT COUNT(*) FROM allergies) as allergies_count;

-- =====================================================
-- 6. XEM DỮ LIỆU
-- =====================================================
-- Xem tất cả users
SELECT id, email, full_name, role, is_active FROM users;

-- Xem tất cả foods
SELECT id, name, name_en, region, food_type, spicy_level, is_vegetarian, calories FROM foods;

-- Xem tất cả ingredients
SELECT * FROM ingredients ORDER BY category;

-- Xem tất cả allergies
SELECT * FROM allergies;

-- =====================================================
-- 7. TÌM KIẾM
-- =====================================================
-- Tìm món ăn theo tên
SELECT * FROM foods WHERE name ILIKE '%phở%';

-- Tìm món ăn theo vùng miền
SELECT * FROM foods WHERE region = 'Miền Bắc';

-- Tìm món ăn cay (spicy_level >= 1)
SELECT * FROM foods WHERE spicy_level >= 1;

-- Tìm món chay
SELECT * FROM foods WHERE is_vegetarian = TRUE;

-- =====================================================
-- 8. THÊM DỮ LIỆU
-- =====================================================
-- Thêm user mới
INSERT INTO users (email, hashed_password, full_name, role)
VALUES ('test@example.com', '$2b$12$xxx', 'Test User', 'user');

-- Thêm món ăn mới
INSERT INTO foods (name, name_en, slug, description, region, food_type, spicy_level, is_vegetarian, calories)
VALUES ('Phở Gà', 'Chicken Pho', 'pho-ga', 'Phở với thịt gà', 'bac', 'mon_nuoc', 0, FALSE, 400);

-- =====================================================
-- 9. CẬP NHẬT DỮ LIỆU
-- =====================================================
-- Cập nhật user
UPDATE users SET full_name = 'New Name' WHERE id = 1;

-- Cập nhật món ăn
UPDATE foods SET calories = 500 WHERE slug = 'pho-bo';

-- Cập nhật ai_label
UPDATE foods SET ai_label = 'pho' WHERE slug IN ('pho-bo', 'pho-ga');

-- =====================================================
-- 10. XÓA DỮ LIỆU
-- =====================================================
-- Xóa user (cẩn thận!)
DELETE FROM users WHERE id = 5;

-- Xóa món ăn
DELETE FROM foods WHERE id = 10;

-- =====================================================
-- 11. XÓA VÀ TẠO LẠI DATABASE
-- =====================================================
-- Ngắt kết nối tất cả sessions
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'vietfood_db'
AND pid <> pg_backend_pid();

-- Xóa database
DROP DATABASE IF EXISTS vietfood_db;

-- Tạo lại database
CREATE DATABASE vietfood_db;

-- =====================================================
-- 12. BACKUP & RESTORE
-- =====================================================
-- Backup (chạy trong terminal, không phải psql)
-- pg_dump -U postgres -d vietfood_db > backup.sql

-- Restore (chạy trong terminal)
-- psql -U postgres -d vietfood_db < backup.sql

-- =====================================================
-- 13. THỐNG KÊ
-- =====================================================
-- Thống kê món ăn theo vùng miền
SELECT region, COUNT(*) as total
FROM foods
GROUP BY region
ORDER BY total DESC;

-- Thống kê interactions
SELECT interaction_type, COUNT(*) as total
FROM interactions
GROUP BY interaction_type;

-- Top 10 món được xem nhiều nhất
SELECT name, name_en, region, food_type, calories, view_count
FROM foods
ORDER BY view_count DESC
LIMIT 10;
