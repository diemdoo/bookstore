import React, { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layout/AdminLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Table, Pagination } from '../../components/ui/Table'
import { booksService, categoriesService } from '../../services/api'
import { Plus, Edit2, Trash2, X, Search } from 'lucide-react'
import type { Book, BookFormData, Category } from '../../types'
import { useToast } from '../../components/ui/Toast'

const BooksManagement: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBook, setEditingBook] = useState<Book | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const toast = useToast()
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; bookId: number | null; bookTitle: string }>({
    isOpen: false,
    bookId: null,
    bookTitle: ''
  })
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  
  const [formData, setFormData] = useState<BookFormData>({
    title: '',
    author: '',
    category: '',
    description: '',
    price: 0,
    stock: 0,
    image_url: '',
    publisher: '',
    publish_date: '',
    distributor: '',
    dimensions: '',
    pages: 0,
    weight: 0,
  })
  
  // Preview slug (readonly, chỉ để hiển thị)
  const [previewSlug, setPreviewSlug] = useState('')
  
  // Track if title has changed (for warning message)
  const [isTitleChanged, setIsTitleChanged] = useState(false)
  const [originalTitle, setOriginalTitle] = useState('')
  
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

  const fetchBooks = async (page: number = 1, search: string = '') => {
    try {
      setLoading(true)
      const data = await booksService.getBooks({ 
        page, 
        per_page: 20, 
        search: search.trim() 
      })
      setBooks(data.books)
      setCurrentPage(data.page)
      setTotalPages(data.pages)
    } catch (error) {
      console.error('Failed to fetch books:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBooks()
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

  const handleOpenModal = (book?: Book) => {
    if (book) {
      setEditingBook(book)
      setFormData({
        title: book.title,
        author: book.author,
        category: book.category,
        description: book.description,
        price: book.price,
        stock: book.stock,
        image_url: book.image_url,
        publisher: book.publisher || '',
        publish_date: book.publish_date || '',
        distributor: book.distributor || '',
        dimensions: book.dimensions || '',
        pages: book.pages || 0,
        weight: book.weight || 0,
      })
      setImagePreview(book.image_url || '')
      setPreviewSlug(book.slug || '')
      setOriginalTitle(book.title)
      setIsTitleChanged(false)
    } else {
      setEditingBook(null)
      setFormData({
        title: '',
        author: '',
        category: '',
        description: '',
        price: 0,
        stock: 0,
        image_url: '',
        publisher: '',
        publish_date: '',
        distributor: '',
        dimensions: '',
        pages: 0,
        weight: 0,
      })
      setImagePreview('')
      setPreviewSlug('')
      setOriginalTitle('')
      setIsTitleChanged(false)
    }
    setSelectedFile(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingBook(null)
    setSelectedFile(null)
    setImagePreview('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate image_url
    if (!formData.image_url) {
      toast.error('Vui lòng upload ảnh sách')
      return
    }
    
    try {
      setLoading(true)
      if (editingBook) {
        await booksService.updateBook(editingBook.id, formData)
        toast.success('Cập nhật sách thành công')
      } else {
        await booksService.createBook(formData)
        toast.success('Thêm sách thành công')
      }
      await fetchBooks(currentPage)
      handleCloseModal()
    } catch (error) {
      console.error('Failed to save book:', error)
      toast.error(error instanceof Error ? error.message : 'Lỗi khi lưu sách')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteClick = (book: Book) => {
    setDeleteConfirm({
      isOpen: true,
      bookId: book.id,
      bookTitle: book.title
    })
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.bookId) return
    
    try {
      await booksService.deleteBook(deleteConfirm.bookId)
      toast.success('Đã xóa sách')
      await fetchBooks(currentPage)
    } catch (error) {
      // Error already handled by handleError
    } finally {
      setDeleteConfirm({ isOpen: false, bookId: null, bookTitle: '' })
    }
  }

  const columns = [
    { 
      key: 'book_code', 
      label: 'Mã Sách',
      width: '10%',
      render: (book: Book) => book.book_code || '-'
    },
    { key: 'title', label: 'Tên Sách', width: '20%' },
    { key: 'publisher', label: 'Nhà Xuất Bản', width: '13%' },
    { key: 'author', label: 'Tác Giả', width: '13%' },
    {
      key: 'price',
      label: 'Giá',
      width: '12%',
      render: (book: Book) => `${book.price.toLocaleString('vi-VN')} đ`,
    },
    {
      key: 'description',
      label: 'Mô tả',
      width: '18%',
      render: (book: Book) => (
        <div className="truncate">{book.description}</div>
      ),
    },
    {
      key: 'actions',
      label: 'Hành Động',
      width: '10%',
      render: (book: Book) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleOpenModal(book)}
            className="text-blue-600 hover:text-blue-800"
            title="Chỉnh sửa"
          >
            <Edit2 size={18} />
          </button>
          <button
            onClick={() => handleDeleteClick(book)}
            className="text-red-600 hover:text-red-800"
            title="Xóa"
          >
            <Trash2 size={18} />
          </button>
        </div>
      )
    }
  ]

  const handleSearch = () => {
    setCurrentPage(1)
    fetchBooks(1, searchQuery)
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setCurrentPage(1)
    fetchBooks(1, '')
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
      const result = await booksService.uploadImage(selectedFile)
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

  return (
    <AdminLayout title="Quản Lý Sách">
      <div className="flex justify-between items-center mb-6 gap-4">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch()
                }
              }}
              placeholder="Tìm kiếm sách theo tên..."
              className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {searchQuery && (
              <button
                onClick={handleClearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                title="Xóa tìm kiếm"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>
        <Button onClick={() => handleOpenModal()} icon={<Plus size={20} />}>
          Thêm Sách
        </Button>
      </div>

      {searchQuery && (
        <div className="mb-4 text-sm text-gray-600">
          Đang hiển thị kết quả tìm kiếm cho "{searchQuery}"
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">Đang tải...</div>
      ) : (
        <>
          {books.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchQuery ? `Không tìm thấy sách nào với từ khóa "${searchQuery}"` : 'Không có sách nào'}
            </div>
          ) : (
            <>
              <Table columns={columns} data={books} />
              {totalPages > 1 && (
                <div className="mt-4">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={(page) => fetchBooks(page, searchQuery)}
                  />
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold">
                {editingBook ? 'Chỉnh Sửa Sách' : 'Thêm Sách Mới'}
              </h2>
              <button onClick={handleCloseModal} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Tên Sách"
              value={formData.title}
              onChange={(e) => {
                const newTitle = e.target.value
                setFormData({ ...formData, title: newTitle })
                // Auto-generate preview slug (readonly, chỉ để hiển thị)
                setPreviewSlug(generateSlug(newTitle))
                // Check if title has changed from original
                if (editingBook && newTitle !== originalTitle) {
                  setIsTitleChanged(true)
                } else {
                  setIsTitleChanged(false)
                }
              }}
              required
            />
            
            {/* Slug preview (readonly) - Always visible, simple version */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Slug (URL) <span className="text-gray-400 text-xs font-normal">(tự động tạo)</span>
              </label>
              <input
                type="text"
                value={previewSlug || editingBook?.slug || ''}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                placeholder="sẽ được tự động tạo từ tên sách"
              />
              <p className="mt-1 text-xs text-gray-500">
                {editingBook 
                  ? (isTitleChanged 
                      ? 'Slug sẽ cập nhật khi lưu (vì tên sách thay đổi)' 
                      : 'Slug hiện tại của sách')
                  : 'Slug sẽ tự động tạo khi lưu sách'}
              </p>
            </div>
            <Input
              label="Tác Giả"
              value={formData.author}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              required
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Thể Loại <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">-- Chọn thể loại --</option>
                {categories.map((cat) => (
                  <option key={cat.key} value={cat.key}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <Input
              label="Giá"
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
              required
            />
            <Input
              label="Số Lượng"
              type="number"
              value={formData.stock}
              onChange={(e) => setFormData({ ...formData, stock: Number(e.target.value) })}
              required
            />
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ảnh Sách <span className="text-red-500">*</span>
              </label>
              
              {/* Image Preview */}
              {(imagePreview || formData.image_url) && (
                <div className="mb-3">
                  <img
                    src={imagePreview || formData.image_url}
                    alt="Preview"
                    className="w-32 h-40 object-cover rounded border border-gray-300"
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
            <Input
              label="Nhà Xuất Bản"
              value={formData.publisher}
              onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
            />
            <Input
              label="Ngày Xuất Bản"
              value={formData.publish_date}
              onChange={(e) => setFormData({ ...formData, publish_date: e.target.value })}
              placeholder="DD/MM/YYYY"
            />
            <Input
              label="Nhà Phát Hành"
              value={formData.distributor}
              onChange={(e) => setFormData({ ...formData, distributor: e.target.value })}
            />
            <Input
              label="Kích Thước (cm)"
              value={formData.dimensions}
              onChange={(e) => setFormData({ ...formData, dimensions: e.target.value })}
              placeholder="15.5 x 24.5 x 3.0"
            />
            <Input
              label="Số Trang"
              type="number"
              value={formData.pages}
              onChange={(e) => setFormData({ ...formData, pages: Number(e.target.value) })}
            />
            <Input
              label="Trọng Lượng (g)"
              type="number"
              value={formData.weight}
              onChange={(e) => setFormData({ ...formData, weight: Number(e.target.value) })}
            />
          </div>
          
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mô Tả <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={handleCloseModal}>
                  Hủy
                </Button>
                <Button type="submit">
                  {editingBook ? 'Cập Nhật' : 'Thêm Mới'}
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
        message={`Bạn có chắc chắn muốn xóa sách "${deleteConfirm.bookTitle}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ isOpen: false, bookId: null, bookTitle: '' })}
        confirmText="Xóa"
        cancelText="Hủy"
        variant="danger"
      />
    </AdminLayout>
  )
}

export default BooksManagement

