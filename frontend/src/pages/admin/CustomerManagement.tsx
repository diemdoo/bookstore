import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Table, Pagination } from '../../components/ui/Table'
import { adminService, authService } from '../../services/api'
import { Plus, Edit2, ToggleLeft, ToggleRight, X } from 'lucide-react'
import type { User } from '../../types'
import { useToast } from '../../components/ui/Toast'
import { useAuth } from '../../contexts/AuthContext'

interface CustomerFormData {
  username: string
  password: string
  email: string
  full_name: string
}

const CustomerManagement: React.FC = () => {
  const { user: currentUser } = useAuth()
  
  // Chặn editor truy cập trang này
  if (currentUser?.role === 'editor') {
    return (
      <AdminLayout title="Quản Lý Khách Hàng">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Không có quyền truy cập</h2>
          <p className="text-gray-600">Chỉ Admin và Moderator mới có quyền quản lý khách hàng.</p>
        </div>
      </AdminLayout>
    )
  }
  const [users, setUsers] = useState<User[]>([])
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
  const [formData, setFormData] = useState<CustomerFormData>({
    username: '',
    password: '',
    email: '',
    full_name: '',
  })
  const toast = useToast()

  const fetchUsers = async (page: number = 1) => {
    try {
      setLoading(true)
      const data = await adminService.getUsers('customer', page, 20)
      setUsers(data.users)
      setCurrentPage(data.page)
      setTotalPages(data.pages)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers(currentPage)
  }, [currentPage])

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user)
      setFormData({
        username: user.username,
        password: '',
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
        toast.warning('Chức năng cập nhật chưa được implement')
      } else {
        await authService.register({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          full_name: formData.full_name,
        })
        toast.success('Khách hàng mới đã được tạo thành công!')
      }
      
      handleCloseModal()
      await fetchUsers()
    } catch (error) {
      console.error('Failed to save customer:', error)
      toast.error(error instanceof Error ? error.message : 'Lỗi khi lưu khách hàng')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleClick = (user: User) => {
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
      toast.success(`Đã ${action} khách hàng`)
      await fetchUsers()
    } catch (error) {
      // Error already handled by handleError
    } finally {
      setToggleConfirm({ isOpen: false, userId: null, userName: '', currentStatus: true })
    }
  }

  const columns = [
    { 
      key: 'customer_code', 
      label: 'Mã KH',
      width: '12%',
      render: (user: User) => user.customer_code || '-'
    },
    { key: 'username', label: 'Username', width: '15%' },
    { key: 'email', label: 'Email', width: '20%' },
    { key: 'full_name', label: 'Họ Tên', width: '18%' },
    {
      key: 'created_at',
      label: 'Ngày Đăng Ký',
      width: '13%',
      render: (user: User) => new Date(user.created_at).toLocaleDateString('vi-VN'),
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
      width: '10%',
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
            onClick={() => handleToggleClick(user)}
            className={user.is_active ? 'text-green-600 hover:text-green-800' : 'text-red-600 hover:text-red-800'}
            title={user.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
          >
            {user.is_active ? <ToggleLeft size={18} /> : <ToggleRight size={18} />}
          </button>
        </div>
      )
    }
  ]

  return (
    <AdminLayout title="Quản Lý Khách Hàng">
      <div className="flex justify-between items-center mb-6">
        <Button onClick={() => handleOpenModal()} icon={<Plus size={20} />}>
          Thêm Khách Hàng
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <>
          <Table columns={columns} data={users} />
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
                {editingUser ? 'Chỉnh Sửa Khách Hàng' : 'Thêm Khách Hàng Mới'}
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


      {/* Toggle Status Confirmation Dialog */}
      <ConfirmDialog
        isOpen={toggleConfirm.isOpen}
        title="Xác Nhận Thay Đổi"
        message={`Bạn có chắc chắn muốn ${toggleConfirm.currentStatus ? 'vô hiệu hóa' : 'kích hoạt'} khách hàng "${toggleConfirm.userName}"?`}
        onConfirm={handleToggleConfirm}
        onCancel={() => setToggleConfirm({ isOpen: false, userId: null, userName: '', currentStatus: true })}
        confirmText={toggleConfirm.currentStatus ? 'Vô Hiệu Hóa' : 'Kích Hoạt'}
        cancelText="Hủy"
        variant={toggleConfirm.currentStatus ? 'danger' : 'primary'}
      />
    </AdminLayout>
  )
}

export default CustomerManagement
