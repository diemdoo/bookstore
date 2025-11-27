import React from 'react'
import type { Order } from '../../types'
import { formatPrice, getStatusText, getStatusBadge } from '../../utils/formatters'

interface OrderCardProps {
  order: Order
  showFullDetails?: boolean
}

const placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='

export const OrderCard: React.FC<OrderCardProps> = ({ order, showFullDetails = true }) => {
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.src = placeholderImage
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm text-gray-600">Mã đơn hàng: #{order.id}</p>
          <p className="text-sm text-gray-600">
            Ngày đặt: {new Date(order.created_at).toLocaleDateString('vi-VN')}
          </p>
        </div>
        <div className="flex gap-2">
          {/* Payment Method Badge */}
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            COD
          </span>
          {/* Order Status Badge */}
          <span className={getStatusBadge(order.status, 'md')}>
            {getStatusText(order.status)}
          </span>
        </div>
      </div>

      {showFullDetails && (
        <>
          <div className="border-t pt-4">
            {order.items && order.items.map((item) => (
              <div key={item.id} className="flex gap-4 mb-3">
                <img
                  src={item.book.image_url || placeholderImage}
                  alt={item.book.title}
                  onError={handleImageError}
                  className="w-16 h-20 object-cover rounded"
                />
                <div className="flex-1">
                  <p className="font-medium">{item.book.title}</p>
                  <p className="text-sm text-gray-600">Số lượng: {item.quantity}</p>
                  <p className="text-sm font-semibold text-primary">
                    {formatPrice(item.price)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-4 flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Địa chỉ: {order.shipping_address}
            </p>
            <p className="text-lg font-bold text-primary">
              Tổng: {formatPrice(order.total_amount)}
            </p>
          </div>
        </>
      )}
    </div>
  )
}

