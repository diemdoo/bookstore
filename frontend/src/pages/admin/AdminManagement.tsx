import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Table, Pagination } from '../../components/ui/Table'
import { adminService } from '../../services/api'
import { Plus, Edit2, ToggleLeft, ToggleRight, X } from 'lucide-react'
import type { User } from '../../types'
import { useToast } from '../../components/ui/Toast'
import { useAuth } from '../../contexts/AuthContext'

interface AdminFormData {
  username: string
  password: string
  email: string
  full_name: string
  role: 'admin' | 'moderator' | 'editor'
}

const AdminManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; userId: number | null; userName: string }>({
    isOpen: false,
    userId: null,
    userName: ''
  })
  const [toggleConfirm, setToggleConfirm] = useState<{ isOpen: boolean; userId: number | null; userName: string; currentStatus: boolean }>({
    isOpen: false,
    userId: null,
    userName: '',
    currentStatus: true
  })
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const itemsPerPage = 20
  const [formData, setFormData] = useState<AdminFormData>({
    username: '',
    password: '',
    email: '',
    full_name: '',
    role: 'moderator',
  })
  const toast = useToast()
  const { user: currentUser } = useAuth()

  // Check if user is moderator or editor (not allowed to manage admins)
  if (currentUser?.role === 'moderator' || currentUser?.role === 'editor') {
    return (
      <AdminLayout title="Quản Lý Quản Trị Viên">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Không có quyền truy cập</h2>
          <p className="text-gray-600">Chỉ Super Admin mới có quyền quản lý quản trị viên.</p>
        </div>
      </AdminLayout>
    )
  }

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await adminService.getUsers()
      // getUsers() without role parameter returns admin/moderator/editor users
      // Data is now paginated response: { users, total, page, per_page, pages }
      const adminUsers = data.users || []
      setUsers(adminUsers)
      setTotalPages(Math.ceil(adminUsers.length / itemsPerPage))
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const paginatedUsers = users.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user)
      setFormData({
        username: user.username,
        password: '', // Don't show password
        email: user.email,
        full_name: user.full_name || '',
        role: (user.role === 'admin' || user.role === 'moderator') ? user.role : 'moderator',
      })
    } else {
      setEditingUser(null)
      setFormData({
        username: '',
        password: '',
        email: '',
        full_name: '',
        role: 'moderator',
      })
    }
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingUser(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      
      if (editingUser) {
        // Update existing admin/moderator account
        const updateData: {
          email: string
          full_name: string
          role: 'admin' | 'moderator'
          password?: string
        } = {
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
        }
        
        // Only include password if it was provided
        if (formData.password && formData.password.trim() !== '') {
          updateData.password = formData.password
        }
        
        await adminService.updateUser(editingUser.id, updateData)
        toast.success('Đã cập nhật thông tin thành công!')
      } else {
        // Create new admin/moderator account
        await adminService.createAdminUser({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
        })
        toast.success(`Đã tạo ${formData.role === 'admin' ? 'Super Admin' : 'Moderator'} thành công!`)
      }
      
      handleCloseModal()
      await fetchUsers()
    } catch (error) {
      console.error('Failed to save admin:', error)
      toast.error(error instanceof Error ? error.message : 'Lỗi khi lưu tài khoản')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleClick = (user: User) => {
    // Check if this is the only active admin
    const activeAdmins = users.filter(u => u.is_active && u.role === 'admin')
    const isOnlyAdmin = activeAdmins.length === 1 && activeAdmins[0].id === user.id
    
    if (isOnlyAdmin && user.is_active) {
      toast.error('Không thể vô hiệu hóa admin duy nhất trong hệ thống. Vui lòng tạo thêm admin khác trước.')
      return
    }
    
    setToggleConfirm({
      isOpen: true,
      userId: user.id,
      userName: user.full_name || user.username,
      currentStatus: user.is_active
    })
  }

  const handleToggleConfirm = async () => {
    if (!toggleConfirm.userId) return
    
    try {
      await adminService.updateUserStatus(toggleConfirm.userId, !toggleConfirm.currentStatus)
      const action = toggleConfirm.currentStatus ? 'vô hiệu hóa' : 'kích hoạt'
      toast.success(`Đã ${action} tài khoản "${toggleConfirm.userName}"`)
      await fetchUsers()
    } catch (error) {
      console.error('Failed to toggle user status:', error)
      toast.error('Lỗi khi thay đổi trạng thái tài khoản')
    } finally {
      setToggleConfirm({ isOpen: false, userId: null, userName: '', currentStatus: true })
    }
  }

  const handleDeleteClick = (user: User) => {
    // Check if this is the only active admin
    const activeAdmins = users.filter(u => u.is_active && u.role === 'admin')
    const isOnlyAdmin = activeAdmins.length === 1 && activeAdmins[0].id === user.id
    
    if (isOnlyAdmin) {
      toast.error('Không thể vô hiệu hóa admin duy nhất trong hệ thống. Vui lòng tạo thêm admin khác trước.')
      return
    }
    
    setDeleteConfirm({
      isOpen: true,
      userId: user.id,
      userName: user.full_name || user.username
    })
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.userId) return
    
    try {
      await adminService.updateUserStatus(deleteConfirm.userId, false) // Deactivate instead of delete
      toast.success('Đã vô hiệu hóa tài khoản')
      await fetchUsers()
    } catch (error) {
      // Error already handled by handleError
    } finally {
      setDeleteConfirm({ isOpen: false, userId: null, userName: '' })
    }
  }

  const columns = [
    { key: 'username', label: 'Username', width: '18%' },
    { key: 'email', label: 'Email', width: '22%' },
    { key: 'full_name', label: 'Họ Tên', width: '20%' },
    {
      key: 'role',
      label: 'Vai Trò',
      width: '12%',
      render: (user: User) => {
        if (user.role === 'admin') {
          return <span className="px-2 py-1 rounded text-xs font-semibold bg-purple-100 text-purple-800">Super Admin</span>
        } else if (user.role === 'moderator') {
          return <span className="px-2 py-1 rounded text-xs font-semibold bg-blue-100 text-blue-800">Moderator</span>
        } else {
          return <span className="px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-800">Editor</span>
        }
      },
    },
    {
      key: 'is_active',
      label: 'Trạng Thái',
      width: '12%',
      render: (user: User) => (
        <span className={`px-2 py-1 rounded text-xs ${
          user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {user.is_active ? 'Hoạt động' : 'Vô hiệu'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Hành Động',
      width: '15%',
      render: (user: User) => {
        // Check if this is the only active admin (chỉ đếm role='admin', không đếm 'moderator')
        const activeAdmins = users.filter(u => u.is_active && u.role === 'admin')
        const isOnlyAdmin = activeAdmins.length === 1 && activeAdmins[0].id === user.id
        const isToggleDisabled = isOnlyAdmin && user.is_active
        
        return (
          <div className="flex gap-2">
            <button
              onClick={() => handleOpenModal(user)}
              className="text-blue-600 hover:text-blue-800"
              title="Chỉnh sửa"
            >
              <Edit2 size={18} />
            </button>
            <button
              onClick={() => handleToggleClick(user)}
              disabled={isToggleDisabled}
              className={`${
                isToggleDisabled 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : user.is_active 
                    ? 'text-green-600 hover:text-green-800' 
                    : 'text-red-600 hover:text-red-800'
              }`}
              title={
                isToggleDisabled 
                  ? 'Không thể vô hiệu hóa admin duy nhất' 
                  : user.is_active 
                    ? 'Vô hiệu hóa' 
                    : 'Kích hoạt'
              }
            >
              {user.is_active ? <ToggleLeft size={18} /> : <ToggleRight size={18} />}
            </button>
          </div>
        )
      }
    }
  ]

  return (
    <AdminLayout title="Quản Lý Quản Trị Viên">
      <div className="flex justify-between items-center mb-6">
        <Button onClick={() => handleOpenModal()} icon={<Plus size={20} />}>
          Thêm Quản Trị Viên
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <>
          <Table columns={columns} data={paginatedUsers} />
          {totalPages > 1 && (
            <div className="mt-4">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </>
      )}

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold">
                {editingUser ? 'Chỉnh Sửa Quản Trị Viên' : 'Thêm Quản Trị Viên Mới'}
              </h2>
              <button onClick={handleCloseModal} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <Input
            label="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            required
            disabled={!!editingUser}
            placeholder="username"
          />
          
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
            placeholder="email@example.com"
          />
          
          <Input
            label="Họ tên"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
            placeholder="Nguyễn Văn A"
          />
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vai Trò <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as 'admin' | 'moderator' | 'editor' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              required
              disabled={editingUser ? (() => {
                // Đếm số admin active KHÁC user đang được edit
                const otherActiveAdmins = users.filter(u => 
                  u.is_active && 
                  u.role === 'admin' && 
                  u.id !== editingUser.id
                )
                
                // Disable nếu:
                // 1. Không còn admin active nào khác và user này là admin (không cho đổi thành moderator/editor)
                // 2. User này là moderator/editor và cố đổi thành admin
                if (otherActiveAdmins.length === 0 && editingUser.role === 'admin') {
                  return true
                }
                if ((editingUser.role === 'moderator' || editingUser.role === 'editor') && formData.role === 'admin') {
                  return true
                }
                return false
              })() : false}
            >
              <option value="editor">Editor (Quản lý nội dung)</option>
              <option value="moderator">Moderator (Quyền hạn chế)</option>
              <option value="admin">Super Admin (Toàn quyền)</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {formData.role === 'admin' 
                ? 'Super Admin có thể quản lý tất cả tính năng, bao gồm quản lý admin khác'
                : formData.role === 'moderator'
                ? 'Moderator có thể quản lý sách, đơn hàng, banner nhưng không thể quản lý admin'
                : 'Editor có thể quản lý sách, banner, categories nhưng không thể quản lý đơn hàng và admin'}
            </p>
            {editingUser && (() => {
              // Đếm số admin active KHÁC user đang được edit
              const otherActiveAdmins = users.filter(u => 
                u.is_active && 
                u.role === 'admin' && 
                u.id !== editingUser.id
              )
              const isOnlyAdmin = otherActiveAdmins.length === 0 && editingUser.role === 'admin'
              const isTryingAdmin = (editingUser.role === 'moderator' || editingUser.role === 'editor') && formData.role === 'admin'
              
              return (
                <>
                  {isOnlyAdmin && (
                    <p className="mt-1 text-xs text-red-500">
                      Không thể đổi role của admin duy nhất thành moderator hoặc editor
                    </p>
                  )}
                  {isTryingAdmin && (
                    <p className="mt-1 text-xs text-red-500">
                      Moderator và Editor không thể đổi thành Super Admin
                    </p>
                  )}
                </>
              )
            })()}
          </div>
          
          {!editingUser && (
            <Input
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              placeholder="Mật khẩu"
            />
          )}
          
          {editingUser && (
            <Input
              label="Password (Để trống nếu không đổi)"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Nhập mật khẩu mới (tùy chọn)"
            />
          )}
          
              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={handleCloseModal}>
                  Hủy
                </Button>
                <Button type="submit">
                  {editingUser ? 'Cập Nhật' : 'Thêm Mới'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}


      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Xác Nhận Vô Hiệu Hóa"
        message={`Bạn có chắc chắn muốn vô hiệu hóa tài khoản "${deleteConfirm.userName}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ isOpen: false, userId: null, userName: '' })}
        confirmText="Vô Hiệu Hóa"
        cancelText="Hủy"
        variant="danger"
      />

      {/* Toggle Status Confirmation Dialog */}
      <ConfirmDialog
        isOpen={toggleConfirm.isOpen}
        title={toggleConfirm.currentStatus ? "Xác Nhận Vô Hiệu Hóa" : "Xác Nhận Kích Hoạt"}
        message={`Bạn có chắc chắn muốn ${toggleConfirm.currentStatus ? 'vô hiệu hóa' : 'kích hoạt'} tài khoản "${toggleConfirm.userName}"?`}
        onConfirm={handleToggleConfirm}
        onCancel={() => setToggleConfirm({ isOpen: false, userId: null, userName: '', currentStatus: true })}
        confirmText={toggleConfirm.currentStatus ? "Vô Hiệu Hóa" : "Kích Hoạt"}
        cancelText="Hủy"
        variant={toggleConfirm.currentStatus ? "danger" : "default"}
      />
    </AdminLayout>
  )
}

export default AdminManagement

