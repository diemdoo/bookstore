import React from 'react'
import { User } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { useSidebar } from '../../contexts/SidebarContext'

interface AdminTopBarProps {
  title: string
}

export const AdminTopBar: React.FC<AdminTopBarProps> = ({ title }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { isCollapsed } = useSidebar()
  const [showMenu, setShowMenu] = React.useState(false)
  const leftMargin = isCollapsed ? 'left-16' : 'left-64'

  const handleLogout = async () => {
    await logout()
    navigate('/admin/login')
  }

  return (
    <div className={`h-16 bg-white border-b border-gray-200 fixed top-0 right-0 ${leftMargin} z-10 transition-all duration-300`}>
      <div className="h-full px-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        
        <div className="flex items-center gap-4">
          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg"
            >
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {user?.full_name || 'Baka'}
              </span>
            </button>
            
            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-20">
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 rounded-lg text-gray-700"
                  >
                    Đăng xuất
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

