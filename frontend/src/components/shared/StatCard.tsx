import React from 'react'

interface StatCardProps {
  title: string
  value: number | string
  highlighted?: boolean
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, highlighted = false }) => {
  return (
    <div
      className={`
        bg-white rounded-lg border-2 p-6 transition-all hover:shadow-md
        ${highlighted ? 'border-primary' : 'border-gray-200 hover:border-gray-300'}
      `}
    >
      <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
      <p className="text-4xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

