import React, { useEffect, useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { BookCard } from '../../components/shared/BookCard'
import { booksService, bannersService, categoriesService } from '../../services/api'
import type { Book, Banner, Category } from '../../types'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const HomePage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const searchQuery = searchParams.get('search') || ''
  
  const [bestSellers, setBestSellers] = useState<Book[]>([])
  const [banners, setBanners] = useState<Banner[]>([])
  const [categorySections, setCategorySections] = useState<Array<{ category: Category, books: Book[] }>>([])
  const [searchResults, setSearchResults] = useState<Book[]>([])
  const [searchTotal, setSearchTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchLoading, setSearchLoading] = useState(false)
  const [currentSlide, setCurrentSlide] = useState(0)

  // Fetch search results when search query exists
  useEffect(() => {
    if (searchQuery.trim()) {
      const fetchSearchResults = async () => {
        try {
          setSearchLoading(true)
          const data = await booksService.getBooks({
            search: searchQuery,
            page: 1,
            per_page: 20
          })
          setSearchResults(data.books)
          setSearchTotal(data.total)
        } catch (error) {
          console.error('Failed to fetch search results:', error)
          setSearchResults([])
          setSearchTotal(0)
        } finally {
          setSearchLoading(false)
        }
      }
      fetchSearchResults()
    } else {
      setSearchResults([])
      setSearchTotal(0)
    }
  }, [searchQuery])

  useEffect(() => {
    // Only fetch normal homepage data if not searching
    if (searchQuery.trim()) {
      setLoading(false)
      return
    }

    const fetchData = async () => {
      try {
        // Fetch best sellers (10 books) and banners in parallel
        const [bestSellersData, bannersData] = await Promise.all([
          booksService.getBestSellers(10),
          bannersService.getBanners('all')
        ])
        
        setBestSellers(bestSellersData.books)
        setBanners(bannersData.banners)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [searchQuery])

  // Fetch category sections separately (only when not searching)
  useEffect(() => {
    if (searchQuery.trim()) {
      return
    }

    const fetchCategoryBooks = async () => {
      try {
        // Fetch categories (already filtered, no 'Sach Ban Chay')
        const categoriesData = await categoriesService.getCategories()
        
        // Fetch 10 books per category in parallel (2 rows x 5 columns)
        const sectionsData = await Promise.all(
          categoriesData.categories.map(async (category) => {
            const booksData = await booksService.getBooks({
              page: 1,
              per_page: 10,
              category: category.key
            })
            return { category, books: booksData.books }
          })
        )
        
        setCategorySections(sectionsData)
      } catch (error) {
        console.error('Failed to fetch category sections:', error)
      }
    }

    fetchCategoryBooks()
  }, [searchQuery])

  // Separate banners by position
  const mainBanners = banners.filter(b => b.position === 'main')
  const sideBanners = banners.filter(b => b.position === 'side_top' || b.position === 'side_bottom')

  useEffect(() => {
    if (mainBanners.length === 0) return
    
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % mainBanners.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [mainBanners.length])

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % mainBanners.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + mainBanners.length) % mainBanners.length)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        {/* Search Results Section */}
        {searchQuery.trim() ? (
          <div className="mb-12">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Kết quả tìm kiếm cho "{searchQuery}"
              </h1>
              <p className="text-gray-600">
                Tìm thấy {searchTotal} {searchTotal === 1 ? 'sách' : 'sách'}
              </p>
            </div>
            
            {searchLoading ? (
              <div className="text-center py-12">Đang tải...</div>
            ) : searchResults.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                Không tìm thấy sách nào với từ khóa "{searchQuery}"
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                {searchResults.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Hero Carousel Section */}
            <div className="flex gap-6 mb-12">
          {/* Main Carousel */}
          <div className="flex-1 relative">
            <div className="relative h-[400px] rounded-lg overflow-hidden">
              {mainBanners.length > 0 ? (
                <>
                  {mainBanners.map((banner, index) => (
                    <div
                      key={banner.id}
                      className={`absolute inset-0 transition-opacity duration-500 ${
                        index === currentSlide ? 'opacity-100' : 'opacity-0'
                      }`}
                      style={{
                        backgroundColor: banner.bg_color,
                        color: banner.text_color,
                      }}
                    >
                      {banner.image_url ? (
                        <div className="relative w-full h-full">
                          <img 
                            src={banner.image_url} 
                            alt={banner.title}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                            <div className="text-center">
                              <h2 className="text-5xl font-bold text-white mb-2">{banner.title}</h2>
                              {banner.description && (
                                <p className="text-xl text-white/90">{banner.description}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <div className="text-center">
                            <h2 className="text-5xl font-bold mb-2">{banner.title}</h2>
                            {banner.description && (
                              <p className="text-xl opacity-90">{banner.description}</p>
                            )}
                          </div>
                        </div>
                      )}
                      {banner.link && (
                        <div 
                          onClick={(e) => {
                            e.preventDefault()
                            if (banner.link) {
                              // Handle internal routes (starting with /) vs external URLs
                              if (banner.link.startsWith('/')) {
                                navigate(banner.link)
                              } else {
                                window.location.href = banner.link
                              }
                            }
                          }}
                          className="absolute inset-0 cursor-pointer"
                          aria-label={banner.title}
                        />
                      )}
                    </div>
                  ))}
                  
                  {/* Arrow Buttons - Only show if more than 1 banner */}
                  {mainBanners.length > 1 && (
                    <>
                      <button
                        onClick={prevSlide}
                        className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/80 hover:bg-white rounded-full flex items-center justify-center shadow-lg z-10"
                      >
                        <ChevronLeft className="h-6 w-6 text-gray-800" />
                      </button>
                      <button
                        onClick={nextSlide}
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/80 hover:bg-white rounded-full flex items-center justify-center shadow-lg z-10"
                      >
                        <ChevronRight className="h-6 w-6 text-gray-800" />
                      </button>
                      
                      {/* Dot Indicators */}
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
                        {mainBanners.map((_, index) => (
                          <button
                            key={index}
                            onClick={() => setCurrentSlide(index)}
                            className={`w-3 h-3 rounded-full transition-all ${
                              index === currentSlide ? 'bg-white w-8' : 'bg-white/50'
                            }`}
                          />
                        ))}
                      </div>
                    </>
                  )}
                </>
              ) : (
                <div className="flex items-center justify-center h-full bg-gradient-to-r from-blue-500 to-purple-600 text-white text-3xl font-bold">
                  Chưa có banner
                </div>
              )}
            </div>
          </div>

          {/* Side Banners */}
          <div className="flex flex-col gap-4">
            {sideBanners.slice(0, 2).map((banner) => (
              <div 
                key={banner.id}
                className="w-96 h-[192px] rounded-lg overflow-hidden relative cursor-pointer"
                style={{
                  backgroundColor: banner.bg_color,
                  color: banner.text_color,
                }}
                onClick={() => {
                  if (banner.link) {
                    // Handle internal routes (starting with /) vs external URLs
                    if (banner.link.startsWith('/')) {
                      navigate(banner.link)
                    } else {
                      window.open(banner.link, '_blank')
                    }
                  }
                }}
              >
                {banner.image_url ? (
                  <div className="relative w-full h-full">
                    <img 
                      src={banner.image_url} 
                      alt={banner.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      <h3 className="text-2xl font-bold text-white">{banner.title}</h3>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <h3 className="text-2xl font-bold">{banner.title}</h3>
                  </div>
                )}
              </div>
            ))}
            {sideBanners.length === 0 && (
              <>
                <div className="w-96 h-[192px] rounded-lg bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white text-2xl font-bold">
                  SALE EXAMPLE
                </div>
                <div className="w-96 h-[192px] rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center text-white text-2xl font-bold">
                  SALE EXAMPLE
                </div>
              </>
            )}
          </div>
        </div>

        {/* Best Sellers Section */}
        <div className="mb-12">
          <div className="bg-primary h-15 flex items-center px-6 mb-6 rounded-t-lg">
            <h2 className="text-white text-xl font-semibold uppercase">
              SẢN PHẨM BÁN CHẠY
            </h2>
          </div>
          
          {loading ? (
            <div className="text-center py-12">Đang tải...</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
              {bestSellers.map((book) => (
                <BookCard key={book.id} book={book} showSold />
              ))}
            </div>
          )}
        </div>

        {/* Category Sections */}
        {categorySections.map(({ category, books: categoryBooks }) => (
          <div key={category.key} className="mb-12">
            <div className="bg-primary h-15 flex items-center px-6 mb-6 rounded-t-lg">
              <h2 className="text-white text-xl font-semibold uppercase">
                {category.name}
              </h2>
            </div>
            
            {categoryBooks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Chưa có sách trong danh mục này
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                  {categoryBooks.map((book) => (
                    <BookCard key={book.id} book={book} showSold categorySlug={category.slug} />
                  ))}
                </div>
                
                <div className="flex justify-center mt-6">
                  <Link
                    to={`/category/${category.slug}`}
                    className="px-6 py-2 border-2 border-primary text-primary rounded-lg font-semibold hover:bg-primary hover:text-white transition-colors flex items-center gap-2"
                  >
                    Xem Thêm
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </>
            )}
          </div>
        ))}
          </>
        )}
      </main>

      <PublicFooter />
    </div>
  )
}

export default HomePage

