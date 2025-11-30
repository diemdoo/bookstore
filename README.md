# 📚 Bookstore - Hệ Thống Quản Lý Bán Sách Online

> **Đồ án Tốt nghiệp** - Website thương mại điện tử bán sách với đầy đủ tính năng quản lý

## 🌟 Giới Thiệu

Bookstore là một hệ thống thương mại điện tử hoàn chỉnh được xây dựng với công nghệ hiện đại:
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Flask (Python) + 3-Layer Architecture
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Deployment**: Docker & Docker Compose

## ✨ Tính Năng Chính

### 👤 Dành cho Khách hàng
- Xem và tìm kiếm sách
- Giỏ hàng và đặt hàng (COD)
- Quản lý đơn hàng và profile
- Giao diện responsive, thân thiện

### 👑 Dành cho Admin
- Dashboard thống kê doanh thu
- Quản lý sách, khách hàng, nhân viên
- Quản lý đơn hàng và cập nhật trạng thái
- Quản lý banner quảng cáo
- Báo cáo sách bán chạy

## 🚀 Quick Start

### Yêu Cầu
- Docker & Docker Compose
- 4GB RAM, 10GB disk space
- Port 5173, 5000, 5432, 5050 available

### Chạy Dự Án (Development)

```bash
# 1. Clone repository
git clone [repository-url]
cd bookstore

# 2. Start tất cả services
docker-compose up -d

# 3. Truy cập
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000
# pgAdmin: http://localhost:5050
```

### 🚢 Production Deployment

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 3. Truy cập
# Frontend: http://localhost (port 80)
# Backend API: http://localhost/api
# pgAdmin: http://localhost:5050

# 4. Verify
curl http://localhost/health  # Should return "healthy"
```

**Production Features:**
- ✅ Nginx serving optimized static build
- ✅ Gunicorn WSGI server with auto-scaled workers
- ✅ Gzip compression & asset caching
- ✅ Environment variable support (`.env.prod`)
- ✅ Restart policies for reliability

See [docs/09-DEPLOYMENT.md](./docs/09-DEPLOYMENT.md) for complete production guide.

### Tài Khoản Mặc Định

| Loại | Username | Password | Mã |
|------|----------|----------|-----|
| **Admin** | `admin` | `admin123` | - |
| **Customer 1** | `user1` | `pass123` | KH001 |
| **Customer 2** | `user2` | `pass123` | KH002 |
| **Staff 1** | `staff1` | `pass123` | NV001 |
| **Staff 2** | `staff2` | `pass123` | NV002 |

## 📖 Tài Liệu Đầy Đủ

**Tất cả tài liệu chi tiết nằm trong thư mục [`docs/`](./docs/)**

### 📋 Mục Lục Tài Liệu

| # | Tài Liệu | Nội Dung |
|---|----------|----------|
| 00 | [README](./docs/00-README.md) | Mục lục tổng hợp |
| 01 | [Giới Thiệu](./docs/01-INTRODUCTION.md) | Tổng quan dự án, mục tiêu, công nghệ |
| 02 | [Kiến Trúc Hệ Thống](./docs/02-SYSTEM_ARCHITECTURE.md) | 3-Layer Architecture, Docker, Flow |
| 03 | [Thiết Kế Database](./docs/03-DATABASE_DESIGN.md) | ERD, Schema, Relationships |
| 04 | [API Documentation](./docs/04-API_DOCUMENTATION.md) | REST API endpoints (TBD) |
| 05 | [Kiến Trúc Backend](./docs/05-BACKEND_ARCHITECTURE.md) | Services, DAOs, DTOs, Docstrings |
| 06 | [Kiến Trúc Frontend](./docs/06-FRONTEND_ARCHITECTURE.md) | Components, Pages, Contexts (TBD) |
| 07 | [Authentication Flow](./docs/07-AUTHENTICATION_FLOW.md) | Luồng đăng nhập/đăng ký (TBD) |
| 08 | [Order Flow](./docs/08-ORDER_FLOW.md) | Luồng đặt hàng (TBD) |
| 09 | [Deployment](./docs/09-DEPLOYMENT.md) | Hướng dẫn triển khai Docker |
| 10 | [User Guide](./docs/10-USER_GUIDE.md) | Hướng dẫn sử dụng |
| 11 | [Testing](./docs/11-TESTING.md) | Test cases, Strategy |
| 12 | [Changelog](./docs/12-CHANGELOG.md) | Lịch sử phát triển |

### 📊 Diagrams

Tất cả diagrams (Mermaid format) trong [`docs/diagrams/`](./docs/diagrams/):
- System Architecture
- Database ERD
- Authentication Flow
- Order Flow
- Cart Flow
- Admin Flow
- Deployment Diagram

## 🛠 Công Nghệ

### Frontend
- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Tailwind CSS** - Styling
- **Vite** - Build Tool & HMR
- **Node.js 22** - Runtime Environment
- **React Router** - Routing
- **Axios** - HTTP Client
- **Nginx** - Web Server (Production)

### Backend
- **Flask 3** - Web Framework
- **Python 3.12** - Programming Language
- **SQLAlchemy** - ORM
- **PostgreSQL 15** - Database
- **bcrypt** - Password Hashing
- **Flask-CORS** - Cross-Origin Support
- **Gunicorn** - WSGI Server (Production)

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **pgAdmin 4** - Database Management
- **Cloudflare R2** - Object Storage

## 📁 Cấu Trúc Dự Án

```
bookstore/
├── backend/                # Flask Backend
│   ├── app.py             # Main app
│   ├── models.py          # ORM models
│   ├── routes/            # API endpoints
│   ├── business/          # Business logic
│   ├── data/              # DAOs
│   └── utils/             # Helpers
│
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # State management
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── public/
│
├── docs/                  # 📚 Documentation
│   ├── 00-README.md      # Mục lục
│   ├── 01-INTRODUCTION.md # Giới thiệu
│   ├── ...                # (13 files total)
│   └── diagrams/          # Mermaid diagrams (7 files)
│
├── docker-compose.yml     # Docker services config
└── README.md             # File này
```

## 🔧 Commands Thường Dùng

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose stop

# Rebuild
docker-compose up -d --build

# Reset database (remove all data)
docker-compose down -v
docker-compose up -d
```

## 🐛 Troubleshooting

### Frontend không load
```bash
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose up -d --build frontend
# Then hard refresh browser (Ctrl+Shift+R)
```

### Database connection issues
```bash
docker-compose logs db
docker-compose restart db
```

### Chi tiết troubleshooting: [docs/09-DEPLOYMENT.md](./docs/09-DEPLOYMENT.md)

## 📞 Liên Hệ & Hỗ Trợ

- **Tác giả**: [Tên sinh viên]
- **Email**: [email]
- **GitHub**: [repository-url]
- **Giảng viên hướng dẫn**: [Tên giảng viên]

## 📝 License

MIT License - Free to use for educational purposes

---

**🎓 Dự án Đồ án Tốt nghiệp**  
**📅 Năm học**: 2024  
**🏫 Trường**: [Tên trường]

**⭐ Nếu project hữu ích, hãy cho một star!**
