# 08 - Luồng Đặt Hàng (Order Flow)

## 🛒 Tổng Quan

Luồng đặt hàng là **core business process** của hệ thống, bao gồm:

### Customer Flow:
1. Browse books → Add to cart (with item selection)
2. View & manage cart (select items, update, delete)
3. Checkout with shipping info (only selected items)
4. Create order (transaction)
5. View order history & track status

### Admin Flow:
1. View all orders
2. Update order status (Pending → Confirmed → Completed/Cancelled)
3. Update payment status (Pending → Paid)
4. Filter & search orders

## 📊 Sequence Diagrams

### Customer Order Flow
**Xem diagram chi tiết:** [`diagrams/customer-order-flow.mmd`](diagrams/customer-order-flow.mmd)

Diagram này bao gồm:
- Browse books với pagination (5x3 grid, "Xem Thêm")
- Add to cart với authentication check
- Cart management với item selection checkboxes
- Bulk delete selected items
- Checkout với selected items only
- Backend transaction: Create order + order items + update stock + clear cart
- View order history với COD badge & status badge

### Admin Order Management Flow
**Xem diagram chi tiết:** [`diagrams/admin-order-management-flow.mmd`](diagrams/admin-order-management-flow.mmd)

Diagram này bao gồm:
- View all orders với customer info
- View order details modal
- Update order status workflow
- Update payment status (independent)
- Filter & search functionality

## 🔄 Complete Order Flow Overview

```mermaid
graph TD
    Start([Customer places order]) --> CreateItems
    CreateItems --> UpdateStock[Update Book Stock]
    UpdateStock --> ClearCart[Clear Cart]
    ClearCart --> CommitTx[COMMIT TRANSACTION]
    
    CommitTx --> OrderSuccess[Order Created]
    OrderSuccess --> RedirectOrders[Redirect to /orders]
    RedirectOrders --> ViewOrders[View Order History<br/>GET /api/orders]
    
    ViewOrders --> OrderDetail[View Order Detail]
    OrderDetail --> CheckStatus{Order Status?}
    
    CheckStatus -->|Pending| Pending[🟡 Chờ xác nhận]
    CheckStatus -->|Confirmed| Confirmed[🔵 Đã xác nhận]
    CheckStatus -->|Completed| Completed[🟢 Hoàn thành]
    CheckStatus -->|Cancelled| Cancelled[🔴 Đã hủy]
    
    Pending --> AdminAction[Admin reviews order]
    AdminAction --> UpdateStatus[Admin updates status<br/>PUT /api/admin/orders/:id]
    UpdateStatus --> Confirmed
    Confirmed --> Ship[Shipping process]
    Ship --> Completed
    
    Completed --> End([End])
    Cancelled --> End
    
    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Workflow fill:#fff4e1
    style OrderSuccess fill:#e1f0ff
```

## 🔄 Detailed Step-by-Step Flows

### 1. Add to Cart Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant FE as Frontend
    participant Cart as CartContext
    participant BE as Backend
    participant DB as Database
    
    C->>FE: Click book card
    FE->>BE: GET /api/books/:id
    BE->>DB: SELECT book WHERE id=?
    DB-->>BE: Book data
    BE-->>FE: Book details
    FE-->>C: Show BookDetailPage
    
    C->>FE: Enter quantity (default: 1)
    C->>FE: Click "Thêm vào giỏ"
    
    FE->>Cart: addToCart(bookId, quantity)
    Cart->>BE: POST /api/cart<br/>{book_id, quantity}
    
    BE->>BE: @login_required<br/>Get user_id from session
    BE->>DB: Check if book in cart?<br/>SELECT * FROM cart<br/>WHERE user_id=? AND book_id=?
    
    alt Book already in cart
        BE->>DB: UPDATE cart<br/>SET quantity = quantity + ?<br/>WHERE id=?
    else New book
        BE->>DB: INSERT INTO cart<br/>(user_id, book_id, quantity)
    end
    
    DB-->>BE: Success
    BE-->>Cart: 201 Created<br/>{cart_item: {...}}
    
    Cart->>Cart: Update cartItems state
    Cart->>FE: Toast.success("Đã thêm vào giỏ")
    FE-->>C: Show success toast<br/>Cart badge updated
```

### 2. Cart Management Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant FE as Frontend
    participant Cart as CartContext
    participant BE as Backend
    participant DB as Database
    
    C->>FE: Click cart icon
    FE->>Cart: Access cartItems
    
    alt Cart empty
        Cart->>FE: cartItems = []
        FE-->>C: Show "Giỏ hàng trống"
    end
    
    Note over C,DB: View Cart
    Cart->>BE: GET /api/cart
    BE->>DB: SELECT cart.*, books.*<br/>FROM cart<br/>JOIN books ON cart.book_id = books.id<br/>WHERE cart.user_id = ?
    DB-->>BE: Cart items with book details
    BE-->>Cart: {cart_items: [...]}
    Cart->>Cart: setCartItems(data)
    FE-->>C: Display cart with items
    
    Note over C,DB: Update Quantity
    C->>FE: Change quantity input
    C->>FE: Click "Cập nhật"
    FE->>Cart: updateQuantity(itemId, newQty)
    Cart->>BE: PUT /api/cart/:id<br/>{quantity: newQty}
    
    BE->>BE: Validate quantity > 0
    BE->>DB: UPDATE cart<br/>SET quantity = ?<br/>WHERE id = ? AND user_id = ?
    DB-->>BE: Success
    BE-->>Cart: 200 OK
    
    Cart->>Cart: Update local cartItems
    Cart->>Cart: Recalculate total price
    FE-->>C: Update UI with new total
    
    Note over C,DB: Remove Item
    C->>FE: Click "Xóa"
    FE->>Cart: removeFromCart(itemId)
    Cart->>BE: DELETE /api/cart/:id
    BE->>DB: DELETE FROM cart<br/>WHERE id = ? AND user_id = ?
    DB-->>BE: Success
    BE-->>Cart: 200 OK
    
    Cart->>Cart: Remove from cartItems
    Cart->>Cart: Recalculate total
    FE-->>C: Item removed, UI updated
```

### 2.1. Item Selection in Cart

**Feature Overview:**

Giỏ hàng hỗ trợ chức năng select/deselect từng item, cho phép khách hàng:
- Chọn sản phẩm để thanh toán (giống Shopee/Lazada)
- Xóa nhiều sản phẩm cùng lúc
- Tổng tiền chỉ tính các sản phẩm được chọn

**Key Features:**
- Mỗi cart item có checkbox riêng
- Checkbox "Chọn tất cả" để select/deselect tất cả items
- Chỉ items được chọn mới được tính vào tổng tiền
- Chỉ items được chọn mới được checkout
- Button "Xóa (X)" xuất hiện khi có ≥1 item selected
- Checkout button hiển thị: "THANH TOÁN (X sản phẩm)"
- Checkout button disabled nếu không có item nào được chọn
- Default state: Tất cả items được chọn khi vào trang

**Implementation Details:**

```typescript
// CartPage.tsx - State management
const [selectedItems, setSelectedItems] = useState<number[]>([])

// Auto-select all items when cart loads
useEffect(() => {
  setSelectedItems(cart.map(item => item.id))
}, [cart.length])

// Select all/deselect all toggle
const handleSelectAll = () => {
  if (selectedItems.length === cart.length) {
    setSelectedItems([]) // Deselect all
  } else {
    setSelectedItems(cart.map(item => item.id)) // Select all
  }
}

// Toggle individual item selection
const handleSelectItem = (itemId: number) => {
  setSelectedItems(prev => {
    if (prev.includes(itemId)) {
      return prev.filter(id => id !== itemId)
    } else {
      return [...prev, itemId]
    }
  })
}

// Delete multiple selected items
const handleDeleteSelected = async () => {
  if (selectedItems.length === 0) return
  
  if (confirm(`Bạn có chắc muốn xóa ${selectedItems.length} sản phẩm đã chọn?`)) {
    try {
      await Promise.all(selectedItems.map(id => removeFromCart(id)))
      toast.success(`Đã xóa ${selectedItems.length} sản phẩm`)
      setSelectedItems([])
    } catch (error) {
      toast.error('Có lỗi khi xóa sản phẩm')
    }
  }
}

// Calculate total for selected items only
const getSelectedTotal = () => {
  return cart
    .filter(item => selectedItems.includes(item.id))
    .reduce((sum, item) => sum + (item.book.price * item.quantity), 0)
}
```

**User Flow:**

```mermaid
flowchart TD
    A[User visits /cart] --> B{Cart has items?}
    B -->|No| C[Show empty cart message]
    B -->|Yes| D[Load all items]
    
    D --> E[Auto-select ALL items]
    E --> F[Display cart with checkboxes]
    
    F --> G{User action?}
    
    G -->|Click individual checkbox| H[Toggle item selection]
    H --> I[Update selectedItems state]
    I --> J[Recalculate total for selected items]
    J --> F
    
    G -->|Click Chọn tất cả| K{All selected?}
    K -->|Yes| L[Deselect all items]
    K -->|No| M[Select all items]
    L --> J
    M --> J
    
    G -->|Click Xóa button| N{Any items selected?}
    N -->|No| F
    N -->|Yes| O[Show confirmation dialog]
    O -->|Confirm| P[Delete all selected items]
    O -->|Cancel| F
    P --> Q[Show success toast]
    Q --> R[Reload cart]
    R --> E
    
    G -->|Click THANH TOÁN| S{Any items selected?}
    S -->|No| T[Button disabled]
    T --> F
    S -->|Yes| U[Navigate to /checkout]
    U --> V[Show CheckoutPage]
```

**UI/UX Notes:**

1. **Checkbox "Chọn tất cả":**
   - Màu xám khi không có item nào được chọn
   - Checked khi TẤT CẢ items được chọn
   - Button "Xóa (X)" hiện bên phải khi có items được chọn

2. **Individual Checkboxes:**
   - Mỗi cart item row có checkbox ở bên trái
   - Checkbox size: `w-5 h-5` cho dễ click
   - Cursor pointer cho UX tốt hơn

3. **Total Amount:**
   - Chỉ tính tổng tiền của items được chọn
   - Auto-update ngay khi user select/deselect

4. **Checkout Button:**
   - Disabled (gray) khi không có item nào được chọn
   - Hiển thị số lượng items: "THANH TOÁN (3 sản phẩm)"
   - Active (green) khi có ≥1 item selected

5. **Delete Selected Button:**
   - Chỉ hiện khi có ≥1 item được chọn
   - Màu đỏ (danger variant)
   - Hiển thị số lượng: "Xóa (5)"

### 3. Checkout & Order Creation Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant FE as Frontend
    participant BE as Backend (Route)
    participant BL as Business Logic<br/>(OrderWorkflow)
    participant DB as Database
    
    C->>FE: Click "Thanh toán"
    FE->>FE: Navigate to /checkout
    FE-->>C: Show CheckoutPage
    
    C->>FE: Fill shipping address
    C->>FE: Fill phone number
    C->>FE: Review order summary
    C->>FE: Click "Đặt hàng"
    
    FE->>FE: Validate:<br/>- Address not empty?<br/>- Phone valid format?
    
    FE->>BE: POST /api/orders<br/>{shipping_address}
    
    BE->>BE: @login_required<br/>Get user_id from session
    
    Note over BE,DB: BEGIN TRANSACTION (trong route function)
    BE->>DB: db.session.begin()
    
    Note over BE,DB: Step 1: Get cart items (query trực tiếp)
    BE->>DB: Cart.query.filter_by(user_id=?).join(Book).all()
    DB-->>BE: Cart items (with book data)
    
    alt Cart is empty
        BE->>DB: db.session.rollback()
        BE-->>FE: 400 Bad Request<br/>{error: "Giỏ hàng trống"}
        FE-->>C: Show error
    end
    
    Note over BE,DB: Step 2: Validate stock
    loop For each cart item
        BE->>BE: Check book.stock >= item.quantity?
        alt Insufficient stock
            BE->>DB: db.session.rollback()
            BE-->>FE: 400 Bad Request<br/>{error: "Sách X không đủ hàng"}
            FE-->>C: Show error
        end
    end
    
    Note over BE,DB: Step 3: Calculate total
    BE->>BE: total = SUM(item.quantity * book.price)
    
    Note over BE,DB: Step 4: Create Order (trực tiếp)
    BE->>BE: new_order = Order(user_id, total_amount, ...)
    BE->>DB: db.session.add(new_order)
    BE->>DB: db.session.flush()  # Để lấy order.id
    
    Note over BE,DB: Step 5: Create Order Items (trực tiếp)
    loop For each cart item
        BE->>BE: order_item = OrderItem(order_id, book_id, quantity, price)
        BE->>DB: db.session.add(order_item)
    end
    
    Note over BE,DB: Step 6: Update Stock (trực tiếp)
    loop For each cart item
        BE->>DB: book.stock -= item.quantity
    end
    
    Note over BE,DB: Step 7: Clear Cart (trực tiếp)
    BE->>DB: Cart.query.filter_by(user_id=?).delete()
    
    Note over BE,DB: COMMIT TRANSACTION
    BE->>DB: db.session.commit()
    DB-->>BE: Transaction successful
    
    Note over BE: Convert to dict trực tiếp
    BE->>BE: order.to_dict()
    
    BE-->>FE: 201 Created<br/>{message: "Đặt hàng thành công",<br/>order: {...}}
    
    FE->>FE: CartContext.clearCart()
    FE->>FE: Toast.success("Đặt hàng thành công!")
    FE->>FE: Navigate to '/orders'
    
    FE-->>C: Show order history page
```

### 4. View Order History Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    
    C->>FE: Click "Đơn hàng của tôi"
    FE->>BE: GET /api/orders
    
    BE->>BE: @login_required<br/>Get user_id
    BE->>DB: SELECT orders.*<br/>FROM orders<br/>WHERE user_id = ?<br/>ORDER BY created_at DESC
    DB-->>BE: Orders list
    
    BE->>DB: For each order:<br/>SELECT order_items.*, books.*<br/>FROM order_items<br/>JOIN books ON order_items.book_id = books.id<br/>WHERE order_id = ?
    DB-->>BE: Order items with book details
    
    BE-->>FE: {orders: [{...items: [...]}, ...]}
    FE-->>C: Display order history
    
    Note over C,FE: Order Status Colors
    FE->>FE: pending → 🟡 Yellow badge
    FE->>FE: confirmed → 🔵 Blue badge
    FE->>FE: completed → 🟢 Green badge
    FE->>FE: cancelled → 🔴 Red badge
    
    C->>FE: Click order to view details
    FE->>BE: GET /api/orders/:id
    BE->>DB: SELECT order with items<br/>WHERE id = ? AND user_id = ?
    DB-->>BE: Order details
    BE-->>FE: {order: {...}}
    FE-->>C: Show full order details:<br/>- Order info<br/>- Items list<br/>- Total amount<br/>- Status<br/>- Shipping address
```

### 5. Admin Order Management Flow

```mermaid
sequenceDiagram
    participant A as Admin
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant Email as Email System<br/>(Future)
    
    A->>FE: Navigate to /admin/orders
    FE->>BE: GET /api/admin/orders
    
    BE->>BE: @admin_required<br/>Check role
    BE->>DB: SELECT orders.*,<br/>users.username, users.full_name<br/>FROM orders<br/>JOIN users ON orders.user_id = users.id<br/>ORDER BY created_at DESC
    DB-->>BE: All orders (all customers)
    
    BE-->>FE: {orders: [...]}
    FE-->>A: Display all orders table
    
    Note over A,DB: View Order Detail
    A->>FE: Click order
    FE->>BE: GET /api/orders/:id
    BE->>DB: SELECT order with items and customer info
    DB-->>BE: Order details
    BE-->>FE: {order: {...}}
    FE-->>A: Show order modal/page:<br/>- Customer info<br/>- Items<br/>- Total<br/>- Address<br/>- Phone<br/>- Current status
    
    Note over A,DB: Update Order Status
    A->>FE: Click "Cập nhật trạng thái"
    FE-->>A: Show status dropdown:<br/>- Pending<br/>- Confirmed<br/>- Completed<br/>- Cancelled
    
    A->>FE: Select new status (e.g., "Confirmed")
    FE->>BE: PUT /api/admin/orders/:id<br/>{status: "confirmed"}
    
    BE->>BE: @admin_required
    BE->>BE: Validate status value
    BE->>DB: UPDATE orders<br/>SET status = ?,<br/>    updated_at = NOW()<br/>WHERE id = ?
    DB-->>BE: Success
    
    BE-->>FE: 200 OK<br/>{message: "Cập nhật thành công"}
    FE->>FE: Toast.success("Đã cập nhật trạng thái")
    FE->>FE: Refresh order list
    
    opt Send Email Notification (Future)
        BE->>Email: Send status update email<br/>to customer
    end
    
    FE-->>A: Updated order list
```

## 🔍 Order Status Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Order created
    
    Pending --> Confirmed: Admin confirms
    Pending --> Cancelled: Customer/Admin cancels
    
    Confirmed --> Completed: Order delivered
    Confirmed --> Cancelled: Issue occurred
    
    Completed --> [*]
    Cancelled --> [*]
    
    note right of Pending
        🟡 Chờ xác nhận
        - Newly created order
        - Awaiting admin review
    end note
    
    note right of Confirmed
        🔵 Đã xác nhận
        - Admin approved
        - Ready for shipping
    end note
    
    note right of Completed
        🟢 Hoàn thành
        - Successfully delivered
        - Customer received
    end note
    
    note right of Cancelled
        🔴 Đã hủy
        - Customer cancelled
        - Admin cancelled
        - Payment failed
        - Out of stock
    end note
```

## 💾 Database Operations

### Cart Operations

```sql
-- Add to cart (if not exists)
INSERT INTO cart (user_id, book_id, quantity, created_at)
VALUES (?, ?, ?, NOW());

-- Add to cart (if exists, update quantity)
UPDATE cart 
SET quantity = quantity + ?
WHERE user_id = ? AND book_id = ?;

-- Get cart with book details
SELECT cart.id, cart.quantity, cart.created_at,
       books.id as book_id, books.title, books.author, 
       books.price, books.image_url, books.stock
FROM cart
JOIN books ON cart.book_id = books.id
WHERE cart.user_id = ?;

-- Update cart item quantity
UPDATE cart 
SET quantity = ?
WHERE id = ? AND user_id = ?;

-- Remove from cart
DELETE FROM cart 
WHERE id = ? AND user_id = ?;

-- Clear cart (after order)
DELETE FROM cart 
WHERE user_id = ?;
```

### Order Operations

```sql
-- Create order
INSERT INTO orders (
    user_id, total_amount, status, payment_status,
    shipping_address, phone, created_at, updated_at
) VALUES (?, ?, 'pending', 'pending', ?, ?, NOW(), NOW())
RETURNING id;

-- Create order items
INSERT INTO order_items (order_id, book_id, quantity, price)
VALUES (?, ?, ?, ?);

-- Update book stock
UPDATE books 
SET stock = stock - ?
WHERE id = ?;

-- Get customer orders
SELECT o.*, 
       COUNT(oi.id) as item_count,
       SUM(oi.quantity) as total_items
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = ?
GROUP BY o.id
ORDER BY o.created_at DESC;

-- Get order with items
SELECT o.*,
       u.username, u.full_name, u.email,
       oi.id as item_id, oi.quantity, oi.price,
       b.id as book_id, b.title, b.author, b.image_url
FROM orders o
JOIN users u ON o.user_id = u.id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN books b ON oi.book_id = b.id
WHERE o.id = ?;

-- Update order status (Admin)
UPDATE orders 
SET status = ?, updated_at = NOW()
WHERE id = ?;
```

## 🔒 Business Rules & Validation

### Cart Validation
- ✅ User must be logged in
- ✅ Book must exist
- ✅ Quantity must be > 0
- ✅ Quantity cannot exceed stock

### Checkout Validation
- ✅ Cart must not be empty
- ✅ Shipping address required (not empty)
- ✅ Phone number required (10-11 digits)
- ✅ All books must have sufficient stock
- ✅ Total amount must be > 0

### Order Workflow Constraints
- ✅ **Atomic transaction**: All steps succeed or all rollback
- ✅ **Stock consistency**: Prevent overselling
- ✅ **Cart clearing**: Automatic after successful order
- ✅ **Price snapshot**: Use current price at order time

### Status Update Rules
- ✅ Only admin can update status
- ✅ Valid status values: pending, confirmed, completed, cancelled
- ✅ Status transitions should be logical (pending → confirmed → completed)

## 🎯 Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| **"Giỏ hàng trống"** | Cart empty at checkout | Add items first |
| **"Sách X không đủ hàng"** | Book stock < quantity | Reduce quantity or wait |
| **"Yêu cầu đăng nhập"** | User not authenticated | Login first |
| **"Địa chỉ không được để trống"** | Missing shipping address | Fill address |
| **"Số điện thoại không hợp lệ"** | Invalid phone format | Use 10-11 digits |

### Transaction Rollback Scenarios

```python
# OrderWorkflow.create_order_with_items()
try:
    db.session.begin()
    
    # Step 1-7...
    
    db.session.commit()
except Exception as e:
    db.session.rollback()  # ← Automatic rollback on any error
    raise e
```

**Rollback triggers:**
- Cart empty
- Insufficient stock
- Invalid data
- Database error
- Any exception during workflow

## 📊 Performance Considerations

### Optimization Strategies

1. **Batch Queries**: Fetch all order items in single query (JOIN)
2. **Indexes**: 
   - `cart(user_id, book_id)` - Composite index
   - `orders(user_id, created_at)` - List orders fast
   - `order_items(order_id)` - Join performance
3. **Transaction Scope**: Minimize transaction duration
4. **Pagination**: Limit orders per page (20 items)

### Query Performance

```sql
-- Efficient: Get orders with item count
EXPLAIN ANALYZE
SELECT o.id, o.total_amount, o.status, 
       COUNT(oi.id) as items
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = 123
GROUP BY o.id
LIMIT 20;

-- Result: ~5-10ms with indexes
```

## 🧪 Testing Scenarios

### Happy Path
1. ✅ Add book to cart → Success
2. ✅ Update quantity → Cart updated
3. ✅ Checkout with valid data → Order created
4. ✅ View order history → Orders displayed
5. ✅ Admin updates status → Status changed

### Edge Cases
1. ⚠️ Add to cart with stock = 0 → Should fail
2. ⚠️ Checkout with insufficient stock → Transaction rollback
3. ⚠️ Concurrent orders for same book → Stock locking
4. ⚠️ Update cart after logout → 401 Unauthorized
5. ⚠️ Admin cancels confirmed order → Should update

---

## 📋 Summary

### Order Flow Summary

**Customer Side:**
1. Browse → Add to cart → Manage cart
2. Checkout → Fill info → Submit order
3. View orders → Track status

**Admin Side:**
1. View all orders
2. Review order details
3. Update status (pending → confirmed → completed)

### Key Components

- **CartContext**: Frontend cart state management
- **OrderWorkflow**: Backend transaction orchestration
- **Database Transaction**: Ensure atomicity
- **Status Lifecycle**: Clear state transitions

### Success Metrics

✅ **Transaction Safety**: All-or-nothing guarantee  
✅ **Stock Consistency**: No overselling  
✅ **User Experience**: Clear feedback at each step  
✅ **Admin Control**: Full order management  

---

**📌 Order flow là core business logic, được implement cẩn thận với transaction management và validation đầy đủ!**

