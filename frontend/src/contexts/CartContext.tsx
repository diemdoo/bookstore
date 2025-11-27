import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { cartService } from '../services/api'
import type { CartItem, CartContextType } from '../types'
import { useAuth } from './AuthContext'

const CartContext = createContext<CartContextType | undefined>(undefined)

export const useCart = (): CartContextType => {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}

interface CartProviderProps {
  children: ReactNode
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [cart, setCart] = useState<CartItem[]>([])
  const [loading, setLoading] = useState(false)
  const { user } = useAuth()

  const refreshCart = async () => {
    if (!user) {
      setCart([])
      return
    }
    
    try {
      setLoading(true)
      const cartItems = await cartService.getCart()
      setCart(cartItems)
    } catch (error) {
      console.error('Failed to fetch cart:', error)
      setCart([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshCart()
  }, [user])

  const addToCart = async (bookId: number, quantity: number) => {
    try {
      setLoading(true)
      await cartService.addToCart({ book_id: bookId, quantity })
      await refreshCart()
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const updateCartItem = async (cartItemId: number, quantity: number) => {
    try {
      setLoading(true)
      await cartService.updateCartItem(cartItemId, quantity)
      await refreshCart()
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const removeFromCart = async (cartItemId: number) => {
    try {
      setLoading(true)
      await cartService.removeFromCart(cartItemId)
      await refreshCart()
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const clearCart = async () => {
    try {
      setLoading(true)
      // Remove all items
      await Promise.all(cart.map(item => cartService.removeFromCart(item.id)))
      setCart([])
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const getTotalAmount = () => {
    return cart.reduce((total, item) => total + item.book.price * item.quantity, 0)
  }

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0)
  }

  const value: CartContextType = {
    cart,
    loading,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    refreshCart,
    getTotalAmount,
    getTotalItems,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

