import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# 1. Product 表 (对应 migrations 0005 & 0006)
# image 字段为 NOT NULL，使用占位路径
cur.execute("""
CREATE TABLE IF NOT EXISTS app_monitor_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    price INTEGER NOT NULL,
    image VARCHAR(100) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    stock INTEGER NOT NULL DEFAULT 999
)
""")

# 2. Article 表 (对应 migrations 0005)
cur.execute("""
CREATE TABLE IF NOT EXISTS app_monitor_article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(20) NOT NULL DEFAULT 'knowledge',
    summary TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    cover_image VARCHAR(100) NULL,
    views INTEGER NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    author_id INTEGER NULL,
    FOREIGN KEY (author_id) REFERENCES auth_user(id) ON DELETE SET NULL
)
""")

# 3. ExchangeRecord 表 (对应 migrations 0005)
cur.execute("""
CREATE TABLE IF NOT EXISTS app_monitor_exchangerecord (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    points_spent INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES app_monitor_product(id) ON DELETE CASCADE
)
""")

conn.commit()
conn.close()
print("Missing tables created successfully.")
