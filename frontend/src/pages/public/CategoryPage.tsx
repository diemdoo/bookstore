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
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
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
        
        // Fetch books in this category - only page 1 for initial load
        const decodedKey = decodeURIComponent(categoryKey)
        const booksData = await categoriesService.getCategoryBooks(decodedKey, {
          page: 1,
          per_page: perPage
        })
        
        setBooks(booksData.books)
        setTotalPages(booksData.pages)
        setCurrentPage(1)
        setHasMore(booksData.pages > 1)
      } catch (error) {
        console.error('Failed to fetch category data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [categoryKey])

  const handleLoadMore = async () => {
    if (loadingMore || !hasMore || !categoryKey) return
    
    const nextPage = currentPage + 1
    setLoadingMore(true)
    
    try {
      const decodedKey = decodeURIComponent(categoryKey)
      const booksData = await categoriesService.getCategoryBooks(decodedKey, {
        page: nextPage,
        per_page: perPage
      })
      
      // Append new books to existing array
      setBooks(prev => [...prev, ...booksData.books])
      setCurrentPage(nextPage)
      setHasMore(nextPage < booksData.pages)
    } catch (error) {
      console.error('Failed to load more books:', error)
    } finally {
      setLoadingMore(false)
    }
  }

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
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {books.map(book => (
                <BookCard key={book.id} book={book} compact showSold={true} />
              ))}
            </div>

            {/* Load More Button */}
            {hasMore && (
              <div className="flex justify-center mt-8">
                <button
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {loadingMore ? (
                    <>
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Đang tải...
                    </>
                  ) : (
                    'Xem Thêm'
                  )}
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

