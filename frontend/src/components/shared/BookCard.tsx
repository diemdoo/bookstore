import React from 'react'
import { useNavigate } from 'react-router-dom'
import { formatPrice } from '../../utils/formatters'
import type { Book } from '../../types'

interface BookCardProps {
  book: Book
  compact?: boolean
  showSold?: boolean
}

export const BookCard: React.FC<BookCardProps> = ({ book, compact = false, showSold = false }) => {
  const navigate = useNavigate()

  // Placeholder image (SVG data URL)
  const placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.src = placeholderImage
  }

  const handleClick = () => {
    if (book.category) {
      // Navigate to category-based book detail page
      const encodedCategory = encodeURIComponent(book.category)
      navigate(`/category/${encodedCategory}/books/${book.id}`)
    }
  }

  return (
    <div
      onClick={handleClick}
      className="group cursor-pointer"
    >
      <div className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 hover:border-primary hover:border">
        <div className="aspect-[3/4] overflow-hidden">
          <img
            src={book.image_url || placeholderImage}
            alt={book.title}
            onError={handleImageError}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className={`${compact ? 'px-2 py-1.5' : 'px-3 py-2'} bg-gray-50 border-t border-gray-100 space-y-0.5`}>
          <h3 className={`font-medium text-gray-900 ${compact ? 'text-xs' : 'text-sm'} text-center line-clamp-2 leading-tight`}>
            {book.title}
          </h3>
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
  )
}

