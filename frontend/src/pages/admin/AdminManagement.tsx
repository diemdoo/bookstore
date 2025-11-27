import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Table, Pagination } from '../../components/ui/Table'
import { adminService, authService } from '../../services/api'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import type { User } from '../../types'
import { useToast } from '../../components/ui/Toast'

interface AdminFormData {
  username: string
  password: string
  email: string
  full_name: string
}

const AdminManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; userId: number | null; userName: string }>({
    isOpen: false,
    userId: null,
    userName: ''
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
  })
  const toast = useToast()

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await adminService.getUsers()
      const adminUsers = data.filter(u => u.role === 'admin')
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
      })
    } else {
      setEditingUser(null)
      setFormData({
        username: '',
        password: '',
        email: '',
        full_name: '',
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
        // Update logic - would need API endpoint
        toast.warning('Chức năng cập nhật chưa được implement')
      } else {
        // Create new admin account
        // Note: Register API creates customer by default, need to update role to admin via admin API
        await authService.register({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          full_name: formData.full_name,
        })
        toast.success('Tài khoản mới đã được tạo. Cần update role thành admin trong DB.')
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

  const handleDeleteClick = (user: User) => {
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
    { key: 'username', label: 'Username' },
    { key: 'email', label: 'Email' },
    { key: 'full_name', label: 'Họ Tên' },
    {
      key: 'is_active',
      label: 'Trạng Thái',
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
      render: (user: User) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleOpenModal(user)}
            className="text-blue-600 hover:text-blue-800"
            title="Chỉnh sửa"
          >
            <Edit2 size={18} />
          </button>
          <button
            onClick={() => handleDeleteClick(user)}
            className="text-red-600 hover:text-red-800"
            title="Xóa"
          >
            <Trash2 size={18} />
          </button>
        </div>
      )
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
    </AdminLayout>
  )
}

export default AdminManagement

