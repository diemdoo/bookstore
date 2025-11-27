import React from 'react'
import { Button } from '../ui/Button'

interface EmptyStateProps {
  message: string
  actionLabel?: string
  onAction?: () => void
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  message,
  actionLabel,
  onAction,
  className = '',
}) => {
  return (
    <div className={`bg-white rounded-lg shadow p-12 text-center ${className}`}>
      <p className="text-gray-600 mb-4">{message}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  )
}

