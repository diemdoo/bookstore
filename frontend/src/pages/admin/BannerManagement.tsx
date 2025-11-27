import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Table, Pagination } from '../../components/ui/Table'
import { bannersService, categoriesService } from '../../services/api'
import { Plus, Edit2, Trash2, ToggleLeft, ToggleRight, X } from 'lucide-react'
import type { Banner, BannerFormData, Category } from '../../types'
import { useToast } from '../../components/ui/Toast'

const BannerManagement: React.FC = () => {
  const [banners, setBanners] = useState<Banner[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBanner, setEditingBanner] = useState<Banner | null>(null)
  const toast = useToast()
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; bannerId: number | null; bannerTitle: string }>({
    isOpen: false,
    bannerId: null,
    bannerTitle: ''
  })
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [linkType, setLinkType] = useState<'category' | 'custom'>('category')
  
  const [formData, setFormData] = useState<BannerFormData>({
    title: '',
    description: '',
    image_url: '',
    link: '',
    bg_color: '#6366f1',
    text_color: '#ffffff',
    position: 'main',
    display_order: 0,
    is_active: true,
  })

  const fetchBanners = async (page: number = 1) => {
    try {
      setLoading(true)
      const data = await bannersService.getAllBanners({ page, per_page: 20 })
      setBanners(data.banners)
      setCurrentPage(data.page)
      setTotalPages(data.pages)
    } catch (error) {
      console.error('Failed to fetch banners:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBanners()
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const data = await categoriesService.getCategories()
      setCategories(data.categories)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }

  const handleOpenModal = (banner?: Banner) => {
    if (banner) {
      setEditingBanner(banner)
      
      // Detect if link is category-based
      const categoryMatch = banner.link?.match(/\/books\?category=(.+)/)
      if (categoryMatch) {
        const categoryKey = decodeURIComponent(categoryMatch[1])
        setLinkType('category')
        setSelectedCategory(categoryKey)
        setFormData({
          title: banner.title,
          description: banner.description || '',
          image_url: banner.image_url,
          link: banner.link || '',
          bg_color: banner.bg_color,
          text_color: banner.text_color,
          position: banner.position,
          display_order: banner.display_order,
          is_active: banner.is_active,
        })
      } else {
        setLinkType('custom')
        setSelectedCategory('')
        setFormData({
          title: banner.title,
          description: banner.description || '',
          image_url: banner.image_url,
          link: banner.link || '',
          bg_color: banner.bg_color,
          text_color: banner.text_color,
          position: banner.position,
          display_order: banner.display_order,
          is_active: banner.is_active,
        })
      }
      setImagePreview(banner.image_url || '')
    } else {
      setEditingBanner(null)
      setLinkType('category')
      setSelectedCategory('')
      setFormData({
        title: '',
        description: '',
        image_url: '',
        link: '',
        bg_color: '#6366f1',
        text_color: '#ffffff',
        position: 'main',
        display_order: 0,
        is_active: true,
      })
      setImagePreview('')
    }
    setSelectedFile(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingBanner(null)
    setSelectedFile(null)
    setImagePreview('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate image_url
    if (!formData.image_url) {
      toast.error('Vui lòng upload ảnh banner')
      return
    }
    
    try {
      if (editingBanner) {
        await bannersService.updateBanner(editingBanner.id, formData)
        toast.success('Cập nhật banner thành công')
      } else {
        await bannersService.createBanner(formData)
        toast.success('Thêm banner thành công')
      }
      handleCloseModal()
      fetchBanners(currentPage)
    } catch (error) {
      console.error('Failed to save banner:', error)
      toast.error(error instanceof Error ? error.message : 'Lỗi khi lưu banner')
    }
  }

  const handleDeleteClick = (banner: Banner) => {
    setDeleteConfirm({
      isOpen: true,
      bannerId: banner.id,
      bannerTitle: banner.title
    })
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.bannerId) return
    
    try {
      await bannersService.deleteBanner(deleteConfirm.bannerId)
      toast.success('Đã xóa banner')
      fetchBanners(currentPage)
    } catch (error) {
      // Error already handled by handleError
    } finally {
      setDeleteConfirm({ isOpen: false, bannerId: null, bannerTitle: '' })
    }
  }

  const handleToggleStatus = async (id: number) => {
    try {
      await bannersService.toggleBannerStatus(id)
      fetchBanners(currentPage)
    } catch (error) {
      console.error('Failed to toggle banner status:', error)
      toast.error('Lỗi khi thay đổi trạng thái banner')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Vui lòng chọn file ảnh')
        return
      }
      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File quá lớn. Kích thước tối đa: 5MB')
        return
      }
      setSelectedFile(file)
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUploadImage = async () => {
    if (!selectedFile) return
    
    try {
      setUploading(true)
      const result = await bannersService.uploadImage(selectedFile)
      setFormData({ ...formData, image_url: result.url })
      setSelectedFile(null)
      setImagePreview('')
      toast.success('Upload ảnh thành công')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Lỗi khi upload ảnh')
    } finally {
      setUploading(false)
    }
  }

  const columns = [
    {
      key: 'id',
      label: 'ID',
      width: '5%',
    },
    {
      key: 'image',
      label: 'Hình ảnh',
      width: '15%',
      render: (banner: Banner) => (
        <img 
          src={banner.image_url} 
          alt={banner.title}
          className="h-16 w-24 object-cover rounded"
        />
      ),
    },
    {
      key: 'title',
      label: 'Tiêu đề',
      width: '20%',
    },
    {
      key: 'position',
      label: 'Vị trí',
      width: '10%',
      render: (banner: Banner) => (
        <span className={`px-2 py-1 rounded text-xs ${
          banner.position === 'main' ? 'bg-blue-100 text-blue-700' :
          banner.position === 'side_top' ? 'bg-green-100 text-green-700' :
          'bg-purple-100 text-purple-700'
        }`}>
          {banner.position === 'main' ? 'Chính' : 
           banner.position === 'side_top' ? 'Phụ trên' : 'Phụ dưới'}
        </span>
      ),
    },
    {
      key: 'display_order',
      label: 'Thứ tự',
      width: '8%',
    },
    {
      key: 'is_active',
      label: 'Trạng thái',
      width: '10%',
      render: (banner: Banner) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          banner.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
        }`}>
          {banner.is_active ? 'Hoạt động' : 'Tắt'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Hành Động',
      render: (banner: Banner) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleOpenModal(banner)}
            className="text-blue-600 hover:text-blue-800"
            title="Chỉnh sửa"
          >
            <Edit2 size={18} />
          </button>
          <button
            onClick={() => handleToggleStatus(banner.id)}
            className="text-green-600 hover:text-green-800"
            title={banner.is_active ? 'Tắt' : 'Bật'}
          >
            {banner.is_active ? <ToggleLeft size={18} /> : <ToggleRight size={18} />}
          </button>
          <button
            onClick={() => handleDeleteClick(banner)}
            className="text-red-600 hover:text-red-800"
            title="Xóa"
          >
            <Trash2 size={18} />
          </button>
        </div>
      ),
    },
  ]

  return (
    <AdminLayout title="Quản Lý Banner">
      <div className="flex justify-between items-center mb-6">
        <Button onClick={() => handleOpenModal()} icon={<Plus size={20} />}>
          Thêm Banner
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <>
          <Table columns={columns} data={banners} />
          {totalPages > 1 && (
            <div className="mt-4">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={(page) => fetchBanners(page)}
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
                {editingBanner ? 'Chỉnh Sửa Banner' : 'Thêm Banner Mới'}
              </h2>
              <button onClick={handleCloseModal} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <Input
            label="Tiêu đề"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            placeholder="VD: Sale cuối năm"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mô tả
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Mô tả ngắn về banner"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ảnh Banner <span className="text-red-500">*</span>
            </label>
            
            {/* Image Preview */}
            {(imagePreview || formData.image_url) && (
              <div className="mb-3">
                <img
                  src={imagePreview || formData.image_url}
                  alt="Preview"
                  className="w-full max-w-md h-48 object-cover rounded border border-gray-300"
                />
              </div>
            )}
            
            {/* File Input */}
            <div className="flex gap-2 mb-2">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-dark cursor-pointer"
              />
              <Button
                type="button"
                onClick={handleUploadImage}
                disabled={!selectedFile || uploading}
                variant="outline"
              >
                {uploading ? 'Đang upload...' : 'Upload'}
              </Button>
            </div>
            
            {/* Current URL (readonly, shown after upload) */}
            {formData.image_url && (
              <div className="text-xs text-gray-500 mt-1 break-all">
                URL: {formData.image_url}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Loại Link
            </label>
            <div className="flex gap-4 mb-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="linkType"
                  value="category"
                  checked={linkType === 'category'}
                  onChange={(e) => {
                    setLinkType('category')
                    setSelectedCategory('')
                    setFormData({ ...formData, link: '' })
                  }}
                  className="mr-2"
                />
                <span className="text-sm">Chọn Category</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="linkType"
                  value="custom"
                  checked={linkType === 'custom'}
                  onChange={(e) => {
                    setLinkType('custom')
                    setSelectedCategory('')
                  }}
                  className="mr-2"
                />
                <span className="text-sm">Link Tùy Chỉnh</span>
              </label>
            </div>

            {linkType === 'category' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    const categoryKey = e.target.value
                    setSelectedCategory(categoryKey)
                    if (categoryKey) {
                      setFormData({ ...formData, link: `/books?category=${encodeURIComponent(categoryKey)}` })
                    } else {
                      setFormData({ ...formData, link: '' })
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">-- Chọn category --</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.key}>
                      {category.name}
                    </option>
                  ))}
                </select>
                {selectedCategory && (
                  <p className="mt-1 text-xs text-gray-500">
                    Link: {formData.link}
                  </p>
                )}
              </div>
            ) : (
              <Input
                label="Link (khi click banner)"
                value={formData.link}
                onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                placeholder="https://example.com/sale hoặc /books"
              />
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Màu nền
              </label>
              <input
                type="color"
                value={formData.bg_color}
                onChange={(e) => setFormData({ ...formData, bg_color: e.target.value })}
                className="w-full h-10 border border-gray-300 rounded-md cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Màu chữ
              </label>
              <input
                type="color"
                value={formData.text_color}
                onChange={(e) => setFormData({ ...formData, text_color: e.target.value })}
                className="w-full h-10 border border-gray-300 rounded-md cursor-pointer"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vị trí
            </label>
            <select
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value as 'main' | 'side_top' | 'side_bottom' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="main">Banner chính (Carousel)</option>
              <option value="side_top">Banner phụ trên</option>
              <option value="side_bottom">Banner phụ dưới</option>
            </select>
          </div>

          <Input
            label="Thứ tự hiển thị"
            type="number"
            value={formData.display_order}
            onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
            min={0}
          />

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
              Kích hoạt ngay
            </label>
          </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={handleCloseModal}>
                  Hủy
                </Button>
                <Button type="submit">
                  {editingBanner ? 'Cập Nhật' : 'Thêm Mới'}
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
        message={`Bạn có chắc chắn muốn xóa banner "${deleteConfirm.bannerTitle}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ isOpen: false, bannerId: null, bannerTitle: '' })}
        confirmText="Xóa"
        cancelText="Hủy"
        variant="danger"
      />
    </AdminLayout>
  )
}

export default BannerManagement

