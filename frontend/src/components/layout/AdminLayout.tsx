import React, { ReactNode } from 'react'
import { AdminSidebar } from './AdminSidebar'
import { AdminTopBar } from './AdminTopBar'
import { SidebarProvider, useSidebar } from '../../contexts/SidebarContext'

interface AdminLayoutProps {
  title: string
  children: ReactNode
}

const AdminLayoutContent: React.FC<AdminLayoutProps> = ({ title, children }) => {
  const { isCollapsed } = useSidebar()
  const sidebarWidth = isCollapsed ? 'ml-16' : 'ml-64'

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminSidebar />
      <AdminTopBar title={title} />
      <main className={`${sidebarWidth} pt-16 transition-all duration-300`}>
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ title, children }) => {
  return (
    <SidebarProvider>
      <AdminLayoutContent title={title}>
        {children}
      </AdminLayoutContent>
    </SidebarProvider>
  )
}

