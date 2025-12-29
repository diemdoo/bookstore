import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { StatCard } from '../../components/shared/StatCard'
import { adminService } from '../../services/api'
import type { Statistics } from '../../types'
import { useAuth } from '../../contexts/AuthContext'

const Dashboard: React.FC = () => {
  const { user: currentUser } = useAuth()
  const [stats, setStats] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Editor không có quyền xem thống kê
    if (currentUser?.role === 'editor') {
      setLoading(false)
      return
    }

    const fetchStatistics = async () => {
      try {
        const data = await adminService.getStatistics()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStatistics()
  }, [currentUser])

  // Editor không có quyền xem thống kê
  if (currentUser?.role === 'editor') {
    return (
      <AdminLayout title="Trang Chủ">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Chào mừng, {currentUser.full_name || currentUser.username}!</h2>
          <p className="text-gray-600 mb-6">
            Bạn có quyền quản lý các module sau:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">📚 Quản Lý Sách</h3>
              <p className="text-sm text-blue-700">Thêm, sửa, xóa sách</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-900 mb-2">📁 Quản Lý Danh Mục</h3>
              <p className="text-sm text-green-700">Quản lý danh mục sách</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="font-semibold text-purple-900 mb-2">🖼️ Quản Lý Banner</h3>
              <p className="text-sm text-purple-700">Quản lý banner quảng cáo</p>
            </div>
          </div>
        </div>
      </AdminLayout>
    )
  }

  if (loading) {
    return (
      <AdminLayout title="Trang Chủ">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Đang tải...</div>
        </div>
      </AdminLayout>
    )
  }

  return (
    <AdminLayout title="Trang Chủ">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Tổng doanh thu"
          value={stats?.total_revenue.toLocaleString('vi-VN') || '0'}
        />
        <StatCard
          title="Tổng số đơn hàng"
          value={stats?.total_orders || 0}
        />
        <StatCard
          title="Đơn chờ xác nhận"
          value={stats?.pending_orders || 0}
        />
        <StatCard
          title="Đơn đã xác nhận"
          value={stats?.confirmed_orders || 0}
        />
        <StatCard
          title="Đơn hoàn thành"
          value={stats?.completed_orders || 0}
        />
        <StatCard
          title="Đơn đã hủy"
          value={stats?.cancelled_orders || 0}
        />
      </div>
    </AdminLayout>
  )
}

export default Dashboard

