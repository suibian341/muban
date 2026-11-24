-- 更新 users 表的 role 列以支持 dev 角色
-- 在 MySQL 客户端中运行此脚本

USE chenghai_b2b;

ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'factory', 'buyer', 'dev') NOT NULL DEFAULT 'factory';

-- 验证修改
DESCRIBE users;
