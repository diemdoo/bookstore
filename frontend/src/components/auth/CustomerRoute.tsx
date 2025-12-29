import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

interface CustomerRouteProps {
  children: React.ReactNode
}

/**
 * Route guard để đảm bảo chỉ customer mới có thể truy cập
 * Nếu admin đã đăng nhập, redirect về /admin
 */
export const CustomerRoute: React.FC<CustomerRouteProps> = ({ children }) => {
  const { user, loading } = useAuth()

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải...</p>
        </div>
      </div>
    )
  }

  // If admin is logged in, redirect to admin dashboard
  if (user && user.role === 'admin') {
    return <Navigate to="/admin" replace />
  }

  // Customer or not logged in, allow access
  return <>{children}</>
}
