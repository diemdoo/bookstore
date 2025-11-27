import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PublicHeader } from '../../components/layout/PublicHeader'
import { PublicFooter } from '../../components/layout/PublicFooter'
import { EmptyState } from '../../components/shared/EmptyState'
import { Button } from '../../components/ui/Button'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { useCart } from '../../contexts/CartContext'
import { useToast } from '../../components/ui/Toast'
import { formatPrice } from '../../utils/formatters'
import { Minus, Plus, Trash2 } from 'lucide-react'

const CartPage: React.FC = () => {
  const { cart, updateCartItem, removeFromCart } = useCart()
  const navigate = useNavigate()
  const toast = useToast()
  const [selectedItems, setSelectedItems] = useState<number[]>([])
  const [dialogState, setDialogState] = useState({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {}
  })

  // Auto-select all items when cart loads or changes
  useEffect(() => {
    setSelectedItems(cart.map(item => item.id))
  }, [cart.length])


  const handleQuantityChange = async (cartItemId: number, newQuantity: number) => {
    if (newQuantity < 1) return
    await updateCartItem(cartItemId, newQuantity)
  }

  const handleRemove = async (cartItemId: number) => {
    setDialogState({
      isOpen: true,
      title: 'Xác nhận xóa',
      message: 'Bạn có chắc muốn xóa sản phẩm này?',
      onConfirm: async () => {
        await removeFromCart(cartItemId)
        toast.success('Đã xóa sản phẩm')
      }
    })
  }

  // Selection handlers
  const handleSelectAll = () => {
    if (selectedItems.length === cart.length) {
      setSelectedItems([]) // Deselect all
    } else {
      setSelectedItems(cart.map(item => item.id)) // Select all
    }
  }

  const handleSelectItem = (itemId: number) => {
    setSelectedItems(prev => {
      if (prev.includes(itemId)) {
        return prev.filter(id => id !== itemId)
      } else {
        return [...prev, itemId]
      }
    })
  }

  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) return
    
    const count = selectedItems.length
    setDialogState({
      isOpen: true,
      title: 'Xác nhận xóa',
      message: `Bạn có chắc muốn xóa ${count} sản phẩm đã chọn?`,
      onConfirm: async () => {
        try {
          // Delete all selected items
          await Promise.all(selectedItems.map(id => removeFromCart(id)))
          toast.success(`Đã xóa ${count} sản phẩm`)
          setSelectedItems([])
        } catch (error) {
          toast.error('Có lỗi khi xóa sản phẩm')
        }
      }
    })
  }

  // Calculate total for selected items only
  const getSelectedTotal = () => {
    return cart
      .filter(item => selectedItems.includes(item.id))
      .reduce((sum, item) => sum + (item.book.price * item.quantity), 0)
  }

  const selectedCount = selectedItems.length
  const isAllSelected = selectedItems.length === cart.length && cart.length > 0

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <PublicHeader />
        <main className="container mx-auto px-4 py-8 flex-1">
          <h1 className="text-2xl font-bold mb-6">GIỎ HÀNG</h1>
          <EmptyState 
            message="Giỏ hàng trống" 
            actionLabel="Tiếp tục mua sắm"
            onAction={() => navigate('/')}
          />
        </main>
        <PublicFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <PublicHeader />

      <main className="container mx-auto px-4 py-8 flex-1">
        <h1 className="text-2xl font-bold mb-6">GIỎ HÀNG ({cart.length} sản phẩm)</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-gray-100 p-4 rounded-lg flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox" 
                  className="rounded w-5 h-5 cursor-pointer"
                  checked={isAllSelected}
                  onChange={handleSelectAll}
                />
                <span className="font-medium">Chọn tất cả ({cart.length} sản phẩm)</span>
              </label>
              
              {selectedCount > 0 && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleDeleteSelected}
                >
                  Xóa ({selectedCount})
                </Button>
              )}
            </div>

            {cart.map((item) => (
              <div key={item.id} className="bg-white p-6 rounded-lg shadow">
                <div className="flex gap-4">
                  <input
                    type="checkbox"
                    className="w-5 h-5 mt-2 cursor-pointer rounded"
                    checked={selectedItems.includes(item.id)}
                    onChange={() => handleSelectItem(item.id)}
                  />
                  <img
                    src={item.book.image_url || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='}
                    alt={item.book.title}
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2U1ZTdlYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='
                    }}
                    className="w-24 h-32 object-cover rounded"
                  />
                  
                  <div className="flex-1">
                    <h3 className="font-medium text-lg mb-2">{item.book.title}</h3>
                    <p className="text-gray-600 mb-4">{formatPrice(item.book.price)}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                          className="w-8 h-8 rounded border hover:bg-gray-50"
                        >
                          <Minus className="h-4 w-4 mx-auto" />
                        </button>
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                          className="w-16 h-8 text-center border rounded"
                        />
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                          className="w-8 h-8 rounded border hover:bg-gray-50"
                        >
                          <Plus className="h-4 w-4 mx-auto" />
                        </button>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <span className="font-semibold text-primary">
                          {formatPrice(item.book.price * item.quantity)}
                        </span>
                        <button
                          onClick={() => handleRemove(item.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-lg shadow sticky top-4">
              <h2 className="font-semibold text-lg mb-4">Tóm tắt đơn hàng</h2>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span>Thành tiền</span>
                  <span className="font-semibold">{formatPrice(getSelectedTotal())}</span>
                </div>
                <div className="flex justify-between text-lg font-bold">
                  <span>Tổng số tiền (gồm VAT)</span>
                  <span className="text-primary">{formatPrice(getSelectedTotal())}</span>
                </div>
              </div>

              <Button
                onClick={() => navigate('/checkout')}
                className="w-full"
                disabled={selectedCount === 0}
              >
                THANH TOÁN ({selectedCount} sản phẩm)
              </Button>
            </div>
          </div>
        </div>
      </main>

      <PublicFooter />
      
      <ConfirmDialog
        isOpen={dialogState.isOpen}
        title={dialogState.title}
        message={dialogState.message}
        onConfirm={dialogState.onConfirm}
        onCancel={() => setDialogState({ ...dialogState, isOpen: false })}
        confirmText="Xóa"
        cancelText="Hủy"
        variant="danger"
      />
    </div>
  )
}

export default CartPage

