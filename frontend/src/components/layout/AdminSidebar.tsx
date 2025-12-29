import React from 'react'
import { NavLink } from 'react-router-dom'
import { Home, Book, Image, Users, UserCircle, FileText, BarChart3, FolderTree, ChevronLeft, ChevronRight } from 'lucide-react'
import { useSidebar } from '../../contexts/SidebarContext'
import { useAuth } from '../../contexts/AuthContext'

export const AdminSidebar: React.FC = () => {
  const { isCollapsed, toggleSidebar } = useSidebar()
  const { user } = useAuth()
  
  const allNavItems = [
    { path: '/admin', label: 'Trang Chủ', icon: Home },
    { path: '/admin/books', label: 'Quản Lý Sách', icon: Book },
    { path: '/admin/categories', label: 'Quản Lý Danh Mục', icon: FolderTree },
    { path: '/admin/banners', label: 'Quản Lý Banner', icon: Image },
    { path: '/admin/admins', label: 'Quản Lý Quản Trị Viên', icon: Users, adminOnly: true },
    { path: '/admin/customers', label: 'Quản Lý Khách Hàng', icon: UserCircle, moderatorOnly: true },
    { path: '/admin/orders', label: 'Quản Lý Hóa Đơn', icon: FileText, moderatorOnly: true },
    { path: '/admin/statistics', label: 'Thống Kê', icon: BarChart3, moderatorOnly: true },
  ]
  
  // Filter nav items: 
  // - moderator và editor không thấy menu "Quản Lý Quản Trị Viên"
  // - editor không thấy "Quản Lý Hóa Đơn", "Quản Lý Khách Hàng" và "Thống Kê"
  const navItems = allNavItems.filter(item => {
    if (item.adminOnly && (user?.role === 'moderator' || user?.role === 'editor')) {
      return false
    }
    if (item.moderatorOnly && user?.role === 'editor') {
      return false
    }
    return true
  })

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-64'} bg-admin-sidebar min-h-screen fixed left-0 top-0 transition-all duration-300 z-20`}>
      {/* Header */}
      <div className={`p-6 ${isCollapsed ? 'px-4' : ''}`}>
        {!isCollapsed && (
          <h1 className="text-white text-xl font-semibold whitespace-nowrap">Trang Quản Lý</h1>
        )}
      </div>
      
      {/* Toggle Button */}
      <div className="px-4 mb-4">
        <button
          onClick={toggleSidebar}
          className="w-full flex items-center justify-center p-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-lg transition-colors"
          aria-label={isCollapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>
      
      {/* Navigation */}
      <nav className="mt-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/admin'}
            className={({ isActive }) =>
              `flex items-center ${isCollapsed ? 'justify-center px-0' : 'gap-3 px-6'} py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors ${
                isActive ? 'bg-gray-700 text-white border-l-4 border-primary' : ''
              }`
            }
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {!isCollapsed && (
              <span className="whitespace-nowrap">{item.label}</span>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}

