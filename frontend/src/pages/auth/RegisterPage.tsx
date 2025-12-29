import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Lock, Mail, UserCircle, ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../components/ui/Toast'

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()

  const validatePassword = (password: string): string | null => {
    if (password.length < 8) {
      return 'Mật khẩu phải có ít nhất 8 ký tự'
    }
    
    const hasLower = /[a-z]/.test(password)
    const hasUpper = /[A-Z]/.test(password)
    const hasDigit = /[0-9]/.test(password)
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
    
    if (!hasLower) {
      return 'Mật khẩu phải có ít nhất 1 chữ cái thường'
    }
    if (!hasUpper) {
      return 'Mật khẩu phải có ít nhất 1 chữ cái in hoa'
    }
    if (!hasDigit) {
      return 'Mật khẩu phải có ít nhất 1 chữ số'
    }
    if (!hasSpecial) {
      return 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt'
    }
    
    return null
  }

  // Check password requirements for UI display
  const getPasswordRequirements = () => {
    const password = formData.password
    return {
      minLength: password.length >= 8,
      hasLower: /[a-z]/.test(password),
      hasUpper: /[A-Z]/.test(password),
      hasDigit: /[0-9]/.test(password),
      hasSpecial: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password),
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      toast.error('Mật khẩu xác nhận không khớp')
      return
    }

    const passwordError = validatePassword(formData.password)
    if (passwordError) {
      toast.error(passwordError)
      return
    }

    setLoading(true)

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      })
      toast.success('Đăng ký thành công!')
      navigate('/')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Đăng ký thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-indigo-700 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Back to Home Link */}
        <div className="mb-6">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Trở về trang chủ
          </Link>
        </div>

        {/* Register Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-3">
              <UserCircle className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Đăng Ký Tài Khoản</h1>
            <p className="text-sm text-gray-500 mt-1">Tạo tài khoản mới để mua sắm</p>
          </div>

          {/* Register Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Họ và tên"
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              placeholder="Nhập họ và tên"
              icon={<UserCircle className="h-5 w-5 text-gray-400" />}
              required
            />

            <Input
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Nhập email"
              icon={<Mail className="h-5 w-5 text-gray-400" />}
              required
            />

            <Input
              label="Tên đăng nhập (Username)"
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="Nhập tên đăng nhập"
              icon={<User className="h-5 w-5 text-gray-400" />}
              required
            />

            <div>
              <Input
                label="Mật khẩu"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Nhập mật khẩu"
                icon={<Lock className="h-5 w-5 text-gray-400" />}
                required
              />
              {/* Password Requirements */}
              <div className="mt-1.5">
                <p className="text-xs text-gray-500 mb-1.5">Yêu cầu mật khẩu:</p>
                <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
                  <div className={getPasswordRequirements().minLength ? 'text-green-600' : 'text-gray-400'}>
                    {getPasswordRequirements().minLength ? '✓' : '•'} Tối thiểu 8 ký tự
                  </div>
                  <div className={getPasswordRequirements().hasLower ? 'text-green-600' : 'text-gray-400'}>
                    {getPasswordRequirements().hasLower ? '✓' : '•'} 1 chữ cái thường
                  </div>
                  <div className={getPasswordRequirements().hasUpper ? 'text-green-600' : 'text-gray-400'}>
                    {getPasswordRequirements().hasUpper ? '✓' : '•'} 1 chữ cái in hoa
                  </div>
                  <div className={getPasswordRequirements().hasDigit ? 'text-green-600' : 'text-gray-400'}>
                    {getPasswordRequirements().hasDigit ? '✓' : '•'} 1 chữ số
                  </div>
                  <div className={`${getPasswordRequirements().hasSpecial ? 'text-green-600' : 'text-gray-400'} col-span-2`}>
                    {getPasswordRequirements().hasSpecial ? '✓' : '•'} 1 ký tự đặc biệt
                  </div>
                </div>
              </div>
            </div>

            <Input
              label="Xác nhận mật khẩu"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              placeholder="Nhập lại mật khẩu"
              icon={<Lock className="h-5 w-5 text-gray-400" />}
              required
            />

            <Button
              type="submit"
              className="w-full"
              loading={loading}
              size="lg"
            >
              Đăng Ký
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-600">
            Đã có tài khoản?{' '}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Đăng nhập
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-white text-sm mt-6">
          © 2024 Bookstore. All rights reserved.
        </p>
      </div>
    </div>
  )
}

export default RegisterPage

