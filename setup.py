"""
运行方式: python setup.py
功能: 创建数据库 + 初始化分类 + 创建默认管理员
"""
import pymysql
from werkzeug.security import generate_password_hash

# ── 配置 ──
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',       # ← 改成你的MySQL密码
    'charset': 'utf8mb4',
}
DB_NAME = 'chenghai_b2b'

# ── 1. 创建数据库 ──
print("[1/3] Creating database...")
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cur.execute(f"USE `{DB_NAME}`")
print(f"  ✓ Database `{DB_NAME}` ready")

# ── 2. 建表 ──
print("[2/3] Creating tables...")
tables = [
    """CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        role ENUM('admin','factory') NOT NULL DEFAULT 'factory',
        is_active TINYINT(1) DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    """CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        name_en VARCHAR(100),
        parent_id INT DEFAULT NULL,
        icon VARCHAR(50),
        sort_order INT DEFAULT 0,
        is_active TINYINT(1) DEFAULT 1,
        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    """CREATE TABLE IF NOT EXISTS factories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        company_name VARCHAR(200) NOT NULL,
        contact_person VARCHAR(100),
        phone VARCHAR(50),
        email VARCHAR(120),
        address VARCHAR(300),
        description TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    """CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        factory_id INT NOT NULL,
        category_id INT DEFAULT NULL,
        title VARCHAR(300) NOT NULL,
        description TEXT,
        images TEXT,
        video_url VARCHAR(500),
        moq INT DEFAULT 1,
        lead_time VARCHAR(100),
        base_price DECIMAL(10,2),
        price_unit VARCHAR(20) DEFAULT 'USD',
        packaging_info TEXT,
        customization TEXT,
        specs TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        is_featured TINYINT(1) DEFAULT 0,
        review_note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (factory_id) REFERENCES factories(id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    """CREATE TABLE IF NOT EXISTS inquiries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT DEFAULT NULL,
        company_name VARCHAR(200),
        contact_name VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(50),
        quantity INT,
        message TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'new',
        admin_reply TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]

for sql in tables:
    cur.execute(sql)
print("  ✓ All tables created")

# ── 3. 初始化数据 ──
print("[3/3] Seeding initial data...")

# 分类
categories = [
    ('Toys', 'Toys', None, '🧸', 1),
    ('  Educational Toys', 'Educational Toys', 1, None, 1),
    ('  Remote Control Toys', 'Remote Control Toys', 1, None, 2),
    ('  Dolls', 'Dolls', 1, None, 3),
    ('  Building Blocks', 'Building Blocks', 1, None, 4),
    ('  Pretend Play', 'Pretend Play', 1, None, 5),
    ('Drones', 'Drones', None, '🚁', 2),
    ('  Mini Drones', 'Mini Drones', 7, None, 1),
    ('  Camera Drones', 'Camera Drones', 7, None, 2),
    ('  RC Aircraft', 'RC Aircraft', 7, None, 3),
    ('Home Appliances', 'Home Appliances', None, '🏠', 3),
    ('  Beauty Tools', 'Beauty Tools', 11, None, 1),
    ('  Home Electronics', 'Home Electronics', 11, None, 2),
    ('  Digital Accessories', 'Digital Accessories', 11, None, 3),
]

# 先插入父级
parent_map = {}
for name, name_en, parent_idx, icon, sort in categories:
    if parent_idx is None:
        cur.execute(
            "INSERT IGNORE INTO categories (name, name_en, parent_id, icon, sort_order) VALUES (%s,%s,%s,%s,%s)",
            (name, name_en, None, icon, sort)
        )
        cur.execute("SELECT id FROM categories WHERE name=%s", (name,))
        parent_map[name] = cur.fetchone()[0]

# 再插入子级
for name, name_en, parent_idx, icon, sort in categories:
    if parent_idx is not None:
        parent_name = categories[parent_idx - 1][0]
        pid = parent_map.get(parent_name)
        cur.execute(
            "INSERT IGNORE INTO categories (name, name_en, parent_id, icon, sort_order) VALUES (%s,%s,%s,%s,%s)",
            (name.strip(), name_en, pid, icon, sort)
        )

# 默认管理员
admin_pw = generate_password_hash('admin123')
cur.execute(
    "INSERT IGNORE INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    ('admin', admin_pw, 'admin')
)

conn.commit()
cur.close()
conn.close()

print("  ✓ Categories seeded")
print("  ✓ Admin account created (admin / admin123)")
print("\n✅ Setup complete! Run the backend with: cd backend && python app.py")
