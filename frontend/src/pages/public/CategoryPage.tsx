import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { BookCard } from '../../components/shared/BookCard'
import { Breadcrumb } from '../../components/ui/Breadcrumb'
import { booksService, categoriesService } from '../../services/api'
import { ChevronDown } from 'lucide-react'
import type { Book, Category } from '../../types'

const CategoryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  
  const [books, setBooks] = useState<Book[]>([])
  const [category, setCategory] = useState<Category | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [sortBy, setSortBy] = useState<string>('newest')
  const perPage = 20

  useEffect(() => {
    const fetchData = async () => {
      if (!slug) return
      
      try {
        setLoading(true)
        
        // Fetch category info by slug
        const categoriesData = await categoriesService.getCategories()
        const foundCategory = categoriesData.categories.find(c => c.slug === slug)
        setCategory(foundCategory || null)
        
        // Fetch books in this category - only page 1 for initial load
        const booksData = await categoriesService.getCategoryBooks(slug, {
          page: 1,
          per_page: perPage,
          sort_by: sortBy
        })
        
        setBooks(booksData.books)
        setTotalPages(booksData.pages)
        setCurrentPage(1)
        setHasMore(booksData.pages > 1)
        
        // Update category from API response if available
        if (booksData.category_name && !foundCategory) {
          setCategory({
            id: 0,
            key: booksData.category_key,
            name: booksData.category_name,
            slug: booksData.category_slug,
            is_active: true
          } as Category)
        }
      } catch (error) {
        console.error('Failed to fetch category data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug, sortBy])

  const handleLoadMore = async () => {
    if (loadingMore || !hasMore || !slug) return
    
    const nextPage = currentPage + 1
    setLoadingMore(true)
    
    try {
      const booksData = await categoriesService.getCategoryBooks(slug, {
        page: nextPage,
        per_page: perPage,
        sort_by: sortBy
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
    { label: category?.name || slug || 'Danh Mục' }
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
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{category.name}</h1>
            {category.description && (
              <p className="text-gray-600">{category.description}</p>
            )}
          </div>
          
          {/* Sort Dropdown */}
          <div className="relative flex-shrink-0">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-br from-white to-gray-50 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer group">
              <span className="text-sm text-gray-600 font-medium">
                Sắp xếp:
              </span>
              <select
                id="sort-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="appearance-none bg-transparent text-sm font-medium text-gray-900 focus:outline-none cursor-pointer pr-6"
                style={{ 
                  backgroundImage: 'none',
                  WebkitAppearance: 'none',
                  MozAppearance: 'none'
                }}
              >
                <option value="newest" className="py-2 px-3 hover:bg-primary-50">Mới nhất</option>
                <option value="price_asc" className="py-2 px-3 hover:bg-primary-50">Giá thấp nhất</option>
                <option value="price_desc" className="py-2 px-3 hover:bg-primary-50">Giá cao nhất</option>
                <option value="bestseller" className="py-2 px-3 hover:bg-primary-50">Bán chạy nhất</option>
              </select>
              <ChevronDown className="h-4 w-4 text-gray-400 absolute right-3 pointer-events-none group-hover:text-primary transition-colors" />
            </div>
          </div>
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
                <BookCard key={book.id} book={book} compact showSold={true} categorySlug={slug} />
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

