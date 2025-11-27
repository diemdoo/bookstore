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

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
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
  image_url: string
  publisher?: string
  publish_date?: string
  distributor?: string
  dimensions?: string
  pages?: number
  weight?: number
  created_at: string
  updated_at: string
}

export interface BookFormData {
  title: string
  author: string
  category: string
  description: string
  price: number
  stock: number
  image_url: string
  publisher?: string
  publish_date?: string
  distributor?: string
  dimensions?: string
  pages?: number
  weight?: number
}

// Cart Types
export interface CartItem {
  id: number
  user_id: number
  book_id: number
  book: Book
  quantity: number
  created_at: string
}

export interface AddToCartRequest {
  book_id: number
  quantity: number
}

// Order Types
export interface Order {
  id: number
  user_id: number
  total_amount: number
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  payment_status: 'pending' | 'paid'
  shipping_address: string
  created_at: string
  updated_at: string
  items: OrderItem[]
  customer_code?: string
  customer_username?: string
  customer_full_name?: string
}

export interface OrderItem {
  id: number
  order_id: number
  book_id: number
  book: Book
  quantity: number
  price: number
}

export interface CreateOrderRequest {
  shipping_address: string
}

// Statistics Types
export interface TopBook {
  id: number
  title: string
  author: string
  image_url?: string
  total_sold: number
}

export interface Statistics {
  total_revenue: number
  total_orders: number
  pending_orders: number
  confirmed_orders: number
  completed_orders: number
  cancelled_orders: number
  orders_by_status: Record<string, number>
  top_books: TopBook[]
}

// API Response Types
export interface ApiResponse<T> {
  message?: string
  data?: T
  error?: string
}

export interface PaginatedResponse<T> {
  books: T[]  // Backend returns 'books' not 'items'
  total: number
  page: number
  per_page: number
  pages: number
}

// Banner Types
export interface Banner {
  id: number
  title: string
  description?: string
  image_url: string
  link?: string
  bg_color: string
  text_color: string
  position: 'main' | 'side_top' | 'side_bottom'
  display_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BannerFormData {
  title: string
  description?: string
  image_url: string
  link?: string
  bg_color?: string
  text_color?: string
  position?: 'main' | 'side_top' | 'side_bottom'
  display_order?: number
  is_active?: boolean
}

// Category Types
export interface Category {
  id?: number
  key: string
  name: string
  description?: string
  display_order?: number
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

// Auth Context Types
export interface AuthContextType {
  user: User | null
  loading: boolean
  setUser: (user: User | null) => void
  login: (username: string, password: string) => Promise<User>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

// Cart Context Types
export interface CartContextType {
  cart: CartItem[]
  loading: boolean
  addToCart: (bookId: number, quantity: number) => Promise<void>
  updateCartItem: (cartItemId: number, quantity: number) => Promise<void>
  removeFromCart: (cartItemId: number) => Promise<void>
  clearCart: () => Promise<void>
  refreshCart: () => Promise<void>
  getTotalAmount: () => number
  getTotalItems: () => number
}

