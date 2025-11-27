import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'

export interface BreadcrumbItem {
  label: string
  href?: string // undefined means current page (not clickable)
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav className="flex items-center space-x-2 text-sm mb-6">
      {items.map((item, index) => {
        const isLast = index === items.length - 1

        return (
          <React.Fragment key={index}>
            {item.href && !isLast ? (
              <Link
                to={item.href}
                className="text-gray-600 hover:text-primary transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className={isLast ? 'text-gray-900 font-medium' : 'text-gray-600'}>
                {item.label}
              </span>
            )}
            
            {!isLast && (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}

