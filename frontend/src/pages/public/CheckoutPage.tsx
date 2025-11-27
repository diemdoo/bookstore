import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useCart } from '../../contexts/CartContext'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../components/ui/Toast'
import { ordersService } from '../../services/api'
import { formatPrice } from '../../utils/formatters'
import { Banknote } from 'lucide-react'

const CheckoutPage: React.FC = () => {
  const { cart, getTotalAmount } = useCart()
  const { user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  
  const [shippingAddress, setShippingAddress] = useState({
    fullName: user?.full_name || '',
    email: user?.email || '',
    phone: '',
    country: 'Việt Nam',
    province: '',
    district: '',
    ward: '',
    address: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const fullAddress = `${shippingAddress.address}, ${shippingAddress.ward}, ${shippingAddress.district}, ${shippingAddress.province}, ${shippingAddress.country}`
    
    setLoading(true)
    try {
      await ordersService.createOrder({ shipping_address: fullAddress })
      // Backend already clears cart in transaction, just refresh cart state
      // This avoids race condition where frontend tries to delete already-deleted items
      toast.success('Đơn hàng đã được đặt thành công! Bạn sẽ thanh toán khi nhận hàng.')
      navigate('/orders')
    } catch (error) {
      console.error('Failed to create order:', error)
      toast.error('Lỗi khi đặt hàng. Vui lòng thử lại.')
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    navigate('/login')
    return null
  }

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-16 flex-1 text-center">
          <p className="text-xl text-gray-600 mb-4">Giỏ hàng trống</p>
          <Button onClick={() => navigate('/')}>Tiếp tục mua sắm</Button>
        </main>
        <PublicFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Shipping Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Shipping Address */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold mb-4">ĐỊA CHỈ GIAO HÀNG</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Họ và tên người nhận"
                    value={shippingAddress.fullName}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, fullName: e.target.value })}
                    required
                  />
                  <Input
                    label="Email"
                    type="email"
                    value={shippingAddress.email}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, email: e.target.value })}
                    required
                  />
                  <Input
                    label="Số điện thoại"
                    value={shippingAddress.phone}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, phone: e.target.value })}
                    placeholder="Ví dụ: 0979123xxx (10 chữ số)"
                    required
                  />
                  <Input
                    label="Quốc gia"
                    value={shippingAddress.country}
                    disabled
                  />
                  <Input
                    label="Tỉnh/Thành phố"
                    value={shippingAddress.province}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, province: e.target.value })}
                    placeholder="Chọn tỉnh/thành phố"
                    required
                  />
                  <Input
                    label="Quận/Huyện"
                    value={shippingAddress.district}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, district: e.target.value })}
                    placeholder="Chọn quận/huyện"
                    required
                  />
                  <Input
                    label="Phường/Xã"
                    value={shippingAddress.ward}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, ward: e.target.value })}
                    placeholder="Chọn phường/xã"
                    required
                  />
                  <Input
                    label="Địa chỉ nhận hàng"
                    value={shippingAddress.address}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, address: e.target.value })}
                    placeholder="Nhập địa chỉ giao hàng"
                    className="md:col-span-2"
                    required
                  />
                </div>
              </div>

              {/* Payment Method */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold mb-4">PHƯƠNG THỨC THANH TOÁN</h2>
                <div className="border-2 border-primary rounded-lg p-4 flex items-center gap-3">
                  <Banknote className="h-8 w-8 text-primary" />
                  <div>
                    <p className="font-medium">Thanh toán bằng tiền mặt khi nhận hàng</p>
                    <p className="text-sm text-gray-600">Thanh toán khi nhận hàng (COD)</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white p-6 rounded-lg shadow sticky top-4 space-y-6">
                <h2 className="text-lg font-semibold">KIỂM TRA LẠI ĐƠN HÀNG</h2>
                
                <div className="space-y-3">
                  {cart.map((item) => (
                    <div key={item.id} className="flex gap-3">
                      <img
                        src={item.book.image_url || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='}
                        alt={item.book.title}
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='
                        }}
                        className="w-16 h-20 object-cover rounded"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium line-clamp-2">{item.book.title}</p>
                        <p className="text-sm text-gray-600">SL: {item.quantity}</p>
                        <p className="text-sm font-semibold text-primary">
                          {formatPrice(item.book.price * item.quantity)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Thành tiền</span>
                    <span>{formatPrice(getTotalAmount())}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Phí vận chuyển (Giao hàng tiêu chuẩn)</span>
                    <span>{formatPrice(0)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold pt-2 border-t">
                    <span>Tổng tiền (gồm VAT)</span>
                    <span className="text-primary">{formatPrice(getTotalAmount())}</span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => navigate('/cart')}
                    className="flex-1"
                  >
                    Quay về đơn hàng
                  </Button>
                  <Button
                    type="submit"
                    loading={loading}
                    className="flex-1"
                  >
                    XÁC NHẬN THANH TOÁN
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </main>

      <PublicFooter />
    </div>
  )
}

export default CheckoutPage

