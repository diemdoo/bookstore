# 📚 Tài Liệu Dự Án Bookstore

> **Đồ án Tốt nghiệp** - Hệ thống Quản lý Bán sách Trực tuyến

## 🎯 Giới thiệu

Bookstore là một hệ thống thương mại điện tử hoàn chỉnh cho việc bán sách trực tuyến. Dự án được xây dựng với kiến trúc hiện đại, chia tách rõ ràng giữa Frontend, Backend và Database, sử dụng Docker để containerization.

## 📊 Diagram Types

Dự án bao gồm 2 loại diagrams để phục vụ các mục đích khác nhau:

### 🎨 High-level Business Flow Diagrams

**Mục đích**: Presentation, báo cáo tốt nghiệp, trình bày với business stakeholders

**Đặc điểm**:
- Tập trung vào business logic và user journey
- Không có technical details (API endpoints, SQL queries)
- Dễ hiểu cho non-technical audiences
- Phù hợp cho overview presentations

**Diagrams**:
- `high-level-customer-journey.mmd` - Customer journey từ browse đến nhận hàng
- `high-level-admin-workflow.mmd` - Admin daily workflow
- `high-level-order-processing.mmd` - Order lifecycle from business perspective

### 🔧 Technical Implementation Diagrams

**Mục đích**: Development, code review, technical documentation

**Đặc điểm**:
- Chi tiết technical implementation
- Bao gồm API endpoints, SQL operations
- Class diagrams, Component diagrams
- Sequence diagrams với API calls
- Database ERD với constraints và indexes

**Diagrams**:
- System Architecture, Data Flow
- Backend Class Diagram, Frontend Component Diagram
- Authentication Flow, Cart Flow
- Customer Order Flow (technical), Admin Order Management (technical)
- Admin module flows (Books, Users, Orders, Banners, Statistics)
- Database ERD (enhanced)
- Deployment Diagram

**📁 Location**: Tất cả diagrams nằm trong `diagrams/` folder, sử dụng Mermaid format (.mmd)

---

## 📋 Mục Lục Tài Liệu

### Phần I: Tổng Quan

- **[01 - Giới Thiệu](./01-INTRODUCTION.md)**
  - Giới thiệu dự án, mục tiêu, phạm vi
  - Các tính năng chính
  - Công nghệ sử dụng
  - Đối tượng người dùng

- **[02 - Kiến Trúc Hệ Thống](./02-SYSTEM_ARCHITECTURE.md)**
  - Kiến trúc tổng thể
  - Kiến trúc Backend đơn giản (Routes → Models)
  - Luồng dữ liệu
  - Docker Architecture
  - Component Diagram

### Phần II: Thiết Kế Hệ Thống

- **[03 - Thiết Kế Cơ Sở Dữ Liệu](./03-DATABASE_DESIGN.md)**
  - Entity Relationship Diagram (ERD)
  - Mô tả các bảng
  - Quan hệ giữa các bảng
  - Indexes và Constraints
  - Seed Data

- **[04 - Tài Liệu API](./04-API_DOCUMENTATION.md)**
  - Danh sách toàn bộ API endpoints
  - Request/Response format
  - Authentication & Authorization
  - Error handling
  - Examples và Test cases

### Phần III: Chi Tiết Kỹ Thuật

- **[05 - Kiến Trúc Backend](./05-BACKEND_ARCHITECTURE.md)**
  - Cấu trúc thư mục Backend
  - Routes Layer (HTTP + Business Logic)
  - Models Layer (SQLAlchemy ORM)
  - Utils Layer (Helper Functions)
  - Code examples và best practices

- **[06 - Kiến Trúc Frontend](./06-FRONTEND_ARCHITECTURE.md)**
  - Cấu trúc thư mục Frontend
  - Components (UI, Layout, Shared)
  - Pages (Public, Auth, Admin)
  - Contexts (State Management)
  - Services và API Integration
  - Routing và Protected Routes

### Phần IV: Luồng Hoạt Động

- **[07 - Luồng Xác Thực](./07-AUTHENTICATION_FLOW.md)**
  - Luồng đăng ký tài khoản
  - Luồng đăng nhập Customer
  - Luồng đăng nhập Admin
  - Session Management
  - Sequence Diagrams

- **[08 - Luồng Đặt Hàng](./08-ORDER_FLOW.md)**
  - Luồng thêm sản phẩm vào giỏ hàng
  - Luồng checkout
  - Luồng tạo đơn hàng
  - Luồng quản lý đơn hàng (Admin)
  - Order Status Updates
  - Sequence Diagrams

### Phần V: Triển Khai & Sử Dụng

- **[09 - Hướng Dẫn Triển Khai](./09-DEPLOYMENT.md)**
  - Requirements (Software, Hardware)
  - Cài đặt và Chạy dự án
  - Docker Compose Configuration
  - Environment Variables
  - Database Initialization
  - Troubleshooting

- **[10 - Hướng Dẫn Sử Dụng](./10-USER_GUIDE.md)**
  - Hướng dẫn cho Guest
  - Hướng dẫn cho Customer
  - Hướng dẫn cho Admin
  - Screenshots và Demos

### Phần VI: Testing & History

- **[11 - Kiểm Thử](./11-TESTING.md)**
  - Test Strategy
  - Unit Tests
  - Integration Tests
  - Manual Test Cases
  - Test Coverage

- **[12 - Lịch Sử Thay Đổi](./12-CHANGELOG.md)**
  - Version history
  - Feature additions
  - Bug fixes
  - Breaking changes

## 📁 Tài Nguyên Bổ Sung

### Diagrams

Tất cả các sơ đồ được viết bằng Mermaid và nằm trong thư mục [`diagrams/`](./diagrams/):

- `system-architecture.mmd` - Kiến trúc tổng thể
- `database-erd.mmd` - Entity Relationship Diagram
- `authentication-flow.mmd` - Flow đăng nhập/đăng ký
- `order-flow.mmd` - Flow đặt hàng
- `cart-flow.mmd` - Flow giỏ hàng
- `admin-flow.mmd` - Flow quản trị
- `deployment-diagram.mmd` - Sơ đồ triển khai

### Screenshots

Các hình ảnh minh họa nằm trong thư mục `images/` (sẽ được cập nhật)

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd bookstore

# Chạy với Docker Compose
docker-compose up -d

# Truy cập ứng dụng
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000
# pgAdmin: http://localhost:5050
```

**Tài khoản mặc định:**
- Admin: `admin` / `admin123`
- Customer: `user1` / `pass123`

## 📞 Liên Hệ & Hỗ Trợ

Nếu có thắc mắc về dự án, vui lòng tham khảo tài liệu trong thư mục `docs/` hoặc xem source code trong repository.

## 📝 Ghi Chú

- Tài liệu này được viết cho mục đích đồ án tốt nghiệp
- Tất cả code đã được test và chạy ổn định
- Backend có comments chi tiết bằng tiếng Việt
- Diagrams sử dụng Mermaid format

---

**Phiên bản tài liệu:** 1.0.0  
**Cập nhật lần cuối:** 2024-11-25

