import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { BookCard } from '../../components/shared/BookCard'
import { booksService, categoriesService } from '../../services/api'
import type { Book, Category } from '../../types'
import { ChevronRight } from 'lucide-react'

const BooksPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const categoryKey = searchParams.get('category')
  
  const [books, setBooks] = useState<Book[]>([])
  const [category, setCategory] = useState<Category | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const perPage = 20

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Fetch category info if specified
        if (categoryKey) {
          const categoriesData = await categoriesService.getCategories()
          const foundCategory = categoriesData.categories.find(c => c.key === categoryKey)
          setCategory(foundCategory || null)
        } else {
          setCategory(null)
        }
        
        // Fetch books
        const booksData = await booksService.getBooks({
          page: currentPage,
          per_page: perPage,
          category: categoryKey || ''
        })
        
        setBooks(booksData.books)
        setTotalPages(booksData.pages)
      } catch (error) {
        console.error('Failed to fetch books:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [categoryKey, currentPage])

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        {/* Breadcrumb */}
        <div className="mb-6 text-sm text-gray-600 flex items-center gap-2">
          <Link to="/" className="hover:text-primary">Trang chủ</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-primary font-medium">
            {category ? category.name : 'Tất cả sách'}
          </span>
        </div>

        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {category ? category.name : 'Tất Cả Sách'}
          </h1>
          {category && (
            <p className="mt-2 text-gray-600">
              Khám phá bộ sưu tập {category.name.toLowerCase()} phong phú của chúng tôi
            </p>
          )}
        </div>

        {/* Books Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">Đang tải...</p>
          </div>
        ) : books.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg">Không có sách trong danh mục này</p>
            <Link to="/" className="mt-4 inline-block text-primary hover:underline">
              ← Quay về trang chủ
            </Link>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-6 mb-8">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-8">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed border"
                >
                  ← Trước
                </button>
                
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  let page: number
                  if (totalPages <= 5) {
                    page = i + 1
                  } else if (currentPage <= 3) {
                    page = i + 1
                  } else if (currentPage >= totalPages - 2) {
                    page = totalPages - 4 + i
                  } else {
                    page = currentPage - 2 + i
                  }
                  
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-4 py-2 rounded-lg ${
                        page === currentPage
                          ? 'bg-primary text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-100'
                      } border`}
                    >
                      {page}
                    </button>
                  )
                })}
                
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed border"
                >
                  Sau →
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <PublicFooter />
    </div>
  )
}

export default BooksPage

