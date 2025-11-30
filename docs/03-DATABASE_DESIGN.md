# 03 - Database Design & Schema

## Overview

- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)

## 📊 Entity Relationship Diagram

**Xem ERD chi tiết với constraints và indexes:** [`diagrams/database-erd.mmd`](diagrams/database-erd.mmd)

### Overview ERD

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        string customer_code UK "KH001, KH002, ..."
        datetime created_at
    }

    BOOKS {
        int id PK
        string title
        string author
        string category "References CATEGORIES.key"
        text description "Unlimited length (TEXT type)"
        decimal price
        int stock
        string image_url
        string publisher
        string publish_date
        string distributor
        string dimensions
        int pages
        int weight
        datetime created_at
        datetime updated_at
    }

    CATEGORIES {
        int id PK
        string key UK "e.g., Sach_Tieng_Viet"
        string name "e.g., Sách Tiếng Việt"
        text description "Unlimited length (TEXT type)"
        int display_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CART {
        int id PK
        int user_id FK
        int book_id FK
        int quantity
        datetime created_at
    }

    ORDERS {
        int id PK
        int user_id FK
        decimal total_amount
        string status
        string payment_status
        text shipping_address
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int book_id FK
        int quantity
        decimal price
    }

    BANNERS {
        int id PK
        string title
        text description "Unlimited length (TEXT type)"
        string image_url
        string link
        string bg_color
        string text_color
        string position
        int display_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    %% Relationships
    USERS ||--o{ CART : "has"
    USERS ||--o{ ORDERS : "places"
    CATEGORIES ||--o{ BOOKS : "categorizes"
    BOOKS ||--o{ CART : "in"
    BOOKS ||--o{ ORDER_ITEMS : "contains"
    ORDERS ||--o{ ORDER_ITEMS : "has"
```

## Tables

### 1. Users Table

**Table Name:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | User ID (auto-increment) |
| username | VARCHAR(80) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(120) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| full_name | VARCHAR(100) | NULL | Full name |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'customer' | user role: admin/customer |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Account status |
| **customer_code** | VARCHAR(20) | UNIQUE, NULL | Customer code (KH001, KH002, ...) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation time |

### 2. Books Table

**Table Name:** `books`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Book ID |
| title | VARCHAR(200) | NOT NULL | Book title |
| author | VARCHAR(100) | NOT NULL | Author name |
| category | VARCHAR(50) | NOT NULL | Book category (references categories.key) |
| description | TEXT | NULL | Book description (unlimited length, supports long text) |
| price | DECIMAL(10,2) | NOT NULL | Book price (VND) |
| stock | INTEGER | NOT NULL, DEFAULT 0 | Stock quantity |
| image_url | VARCHAR(500) | NULL | Cover image URL |
| publisher | VARCHAR(200) | NULL | Publisher name |
| publish_date | VARCHAR(20) | NULL | Publish date |
| distributor | VARCHAR(200) | NULL | Distributor |
| dimensions | VARCHAR(100) | NULL | Size (cm) |
| pages | INTEGER | NULL | Number of pages |
| weight | INTEGER | NULL | Weight (grams) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Created time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Updated time |

### 3. Categories Table

**Table Name:** `categories`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Category ID |
| key | VARCHAR(50) | UNIQUE, NOT NULL | Category key (e.g., 'Sach_Tieng_Viet') |
| name | VARCHAR(100) | NOT NULL | Display name (e.g., 'Sách Tiếng Việt') |
| description | TEXT | NULL | Category description (unlimited length) |
| display_order | INTEGER | DEFAULT 0 | Display order in UI |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Created time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Updated time |

### 4. Cart Table

**Table Name:** `cart`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Cart item ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | User ID |
| book_id | INTEGER | FOREIGN KEY (books.id), NOT NULL | Book ID |
| quantity | INTEGER | NOT NULL, DEFAULT 1 | Quantity |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Added time |

### 4. Orders Table

**Table Name:** `orders`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Order ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | User ID |
| total_amount | DECIMAL(10,2) | NOT NULL | Total order amount |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Order status |
| payment_status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Payment status |
| shipping_address | TEXT | NOT NULL | Delivery address |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Order time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update |

**Status Values:**
- `pending` - Chờ xác nhận
- `confirmed` - Đã xác nhận
- `cancelled` - Đã hủy
- `completed` - Hoàn thành

**Payment Status:**
- `pending` - Chưa thanh toán
- `paid` - Đã thanh toán

### 5. Order Items Table

**Table Name:** `order_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Order item ID |
| order_id | INTEGER | FOREIGN KEY (orders.id), NOT NULL | Order ID |
| book_id | INTEGER | FOREIGN KEY (books.id), NOT NULL | Book ID |
| quantity | INTEGER | NOT NULL | Quantity ordered |
| price | DECIMAL(10,2) | NOT NULL | Price at order time |

### 6. Banners Table

**Table Name:** `banners`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Banner ID |
| title | VARCHAR(200) | NOT NULL | Banner title |
| description | TEXT | NULL | Banner description (unlimited length) |
| image_url | VARCHAR(500) | NOT NULL | Banner image URL |
| link | VARCHAR(500) | NULL | Click destination URL |
| bg_color | VARCHAR(50) | DEFAULT '#6366f1' | Background color |
| text_color | VARCHAR(50) | DEFAULT '#ffffff' | Text color |
| position | VARCHAR(20) | DEFAULT 'main' | Position: main/side_top/side_bottom |
| display_order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Created time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Updated time |

## Relationships

- **Users → Cart**: One-to-Many (One user can have many cart items)
- **Users → Orders**: One-to-Many (One user can place many orders)
- **Categories → Books**: One-to-Many (One category can have many books)
- **Books → Cart**: One-to-Many (One book can be in many carts)
- **Books → Order Items**: One-to-Many (One book can be in many orders)
- **Orders → Order Items**: One-to-Many (One order contains many items)

## Indexes

- `users.username` - UNIQUE index for fast login lookup
- `users.email` - UNIQUE index for uniqueness check
- `users.customer_code` - UNIQUE index for customer lookup
- `cart.user_id` - Index for cart queries
- `orders.user_id` - Index for order history queries
- `categories.key` - UNIQUE index for category lookup
- `books.category` - Index for category filtering

---

*Last updated: November 2024*

