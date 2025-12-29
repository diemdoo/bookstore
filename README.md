# Bookstore - Website bán sách trực tuyến tích hợp chatbot hỗ trợ khách hàng

## Giới Thiệu

Bookstore là một hệ thống thương mại điện tử hoàn chỉnh được xây dựng với công nghệ hiện đại:
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Flask (Python)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Deployment**: Docker & Docker Compose
- **Cloud Storage**: R2 & Bucket

## Tính Năng Chính

### Dành cho Khách hàng
- Xem và tìm kiếm sách
- Giỏ hàng và đặt hàng (COD)
- Quản lý đơn hàng và profile
- Giao diện responsive, thân thiện

### Dành cho Admin
- Dashboard thống kê doanh thu
- Quản lý sách, khách hàng, nhân viên
- Quản lý đơn hàng và cập nhật trạng thái
- Quản lý banner quảng cáo
- Báo cáo sách bán chạy

### Chạy Dự Án (Development)

```bash
# 1. Clone repository
git clone [repository-url]
cd bookstore

# 2. Start tất cả services
docker-compose up -d


### Production Deployment

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify
curl http://localhost/health  # Should return "healthy"
```


## Commands Thường Dùng

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

## Troubleshooting

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

