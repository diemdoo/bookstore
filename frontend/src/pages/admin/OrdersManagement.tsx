import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Table } from '../../components/ui/Table'
import { adminService } from '../../services/api'
import { useToast } from '../../components/ui/Toast'
import { getStatusText, getStatusBadge } from '../../utils/formatters'
import { Edit2, X } from 'lucide-react'
import type { Order } from '../../types'

const OrdersManagement: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOrder, setEditingOrder] = useState<Order | null>(null)
  const [formData, setFormData] = useState({
    status: 'pending',
    payment_status: 'pending'
  })
  const toast = useToast()

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await adminService.getAllOrders()
      setOrders(data)
    } catch (error) {
      console.error('Failed to fetch orders:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
  }, [])

  const handleEdit = (order: Order) => {
    setEditingOrder(order)
    setFormData({
      status: order.status,
      payment_status: order.payment_status
    })
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingOrder(null)
    setFormData({
      status: 'pending',
      payment_status: 'pending'
    })
  }

  const handleSubmit = async () => {
    if (!editingOrder) return

    try {
      setLoading(true)
      await adminService.updateOrderStatus(editingOrder.id, formData)
      toast.success('Đã cập nhật trạng thái đơn hàng')
      await fetchOrders()
      handleCloseModal()
    } catch (error) {
      console.error('Failed to update order status:', error)
      toast.error('Lỗi khi cập nhật trạng thái')
    } finally {
      setLoading(false)
    }
  }

  const renderStatusBadge = (status: string) => {
    return (
      <span className={getStatusBadge(status, 'sm')}>
        {getStatusText(status)}
      </span>
    )
  }

  const columns = [
    {
      key: 'invoice_code',
      label: 'Mã Hóa Đơn',
      render: (order: Order) => `HD${order.id.toString().padStart(6, '0')}`,
    },
    {
      key: 'customer',
      label: 'Khách Hàng',
      render: (order: Order) => {
        if (order.customer_code) {
          return `${order.customer_code} - ${order.customer_full_name || order.customer_username || `User ${order.user_id}`}`
        }
        return order.customer_full_name || order.customer_username || `User ${order.user_id}`
      },
    },
    {
      key: 'total_amount',
      label: 'Tổng Tiền',
      render: (order: Order) => `${order.total_amount.toLocaleString('vi-VN')} đ`,
    },
    {
      key: 'created_at',
      label: 'Ngày Lập',
      render: (order: Order) => new Date(order.created_at).toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }),
    },
    {
      key: 'status',
      label: 'Tình Trạng',
      render: (order: Order) => renderStatusBadge(order.status),
    },
    {
      key: 'actions',
      label: 'Hành Động',
      render: (order: Order) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleEdit(order)}
            className="text-blue-600 hover:text-blue-800"
            title="Sửa trạng thái"
          >
            <Edit2 size={18} />
          </button>
        </div>
      )
    }
  ]

  return (
    <AdminLayout title="Quản Lý Hóa Đơn">
      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <Table columns={columns} data={orders} />
      )}

      {/* Edit Status Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold">Cập Nhật Trạng Thái Đơn Hàng</h2>
              <button onClick={handleCloseModal} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Trạng Thái Đơn Hàng
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="pending">Chờ xác nhận</option>
              <option value="confirmed">Đã xác nhận</option>
              <option value="completed">Hoàn thành</option>
              <option value="cancelled">Đã hủy</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Trạng Thái Thanh Toán
            </label>
            <select
              value={formData.payment_status}
              onChange={(e) => setFormData({ ...formData, payment_status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="pending">Chưa thanh toán</option>
              <option value="paid">Đã thanh toán</option>
            </select>
          </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={handleCloseModal}>
                  Hủy
                </Button>
                <Button type="button" onClick={handleSubmit}>
                  Cập Nhật
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  )
}

export default OrdersManagement

