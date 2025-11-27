/**
 * Utility functions for formatting data
 */

/**
 * Format price to Vietnamese currency
 */
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}

/**
 * Get Vietnamese text for order status
 */
export const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'Chờ xác nhận',
    confirmed: 'Đã xác nhận',
    completed: 'Hoàn thành',
    cancelled: 'Đã hủy',
  }
  return statusMap[status] || status
}

/**
 * Get Tailwind CSS classes for order status badge
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return colorMap[status] || 'bg-gray-100 text-gray-800'
}

/**
 * Get status badge component with consistent styling
 */
export const getStatusBadge = (status: string, size: 'sm' | 'md' = 'md'): string => {
  const sizeClasses = size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm'
  const colorClasses = getStatusColor(status)
  return `${sizeClasses} rounded-full font-medium ${colorClasses}`
}

/**
 * Get Tailwind CSS classes for order status progress bars (darker colors for progress bars)
 */
export const getStatusProgressColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: 'bg-yellow-500',
    confirmed: 'bg-blue-500',
    completed: 'bg-green-500',
    cancelled: 'bg-red-500',
  }
  return colorMap[status] || 'bg-gray-500'
}

