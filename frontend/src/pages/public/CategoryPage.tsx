import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { BookCard } from '../../components/shared/BookCard'
import { Breadcrumb } from '../../components/ui/Breadcrumb'
import { booksService, categoriesService } from '../../services/api'
import type { Book, Category } from '../../types'

const CategoryPage: React.FC = () => {
  const { categoryKey } = useParams<{ categoryKey: string }>()
  
  const [books, setBooks] = useState<Book[]>([])
  const [category, setCategory] = useState<Category | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const perPage = 20

  useEffect(() => {
    const fetchData = async () => {
      if (!categoryKey) return
      
      try {
        setLoading(true)
        
        // Fetch category info
        const categoriesData = await categoriesService.getCategories()
        const foundCategory = categoriesData.categories.find(c => c.key === categoryKey)
        setCategory(foundCategory || null)
        
        // Fetch books in this category using RESTful endpoint
        // Decode categoryKey from URL if needed
        const decodedKey = decodeURIComponent(categoryKey)
        const booksData = await categoriesService.getCategoryBooks(decodedKey, {
          page: currentPage,
          per_page: perPage
        })
        
        setBooks(booksData.books)
        setTotalPages(booksData.pages)
      } catch (error) {
        console.error('Failed to fetch category data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [categoryKey, currentPage])

  const breadcrumbItems = [
    { label: 'Trang chủ', href: '/' },
    { label: category?.name || categoryKey || 'Danh Mục' }
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-8 flex-1 text-center">Đang tải...</main>
        <PublicFooter />
      </div>
    )
  }

  if (!category) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-8 flex-1">
          <Breadcrumb items={breadcrumbItems} />
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Danh mục không tồn tại</h1>
            <Link to="/" className="text-primary hover:underline">Quay về trang chủ</Link>
          </div>
        </main>
        <PublicFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        <Breadcrumb items={breadcrumbItems} />

        {/* Category Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{category.name}</h1>
          {category.description && (
            <p className="text-gray-600">{category.description}</p>
          )}
        </div>

        {/* Books Grid */}
        {books.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Không có sách nào trong danh mục này.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {books.map(book => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Trang trước
                </button>
                
                <span className="px-4 py-2 text-gray-700">
                  Trang {currentPage} / {totalPages}
                </span>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Trang sau
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

export default CategoryPage

