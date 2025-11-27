import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { StatCard } from '../../components/shared/StatCard'
import { adminService } from '../../services/api'
import type { Statistics } from '../../types'

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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
  }, [])

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

