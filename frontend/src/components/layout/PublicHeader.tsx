import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, ShoppingCart, User, BookOpen } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useCart } from '../../contexts/CartContext'
import { CategoryMenu } from '../shared/CategoryMenu'

export const PublicHeader: React.FC = () => {
  const { user, logout } = useAuth()
  const { getTotalItems } = useCart()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = React.useState(false)
  const [searchQuery, setSearchQuery] = React.useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <header className="bg-primary text-white sticky top-0 z-50 shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-2xl font-semibold whitespace-nowrap">
            <BookOpen className="h-8 w-8" />
            <span className="hidden sm:inline">BookStore</span>
          </Link>

          {/* Category Menu */}
          <CategoryMenu />

          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm Sách"
                className="w-full pl-10 pr-4 py-2 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-white"
              />
            </div>
          </form>

          {/* Navigation */}
          <div className="flex items-center gap-6">
            {/* Cart */}
            <Link to="/cart" className="hover:text-gray-200 transition-colors relative">
              <ShoppingCart className="h-6 w-6" />
              {getTotalItems() > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {getTotalItems()}
                </span>
              )}
              <span className="sr-only">Giỏ Hàng</span>
            </Link>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="hover:text-gray-200 transition-colors flex items-center gap-2"
              >
                <User className="h-6 w-6" />
                <span>{user ? user.full_name : 'Tài Khoản'}</span>
              </button>

              {showUserMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-20 py-2">
                    {user ? (
                      <>
                        {user.role === 'admin' && (
                          <Link
                            to="/admin"
                            className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                            onClick={() => setShowUserMenu(false)}
                          >
                            Quản trị
                          </Link>
                        )}
                        {user.role === 'customer' && (
                          <Link
                            to="/profile"
                            className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                            onClick={() => setShowUserMenu(false)}
                          >
                            Thông tin cá nhân
                          </Link>
                        )}
                        <Link
                          to="/orders"
                          className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                          onClick={() => setShowUserMenu(false)}
                        >
                          Đơn hàng của tôi
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50"
                        >
                          Đăng xuất
                        </button>
                      </>
                    ) : (
                      <>
                        <Link
                          to="/login"
                          className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                          onClick={() => setShowUserMenu(false)}
                        >
                          Đăng nhập
                        </Link>
                        <Link
                          to="/register"
                          className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                          onClick={() => setShowUserMenu(false)}
                        >
                          Đăng ký
                        </Link>
                      </>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

