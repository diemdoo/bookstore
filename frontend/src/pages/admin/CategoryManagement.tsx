import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { categoriesService } from '../../services/api'
import { Category } from '../../types'
import { Table } from '../../components/ui/Table'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useToast } from '../../components/ui/Toast'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'

const CategoryManagement: React.FC = () => {
  const { success, error: showError } = useToast()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; categoryId: number | null; categoryName: string }>({
    isOpen: false,
    categoryId: null,
    categoryName: ''
  })
  
  // Helper function to generate slug from Vietnamese text
  const generateSlug = (text: string): string => {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
      .replace(/[^\w\s-]/g, '') // Remove special characters
      .replace(/[-\s]+/g, '-') // Replace spaces and multiple dashes with single dash
      .trim()
      .replace(/^-+|-+$/g, '') // Remove leading/trailing dashes
  }

  // Form state (không cần key và slug trong form, backend tự generate)
  const [formData, setFormData] = useState<Partial<Category>>({
    name: '',
    description: '',
    display_order: 0,
    is_active: true
  })
  
  // Preview slug (readonly, chỉ để hiển thị)
  const [previewSlug, setPreviewSlug] = useState('')

  useEffect(() => {
    fetchCategories()
  }, [])

  // Update preview slug when name changes (only for new categories)
  useEffect(() => {
    if (formData.name && !editingCategory) {
      // Only preview for new categories
      setPreviewSlug(generateSlug(formData.name))
    }
  }, [formData.name, editingCategory])

  const fetchCategories = async () => {
    try {
      setLoading(true)
      const data = await categoriesService.getCategories(true) // Include inactive
      setCategories(data.categories)
    } catch (err) {
      showError('Lỗi khi tải danh sách danh mục')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (category?: Category) => {
    if (category) {
      setEditingCategory(category)
      setFormData({
        name: category.name,
        description: category.description || '',
        display_order: category.display_order || 0,
        is_active: category.is_active ?? true
      })
      setPreviewSlug(category.slug)
    } else {
      setEditingCategory(null)
      setFormData({
        name: '',
        description: '',
        display_order: 0,
        is_active: true
      })
      setPreviewSlug('')
    }
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingCategory(null)
    setFormData({
      name: '',
      description: '',
      display_order: 0,
      is_active: true
    })
    setPreviewSlug('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Chỉ gửi các field cần thiết, không gửi key và slug (backend tự generate)
    const submitData = {
      name: formData.name,
      description: formData.description,
      display_order: formData.display_order,
      is_active: formData.is_active
    }
    
    try {
      if (editingCategory) {
        await categoriesService.updateCategory(editingCategory.id!, submitData)
        success('Cập nhật danh mục thành công')
      } else {
        await categoriesService.createCategory(submitData)
        success('Thêm danh mục thành công')
      }
      
      handleCloseModal()
      fetchCategories()
    } catch (err) {
      // Error already handled by handleError
    }
  }

  const handleDeleteClick = (category: Category) => {
    setDeleteConfirm({
      isOpen: true,
      categoryId: category.id!,
      categoryName: category.name
    })
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.categoryId) return
    
    try {
      await categoriesService.deleteCategory(deleteConfirm.categoryId)
      success('Xóa danh mục thành công')
      fetchCategories()
    } catch (err) {
      // Error already handled by handleError
    } finally {
      setDeleteConfirm({ isOpen: false, categoryId: null, categoryName: '' })
    }
  }

  const columns = [
    { 
      key: 'category_code', 
      label: 'Mã DM',
      width: '10%',
      render: (item: Category) => item.category_code || '-'
    },
    { key: 'name', label: 'Tên Danh Mục', width: '22%' },
    { key: 'slug', label: 'Slug (URL)', width: '18%' },
    { key: 'description', label: 'Mô Tả', width: '19%' },
    { key: 'display_order', label: 'Thứ Tự', width: '8%' },
    { 
      key: 'is_active', 
      label: 'Trạng Thái',
      width: '12%',
      render: (item: Category) => (
        <span className={`px-2 py-1 rounded text-xs ${item.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {item.is_active ? 'Hoạt động' : 'Tắt'}
        </span>
      )
    },
    {
      key: 'actions',
      label: 'Hành Động',
      width: '13%',
      render: (item: Category) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleOpenModal(item)}
            className="text-blue-600 hover:text-blue-800"
            title="Chỉnh sửa"
          >
            <Edit2 size={18} />
          </button>
          <button
            onClick={() => handleDeleteClick(item)}
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
    <AdminLayout title="Quản Lý Danh Mục">
      <div className="flex justify-between items-center mb-6">
        <Button onClick={() => handleOpenModal()} icon={<Plus size={20} />}>
          Thêm Danh Mục
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <Table columns={columns} data={categories} />
      )}

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold">
                {editingCategory ? 'Chỉnh Sửa Danh Mục' : 'Thêm Danh Mục Mới'}
              </h2>
              <button onClick={handleCloseModal} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <Input
                label="Tên Danh Mục"
                value={formData.name}
                onChange={(e) => {
                  const newName = e.target.value
                  setFormData({ ...formData, name: newName })
                  // Auto-generate preview slug (readonly, chỉ để hiển thị)
                  setPreviewSlug(generateSlug(newName))
                }}
                required
                placeholder="e.g., Sách Tiếng Việt"
              />

              {/* Slug preview (readonly) - Giống BooksManagement */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Slug (URL) <span className="text-gray-400 text-xs font-normal">(tự động tạo)</span>
                </label>
                <input
                  type="text"
                  value={previewSlug || editingCategory?.slug || ''}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                  placeholder="sẽ được tự động tạo từ tên danh mục"
                />
                <p className="mt-1 text-xs text-gray-500">
                  {editingCategory
                    ? (formData.name !== editingCategory.name
                        ? 'Slug sẽ cập nhật khi lưu (vì tên danh mục thay đổi)'
                        : 'Slug hiện tại của danh mục')
                    : 'Slug sẽ tự động tạo khi lưu danh mục'}
                </p>
              </div>

              {/* Slug preview (readonly) */}
              {(previewSlug || editingCategory) && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Slug (URL) <span className="text-gray-400 text-xs">(tự động tạo)</span>
                  </label>
                  <input
                    type="text"
                    value={previewSlug || editingCategory?.slug || ''}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                    placeholder="sẽ được tự động tạo từ tên danh mục"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    {editingCategory 
                      ? 'Slug sẽ được tự động cập nhật nếu tên danh mục thay đổi'
                      : 'Slug sẽ được tự động tạo và đảm bảo unique'}
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mô Tả
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Mô tả về danh mục này..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <Input
                label="Thứ Tự Hiển Thị"
                type="number"
                value={formData.display_order?.toString() || '0'}
                onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
                min="0"
              />

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                  Hoạt động
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={handleCloseModal}>
                  Hủy
                </Button>
                <Button type="submit">
                  {editingCategory ? 'Cập Nhật' : 'Thêm'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Xác Nhận Xóa"
        message={`Bạn có chắc chắn muốn xóa danh mục "${deleteConfirm.categoryName}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ isOpen: false, categoryId: null, categoryName: '' })}
        confirmText="Xóa"
        cancelText="Hủy"
        variant="danger"
      />
    </AdminLayout>
  )
}

export default CategoryManagement

