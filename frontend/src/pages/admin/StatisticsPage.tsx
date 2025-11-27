import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { StatCard } from '../../components/shared/StatCard'
import { adminService } from '../../services/api'
import { formatPrice, getStatusText, getStatusProgressColor } from '../../utils/formatters'
import type { Statistics } from '../../types'
import { BookOpen } from 'lucide-react'

const StatisticsPage: React.FC = () => {
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
      <AdminLayout title="Thống Kê">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Đang tải...</div>
        </div>
      </AdminLayout>
    )
  }

  if (!stats) {
    return (
      <AdminLayout title="Thống Kê">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Không thể tải dữ liệu thống kê</div>
        </div>
      </AdminLayout>
    )
  }

  const totalOrdersCount = stats.total_orders || 0
  const statusEntries = Object.entries(stats.orders_by_status || {})

  return (
    <AdminLayout title="Thống Kê">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Tổng doanh thu"
          value={formatPrice(stats.total_revenue)}
        />
        <StatCard
          title="Tổng đơn hàng"
          value={stats.total_orders}
        />
        <StatCard
          title="Đơn hoàn thành"
          value={stats.completed_orders}
        />
        <StatCard
          title="Đơn đã hủy"
          value={stats.cancelled_orders}
        />
      </div>

      {/* Orders by Status Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-6">Đơn hàng theo trạng thái</h2>
        
        {statusEntries.length > 0 ? (
          <div className="space-y-4">
            {statusEntries.map(([status, count]) => {
              const percentage = totalOrdersCount > 0 ? (count / totalOrdersCount) * 100 : 0
              return (
                <div key={status}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {getStatusText(status)}
                    </span>
                    <span className="text-sm text-gray-600">
                      {count} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-8 overflow-hidden">
                    <div
                      className={`${getStatusProgressColor(status)} h-8 rounded-full flex items-center px-3 transition-all`}
                      style={{ width: `${Math.max(percentage, 5)}%` }}
                    >
                      <span className="text-white text-sm font-medium">
                        {count}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">Chưa có dữ liệu đơn hàng</p>
        )}
      </div>

      {/* Top 10 Selling Books */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-6">Top 10 Sách Bán Chạy</h2>
        
        {stats.top_books && stats.top_books.length > 0 ? (
          <div className="grid grid-cols-5 gap-6">
            {stats.top_books.map((book, index) => (
              <div key={book.id} className="relative">
                {/* Ranking badge */}
                <div className="absolute -top-2 -left-2 z-10">
                  <span
                    className={`
                      inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold shadow-lg
                      ${index === 0 ? 'bg-yellow-400 text-yellow-900' : ''}
                      ${index === 1 ? 'bg-gray-300 text-gray-800' : ''}
                      ${index === 2 ? 'bg-orange-400 text-orange-900' : ''}
                      ${index > 2 ? 'bg-blue-100 text-blue-800' : ''}
                    `}
                  >
                    #{index + 1}
                  </span>
                </div>
                
                {/* Book card */}
                <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                  <div className="aspect-[3/4] mb-3 bg-gray-100 rounded overflow-hidden relative">
                    {book.image_url ? (
                      <img
                        src={book.image_url}
                        alt={book.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                          const placeholder = target.nextElementSibling as HTMLElement
                          if (placeholder) {
                            placeholder.style.display = 'flex'
                          }
                        }}
                      />
                    ) : null}
                    <div 
                      className={`w-full h-full flex items-center justify-center ${book.image_url ? 'hidden' : ''}`}
                    >
                      <BookOpen className="h-12 w-12 text-gray-400" />
                    </div>
                  </div>
                  <h3 className="font-medium text-sm line-clamp-2 mb-2 min-h-[40px]">
                    {book.title}
                  </h3>
                  <p className="text-xs text-gray-600 mb-3 truncate">{book.author}</p>
                  <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-center">
                    <span className="text-sm font-bold">{book.total_sold}</span>
                    <span className="text-xs ml-1">đã bán</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">Chưa có dữ liệu sách bán chạy</p>
        )}
      </div>
    </AdminLayout>
  )
}

export default StatisticsPage

