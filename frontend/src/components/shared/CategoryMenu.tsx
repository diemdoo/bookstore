import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, ChevronDown } from 'lucide-react'
import { categoriesService } from '../../services/api'
import type { Category } from '../../types'

export const CategoryMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await categoriesService.getCategories()
        setCategories(data.categories)
      } catch (error) {
        console.error('Failed to fetch categories:', error)
      }
    }
    fetchCategories()
  }, [])

  const handleCategoryClick = (slug: string) => {
    navigate(`/category/${slug}`)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
      >
        <Menu className="h-5 w-5" />
        <span className="hidden md:inline">Danh Mục</span>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          {/* Dropdown */}
          <div className="absolute left-0 mt-2 w-64 bg-white rounded-lg shadow-xl border z-20 py-2">
            {categories.length === 0 ? (
              <div className="px-4 py-2 text-gray-500 text-sm">Đang tải...</div>
            ) : (
              categories.map((category) => (
                <button
                  key={category.key}
                  onClick={() => handleCategoryClick(category.slug)}
                  className="w-full text-left px-4 py-3 text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  {category.name}
                </button>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}

