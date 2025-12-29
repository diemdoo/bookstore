import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatPrice } from '../../utils/formatters'
import { categoriesService } from '../../services/api'
import type { Book } from '../../types'

interface BookCardProps {
  book: Book
  compact?: boolean
  showSold?: boolean
  categorySlug?: string // Category slug để build URL với category context
}

export const BookCard: React.FC<BookCardProps> = ({ book, compact = false, showSold = false, categorySlug }) => {
  const navigate = useNavigate()
  const [resolvedCategorySlug, setResolvedCategorySlug] = useState<string | undefined>(categorySlug)

  // Placeholder image (SVG data URL)
  const placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='

  // Resolve category slug from book.category (key) if not provided
  useEffect(() => {
    if (!categorySlug && book.category) {
      categoriesService.getCategories()
        .then(data => {
          const foundCategory = data.categories.find(c => c.key === book.category)
          if (foundCategory) {
            setResolvedCategorySlug(foundCategory.slug)
          }
        })
        .catch(() => {
          // Silently fail, will use fallback URL
        })
    }
  }, [categorySlug, book.category])

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.src = placeholderImage
  }

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault() // Prevent any default behavior
    e.stopPropagation() // Stop event bubbling
    
    // Error handling: Check if slug exists
    if (!book.slug) {
      console.error('ERROR: Book slug is missing!', book)
      return
    }
    
    // Navigate to book detail page with category context
    const catSlug = categorySlug || resolvedCategorySlug
    const targetUrl = catSlug 
      ? `/category/${catSlug}/books/${book.slug}` 
      : `/books/${book.slug}`
    
    navigate(targetUrl)
  }

  return (
    <div
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleClick(e as any)
        }
      }}
      role="button"
      tabIndex={0}
      aria-label={`Xem chi tiết sách ${book.title}`}
      className="group cursor-pointer h-full"
      style={{ cursor: 'pointer' }} // Force cursor style to override any CSS conflicts
    >
      <div className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 hover:border-primary hover:border h-full flex flex-col">
        <div className="w-full aspect-[3/4] overflow-hidden flex-shrink-0">
          <img
            src={book.image_url || placeholderImage}
            alt={book.title}
            onError={handleImageError}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className={`${compact ? 'px-2 py-1.5' : 'px-3 py-2'} bg-gray-50 border-t border-gray-100 flex-1 flex flex-col`}>
          <h3 className={`font-medium text-gray-900 ${compact ? 'text-xs' : 'text-sm'} text-center line-clamp-2 leading-tight mb-1`}>
            {book.title}
          </h3>
          <div className="mt-auto">
            <p className={`text-primary font-semibold ${compact ? 'text-base' : 'text-lg'} text-center`}>
              {formatPrice(book.price)}
            </p>
            {showSold && book.sold !== undefined && book.sold > 0 && (
              <p className="text-gray-500 text-xs text-center mt-1">
                Đã bán {book.sold}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

