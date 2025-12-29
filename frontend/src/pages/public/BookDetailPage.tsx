import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { Button } from '../../components/ui/Button'
import { Breadcrumb } from '../../components/ui/Breadcrumb'
import { booksService, categoriesService } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import { useCart } from '../../contexts/CartContext'
import { useToast } from '../../components/ui/Toast'
import { Minus, Plus, ShoppingCart, CreditCard } from 'lucide-react'
import { formatPrice } from '../../utils/formatters'
import type { Book, Category } from '../../types'

// Placeholder image (SVG data URL)
const PLACEHOLDER_IMAGE = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='

const BookDetailPage: React.FC = () => {
  const { slug: categorySlug, bookSlug } = useParams<{ slug: string; bookSlug: string }>()
  const [book, setBook] = useState<Book | null>(null)
  const [category, setCategory] = useState<Category | null>(null)
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  const { addToCart } = useCart()
  const toast = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    const fetchBook = async () => {
      if (!bookSlug) return
      
      try {
        if (categorySlug) {
          // Preferred: Fetch book using category slug and book slug endpoint (keeps category context)
          const data = await categoriesService.getCategoryBook(categorySlug, bookSlug)
          setBook(data.book)
          
          // Set category from API response
          if (data.category_slug && data.category_name) {
            setCategory({
              id: 0,
              key: data.category_key,
              name: data.category_name,
              slug: data.category_slug,
              is_active: true
            } as Category)
          }
        } else {
          // Fallback: Get all books and find by slug (less efficient but works)
          console.log('Fetching book without category context, using fallback method')
          const booksData = await booksService.getBooks({ per_page: 1000 }) // Get all books
          const foundBook = booksData.books.find(b => b.slug === bookSlug)
          
          if (foundBook) {
            setBook(foundBook)
            
            // Try to get category info
            try {
              const categoriesData = await categoriesService.getCategories()
              const foundCategory = categoriesData.categories.find(c => c.key === foundBook.category)
              if (foundCategory) {
                setCategory(foundCategory)
              }
            } catch (catError) {
              console.error('Failed to fetch category:', catError)
            }
          } else {
            console.error('Book not found with slug:', bookSlug)
          }
        }
      } catch (error) {
        console.error('Failed to fetch book:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchBook()
  }, [bookSlug, categorySlug])

  const handleAddToCart = async () => {
    if (!user) {
      navigate('/login')
      return
    }
    if (!book) return

    try {
      await addToCart(book.id, quantity)
      toast.success('Đã thêm vào giỏ hàng!')
    } catch (error) {
      toast.error('Lỗi khi thêm vào giỏ hàng')
    }
  }

  const handleBuyNow = async () => {
    if (!user) {
      navigate('/login')
      return
    }
    await handleAddToCart()
    navigate('/cart')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-8 flex-1 text-center">Đang tải...</main>
        <PublicFooter />
      </div>
    )
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-8 flex-1 text-center">Không tìm thấy sách</main>
        <PublicFooter />
      </div>
    )
  }

  const breadcrumbItems = [
    { label: 'Trang chủ', href: '/' },
    ...(category && categorySlug ? [{ label: category.name, href: `/category/${categorySlug}` }] : []),
    { label: book.title }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        <Breadcrumb items={breadcrumbItems} />
        
        <div className="py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* Book Image */}
            <div className="flex items-center justify-center">
              <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-md">
                <img
                  src={book.image_url || PLACEHOLDER_IMAGE}
                  alt={book.title}
                  onError={(e) => {
                    e.currentTarget.src = PLACEHOLDER_IMAGE
                  }}
                  className="w-full object-contain rounded"
                />
              </div>
            </div>

            {/* Book Info */}
            <div className="space-y-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 leading-snug mb-3">{book.title}</h1>
                
                <div className="space-y-1 text-sm text-gray-600">
                  <div>
                    <span className="font-medium text-gray-900">Tác giả:</span> {book.author}
                  </div>
                  {book.publisher && (
                    <div>
                      <span className="font-medium text-gray-900">NXB:</span> {book.publisher}
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-3 border-t border-gray-200">
                <div className="text-3xl font-bold text-primary mb-1">
                  {formatPrice(book.price)}
                </div>
                {book.sold !== undefined && book.sold > 0 && (
                  <div className="text-sm text-gray-500 mb-1">
                    Đã bán {book.sold}
                  </div>
                )}
                <div>
                  {book.stock > 0 ? (
                    <span className="inline-flex px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-xs font-semibold border border-green-200">
                      Còn hàng
                    </span>
                  ) : (
                    <span className="inline-flex px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs font-semibold border border-red-200">
                      Hết hàng
                    </span>
                  )}
                </div>
              </div>

              {user && book.stock > 0 && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-medium text-gray-600">Số lượng:</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        className="w-7 h-7 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-50 hover:border-gray-400 transition-all active:scale-95"
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                        className="w-16 h-7 text-center border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                      <button
                        onClick={() => setQuantity(Math.min(book.stock, quantity + 1))}
                        className="w-7 h-7 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-50 hover:border-gray-400 transition-all active:scale-95"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={handleBuyNow} className="flex-1 h-9 text-sm font-semibold shadow-sm hover:shadow-md transition-shadow">
                      <CreditCard className="h-4 w-4 mr-2" />
                      Mua Ngay
                    </Button>
                    <Button onClick={handleAddToCart} variant="outline" className="flex-1 h-9 text-sm font-semibold border-2 hover:bg-gray-50 transition-colors">
                      <ShoppingCart className="h-4 w-4 mr-2" />
                      Thêm Giỏ Hàng
                    </Button>
                  </div>
                </div>
              )}

              {!user && (
                <div className="p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg shadow-sm">
                  <p className="text-sm text-yellow-800">
                    Vui lòng <a href="/login" className="text-primary hover:underline font-semibold">đăng nhập</a> để mua sản phẩm
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Details Section */}
          <div className="mt-16 space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-gray-900 text-lg font-semibold border-b-2 border-primary pb-3 mb-4">
                THÔNG TIN CHI TIẾT
              </h2>
              <div className="space-y-3">
                <p><span className="font-medium">Mã Sách:</span> {book.id}</p>
                <p><span className="font-medium">Nhà Xuất Bản:</span> {book.publisher || 'N/A'}</p>
                <p><span className="font-medium">Tác Giả:</span> {book.author}</p>
                <p><span className="font-medium">Năm Xuất Bản:</span> {book.publish_date || 'N/A'}</p>
                <p><span className="font-medium">Số Trang:</span> {book.pages || 'N/A'}</p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-gray-900 text-lg font-semibold border-b-2 border-primary pb-3 mb-4">
                GIỚI THIỆU SẢN PHẨM
              </h2>
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line text-base">
                  {book.description}
                </p>
              </div>
            </div>

          </div>
        </div>
      </main>

      <PublicFooter />
    </div>
  )
}

export default BookDetailPage

