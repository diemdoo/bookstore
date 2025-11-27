import React from 'react'
import { NavLink } from 'react-router-dom'
import { Home, Book, Image, Users, UserCircle, FileText, BarChart3, FolderTree } from 'lucide-react'

export const AdminSidebar: React.FC = () => {
  const navItems = [
    { path: '/admin', label: 'Trang Chủ', icon: Home },
    { path: '/admin/books', label: 'Quản Lý Sách', icon: Book },
    { path: '/admin/categories', label: 'Quản Lý Danh Mục', icon: FolderTree },
    { path: '/admin/banners', label: 'Quản Lý Banner', icon: Image },
    { path: '/admin/admins', label: 'Quản Lý Quản Trị Viên', icon: Users },
    { path: '/admin/customers', label: 'Quản Lý Khách Hàng', icon: UserCircle },
    { path: '/admin/orders', label: 'Quản Lý Hóa Đơn', icon: FileText },
    { path: '/admin/statistics', label: 'Thống Kê', icon: BarChart3 },
  ]

  return (
    <div className="w-64 bg-admin-sidebar min-h-screen fixed left-0 top-0">
      <div className="p-6">
        <h1 className="text-white text-xl font-semibold">Trang Quản Lý</h1>
      </div>
      
      <nav className="mt-6">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/admin'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors ${
                isActive ? 'bg-gray-700 text-white border-l-4 border-primary' : ''
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}

