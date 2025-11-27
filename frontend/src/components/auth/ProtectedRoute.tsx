import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
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

  // If not authenticated, redirect to admin login
  if (!user) {
    return <Navigate to="/admin/login" replace />
  }

  // Check if user has admin role (admin routes only)
  if (user.role !== 'admin') {
    return <Navigate to="/" replace />
  }

  // User is authenticated and has admin role, render the protected content
  return <>{children}</>
}

