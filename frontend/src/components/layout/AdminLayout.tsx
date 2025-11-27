import React, { ReactNode } from 'react'
import { AdminSidebar } from './AdminSidebar'
import { AdminTopBar } from './AdminTopBar'

interface AdminLayoutProps {
  title: string
  children: ReactNode
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ title, children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <AdminSidebar />
      <AdminTopBar title={title} />
      <main className="ml-64 pt-16">
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}

