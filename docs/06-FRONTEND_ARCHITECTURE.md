# 06 - Kiến Trúc Frontend Chi Tiết

## 📦 Tổng Quan

Frontend được xây dựng với **React 18**, **TypeScript**, và **Tailwind CSS**, sử dụng **Vite** làm build tool. Ứng dụng là một **Single Page Application (SPA)** với client-side routing.

**📊 Xem Component Diagram:** [`diagrams/frontend-component-diagram.mmd`](diagrams/frontend-component-diagram.mmd)

## 🏗 Cấu Trúc Frontend

```
frontend/
├── src/
│   ├── main.tsx                 # Entry point
│   ├── App.tsx                  # Root component với routing
│   ├── index.css                # Global styles (Tailwind)
│   │
│   ├── components/              # React components
│   │   ├── ui/                 # 🎨 Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── Breadcrumb.tsx  # Navigation breadcrumb
│   │   │   └── ConfirmDialog.tsx
│   │   │
│   │   ├── layout/             # 📐 Layout components
│   │   │   ├── PublicHeader.tsx
│   │   │   ├── PublicFooter.tsx
│   │   │   ├── AdminLayout.tsx
│   │   │   ├── AdminSidebar.tsx
│   │   │   └── AdminTopBar.tsx
│   │   │
│   │   ├── shared/             # 🔄 Shared components
│   │   │   ├── BookCard.tsx
│   │   │   └── StatCard.tsx
│   │   │
│   │   └── auth/               # 🔐 Auth components
│   │       └── ProtectedRoute.tsx
│   │
│   ├── pages/                   # 📄 Page components
│   │   ├── public/             # Public pages
│   │   │   ├── HomePage.tsx
│   │   │   ├── BooksPage.tsx
│   │   │   ├── CategoryPage.tsx  # Category browse page
│   │   │   ├── BookDetailPage.tsx
│   │   │   ├── CartPage.tsx
│   │   │   ├── CheckoutPage.tsx
│   │   │   ├── OrdersPage.tsx
│   │   │   └── ProfilePage.tsx
│   │   │
│   │   ├── auth/               # Auth pages
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── AdminLoginPage.tsx
│   │   │
│   │   └── admin/              # Admin pages
│   │       ├── Dashboard.tsx
│   │       ├── BooksManagement.tsx
│   │       ├── CustomerManagement.tsx
│   │       ├── AdminManagement.tsx
│   │       ├── OrdersManagement.tsx
│   │       ├── BannerManagement.tsx
│   │       └── StatisticsPage.tsx
│   │
│   ├── contexts/                # ⚡ React Context (State)
│   │   ├── AuthContext.tsx     # Authentication state
│   │   ├── CartContext.tsx     # Shopping cart state
│   │   └── Toast context in Toast.tsx
│   │
│   ├── services/                # 🌐 API services
│   │   └── api.ts              # Axios setup & API calls
│   │
│   └── types/                   # 📘 TypeScript types
│       └── index.ts            # All type definitions
│
├── public/                      # Static assets
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── tsconfig.json               # TypeScript config
├── tailwind.config.js          # Tailwind config
└── vite.config.ts              # Vite config
```

## 🎨 Component Architecture

### 1. UI Components (`components/ui/`)

**Reusable, presentational components** không chứa business logic.

#### Button.tsx
```typescript
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: React.ReactNode
  className?: string
}

export const Button: React.FC<ButtonProps>
```

**Variants:**
- `primary`: Blue background (default)
- `secondary`: Gray background
- `danger`: Red background

**Usage:**
```tsx
<Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
  Submit
</Button>
```

#### Input.tsx
```typescript
interface InputProps {
  label?: string
  type?: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  required?: boolean
  disabled?: boolean
  icon?: React.ReactNode
  error?: string
  textarea?: boolean
  rows?: number
}
```

#### Breadcrumb.tsx
```typescript
interface BreadcrumbItem {
  label: string
  href?: string  // undefined means current page (not clickable)
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export const Breadcrumb: React.FC<BreadcrumbProps>
```

**Features:**
- Displays navigation path (e.g., Trang chủ > Category > Book)
- Clickable links for navigation (except last item)
- ChevronRight separator between items
- Current page shown in bold, not clickable

**Usage:**
```tsx
const breadcrumbItems = [
  { label: 'Trang chủ', href: '/' },
  { label: 'Sách Tiếng Việt', href: '/category/Sach_Tieng_Viet' },
  { label: 'Đắc Nhân Tâm' }  // Current page, no href
]

<Breadcrumb items={breadcrumbItems} />
```

#### Table.tsx
```typescript
interface Column<T> {
  key: string
  label: string
  width?: string
  render?: (item: T) => React.ReactNode
}

interface TableProps<T> {
  data: T[]
  columns: Column<T>[]
  loading?: boolean
  keyExtractor: (item: T) => string | number
  actions?: (item: T) => React.ReactNode
}
```

**Features:**
- Generic type support
- Custom render functions
- Action column
- Loading state
- Pagination component

#### Toast.tsx
```typescript
type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
}

// Context
export const ToastContext = React.createContext<ToastContextType>()
export const useToast = () => useContext(ToastContext)
```

**Usage:**
```tsx
const toast = useToast()
toast.success('Đăng nhập thành công!')
toast.error('Lỗi kết nối')
```

#### ConfirmDialog.tsx
```typescript
interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'primary'
}
```

**Features:**
- Custom confirmation modal thay thế `confirm()`
- Keyboard support (Enter = confirm, Escape = cancel)
- Backdrop click to cancel
- Color variants (danger for delete, primary for other actions)
- Animated fade-in
- Body scroll lock when open

**Usage:**
```tsx
const [dialogState, setDialogState] = useState({
  isOpen: false,
  title: '',
  message: '',
  onConfirm: () => {}
})

// Show dialog
setDialogState({
  isOpen: true,
  title: 'Xác nhận xóa',
  message: 'Bạn có chắc muốn xóa sản phẩm này?',
  onConfirm: async () => {
    await deleteItem(id)
    toast.success('Đã xóa')
  }
})

// Render
<ConfirmDialog
  isOpen={dialogState.isOpen}
  title={dialogState.title}
  message={dialogState.message}
  onConfirm={dialogState.onConfirm}
  onCancel={() => setDialogState({...dialogState, isOpen: false})}
  confirmText="Xóa"
  cancelText="Hủy"
  variant="danger"
/>
```

### 2. Layout Components (`components/layout/`)

#### PublicHeader.tsx
```typescript
const PublicHeader: React.FC = () => {
  const { user, logout } = useAuth()
  const { getTotalItems } = useCart()
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery)}`)
    }
  }
  
  // Features:
  // - Search bar (navigates to homepage with search query parameter)
  // - Cart icon với badge (số items)
  // - User menu dropdown (login/logout/profile)
  // - Category menu (hamburger icon)
}
```

#### PublicFooter.tsx
```typescript
const PublicFooter: React.FC = () => {
  // Features:
  // - Company info
  // - Social media links
  // - Contact info
  // - Copyright notice
}
```

#### AdminLayout.tsx
```typescript
interface AdminLayoutProps {
  title: string
  children: React.ReactNode
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ title, children }) => {
  // Combines AdminSidebar + AdminTopBar + content area
  // Fixed sidebar (left), TopBar (top), scrollable content
}
```

### Page Layout Patterns

#### Public Pages Layout Pattern

**All public pages follow a consistent layout pattern** to ensure the footer stays at the bottom of the viewport:

```tsx
return (
  <div className="min-h-screen bg-gray-50 flex flex-col">
    <PublicHeader />
    
    <main className="container mx-auto px-4 py-8 flex-1">
      {/* Page content */}
    </main>
    
    <PublicFooter />
  </div>
)
```

**Key Points:**
- **Wrapper div**: Uses `flex flex-col` to create a vertical flex container
- **Main element**: Uses `flex-1` to grow and fill available space, pushing footer to bottom
- **Footer**: Always stays at bottom of viewport when content is short, or below content when content is long
- **Consistency**: All public pages (HomePage, BooksPage, CategoryPage, BookDetailPage, CartPage, CheckoutPage, OrdersPage, ProfilePage) use this pattern

**Benefits:**
- Consistent footer positioning across all pages
- Footer always visible at bottom, even with minimal content
- Better user experience with predictable layout

#### AdminSidebar.tsx
```typescript
const AdminSidebar: React.FC = () => {
  const navItems = [
    { path: '/admin', label: 'Trang Chủ', icon: Home },
    { path: '/admin/books', label: 'Quản Lý Sách', icon: Book },
    { path: '/admin/banners', label: 'Quản Lý Banner', icon: Image },
    { path: '/admin/admins', label: 'Quản Lý Quản Trị Viên', icon: Users },
    { path: '/admin/customers', label: 'Quản Lý Khách Hàng', icon: UserCircle },
    { path: '/admin/orders', label: 'Quản Lý Hóa Đơn', icon: FileText },
    { path: '/admin/statistics', label: 'Thống Kê', icon: BarChart3 },
  ]
  
  // Uses NavLink với active styling
}
```

### 3. Shared Components (`components/shared/`)

#### BookCard.tsx
```typescript
interface BookCardProps {
  book: Book
}

const BookCard: React.FC<BookCardProps> = ({ book }) => {
  // Display:
  // - Book image (aspect ratio 3:4)
  // - Title (text-sm, line-clamp-2, min-h-[2.5rem])
  // - Price (text-lg, formatted VND)
  // - Click to navigate to detail page
}
```

**Layout:** 
- **Compact design**: Reduced padding (`px-3 py-2.5`) for tighter spacing
- **Visual connection**: Title and price share a `bg-gray-50` background with `border-t` separator
- **Typography**: Title uses `text-sm`, price uses `text-lg` for better hierarchy
- **Spacing**: Reduced gap between title and price (`mt-1` instead of `mt-2`)
- **Aspect ratio**: 3:4 for image (maintained)
- **Hover effects**: 
  - Image scale on hover (`group-hover:scale-105`)
  - Shadow enhancement (`hover:shadow-md`)
  - Border highlight (`hover:border-primary`)
- **Responsive**: Text truncation with `line-clamp-2` for long titles

#### StatCard.tsx
```typescript
interface StatCardProps {
  title: string
  value: string | number
  icon?: React.ReactNode
  highlighted?: boolean
}

// Used in Dashboard and Statistics page
```

### 4. Auth Components (`components/auth/`)

#### ProtectedRoute.tsx
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth()
  
  // Flow:
  // 1. Show loading spinner while checking auth
  // 2. If not authenticated, redirect to /admin/login
  // 3. If authenticated, render children
}
```

## 📄 Pages Architecture

### Public Pages

#### HomePage.tsx
```typescript
const HomePage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''
  
  const [bestSellers, setBestSellers] = useState<Book[]>([])
  const [banners, setBanners] = useState<Banner[]>([])
  const [categorySections, setCategorySections] = useState<Array<{ category: Category, books: Book[] }>>([])
  const [searchResults, setSearchResults] = useState<Book[]>([])
  const [searchTotal, setSearchTotal] = useState(0)
  
  // Features:
  // - Search functionality: Reads search query from URL (?search=query)
  // - When search query exists: Shows search results instead of homepage content
  // - Search results: Displays "Kết quả tìm kiếm cho '{query}'" with result count
  // - When no search: Shows normal homepage with:
  //   - Banner carousel (main + side banners)
  //   - Best sellers section (10 books, 5 columns x 2 rows)
  //   - Category sections (5 books per category, 5 columns)
  // - All book displays use 5-column grid layout
}
```

#### CategoryPage.tsx
```typescript
const CategoryPage: React.FC = () => {
  const { categoryKey } = useParams()
  const [books, setBooks] = useState<Book[]>([])
  const [category, setCategory] = useState<Category | null>(null)
  
  // Features:
  // - Breadcrumb navigation (Trang chủ > Category Name)
  // - Display category info (name, description)
  // - List books in category with pagination
  // - 5-column grid layout
}
```

#### BookDetailPage.tsx
```typescript
const BookDetailPage: React.FC = () => {
  const { id } = useParams()
  const [book, setBook] = useState<Book | null>(null)
  const [category, setCategory] = useState<Category | null>(null)
  const [quantity, setQuantity] = useState(1)
  const { addToCart } = useCart()
  
  // Features:
  // - Breadcrumb navigation (Trang chủ > Category > Book Title)
  // - Book details (image, title, author, description, price, etc.)
  // - Add to cart with quantity selector
  // - Toast notifications
}
```

#### CartPage.tsx
```typescript
const CartPage: React.FC = () => {
  const { cart, updateCartItem, removeFromCart, getTotalAmount } = useCart()
  const navigate = useNavigate()
  const toast = useToast()
  const [selectedItems, setSelectedItems] = useState<number[]>([])
  
  // Auto-select all items when cart loads or changes
  useEffect(() => {
    setSelectedItems(cart.map(item => item.id))
  }, [cart.length])
  
  // Selection handlers
  const handleSelectAll = () => {
    if (selectedItems.length === cart.length) {
      setSelectedItems([]) // Deselect all
    } else {
      setSelectedItems(cart.map(item => item.id)) // Select all
    }
  }
  
  const handleSelectItem = (itemId: number) => {
    setSelectedItems(prev => {
      if (prev.includes(itemId)) {
        return prev.filter(id => id !== itemId)
      } else {
        return [...prev, itemId]
      }
    })
  }
  
  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) return
    
    if (confirm(`Bạn có chắc muốn xóa ${selectedItems.length} sản phẩm đã chọn?`)) {
      try {
        await Promise.all(selectedItems.map(id => removeFromCart(id)))
        toast.success(`Đã xóa ${selectedItems.length} sản phẩm`)
        setSelectedItems([])
      } catch (error) {
        toast.error('Có lỗi khi xóa sản phẩm')
      }
    }
  }
  
  // Calculate total for selected items only
  const getSelectedTotal = () => {
    return cart
      .filter(item => selectedItems.includes(item.id))
      .reduce((sum, item) => sum + (item.book.price * item.quantity), 0)
  }
  
  const selectedCount = selectedItems.length
  const isAllSelected = selectedItems.length === cart.length && cart.length > 0
  
  // Features:
  // - List all cart items with checkboxes
  // - "Chọn tất cả" checkbox to select/deselect all items
  // - Individual item selection
  // - Update quantity for individual items
  // - Remove single item
  // - Bulk delete selected items
  // - Total price calculation for selected items only
  // - Checkout button → /checkout (disabled if no items selected)
  // - Shows selected count in checkout button: "THANH TOÁN (X sản phẩm)"
}
```

#### CheckoutPage.tsx
```typescript
const CheckoutPage: React.FC = () => {
  const { cartItems, getTotalPrice, clearCart } = useCart()
  const [address, setAddress] = useState('')
  const [phone, setPhone] = useState('')
  
  // Flow:
  // 1. Show cart summary
  // 2. Collect shipping info
  // 3. POST /api/orders
  // 4. Clear cart
  // 5. Redirect to /orders
}
```

#### ProfilePage.tsx
```typescript
const ProfilePage: React.FC = () => {
  const { user, setUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({ full_name: '', email: '' })
  const [orders, setOrders] = useState<Order[]>([])
  
  // Features:
  // - View/Edit profile (full_name, email)
  // - Order history
  // - Toggle edit mode
}
```

### Auth Pages

#### LoginPage.tsx & RegisterPage.tsx
```typescript
// Standard login/register forms với UI design đồng bộ với AdminLoginPage
// Design Pattern:
// - Gradient background: bg-gradient-to-br from-primary to-indigo-700
// - White card: bg-white rounded-2xl shadow-2xl
// - Icon header: Icon circle (User cho login, UserCircle cho register)
// - Title và subtitle rõ ràng
// - Footer copyright
// - Use AuthContext.login() / register()
// - Use Toast notifications thay vì error state
// - Redirect on success
```

**UI Design Pattern (Đồng bộ với AdminLoginPage):**
- **Background**: Gradient từ primary đến indigo-700
- **Card**: White với rounded-2xl và shadow-2xl
- **Header**: Icon circle (16x16) với icon trắng, title (text-3xl), subtitle (text-gray-600)
- **Form**: Space-y-6 cho spacing, Input components với icon
- **Button**: Full width, size="lg"
- **Footer**: Copyright text màu trắng

#### AdminLoginPage.tsx
```typescript
// Dedicated admin login page at /admin/login
// Same UI design pattern as LoginPage/RegisterPage
// Gradient background, icon header (Lock icon)
// Link back to customer site
// Redirect to /admin on success
```

### Admin Pages

All admin management pages (Books, Banners, Admins, Customers, Orders, Categories) follow a **consistent, standardized pattern** for maintainability and user experience.

#### Admin Page Pattern

**Standardized Structure:**

1. **Layout**: Wrapped in `AdminLayout` with title prop
2. **Header**: Action button (with icon) at top right
3. **Table**: Data display with inline action buttons
4. **Modal**: Custom inline modal for forms (not Modal component)
5. **Confirmation**: `ConfirmDialog` component for delete/destructive actions

**Icon Button Actions Pattern:**

All admin tables use direct icon buttons for actions instead of dropdown menus:

```tsx
{
  key: 'actions',
  label: 'Hành Động',
  render: (item: Type) => (
    <div className="flex gap-2">
      <button
        onClick={() => handleEdit(item)}
        className="text-blue-600 hover:text-blue-800"
        title="Chỉnh sửa"
      >
        <Edit2 size={18} />
      </button>
      <button
        onClick={() => handleDelete(item)}
        className="text-red-600 hover:text-red-800"
        title="Xóa"
      >
        <Trash2 size={18} />
      </button>
    </div>
  )
}
```

**Common Action Icons:**
- **Edit**: `Edit2` icon, blue color (`text-blue-600 hover:text-blue-800`)
- **Delete**: `Trash2` icon, red color (`text-red-600 hover:text-red-800`)
- **Toggle Status**: `ToggleLeft`/`ToggleRight` icons, green color (`text-green-600 hover:text-green-800`)

**Custom Modal Structure:**

Admin pages use inline custom modals instead of the Modal component for consistency:

```tsx
{isModalOpen && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-center p-6 border-b">
        <h2 className="text-xl font-semibold">
          {editing ? 'Chỉnh Sửa' : 'Thêm Mới'}
        </h2>
        <button onClick={handleClose} className="text-gray-500 hover:text-gray-700">
          <X size={24} />
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {/* Form fields here */}
        
        {/* Buttons */}
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="outline" onClick={handleClose}>
            Hủy
          </Button>
          <Button type="submit">
            {editing ? 'Cập Nhật' : 'Thêm Mới'}
          </Button>
        </div>
      </form>
    </div>
  </div>
)}
```

**Header Button Pattern:**

```tsx
<AdminLayout title="Page Title">
  <div className="flex justify-between items-center mb-6 gap-4">
    {/* Optional: Search input (e.g., BooksManagement) */}
    <div className="flex-1 max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSearch()
            }
          }}
          placeholder="Tìm kiếm..."
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        {searchQuery && (
          <button onClick={handleClearSearch} className="absolute right-3 top-1/2 -translate-y-1/2">
            <X size={18} />
          </button>
        )}
      </div>
    </div>
    
    <Button onClick={handleAdd} icon={<Plus size={20} />}>
      Thêm Item
    </Button>
  </div>
  
  {/* Table */}
</AdminLayout>
```

**Benefits of This Pattern:**
- ✅ Consistent UI/UX across all admin pages
- ✅ Cleaner code with less component dependencies
- ✅ Better visual hierarchy
- ✅ More intuitive actions (no hidden dropdowns)
- ✅ Easier maintenance and onboarding

#### Dashboard.tsx
```typescript
const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Statistics>()
  
  // Display:
  // - Overview stat cards (revenue, orders, etc.)
  // - Recent orders table
  // - Quick actions
}
```

#### BooksManagement.tsx
```typescript
const BooksManagement: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBook, setEditingBook] = useState<Book | null>(null)
  
  const fetchBooks = async (page: number = 1, search: string = '') => {
    const data = await booksService.getBooks({ 
      page, 
      per_page: 20, 
      search: search.trim() 
    })
    // ... update state
  }
  
  // CRUD Operations:
  // - List with pagination
  // - Create (modal form)
  // - Update (modal form)
  // - Delete (confirmation)
  // - Search: Search input on same line as "Thêm Sách" button
  //   - Search by book title (case-insensitive partial match)
  //   - Search on Enter key press
  //   - Clear button (X) to reset search
  //   - Shows search status message when active
  //   - Pagination works with search query
  // - Image Upload: File upload component replaces URL input
  //   - File picker with preview
  //   - Upload to R2 bucket
  //   - Auto-populate image_url after upload
  // - Form Fields:
  //   - Description: textarea (rows=4), không giới hạn ký tự (TEXT type)
  //   - Other fields: standard input fields
}
```

**Similar patterns for:**
- CustomerManagement.tsx
- AdminManagement.tsx
- OrdersManagement.tsx
- BannerManagement.tsx

## ⚡ State Management (Contexts)

### AuthContext.tsx

```typescript
interface AuthContextType {
  user: User | null
  loading: boolean
  setUser: (user: User | null) => void
  login: (username: string, password: string) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    checkAuth() // Check on mount
  }, [])
  
  // Implementation...
}
```

**Usage:**
```tsx
const { user, login, logout } = useAuth()

if (user) {
  return <p>Welcome {user.full_name}</p>
}
```

### CartContext.tsx

```typescript
interface CartContextType {
  cartItems: CartItemWithBook[]
  addToCart: (bookId: number, quantity: number) => Promise<void>
  updateQuantity: (cartItemId: number, quantity: number) => Promise<void>
  removeFromCart: (cartItemId: number) => Promise<void>
  clearCart: () => void
  getTotalItems: () => number
  getTotalPrice: () => number
  fetchCart: () => Promise<void>
}

export const CartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [cartItems, setCartItems] = useState<CartItemWithBook[]>([])
  const { user } = useAuth()
  
  useEffect(() => {
    if (user) {
      fetchCart()
    } else {
      setCartItems([])
    }
  }, [user])
  
  // Implementation...
}
```

**Usage:**
```tsx
const { cartItems, addToCart, getTotalItems } = useCart()

<button onClick={() => addToCart(bookId, 2)}>
  Add to Cart
</button>

<CartIcon badge={getTotalItems()} />
```

## 🌐 API Service (`services/api.ts`)

```typescript
import axios, { AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Send cookies (session)
  headers: {
    'Content-Type': 'application/json',
  },
})

// Error handler
const handleError = (error: AxiosError) => {
  if (error.response) {
    const data = error.response.data
    let message = 'An error occurred'
    if (typeof data === 'string') {
      message = data
    } else if (data && typeof data === 'object') {
      message = (data as any).error || (data as any).message || message
    }
    throw new Error(message)
  }
  // ... other error types
}

// Auth Service
export const authService = {
  async login(data: LoginRequest): Promise<User> { ... },
  async register(data: RegisterRequest): Promise<User> { ... },
  async logout(): Promise<void> { ... },
  async getCurrentUser(): Promise<User> { ... },
  async updateProfile(data: UpdateProfileRequest): Promise<User> { ... },
}

// Books Service
export const booksService = {
  async getBooks(params: GetBooksParams): Promise<GetBooksResponse> { ... },
  async getBookById(id: number): Promise<Book> { ... },
  async createBook(data: BookFormData): Promise<Book> { ... },
  async updateBook(id: number, data: BookFormData): Promise<Book> { ... },
  async deleteBook(id: number): Promise<void> { ... },
}

// Cart Service
export const cartService = {
  async getCart(): Promise<CartItemWithBook[]> { ... },
  async addToCart(data: AddToCartRequest): Promise<CartItemWithBook> { ... },
  async updateCartItem(id: number, quantity: number): Promise<void> { ... },
  async removeFromCart(id: number): Promise<void> { ... },
}

// Orders Service
export const ordersService = {
  async createOrder(data: CreateOrderRequest): Promise<Order> { ... },
  async getOrders(): Promise<Order[]> { ... },
  async getOrderById(id: number): Promise<Order> { ... },
}

// Admin Service
export const adminService = {
  async getUsers(): Promise<User[]> { ... },
  async updateUserStatus(userId: number, isActive: boolean): Promise<void> { ... },
  async getStatistics(): Promise<Statistics> { ... },
  async updateOrderStatus(orderId: number, status: string): Promise<void> { ... },
}

// Banners Service
export const bannersService = {
  async getBanners(position: string): Promise<GetBannersResponse> { ... },
  async createBanner(data: BannerFormData): Promise<Banner> { ... },
  async updateBanner(id: number, data: Partial<BannerFormData>): Promise<Banner> { ... },
  async deleteBanner(id: number): Promise<void> { ... },
}
```

## 📘 TypeScript Types (`types/index.ts`)

```typescript
// User Types
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'admin' | 'customer'
  is_active: boolean
  customer_code?: string
  created_at: string
}

// Book Types
export interface Book {
  id: number
  title: string
  author: string
  category: string
  description: string
  price: number
  stock: number
  image_url?: string
  publisher?: string
  publish_date?: string
  pages?: number
  dimensions?: string
  weight?: number
  created_at: string
  updated_at: string
}

// Cart Types
export interface CartItem {
  id: number
  user_id: number
  book_id: number
  quantity: number
  created_at: string
}

export interface CartItemWithBook extends CartItem {
  book: Book
}

// Order Types
export interface Order {
  id: number
  user_id: number
  total_amount: number
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  payment_status: 'pending' | 'paid'
  shipping_address: string
  phone: string
  created_at: string
  updated_at: string
  items?: OrderItem[]
}

export interface OrderItem {
  id: number
  order_id: number
  book_id: number
  quantity: number
  price: number
  book: Book
}

// ... more types (Banner, Statistics, etc.)
```

## 🛣 Routing (`App.tsx`)

```typescript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <CartProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/book/:id" element={<BookDetailPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/orders" element={<OrdersPage />} />
              <Route path="/profile" element={
                <ProtectedRoute><ProfilePage /></ProtectedRoute>
              } />

              {/* Admin Routes */}
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/admin" element={
                <ProtectedRoute><Dashboard /></ProtectedRoute>
              } />
              <Route path="/admin/books" element={
                <ProtectedRoute><BooksManagement /></ProtectedRoute>
              } />
              {/* ... more admin routes */}

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </CartProvider>
      </AuthProvider>
    </ToastProvider>
  )
}
```

## 🎨 Styling (Tailwind CSS)

### Configuration (`tailwind.config.js`)

```javascript
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1', // Indigo
        'admin-sidebar': '#1e293b', // Slate
      },
    },
  },
  plugins: [],
}
```

### Usage Patterns

**Responsive Design:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
  {/* 1 col mobile, 3 tablet, 5 desktop */}
</div>
```

**Common Patterns:**
```tsx
// Card
<div className="bg-white rounded-lg shadow p-6">

// Button Primary
<button className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90">

// Input
<input className="border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary">

// Badge
<span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
```

## ⚡ Performance Optimizations

### Code Splitting
```typescript
// Route-based code splitting
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'))
```

### Memoization
```typescript
const MemoizedBookCard = React.memo(BookCard)
```

### Debouncing
```typescript
const debouncedSearch = useMemo(
  () => debounce((query) => searchBooks(query), 300),
  []
)
```

## 🔒 Security

### XSS Prevention
- React automatically escapes values
- Sanitize user input before rendering
- Use `dangerouslySetInnerHTML` carefully

### CSRF Protection
- Session cookies với `httpOnly=True`
- SameSite cookie attribute

### Input Validation
- Client-side validation (immediate feedback)
- Server-side validation (security)

---

## 📊 Summary

### Component Hierarchy

```
App (Router + Providers)
├── Public Pages
│   ├── PublicHeader + PublicFooter
│   └── Page Content
│       ├── UI Components (Button, Input, etc.)
│       └── Shared Components (BookCard, etc.)
└── Admin Pages
    ├── AdminLayout (Sidebar + TopBar)
    └── Page Content
        ├── UI Components (Table, Modal, etc.)
        └── Forms
```

### Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
API Service Call (axios)
    ↓
Backend REST API
    ↓
Response
    ↓
Update Local State / Context
    ↓
Re-render Components
```

### Key Patterns

✅ **Component Composition** - Reusable, composable components  
✅ **Context API** - Global state (Auth, Cart)  
✅ **Custom Hooks** - useAuth(), useCart(), useToast()  
✅ **TypeScript** - Type safety throughout  
✅ **Tailwind CSS** - Utility-first styling  
✅ **Protected Routes** - Authentication guards  
✅ **Toast Notifications** - Better UX than alerts  

---

**📌 Frontend chuẩn React best practices, TypeScript type-safe, và Tailwind modern UI!**

