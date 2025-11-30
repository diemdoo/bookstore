# Changelog - Bookstore Migration

## [2.14.1] - 2024-12-XX

### Added
- **Category Selector in Banner Management**
  - Added category dropdown selector in BannerManagement component
  - Admin can now choose category from dropdown instead of manually typing link
  - Auto-generates link in format `/books?category={categoryKey}` when category is selected
  - Added option to switch between "Chọn Category" and "Link Tùy Chỉnh" modes
  - When editing existing banners, automatically detects if link is category-based and pre-selects category
  - Updated `frontend/src/pages/admin/BannerManagement.tsx`: Added category selector UI and logic
  - Updated `docs/10-USER_GUIDE.md`: Updated banner management instructions with category selector feature

---

## [2.14.0] - 2024-12-XX

### Changed
- **Banner Links Improvement**
  - Updated banner links from hardcoded book IDs to category-based links for better flexibility
  - Main banners (3 banners) now link to `/books?category=Sach Tieng Viet`
  - Side banner 1 ("FLASH SALE HÔM NAY") now links to `/books?category=Truyen Tranh`
  - Side banner 2 ("SÁCH THIẾU NHI") now links to `/books?category=Van Phong Pham`
  - Updated `backend/seed_data.py`: Changed all banner links to category-based URLs
  - Updated `docs/SEEDING.md`: Added detailed banner link information
  - Updated `docs/04-API_DOCUMENTATION.md`: Changed banner example link from `/sale` to category link
  - Updated `docs/10-USER_GUIDE.md`: Added note about using category links for banners
  - Updated `docs/diagrams/admin-banners-flow.mmd`: Added example of category link format

---

## [2.13.1] - 2024-12-XX

### Changed
- **Route Path Update**
  - Changed admin management route from `/admin/staff` to `/admin/admins` for consistency
  - Updated `frontend/src/App.tsx`: Route path changed to `/admin/admins`
  - Updated `frontend/src/components/layout/AdminSidebar.tsx`: Navigation path updated
  - Updated `docs/06-FRONTEND_ARCHITECTURE.md`: Documentation reflects new route path

---

## [2.13.0] - 2024-12-XX

### Removed
- **Staff Role and staff_code Field Removal**
  - Removed `staff` role from authentication system
  - Removed `staff_code` field from User model and database
  - Removed `generate_staff_code()` static method from User model
  - Removed staff accounts from seed data (staff1, staff2)
  - Simplified authentication system to only support `admin` and `customer` roles
  - Updated all documentation and diagrams to reflect role simplification

### Changed
- **Backend Changes**
  - `backend/models.py`: Changed role default from `'user'` to `'customer'`
  - `backend/models.py`: Removed `staff_code` column from User model
  - `backend/models.py`: Removed `generate_staff_code()` method
  - `backend/models.py`: Updated `to_dict()` to remove `staff_code`
  - `backend/utils/helpers.py`: Updated `admin_required` decorator docstring (admin-only, not admin/staff)
  - `backend/seed_data.py`: Removed staff1 and staff2 seed accounts
  - `backend/business/dto/user_dto.py`: Removed `staff_code` field, updated role default to `'customer'`

- **Frontend Changes**
  - `frontend/src/components/auth/ProtectedRoute.tsx`: Added role check (only `role === 'admin'` allowed)
  - `frontend/src/pages/auth/LoginPage.tsx`: Added redirect logic (admin → `/admin`, customer → `/`)
  - `frontend/src/contexts/AuthContext.tsx`: Updated `login()` to return User object
  - `frontend/src/pages/admin/StaffManagement.tsx`: Updated to manage admin accounts instead of staff
  - `frontend/src/pages/admin/StaffManagement.tsx`: Removed `staff_code` column from table
  - `frontend/src/types/index.ts`: Updated User interface: `role: 'admin' | 'customer'` (removed 'staff' and 'user')
  - `frontend/src/types/index.ts`: Removed `staff_code` field from User interface

- **Documentation Updates**
  - `docs/01-INTRODUCTION.md`: Removed Staff user type section
  - `docs/02-SYSTEM_ARCHITECTURE.md`: Updated role-based authorization to only `admin` and `customer`
  - `docs/03-DATABASE_DESIGN.md`: Updated role constraint to `CHECK(role IN ('admin','customer'))`
  - `docs/03-DATABASE_DESIGN.md`: Removed `staff_code` field from table definition and ERD
  - `docs/04-API_DOCUMENTATION.md`: Updated admin routes to admin-only (not admin/staff)
  - `docs/07-AUTHENTICATION_FLOW.md`: Removed staff login flow references
  - All diagrams in `docs/diagrams/`: Updated to remove staff references and `staff_code` field

### Technical
- Database migration required: Remove `staff_code` column from `users` table
- Role constraint update: `CHECK(role IN ('admin','customer'))`
- All authentication flows now simplified: Admin → `/admin`, Customer → `/`

---

## [2.12.0] - 2024-12-XX

### Changed
- **User Login/Register UI Synchronization**
  - Synchronized LoginPage and RegisterPage UI design with AdminLoginPage
  - Replaced gray background with gradient background (`bg-gradient-to-br from-primary to-indigo-700`)
  - Added icon header (User icon for login, UserCircle for register) in circular badge
  - Improved card design: `rounded-2xl shadow-2xl` for better visual appeal
  - Added title and subtitle for better UX
  - Added footer copyright text
  - Removed unnecessary overlay (`bg-black/50`) and close button
  - Replaced error state with Toast notifications for consistent UX
  - Improved form spacing: `space-y-6` for better readability
  - Button size: `size="lg"` for better touch targets

### Technical
- Frontend: `frontend/src/pages/auth/LoginPage.tsx` - Complete UI redesign with gradient background and icon header
- Frontend: `frontend/src/pages/auth/RegisterPage.tsx` - Complete UI redesign with gradient background and icon header
- Documentation: Updated `docs/06-FRONTEND_ARCHITECTURE.md` - Added UI design pattern documentation
- Documentation: Updated `docs/10-USER_GUIDE.md` - Updated login/register instructions with new UI descriptions

---

## [2.11.0] - 2024-11-25

### Added
- **Banner Image Upload Feature**
  - Replaced manual URL input with file upload component in BannerManagement
  - Upload banner images directly to Cloudflare R2 (folder `banners/`)
  - Image preview before upload
  - File validation (type: image/*, max size: 5MB)
  - Consistent UX with BooksManagement image upload

### Changed
- **BannerManagement Component**
  - Removed manual URL input field
  - Added file upload UI with preview and upload button
  - Added `bannersService.uploadImage()` method
  - Updated form validation to require uploaded image

- **BookCard UI Improvements**
  - Compact design: Reduced padding from `p-4` to `px-3 py-2.5` for tighter spacing
  - Visual connection: Added `bg-gray-50` background and `border-t` separator for title+price area
  - Improved typography: Title uses `text-sm`, price uses `text-lg` for better hierarchy
  - Reduced spacing: Title-price gap reduced from `mt-2` to `mt-1`
  - Reduced title height: `min-h-[3rem]` to `min-h-[2.5rem]` for more compact cards
  - Enhanced hover effects: Added border highlight (`hover:border-primary`)

- **Seed Data Updates**
  - Updated banner image URLs to use `banners/` folder instead of `books/` folder
  - Banner URLs now point to `https://cdn.duyne.me/banners/...` for better organization

### Technical
- Frontend: `frontend/src/pages/admin/BannerManagement.tsx` - Added file upload handlers and UI
- Frontend: `frontend/src/services/api.ts` - Added `bannersService.uploadImage()` method
- Frontend: `frontend/src/components/shared/BookCard.tsx` - Improved UI with compact design and visual connection
- Backend: `backend/routes/upload.py` - Added folder parameter support (default: 'books', supports 'banners')
- Backend: `backend/seed_data.py` - Updated banner URLs to use `banners/` folder
- Documentation: Updated user guide, API docs, frontend architecture, and changelog

---

## [2.10.1] - 2024-11-25

### Documentation
- **Updated Database Design Documentation**
  - Clarified that `description` fields (Books, Categories, Banners) use TEXT type with **unlimited length**
  - Updated ERD diagrams to note TEXT type supports long text without character limits
  - Updated API documentation to specify description field accepts unlimited characters
  - Updated Frontend Architecture docs to note description uses textarea without maxLength

### Changed
- **Domain Update**
  - Updated all image URLs from `cdn.duynhne.me` to `cdn.duyne.me` in seed_data.py
  - Updated docker-compose.yml default domain to `cdn.duyne.me`
  - Reseeded database with corrected domain URLs

---

## [2.10.0] - 2024-11-24

### Changed
- **Migrated from MinIO to Cloudflare R2**
  - Replaced MinIO object storage with Cloudflare R2
  - Updated storage service to use boto3 instead of minio library
  - All configuration now via environment variables from `.env` file (no hardcoded values)
  - Public URLs now use custom domain `cdn.duyne.me` instead of presigned URLs
  - Removed MinIO Docker service from both `docker-compose.yml` and `docker-compose.prod.yml`
  - Removed `minio_data` and `minio_data_prod` volumes

### Added
- **Cloudflare R2 Configuration**
  - New environment variables: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_DOMAIN`
  - `.env.example` template file for R2 credentials
  - Production deployment requires `.env` file with all R2 credentials (no defaults)

### Removed
- MinIO dependency (`minio==7.2.0`) from `backend/requirements.txt`
- MinIO service from Docker Compose files
- MinIO-related environment variables (`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`)

### Technical
- Backend: `backend/utils/storage.py` - Complete rewrite using boto3 for R2
- Backend: `backend/routes/upload.py` - Updated docstring to reference R2
- Backend: `backend/requirements.txt` - Replaced `minio==7.2.0` with `boto3==1.34.0`
- Docker: Removed MinIO service and volumes from compose files
- Docker: Updated environment variables to use R2 configuration
- Documentation: Updated all references from MinIO to Cloudflare R2

### Migration Notes
- No data migration required (user confirmed)
- Existing image URLs in database remain unchanged (they're external URLs)
- Backward compatible - API endpoints remain the same
- Production deployment requires `.env` file with R2 credentials

---

## [2.9.3] - 2024-11-24

### Added
- **Public Search Functionality**
  - HomePage now handles search query parameter (`?search=query`)
  - Displays search results instead of homepage content when search query exists
  - Shows "Kết quả tìm kiếm cho '{query}'" heading with result count
  - Search results displayed in 5-column grid layout
  - Shows "Không tìm thấy sách nào" message when no results found
  - Search integrates with PublicHeader search input (navigates to `/?search=query`)

- **Admin BooksManagement Search**
  - Added search input on same line as "Thêm Sách" button
  - Search by book title (case-insensitive partial match)
  - Search on Enter key press
  - Clear button (X icon) to reset search
  - Shows search status message: "Đang hiển thị kết quả tìm kiếm cho '{query}'"
  - Pagination works correctly with search query
  - Empty state message when no search results

### Changed
- **AdminTopBar**
  - Removed unused search input (was placeholder only, no functionality)
  - Removed unused `Search` icon import
  - Simplified to show only title and user menu

### Technical
- Frontend: `frontend/src/pages/public/HomePage.tsx`, `frontend/src/pages/admin/BooksManagement.tsx`, `frontend/src/components/layout/AdminTopBar.tsx`
- Backend: Uses existing `/api/books?search=query` endpoint (no changes needed)
- API: `booksService.getBooks({ search, page, per_page })` already supported search parameter

### Documentation
- Updated `docs/06-FRONTEND_ARCHITECTURE.md`:
  - Added search functionality documentation for HomePage
  - Added search functionality documentation for BooksManagement
  - Updated PublicHeader to document search navigation
  - Updated Admin Page Pattern to include optional search input example
  - Removed AdminTopBar search mention

---

## [2.9.2] - 2024-11-24

### Changed
- **Standardized Admin Management Pages**
  - Refactored all admin management pages (Books, Banners, Staff, Customers, Orders) to follow CategoryManagement's superior UI pattern
  - Replaced Modal component imports with custom inline modals for consistency
  - Replaced ActionMenu dropdowns with direct icon buttons (Edit2, Trash2, ToggleLeft/Right)
  - Unified form layouts and button styling across all admin pages
  - Removed redundant page titles (AdminLayout already provides title)
  - Consistent action button colors: blue for edit, red for delete, green for toggle
  - Improved visual hierarchy and spacing throughout admin UI

### Improved
- **Better UX in Admin Panel**
  - More intuitive action buttons with hover states and tooltips
  - Cleaner code structure with less component dependencies
  - Faster access to actions (no dropdown menus to open)
  - Consistent modal structure and behavior across all CRUD operations
  - Better responsive behavior on mobile devices

### Removed
- **Unused Components**
  - Removed ActionMenu and ActionMenuItem components from Table.tsx
  - Cleaned up unused import of MoreVertical icon
  - Removed Modal component usage from all admin pages (using inline custom modals instead)

### Documentation
- Updated `docs/06-FRONTEND_ARCHITECTURE.md` with detailed "Admin Page Pattern" section
- Documented standardized modal structure, icon button patterns, and header layout
- Added code examples for consistent implementation across admin pages

---

## [2.9.1] - 2024-11-23

### Added
- **Breadcrumb Navigation**
  - Created reusable `Breadcrumb` component in `frontend/src/components/ui/Breadcrumb.tsx`
  - Added breadcrumb to BookDetailPage showing navigation path: Trang chủ > Category > Book Title
  - All breadcrumb items are clickable except the current page (last item)
  - Integrated with category data to display proper category names

- **Category Page**
  - Created dedicated `CategoryPage` at route `/category/:categoryKey`
  - Displays category information (name, description)
  - Lists all books in the selected category
  - Includes breadcrumb navigation: Trang chủ > Category Name
  - Features pagination for large category listings
  - 5-column grid layout for book display

### Changed
- **BookDetailPage Navigation**
  - Added breadcrumb navigation showing: Trang chủ > Category > Book Title
  - Category name in breadcrumb links to dedicated category page
  - Fetches category information alongside book details for accurate display

- **Routing**
  - Added new route: `/category/:categoryKey` for category browsing
  - Updated App.tsx with CategoryPage import and route registration

### Technical
- Components: `frontend/src/components/ui/Breadcrumb.tsx`, `frontend/src/pages/public/CategoryPage.tsx`
- Updated: `frontend/src/pages/public/BookDetailPage.tsx`, `frontend/src/App.tsx`
- Documentation: Updated `docs/06-FRONTEND_ARCHITECTURE.md` with new components and navigation flow

---

## [2.9.0] - 2024-11-23

### Added
- **Categories Management (Database-Based)**
  - Created `categories` table in database
  - Added Category model with fields: id, key, name, description, display_order, is_active
  - Implemented CategoryDAO, CategoryDTO, and CategoryService
  - Added admin CRUD API endpoints for categories (/api/admin/categories)
  - Created CategoryManagement page in admin panel with full CRUD UI
  - Categories now stored in database instead of hardcoded constants
  - Admins can add, edit, delete, and toggle category status via UI

### Changed
- Removed hardcoded categories from `constants.py`
- Updated `/api/books/categories` to `/api/categories` endpoint
- Book.category now references `categories.key` (soft reference)
- Updated frontend categoriesService to use new database endpoints
- Updated Category type in frontend to match database fields
- Added category management link to admin sidebar

### Technical
- Backend: `backend/models.py`, `backend/data/category_dao.py`, `backend/business/dto/category_dto.py`, `backend/business/services/category_service.py`, `backend/routes/categories.py`
- Frontend: `frontend/src/pages/admin/CategoryManagement.tsx`, `frontend/src/types/index.ts`, `frontend/src/services/api.ts`
- Database: Added `categories` table with seed data for 4 initial categories
- Documentation: Updated ERD, API docs, database schema

---

## [2.8.0] - 2024-11-23

### Dynamic Best Sellers Implementation

#### Changed
- **Best Sellers Logic**: Changed from static category to dynamic computation
  - Removed 'Sach Ban Chay' from `backend/constants.py` CATEGORIES list
  - Best sellers now computed from actual order history (top books by quantity sold)
  - Homepage displays top 10 best-selling books (2x5 grid) without "Xem Thêm" button
  - Category dropdown now shows only 4 categories (no "Sách Bán Chạy")

#### Added
- **New API Endpoint**: `GET /api/books/bestsellers?limit=10`
  - Returns top N books by total quantity sold from `order_items`
  - Falls back to first N books (by ID) if no orders exist yet
- **Frontend Service**: `booksService.getBestSellers(limit)`

#### Updated
- **Seed Data**: Moved 6 books from 'Sach Ban Chay' to 'Sach Tieng Viet'
  - Total books: 60 (was 66)
  - Distribution: Sach Tieng Viet (21), Truyen Tranh (15), Do Trang Tri (15), Van Phong Pham (15)
- **HomePage**: Now fetches best sellers from new API instead of category query
- **Documentation**: 
  - Updated `docs/04-API_DOCUMENTATION.md` with bestsellers endpoint
  - Updated `docs/06-FRONTEND_ARCHITECTURE.md` HomePage section
  - Updated `docs/03-DATABASE_DESIGN.md` category notes

#### Removed
- 'Sach Ban Chay' as a static category
- "Xem Thêm" button from best sellers section on homepage

---

## [2.6.1] - 2024-11-21

### Bug Fixes & High-level Diagrams

#### Fixed Mermaid Parse Errors
- **Issue**: Dấu ngoặc đơn `()` trong text nodes gây conflict với Mermaid syntax
- **Fixed files**:
  - `docs/diagrams/admin-orders-flow.mmd`: Changed `(Chưa TT)` → `- Chưa TT`
  - `docs/diagrams/admin-order-management-flow.mmd`: Fixed 3 locations với ngoặc đơn
- **Result**: All diagrams now render correctly on GitHub và Mermaid viewers

#### Added High-level Business Flow Diagrams

Created 3 new diagrams cho presentations và business overview:

1. **`high-level-customer-journey.mmd`** - Customer Journey (Business Perspective)
   - Visit website → Browse books
   - Add to cart → Select items
   - Checkout → Fill address
   - Place order with COD
   - Track order status
   - Receive & pay
   - Complete journey
   - NO API endpoints, NO SQL, focus on user experience

2. **`high-level-admin-workflow.mmd`** - Admin Daily Workflow (Business Perspective)
   - Login to admin panel
   - View dashboard overview
   - Manage books, orders, users, content
   - View statistics
   - Logout
   - Focus on business actions, không có technical implementation

3. **`high-level-order-processing.mmd`** - Order Lifecycle (Business Perspective)
   - Order placement by customer
   - Admin review & confirmation
   - Order preparation
   - Shipping process
   - Delivery & COD payment
   - Order completion
   - Post-delivery support
   - Sequence diagram format, business flow only

#### Documentation Updates
- **`docs/00-README.md`**: Added "Diagram Types" section
  - Explained difference giữa High-level và Technical diagrams
  - Listed all diagrams theo category
  - Clear purpose và use cases cho mỗi loại
  
#### Summary
- **Total Diagrams**: 16 → 19 files
- **Fixed**: 2 files với parse errors
- **New**: 3 high-level business diagrams
- **Updated**: 2 documentation files

#### Benefits
- ✅ All Mermaid diagrams render correctly
- ✅ Flexible presentation options: business view vs technical view
- ✅ Better for thesis defense: start with overview, then dive into details
- ✅ Suitable for different audiences: stakeholders vs developers

---

## [2.6.0] - 2024-11-21

### Diagram Refactoring for Thesis Report

#### Overview
Refactored all diagrams để phù hợp với đồ án tốt nghiệp:
- **Before**: 7 diagrams (some too long và phức tạp)
- **After**: 16 diagrams (clear, concise, professional)

#### New Admin Diagrams (6 files)
Tách `admin-flow.mmd` (128 lines) thành 6 diagrams riêng biệt:

1. **`admin-overview.mmd`**: Tổng quan admin panel với 5 modules
2. **`admin-books-flow.mmd`**: CRUD operations cho Books (add, edit, delete, search/filter)
3. **`admin-users-flow.mmd`**: Quản lý Customers & Staff (auto-generate codes, toggle status)
4. **`admin-orders-flow.mmd`**: Order management từ phía admin (update status, payment)
5. **`admin-banners-flow.mmd`**: CRUD operations cho Banners (upload, toggle, delete)
6. **`admin-statistics-flow.mmd`**: Statistics dashboard (revenue, orders, top books)

#### New Order Flow Diagrams (2 files)
Tách `order-flow.mmd` (139 lines) thành 2 perspectives:

1. **`customer-order-flow.mmd`**: Customer journey (browse → cart → checkout → track)
   - Item selection với checkboxes
   - Bulk delete selected items
   - Checkout với selected items only
   - View order history với badges
   
2. **`admin-order-management-flow.mmd`**: Admin order management
   - View all orders
   - Update order status workflow
   - Update payment status (independent)
   - Filter & search

#### New Relationship Diagrams (3 files)

1. **`backend-class-diagram.mmd`**: UML Class Diagram
   - Models (User, Book, Order, OrderItem, Cart, Banner)
   - DAOs (Data Access Objects)
   - DTOs (Data Transfer Objects)
   - Services (Business Logic)
   - Validators
   - Workflows
   - Relationships với arrows và dependencies

2. **`frontend-component-diagram.mmd`**: React Component Hierarchy
   - App → Router → Routes
   - Public Routes (HomePage, CartPage, CheckoutPage, etc.)
   - Admin Routes (Dashboard, Management pages)
   - UI Components Library (Button, Input, Table, Modal, Toast, etc.)
   - Contexts (Auth, Cart, Toast)
   - Services (API layer)
   - Component dependencies

3. **`data-flow-diagram.mmd`**: End-to-end Data Flow
   - User → Browser → React → Context → API Service
   - HTTP → Nginx → Flask → Services → DAOs → PostgreSQL
   - Specific flows: Authentication, Cart, Order, File Upload
   - Request/Response cycle với 27 steps

#### Enhanced Database ERD

**Updated `database-erd.mmd`** với detailed constraints:
- PRIMARY KEY, FOREIGN KEY specifications
- UNIQUE, NOT NULL constraints
- CHECK constraints (role IN, status IN, price >= 0, stock >= 0)
- DEFAULT values
- INDEX columns
- ON DELETE CASCADE/RESTRICT rules
- Relationship cardinality với foreign key notes

#### Documentation Updates

Updated diagram references trong các docs:
- `docs/02-SYSTEM_ARCHITECTURE.md`: Link to system-architecture.mmd & data-flow-diagram.mmd
- `docs/03-DATABASE_DESIGN.md`: Link to enhanced database-erd.mmd
- `docs/05-BACKEND_ARCHITECTURE.md`: Link to backend-class-diagram.mmd
- `docs/06-FRONTEND_ARCHITECTURE.md`: Link to frontend-component-diagram.mmd
- `docs/08-ORDER_FLOW.md`: Link to customer-order-flow.mmd & admin-order-management-flow.mmd

#### Cleanup

Removed old complex diagrams:
- `admin-flow.mmd` (replaced by 6 new files)
- `order-flow.mmd` (replaced by 2 new files)

#### Benefits

- ✅ Mỗi diagram ngắn gọn (~30-50 lines instead of 128-139)
- ✅ Dễ hiểu, dễ present trong báo cáo tốt nghiệp
- ✅ Professional structure with clear separation of concerns
- ✅ Comprehensive coverage: flows, relationships, data models
- ✅ Suitable for thesis defense và documentation

---

## [2.5.0] - 2024-11-21

### CI/CD Setup

#### GitHub Actions Workflow
- **Created `.github/workflows/docker-build.yml`**: Automated Docker image build and push
  - Triggers on push to `main` branch
  - Builds both frontend and backend images
  - Pushes to GitHub Container Registry (ghcr.io)
  - Images: `ghcr.io/duynhne/bookstore-frontend:latest` và `ghcr.io/duynhne/bookstore-backend:latest`
  - Uses Docker Buildx for multi-platform support
  - Implements GitHub Actions cache for faster builds
  - Build time: ~3-5 minutes
  
#### Production Deployment Updates
- **Updated `docker-compose.prod.yml`**: Changed from build to use pre-built images
  - Backend: `image: ghcr.io/duynhne/bookstore-backend:latest`
  - Frontend: `image: ghcr.io/duynhne/bookstore-frontend:latest`
  - Eliminates need to build on production server
  - Faster deployment with `docker-compose pull`
  - Consistent images across environments
  
#### Documentation Updates
- **`docs/09-DEPLOYMENT.md`**: Added comprehensive CI/CD section
  - GitHub Actions workflow explanation
  - Setup instructions for GitHub Container Registry
  - Deploy with pre-built images guide
  - Troubleshooting CI/CD issues
  - Local build vs CI/CD comparison table
  
- **`.gitignore`**: Enhanced with additional exclusions
  - Node.js (node_modules, npm-debug.log)
  - Docker volumes (postgres_data_prod, minio_data_prod, pgadmin_data_prod)
  - Frontend build artifacts (dist, build)
  
### Bug Fixes
- **Frontend Build**: Fixed Vite build errors for production
  - Added `@types/node` to package.json for Node.js type declarations
  - Updated `vite.config.ts` to use ES module compatible `__dirname` (fileURLToPath)
  - Changed `index.html` script path from `/src/main.tsx` to `./src/main.tsx`
  - Added `base: '/'` to Vite config
  
### Benefits
- ✅ Automated builds on every push to main
- ✅ No manual Docker build required on production
- ✅ Consistent images across all environments
- ✅ Faster deployments with pre-built images
- ✅ GitHub Container Registry integration (free)
- ✅ Cached builds for speed improvement

## [2.4.0] - 2024-11-21

### Upgraded Versions

#### Python 3.11 → 3.12
- **Performance**: Up to 5% faster execution
- **Better error messages**: Improved debugging experience
- **New syntax features**: Enhanced language capabilities
- **Compatibility**: All dependencies tested and working

#### Node.js 18 → 22
- **Latest LTS**: Long-term support until April 2027
- **Performance improvements**: Faster build and runtime
- **Security updates**: Latest security patches
- **Better ES module support**: Enhanced import/export handling

### Files Updated
- `backend/Dockerfile`: FROM python:3.11-slim → python:3.12-slim
- `frontend/Dockerfile`: FROM node:18-alpine → node:22-alpine
- `frontend/Dockerfile.dev`: FROM node:18-alpine → node:22-alpine

### Testing
- ✅ Development environment: Built and tested successfully
  - Frontend: http://localhost:5173 (Vite dev server with Node 22)
  - Backend: http://localhost:5000 (Flask with Python 3.12)
  
- ✅ Production environment: Built and tested successfully  
  - Frontend: http://localhost (Nginx serving React build from Node 22)
  - Backend: http://localhost/api (Gunicorn with Python 3.12)

### Compatibility
- All Python packages compatible with 3.12
- All npm packages compatible with Node 22
- No breaking changes detected

---

## [2.3.0] - 2024-11-21

### New Features

#### Production Deployment Setup
- **Nginx Configuration**: Created `frontend/nginx.conf` for serving static frontend and proxying API requests
  - Gzip compression for performance
  - Cache headers for static assets
  - Reverse proxy for `/api` endpoints
  - Health check endpoint at `/health`
  
- **Gunicorn Configuration**: Created `backend/gunicorn.conf.py` for production WSGI server
  - Auto-scaled workers based on CPU count (cores * 2 + 1)
  - Timeout settings (120s)
  - Graceful shutdown (30s)
  - Preload app for better performance
  - Structured logging to stdout/stderr
  
- **Production Compose**: Created `docker-compose.prod.yml`
  - Multi-stage Docker build for frontend (build → nginx)
  - Gunicorn command for backend
  - Environment variable support via `.env.prod`
  - Restart policies for all services
  - Separate production volumes
  
- **Environment Example**: Created `.env.prod.example` for production secrets template

### Backend Changes
- **app.py**: Exposed app instance at module level for Gunicorn
  - Added `app = create_app()` before `if __name__ == '__main__'`
  - Moved seed_database() call to module level

- **requirements.txt**: Added `gunicorn==21.2.0`

### Frontend Changes  
- **CheckoutPage.tsx**: Removed unused `clearCart` import to fix production TypeScript build error

### Documentation Updates
- **docs/09-DEPLOYMENT.md**: 
  - Added comprehensive Production Deployment section
  - Documented production vs development differences
  - Added production management commands
  - Included HTTPS setup guide
  - Added security and monitoring considerations
  
- **README.md**: Updated with production deployment quick start (to be updated)

### Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Access
# Frontend: http://localhost (port 80)
# Backend API: http://localhost/api
```

### Production Features
- **Frontend**: Nginx serving optimized static build
- **Backend**: Gunicorn with 15 workers (auto-scaled)
- **Performance**: Gzip compression, asset caching, efficient worker management
- **Reliability**: Healthchecks, restart policies, graceful shutdowns
- **Security**: Environment variable support for secrets

---

## [2.2.0] - 2024-11-21

### Bug Fixes

#### Fixed Order Creation - Double Cart Clear Issue
- **Root Cause**: Backend automatically clears cart after order creation within transaction, then frontend also tried to clear cart, causing race condition with multiple error toasts
- **Fix**: Removed redundant `clearCart()` call from CheckoutPage.tsx
- **Why**: Backend already clears cart in `OrderWorkflow.create_order()` as part of atomic transaction (line 91: `CartDAO.delete_by_user_id(user_id)`)
- **Result**: Clean order creation with no errors, cart is properly cleared by backend transaction

#### Fixed Admin OrdersManagement - Implemented Order Status Editing
- **Problem**: Edit and Delete buttons in OrdersManagement had empty onClick handlers
- **Fix**: Implemented full order status edit modal with select dropdowns
- **Features**:
  - Modal for editing Order Status (pending → confirmed → completed / cancelled)
  - Modal for editing Payment Status (pending → paid)
  - Connected to existing backend API: `PUT /admin/orders/:id/status`
  - Removed Delete button (no backend delete API exists)
  - Added toast notifications for success/error feedback
- **Result**: Admin can now update order status and payment status through clean UI

### New Features

#### ConfirmDialog Component
- **Custom Confirmation Modal**: Replaced all native `confirm()` dialogs with custom ConfirmDialog component
- **Consistent UI/UX**: Themed confirmation dialogs across client and admin panels
- **Enhanced UX**: Keyboard support (Enter/Escape), backdrop click, animated transitions
- **Color Variants**: Danger (red) for delete actions, Primary (blue) for other confirmations
- **Better Accessibility**: Screen reader friendly, focus management, body scroll lock

### Implementation
- **Client Side (CartPage)**: 2 confirms replaced
  - Delete single item confirmation
  - Delete multiple selected items confirmation
- **Admin Side**: 4 confirms replaced
  - BannerManagement: Delete banner
  - BooksManagement: Delete book
  - StaffManagement: Deactivate staff
  - CustomerManagement: Activate/Deactivate customer

### Frontend Changes
- **New Component**: `ConfirmDialog.tsx` in `components/ui/`
- **Updated Pages**: CartPage, BannerManagement, BooksManagement, StaffManagement, CustomerManagement
- **Improved UX**: All destructive actions now have consistent, beautiful confirmation dialogs

### Notes
- Replaces browser native `confirm()` which had inconsistent styling
- Dialog state managed via local component state
- Auto-closes on confirm action
- Maintains user flow with proper keyboard navigation

#### Cart Item Selection System
- **Select Items**: Added checkbox for each cart item and "Chọn tất cả" checkbox
- **Selective Checkout**: Only selected items are calculated in total and can be checked out
- **Bulk Delete**: New "Xóa (X)" button to delete multiple selected items at once
- **Smart Default**: All items are auto-selected when cart page loads
- **Dynamic UI**: Checkout button shows selected count: "THANH TOÁN (X sản phẩm)"
- **UX Improvements**: Checkout button is disabled when no items are selected

### Frontend Changes
- **CartPage.tsx**: Added selection state management with `useState` and `useEffect`
  - `selectedItems` state to track selected item IDs
  - `handleSelectAll()` to toggle all items selection
  - `handleSelectItem()` to toggle individual item
  - `handleDeleteSelected()` to delete multiple items
  - `getSelectedTotal()` to calculate total for selected items only
- **UI Updates**: 
  - Added checkboxes (w-5 h-5) to each cart item row
  - Added "Xóa (X)" button (danger variant) that appears when items are selected
  - Updated checkout button to display selected count and disable state
  - Updated total amount display to reflect selected items only

### Documentation
- **08-ORDER_FLOW.md**: Added "2.1. Item Selection in Cart" section with:
  - Feature overview and user flow
  - Implementation details with code examples
  - Flowchart diagram showing selection logic
  - UI/UX notes for design reference
- **06-FRONTEND_ARCHITECTURE.md**: Updated CartPage.tsx section with:
  - Selection state management details
  - All handler functions with implementation
  - Updated feature list

### Notes
- Feature inspired by popular e-commerce platforms (Shopee/Lazada)
- Selection state is UI-only (local state), not persisted to backend
- Cart items are still fully loaded, selection only affects display/checkout
- All changes include proper error handling with toast notifications

## [2.1.0] - 2024-11-19

### New Features

#### Customer Profile Management
- **Profile Page**: Added dedicated profile page for customers at `/profile`
- **View Mode**: Display customer code (Mã KH), username, full name, and email (read-only)
- **Edit Mode**: Customers can edit full name and email with validation
- **Order History**: Integrated order history within the profile page
- **Navigation**: Added "Thông tin cá nhân" link in user menu dropdown (customer-only)

### Backend Changes
- **New Endpoint**: `PUT /api/profile` for updating customer profile
- **Validation**: Email uniqueness validation (excluding current user)
- **Business Logic**: Added `update_profile()` method in `AuthService`
- **Data Access**: Added `update_profile()` method in `UserDAO`

### Frontend Changes
- **New Page**: `ProfilePage.tsx` with view/edit modes and order history
- **API Integration**: Added `updateProfile()` to authService
- **Route**: Added `/profile` route with authentication check
- **Header Update**: Added profile menu item for customers

### Notes
- Password change is intentionally not included (simplified feature)
- Profile is restricted to customers only (role check)
- All changes include proper error handling and user feedback

## [2.0.0] - 2024-11-18

### Major Changes - Frontend Migration

#### Migrated from Vanilla JS to React + TypeScript + Tailwind CSS

**Old Tech Stack:**
- HTML, CSS, JavaScript (Vanilla JS)
- Separate HTML files for each page
- jQuery-like DOM manipulation
- Inline styles and separate CSS files

**New Tech Stack:**
- React 18 with TypeScript
- Vite as build tool and dev server
- Tailwind CSS for styling
- React Router v6 for routing
- Axios for API calls
- Context API for state management

### Breaking Changes

- Frontend now runs on port 5173 (Vite dev server) instead of being served by Flask
- All old HTML/CSS/JS files have been removed
- Frontend structure completely reorganized into React component architecture

### New Features

#### Admin Panel
- Modern, clean interface matching Figma designs
- Dark sidebar with improved navigation
- Statistics dashboard with 6 key metrics cards
- Books Management with full CRUD operations and modal forms
- Staff Management interface
- Customer Management interface  
- Orders Management with status badges

#### Customer-Facing Pages
- Redesigned homepage with hero carousel and best sellers
- Modern login/register pages with form validation
- Enhanced book detail page with rating system
- Improved cart page with quantity controls
- Streamlined checkout flow (COD payment)
- Order history page

#### Technical Improvements
- TypeScript for type safety
- Centralized API service layer
- Context-based state management (Auth, Cart)
- Reusable UI components (Button, Input, Modal, Table)
- Responsive design with mobile support
- Modern color palette and typography
- Smooth animations and transitions

### Files Added

#### Configuration
- `frontend/package.json` - Dependencies and scripts
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/vite.config.ts` - Vite configuration with proxy
- `frontend/tailwind.config.js` - Tailwind CSS configuration
- `frontend/postcss.config.js` - PostCSS configuration
- `frontend/Dockerfile` - Production Docker build
- `frontend/Dockerfile.dev` - Development Docker build
- `frontend/nginx.conf` - Nginx configuration for production

#### Source Code
- `frontend/src/types/index.ts` - TypeScript type definitions
- `frontend/src/services/api.ts` - API service layer
- `frontend/src/contexts/AuthContext.tsx` - Authentication context
- `frontend/src/contexts/CartContext.tsx` - Shopping cart context
- `frontend/src/components/ui/*` - Reusable UI components
- `frontend/src/components/layout/*` - Layout components
- `frontend/src/components/shared/*` - Shared components
- `frontend/src/pages/admin/*` - Admin pages
- `frontend/src/pages/public/*` - Customer pages
- `frontend/src/pages/auth/*` - Authentication pages

### Files Removed

- All HTML files (`index.html`, `login.html`, `register.html`, `book-detail.html`, `cart.html`, `checkout.html`, `orders.html`)
- All admin HTML files (`admin/dashboard.html`, `admin/books-management.html`, `admin/users-management.html`, `admin/orders-management.html`, `admin/statistics.html`)
- `frontend/css/` directory (replaced by Tailwind CSS)
- `frontend/js/` directory (replaced by React components)
- `frontend/assets/` directory (empty)

### Files Kept

- `frontend/images/` - Product images referenced in database

### Modified Files

- `backend/app.py` - Updated CORS configuration for Vite dev server
- `docker-compose.yml` - Added frontend service
- `README.md` - Updated tech stack and setup instructions
- `DOCUMENTATION.md` - Updated frontend architecture

### Development Workflow

**Before:**
```bash
docker-compose up -d
# Access at http://localhost:5000
```

**After:**
```bash
# Option 1: Docker (both frontend and backend)
docker-compose up -d
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000/api

# Option 2: Local development (recommended)
# Terminal 1 - Backend
docker-compose up -d db minio backend

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Migration Date
November 18, 2024

### Notes
- All functionality from the old version has been preserved
- UI/UX significantly improved with modern design
- Better code organization and maintainability
- Improved developer experience with TypeScript and hot reload
- Production build optimized with Vite


