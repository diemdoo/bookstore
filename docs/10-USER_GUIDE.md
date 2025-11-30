# 10 - Hướng Dẫn Sử Dụng

## 👤 Dành Cho Guest (Khách truy cập)

### 1. Xem Danh Sách Sách

1. Truy cập http://localhost:5173
2. Trang chủ hiển thị 15 sách đầu tiên (layout 5x3)
3. Click "Xem Thêm" để load thêm sách

### 2. Xem Chi Tiết Sách

1. Click vào bất kỳ cuốn sách nào
2. Xem thông tin chi tiết: Tên, tác giả, giá, mô tả, NXB
3. Nhấn "Thêm vào giỏ" sẽ yêu cầu đăng nhập

### 3. Đăng Ký Tài Khoản

1. Click "Tài Khoản" → "Đăng ký"
2. Trang đăng ký với gradient background đẹp (màu xanh), icon header
3. Điền thông tin:
   - Họ và tên đầy đủ
   - Email (unique, valid format)
   - Username (unique)
   - Password (minimum 6 characters)
   - Xác nhận mật khẩu
4. Click "Đăng Ký"
5. Toast notification xác nhận thành công
6. Tự động đăng nhập và chuyển về trang chủ

### 4. Đăng Nhập

1. Click "Tài Khoản" → "Đăng nhập"
2. Trang đăng nhập với gradient background đẹp (màu xanh), icon header (UI đồng bộ với admin login)
3. Nhập Username và Password
4. Click "Đăng Nhập"
5. Toast notification xác nhận thành công
6. Chuyển về trang chủ

---

## 🛍 Dành Cho Customer (Khách hàng)

### 1. Quản Lý Giỏ Hàng

**Thêm sách vào giỏ:**
1. Vào trang chi tiết sách
2. Nhập số lượng
3. Click "Thêm vào giỏ hàng"
4. Toast notification xác nhận thành công

**Xem giỏ hàng:**
1. Click icon giỏ hàng ở header
2. Xem danh sách sách đã thêm
3. Tổng tiền được tính tự động

**Cập nhật giỏ hàng:**
1. Thay đổi số lượng
2. Click "Cập nhật"
3. Hoặc click "Xóa" để xóa item

### 2. Đặt Hàng

1. Vào giỏ hàng
2. Click "Thanh toán"
3. Điền thông tin:
   - Địa chỉ giao hàng
   - Số điện thoại
4. Xác nhận đơn hàng
5. Giỏ hàng được clear tự động
6. Chuyển đến trang đơn hàng

### 3. Xem Đơn Hàng

1. Click "Tài Khoản" → "Đơn hàng của tôi"
2. Xem tất cả đơn hàng đã đặt
3. Mỗi đơn hiển thị:
   - Mã đơn hàng
   - Ngày đặt
   - Trạng thái
   - Tổng tiền
   - Chi tiết sản phẩm

**Trạng thái đơn hàng:**
- 🟡 **Chờ xác nhận**: Đơn mới tạo
- 🔵 **Đã xác nhận**: Admin đã xác nhận
- 🟢 **Hoàn thành**: Đã giao hàng
- 🔴 **Đã hủy**: Đơn bị hủy

### 4. Quản Lý Profile

1. Click "Tài Khoản" → "Thông tin cá nhân"
2. Xem thông tin:
   - Username (không đổi được)
   - Họ tên
   - Email
3. Click "Chỉnh sửa" để cập nhật
4. Lưu thay đổi

**Lưu ý:** Không thể đổi mật khẩu qua giao diện này

### 5. Đăng Xuất

1. Click "Tài Khoản" → "Đăng xuất"
2. Session sẽ bị clear
3. Chuyển về trang chủ

---

## 👑 Dành Cho Admin

### 1. Đăng Nhập Admin

1. Truy cập http://localhost:5173/admin/login
2. Nhập credentials Admin
3. Click "Đăng Nhập"
4. Chuyển đến Admin Dashboard

### 2. Dashboard

- Xem tổng quan thống kê
- Số đơn hàng, khách hàng, sản phẩm
- Biểu đồ doanh thu

### 3. Quản Lý Sách

**Xem danh sách:**
1. Sidebar → "Quản Lý Sách"
2. Xem tất cả sách với pagination
3. Tìm kiếm, lọc sách

**Thêm sách mới:**
1. Click "Thêm Sách"
2. Điền form:
   - Tên sách (required)
   - Tác giả (required)
   - Thể loại (required)
   - Giá (required, > 0)
   - Số lượng (required, >= 0)
   - Mô tả
   - NXB, năm xuất bản, kích thước, số trang, trọng lượng
   - URL hình ảnh
3. Click "Lưu"

**Sửa sách:**
1. Click icon "Edit" ở sách cần sửa
2. Form điền sẵn thông tin hiện tại
3. Chỉnh sửa và "Lưu"

**Xóa sách:**
1. Click icon "Trash"
2. Xác nhận xóa
3. Sách bị xóa khỏi database

### 4. Quản Lý Khách Hàng

**Xem danh sách:**
1. Sidebar → "Quản Lý Khách Hàng"
2. Xem tất cả customers (role=customer)
3. Hiển thị: Mã KH, Username, Email, Họ tên, Ngày đăng ký, Trạng thái

**Thêm khách hàng:**
1. Click "Thêm Khách Hàng"
2. Điền form
3. Customer code tự động generate (KH001, KH002, ...)

**Khóa/Mở tài khoản:**
1. Click "Toggle Status"
2. Chuyển `is_active` thành `true`/`false`
3. Customer không thể login nếu `is_active=false`

### 5. Quản Lý Đơn Hàng

**Xem tất cả đơn:**
1. Sidebar → "Quản Lý Hóa Đơn"
2. Xem orders của tất cả customers
3. Lọc theo trạng thái

**Chi tiết đơn:**
1. Click vào đơn hàng
2. Xem chi tiết: Khách hàng, sản phẩm, địa chỉ, SĐT, tổng tiền

**Cập nhật trạng thái:**
1. Click "Cập nhật trạng thái"
2. Chọn trạng thái mới:
   - Pending → Confirmed
   - Confirmed → Completed
   - Any → Cancelled
3. Customer có thể thấy trạng thái mới

### 7. Quản Lý Banner

**Xem banner:**
1. Sidebar → "Quản Lý Banner"
2. Xem tất cả banners
3. 3 positions: main, side_top, side_bottom

**Thêm banner:**
1. Click "Thêm Banner"
2. Điền:
   - Title
   - Description (optional)
   - **Upload ảnh**: Click "Chọn file" → Chọn ảnh → Click "Upload"
   - **Link**: 
     - Chọn "Chọn Category" → Chọn category từ dropdown (tự động tạo link `/books?category=...`)
     - Hoặc chọn "Link Tùy Chỉnh" → Nhập link thủ công (ví dụ: `/books`, `/book/1`)
   - Position (main/side_top/side_bottom)
   - Background color
   - Text color
3. Click "Lưu"

**Lưu ý:** 
- Ảnh banner được upload trực tiếp lên Cloudflare R2 (folder `banners/`)
- Hỗ trợ định dạng: JPG, PNG, GIF, WebP
- Kích thước tối đa: 5MB
- Preview ảnh hiển thị trước khi upload

**Active/Inactive:**
1. Toggle trạng thái banner
2. Chỉ active banners hiển thị ở trang chủ

### 8. Thống Kê

1. Sidebar → "Thống Kê"
2. Xem:
   - Tổng doanh thu
   - Tổng đơn hàng
   - Đơn hoàn thành
   - Đơn đã hủy
3. Biểu đồ đơn hàng theo trạng thái
4. Top 10 sách bán chạy (grid 5 cột)

### 9. Đăng Xuất

1. Click avatar → "Đăng xuất"
2. Redirect về `/admin/login`

---

## 🔧 Tips & Best Practices

### Cho Customer

✅ **DO:**
- Kiểm tra giỏ hàng trước khi checkout
- Điền đầy đủ địa chỉ và SĐT
- Theo dõi trạng thái đơn hàng
- Cập nhật thông tin profile khi thay đổi email

❌ **DON'T:**
- Đặt hàng mà không kiểm tra thông tin giao hàng
- Refresh page trong lúc checkout (có thể tạo đơn trùng)
- Share account với người khác

### Cho Admin

✅ **DO:**
- Cập nhật trạng thái đơn hàng kịp thời
- Kiểm tra stock trước khi confirm order
- Backup database định kỳ
- Review statistics thường xuyên

❌ **DON'T:**
- Xóa sách đang có trong orders
- Khóa customer account mà không lý do
- Để đơn hàng ở trạng thái pending quá lâu

---

## ❓ Câu Hỏi Thường Gặp

**Q: Làm sao để reset mật khẩu?**  
A: Hiện tại chưa có tính năng reset password. Liên hệ admin để được hỗ trợ.

**Q: Tại sao không thêm được sách vào giỏ?**  
A: Kiểm tra:
- Đã đăng nhập chưa?
- Sách còn hàng không? (stock > 0)
- Số lượng nhập có hợp lệ không?

**Q: Đơn hàng bao lâu được xác nhận?**  
A: Admin sẽ xác nhận trong vòng 24h. Kiểm tra trạng thái trong "Đơn hàng của tôi".

**Q: Có thể hủy đơn hàng không?**  
A: Chỉ admin mới có thể cancel orders. Liên hệ admin nếu cần hủy.

**Q: Làm sao để xem database?**  
A: Admin có thể dùng pgAdmin tại http://localhost:5050

---

**📌 Tóm tắt:**
- Guest: Browse và register
- Customer: Cart, Order, Profile
- Admin: Full CRUD trên Books/Users/Orders/Banners
- Thống kê và reports cho admin

