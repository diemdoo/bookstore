# 01 - Giới Thiệu Dự Án

## 📖 Tổng Quan

Bookstore là một hệ thống thương mại điện tử hoàn chỉnh được thiết kế để quản lý và bán sách trực tuyến. Dự án được phát triển như một đồ án tốt nghiệp, thể hiện việc ứng dụng các kiến thức về lập trình web, thiết kế hệ thống, và quản lý dự án phần mềm.

## 🎯 Mục Tiêu Dự Án

### Mục Tiêu Chính

1. **Xây dựng hệ thống E-commerce hoàn chỉnh** cho việc bán sách trực tuyến
2. **Áp dụng kiến trúc phần mềm đơn giản và dễ hiểu** (Simple Architecture: Routes → Models, REST API)
3. **Sử dụng công nghệ mới nhất** (React, TypeScript, Flask, Docker)
4. **Đảm bảo trải nghiệm người dùng tốt** (Responsive, Intuitive UI)
5. **Quản lý dữ liệu hiệu quả** (PostgreSQL, Data validation)

### Mục Tiêu Phụ

- Học và áp dụng Docker containerization
- Thực hành Git workflow và version control
- Viết documentation chuyên nghiệp
- Implement authentication và authorization
- Xây dựng admin dashboard đầy đủ

## 🌟 Tính Năng Chính

### Đối Với Guest (Khách truy cập)

- ✅ Xem danh sách sách với pagination
- ✅ Tìm kiếm sách theo tên, tác giả, thể loại
- ✅ Xem chi tiết sách (mô tả, giá, tác giả, NXB)
- ✅ Xem banner quảng cáo
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập vào hệ thống

### Đối Với Customer (Khách hàng đã đăng nhập)

- ✅ Tất cả tính năng của Guest
- ✅ Thêm sách vào giỏ hàng
- ✅ Cập nhật số lượng sách trong giỏ
- ✅ Xóa sách khỏi giỏ hàng
- ✅ Đặt hàng với phương thức COD
- ✅ Xem lịch sử đơn hàng
- ✅ Xem và cập nhật thông tin cá nhân
- ✅ Quản lý profile (họ tên, email)

### Đối Với Admin (Quản trị viên)

- ✅ Đăng nhập vào admin panel riêng biệt
- ✅ **Quản lý Sách**: CRUD operations cho sách
- ✅ **Quản lý Banner**: Tạo/sửa/xóa banner quảng cáo
- ✅ **Quản lý Khách hàng**: Xem danh sách, khóa/mở tài khoản
- ✅ **Quản lý Quản trị viên**: Quản lý admin accounts
- ✅ **Quản lý Đơn hàng**: Xem và cập nhật trạng thái đơn
- ✅ **Thống kê**: Dashboard với charts và top selling books
- ✅ Xem thống kê doanh thu, số đơn hàng
- ✅ Xem sách bán chạy nhất

## 🛠 Công Nghệ Sử Dụng

### Frontend

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| **React** | 18.x | UI Library |
| **TypeScript** | 5.x | Type Safety |
| **Tailwind CSS** | 3.x | Styling Framework |
| **Vite** | 5.x | Build Tool |
| **React Router** | 6.x | Client-side Routing |
| **Axios** | 1.x | HTTP Client |
| **Lucide React** | Latest | Icon Library |

**Lý do chọn:**
- React: Popular, component-based, large ecosystem
- TypeScript: Type safety, better IDE support, fewer runtime errors
- Tailwind: Utility-first, fast development, consistent design
- Vite: Fast HMR, modern build tool

### Backend

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| **Flask** | 3.x | Web Framework |
| **Python** | 3.11+ | Programming Language |
| **Flask-SQLAlchemy** | 3.x | ORM |
| **Flask-CORS** | Latest | Cross-Origin Resource Sharing |
| **bcrypt** | Latest | Password Hashing |
| **psycopg2** | Latest | PostgreSQL Adapter |

**Lý do chọn:**
- Flask: Lightweight, flexible, easy to learn
- Python: Readable, popular for backend development
- SQLAlchemy: Powerful ORM, database-agnostic

### Database

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| **PostgreSQL** | 15.x | Relational Database |
| **pgAdmin 4** | Latest | Database Management Tool |

**Lý do chọn:**
- PostgreSQL: Robust, ACID-compliant, excellent for relational data
- Open-source và production-ready

### DevOps & Tools

| Công nghệ | Mục đích |
|-----------|----------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Git** | Version Control |
| **Cloudflare R2** | Object Storage (for image uploads) |

## 📊 Phạm Vi Dự Án

### Trong Phạm Vi (Included)

✅ User authentication & authorization  
✅ Product catalog với search & filter  
✅ Shopping cart functionality  
✅ Order management system  
✅ Admin dashboard  
✅ COD payment method  
✅ Responsive design  
✅ Session-based authentication  
✅ Customer & Admin management  
✅ Statistics & reporting  
✅ Banner management system  
✅ Customer profile management

### Ngoài Phạm Vi (Excluded)

❌ Online payment integration (VNPay, MoMo)  
❌ Email notifications  
❌ SMS notifications  
❌ Product reviews & ratings  
❌ Wishlist functionality  
❌ Real-time chat support  
❌ Multi-language support  
❌ Mobile apps (iOS/Android)  
❌ Advanced search với filters phức tạp  
❌ Recommendation system

## 👥 Đối Tượng Người Dùng

### 1. Guest (Khách truy cập)
- **Ai?** Người dùng chưa đăng ký/đăng nhập
- **Mục đích?** Xem và tìm kiếm sách
- **Nhu cầu?** Dễ dàng browse và tìm sách mình muốn

### 2. Customer (Khách hàng)
- **Ai?** Người dùng đã đăng ký và đăng nhập
- **Mục đích?** Mua sách trực tuyến
- **Nhu cầu?** Giỏ hàng, đặt hàng, theo dõi đơn hàng

### 3. Admin (Quản trị viên)
- **Ai?** Quản lý hệ thống, chủ shop
- **Mục đích?** Quản lý toàn bộ hệ thống
- **Nhu cầu?** Dashboard, quản lý sách/users/orders, thống kê

## 🏗 Mô Hình Phát Triển

### Quy Trình Phát Triển

1. **Phân tích yêu cầu** - Xác định features cần thiết
2. **Thiết kế hệ thống** - ERD, Architecture diagrams
3. **Thiết kế giao diện** - Wireframes, UI/UX design
4. **Phát triển Backend** - API, Database, Business logic
5. **Phát triển Frontend** - Components, Pages, Integration
6. **Testing** - Unit tests, Integration tests, Manual testing
7. **Deployment** - Docker, Docker Compose
8. **Documentation** - Technical docs, User guides

### Phương Pháp

- **Agile approach** với iterative development
- **Version control** với Git
- **Code review** và refactoring liên tục
- **Documentation-driven** development

## 📈 Kết Quả Đạt Được

### Về Kỹ Thuật

✅ Hệ thống hoàn chỉnh với đầy đủ tính năng CRUD  
✅ REST API được document đầy đủ  
✅ Frontend responsive và user-friendly  
✅ Database được thiết kế chuẩn hóa  
✅ Code được tổ chức theo best practices  
✅ Containerized với Docker  

### Về Học Tập

✅ Nắm vững React & TypeScript  
✅ Hiểu rõ Flask backend development  
✅ Thực hành database design  
✅ Áp dụng software architecture patterns  
✅ Học cách viết documentation chuyên nghiệp  
✅ Thực hành Git workflow  

## 🔮 Hướng Phát Triển Tương Lai

### Short-term (< 3 tháng)

- [ ] Thêm payment integration (VNPay)
- [ ] Email notifications cho orders
- [ ] Product reviews & ratings
- [ ] Advanced search filters

### Long-term (> 3 tháng)

- [ ] Mobile app (React Native)
- [ ] AI-powered recommendations
- [ ] Real-time inventory management
- [ ] Analytics dashboard nâng cao
- [ ] Multi-vendor support

---

**📌 Tóm tắt:** Bookstore là một dự án đồ án tốt nghiệp hoàn chỉnh, thể hiện việc áp dụng kiến thức về web development, software architecture, và best practices trong phát triển phần mềm hiện đại.

