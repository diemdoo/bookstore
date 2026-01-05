import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../components/ui/Toast'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Lock, User, ArrowLeft } from 'lucide-react'

const AdminLoginPage: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { adminLogin, user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()

  // Redirect customer users away from admin login
  useEffect(() => {
    if (!authLoading && user && user.role === 'customer') {
      navigate('/')
    }
  }, [user, authLoading, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!username || !password) {
      toast.error('Vui lòng nhập đầy đủ thông tin')
      return
    }

    setLoading(true)
    try {
      await adminLogin(username, password)
      toast.success('Đăng nhập thành công!')
      navigate('/admin')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Đăng nhập thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-indigo-700 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Back to Customer Site Link */}
        <div className="mb-6">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Về Trang Khách Hàng
          </Link>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Lock className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Quản Trị Viên</h1>
            <p className="text-gray-600 mt-2">Đăng nhập hệ thống quản lý</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Tên Đăng Nhập"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên đăng nhập"
              icon={<User className="h-5 w-5 text-gray-400" />}
              required
            />

            <Input
              label="Mật Khẩu"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              icon={<Lock className="h-5 w-5 text-gray-400" />}
              required
            />

            <Button
              type="submit"
              className="w-full"
              loading={loading}
              size="lg"
            >
              Đăng Nhập
            </Button>
          </form>

          {/* Info */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800 text-center">
               Trang dành riêng cho quản trị viên
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-white text-sm mt-6">
          © 2024 Bookstore. All rights reserved.
        </p>
      </div>
    </div>
  )
}

export default AdminLoginPage

