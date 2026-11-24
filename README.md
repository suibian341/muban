# B2B/B2C 可复用项目模板

## 项目简介

基于 Flask + Vue3 的电商平台模板，支持两种运营模式：
- **B2C独立站模式**：管理员直接管理商品，前台显示价格
- **B2B模式**：工厂入驻审核，前台隐藏价格，通过询盘获取报价

## 快速开始

### 1. 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 2. 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 编辑 config.py 设置数据库连接信息

# 初始化数据库
python migrate_db.py

# 创建开发者账号
python seed_dev_user.py

# 启动后端服务
python app.py
```

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

### 4. 开发者登录

- URL: http://localhost:5173/dev
- 账号: suibian341
- 密码: 135260352

## 模式切换

### 方式1: 开发者后台（推荐）

1. 登录开发者后台 `/dev`
2. 点击"模式切换"开关
3. 选择 B2C 或 B2B 模式
4. 保存后前台页面自动适配

### 方式2: 数据库直接修改

```sql
-- 切换到 B2C 模式
UPDATE site_settings SET value='b2c' WHERE key='site_mode';

-- 切换到 B2B 模式
UPDATE site_settings SET value='b2b' WHERE key='site_mode';
```

## 功能差异

| 功能 | B2C模式 | B2B模式 |
|------|---------|---------|
| 工厂入驻 | ❌ 隐藏 | ✅ 显示 |
| 工厂审核 | ❌ 不需要 | ✅ 需要 |
| 商品审核 | ❌ 不需要 | ✅ 需要 |
| 前台显示价格 | ✅ 显示 | ❌ 隐藏 |
| 询盘系统 | ✅ 可选 | ✅ 必需 |
| 工厂后台 | ❌ 不可用 | ✅ 可用 |

## 开发者后台功能

### 1. 数据统计
- 查看所有用户、工厂、商品、询盘数量
- 按状态分类统计
- 实时数据更新

### 2. 模式切换
- 一键切换 B2C/B2B 模式
- 实时生效，无需重启
- 前台自动适配

### 3. 品牌设置
- 上传 Logo（浅色/深色/图标）
- 实时预览
- 支持多种图片格式

### 4. 页脚编辑
- 编辑公司信息
- 管理页脚链接
- 自定义版权文字
- JSON 配置支持

### 5. 数据查看
- 查看所有后台的数据
- 使用所有后台功能
- 跨角色访问权限

## 角色权限

| 角色 | 权限说明 |
|------|---------|
| dev | 开发者，可访问所有后台，配置系统设置 |
| admin | 管理员，审核工厂和商品，管理询盘 |
| factory | 工厂，上传商品，查看询盘 |
| buyer | 买家，提交询盘，查看订单 |

## 自定义配置

所有配置存储在 `site_settings` 表中，可通过开发者后台或直接修改数据库。

### 配置项列表

| 配置键 | 说明 | 示例值 |
|--------|------|--------|
| site_mode | 站点模式 | 'b2c' 或 'b2b' |
| logo_light | Logo URL（浅色背景） | '/uploads/logo-light.png' |
| logo_dark | Logo URL（深色背景） | '/uploads/logo-dark.png' |
| logo_icon | 图标 URL | '/uploads/icon.png' |
| footer_company_name | 公司名称 | 'Your Company' |
| footer_company_info | 公司信息 | 'Company description' |
| footer_links | 页脚链接（JSON） | '[{"label":"About","url":"/about"}]' |
| footer_copyright | 版权文字 | '© 2024 Your Company' |

## 部署到生产环境

### 后端部署

```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 或使用 uWSGI
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4
```

### 前端部署

```bash
# 构建生产版本
npm run build

# 将 dist 目录部署到 Nginx/Apache
# Nginx 配置示例：
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
    }
}
```

### 环境变量配置

**后端 (.env)**
```
DATABASE_URL=mysql://user:password@localhost/dbname
JWT_SECRET_KEY=your-secret-key
UPLOAD_FOLDER=/path/to/uploads
```

**前端 (.env.production)**
```
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_WHATSAPP=8619876475649
VITE_WECHAT_QR=/wechat-qr.jpg
```

## 技术栈

### 后端
- Flask 2.x - Web 框架
- SQLAlchemy - ORM
- MySQL - 数据库
- Flask-JWT-Extended - JWT 认证
- Flask-CORS - 跨域支持

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Element Plus - UI 组件库
- Vue Router - 路由管理
- Vue I18n - 国际化（支持中英文）
- Axios - HTTP 客户端

## 目录结构

```
muban/
├── backend/
│   ├── app.py                 # 应用入口
│   ├── models.py              # 数据模型
│   ├── config.py              # 配置文件
│   ├── migrate_db.py          # 数据库迁移
│   ├── seed_dev_user.py       # 开发者账号种子
│   ├── routes/
│   │   ├── auth.py            # 认证路由
│   │   ├── products.py        # 商品路由
│   │   ├── factories.py       # 工厂路由
│   │   ├── admin.py           # 管理员路由
│   │   ├── dev.py             # 开发者路由
│   │   └── public.py          # 公开路由
│   └── requirements.txt       # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── dev/           # 开发者后台
│   │   │   ├── admin/         # 管理员后台
│   │   │   ├── factory/       # 工厂后台
│   │   │   └── buyer/         # 买家后台
│   │   ├── components/        # 公共组件
│   │   ├── composables/       # 组合式函数
│   │   ├── router/            # 路由配置
│   │   └── api.js             # API 客户端
│   ├── package.json           # Node 依赖
│   └── vite.config.js         # Vite 配置
└── README.md                  # 本文件
```

## 常见问题

### Q: 如何添加新的配置项？

A: 在 `site_settings` 表中插入新记录，然后在开发者后台或前端代码中读取。

```sql
INSERT INTO site_settings (key, value) VALUES ('new_config', 'value');
```

### Q: 如何重置开发者密码？

A: 运行 `seed_dev_user.py` 脚本会重置密码为默认值。

### Q: B2C 模式下工厂如何上传商品？

A: B2C 模式下工厂功能被禁用，商品由管理员直接上传。

### Q: 如何自定义 Logo？

A: 登录开发者后台 → 品牌设置 → 上传 Logo 文件。

### Q: 如何备份数据？

A: 使用 mysqldump 备份数据库：
```bash
mysqldump -u user -p dbname > backup.sql
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持 B2C/B2B 双模式
- 开发者后台完整功能
- 多语言支持（中英文）

## 许可证

MIT License

## 技术支持

如有问题，请联系：
- Email: dev@example.com
- GitHub: https://github.com/yourusername/muban
