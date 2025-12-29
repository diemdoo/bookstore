import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import { ToastProvider } from './components/ui/Toast'

// Public Pages
import HomePage from './pages/public/HomePage'
import BooksPage from './pages/public/BooksPage'
import CategoryPage from './pages/public/CategoryPage'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import BookDetailPage from './pages/public/BookDetailPage'
import CartPage from './pages/public/CartPage'
import CheckoutPage from './pages/public/CheckoutPage'
import OrdersPage from './pages/public/OrdersPage'
import ProfilePage from './pages/public/ProfilePage'

// Admin Pages
import AdminLoginPage from './pages/auth/AdminLoginPage'
import AdminDashboard from './pages/admin/Dashboard'
import BooksManagement from './pages/admin/BooksManagement'
import CategoryManagement from './pages/admin/CategoryManagement'
import BannerManagement from './pages/admin/BannerManagement'
import AdminManagement from './pages/admin/AdminManagement'
import CustomerManagement from './pages/admin/CustomerManagement'
import OrdersManagement from './pages/admin/OrdersManagement'
import StatisticsPage from './pages/admin/StatisticsPage'

// Auth Components
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { CustomerRoute } from './components/auth/CustomerRoute'

// Shared Components
import { Chatbot } from './components/shared/Chatbot'

// Component to conditionally render Chatbot
const ConditionalChatbot = () => {
  const location = useLocation()
  const isAdminPage = location.pathname.startsWith('/admin')
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'
  return !isAdminPage && !isAuthPage ? <Chatbot /> : null
}

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <CartProvider>
          <Router>
            <ConditionalChatbot />
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/books" element={<BooksPage />} />
            <Route path="/category/:slug" element={<CategoryPage />} />
            <Route path="/category/:slug/books/:bookSlug" element={<BookDetailPage />} />
            <Route path="/books/:bookSlug" element={<BookDetailPage />} />
            <Route path="/login" element={<CustomerRoute><LoginPage /></CustomerRoute>} />
            <Route path="/register" element={<CustomerRoute><RegisterPage /></CustomerRoute>} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/profile" element={<ProfilePage />} />

            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/books" element={<ProtectedRoute><BooksManagement /></ProtectedRoute>} />
            <Route path="/admin/categories" element={<ProtectedRoute><CategoryManagement /></ProtectedRoute>} />
            <Route path="/admin/banners" element={<ProtectedRoute><BannerManagement /></ProtectedRoute>} />
            <Route path="/admin/admins" element={<ProtectedRoute><AdminManagement /></ProtectedRoute>} />
            <Route path="/admin/customers" element={<ProtectedRoute><CustomerManagement /></ProtectedRoute>} />
            <Route path="/admin/orders" element={<ProtectedRoute><OrdersManagement /></ProtectedRoute>} />
            <Route path="/admin/statistics" element={<ProtectedRoute><StatisticsPage /></ProtectedRoute>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </CartProvider>
    </AuthProvider>
    </ToastProvider>
  )
}

export default App
