# 11 - Kiểm Thử

## 🧪 Test Strategy

Dự án sử dụng **Manual Testing** approach với test cases được document rõ ràng.

### Test Levels

1. **Unit Testing** - Test từng function/component riêng lẻ (planned)
2. **Integration Testing** - Test interaction giữa các layers (manual)
3. **System Testing** - Test toàn bộ hệ thống end-to-end (manual)
4. **User Acceptance Testing** - Test với user thật (manual)

## ✅ Manual Test Cases

### Authentication Tests

| ID | Test Case | Steps | Expected Result | Status |
|----|-----------|-------|-----------------|--------|
| AUTH-001 | Register thành công | 1. Fill form<br/>2. Submit | User created, auto login | ✅ Pass |
| AUTH-002 | Register với username trùng | 1. Use existing username<br/>2. Submit | Error: "Username đã tồn tại" | ✅ Pass |
| AUTH-003 | Login thành công | 1. Enter correct credentials<br/>2. Submit | Redirect to homepage | ✅ Pass |
| AUTH-004 | Login fail với wrong password | 1. Enter wrong password<br/>2. Submit | Error: "Sai mật khẩu" | ✅ Pass |
| AUTH-005 | Logout | 1. Click logout | Session cleared, redirect | ✅ Pass |

### Books Management Tests (Admin)

| ID | Test Case | Expected Result | Status |
|----|-----------|-----------------|--------|
| BOOK-001 | Create book | Book created successfully | ✅ Pass |
| BOOK-002 | Create book với price < 0 | Validation error | ✅ Pass |
| BOOK-003 | Update book | Book updated | ✅ Pass |
| BOOK-004 | Delete book | Book deleted | ✅ Pass |
| BOOK-005 | Search books | Filtered results | ✅ Pass |
| BOOK-006 | Pagination | Correct page data | ✅ Pass |

### Shopping Cart Tests

| ID | Test Case | Expected Result | Status |
|----|-----------|-----------------|--------|
| CART-001 | Add book to cart | Item added | ✅ Pass |
| CART-002 | Add same book twice | Quantity updated | ✅ Pass |
| CART-003 | Update quantity | Cart updated | ✅ Pass |
| CART-004 | Remove item | Item removed | ✅ Pass |
| CART-005 | View cart | All items displayed | ✅ Pass |

### Order Tests

| ID | Test Case | Expected Result | Status |
|----|-----------|-----------------|--------|
| ORD-001 | Create order | Order created, cart cleared | ✅ Pass |
| ORD-002 | Create order với empty cart | Error | ✅ Pass |
| ORD-003 | View order history | All orders displayed | ✅ Pass |
| ORD-004 | Admin update order status | Status updated | ✅ Pass |

### Admin Panel Tests

| ID | Test Case | Expected Result | Status |
|----|-----------|-----------------|--------|
| ADM-001 | Admin login | Access granted | ✅ Pass |
| ADM-002 | Customer access admin | Redirect to login | ✅ Pass |
| ADM-003 | View statistics | Stats displayed | ✅ Pass |
| ADM-004 | Manage customers | CRUD operations work | ✅ Pass |

## 🔍 Test Data

### Test Users

```python
# Admin
username: admin
password: admin123
role: admin

# Customers
username: user1, user2
password: pass123
role: customer
codes: KH001, KH002
```

### Test Books

- 30 sample books seeded automatically
- Categories: Kỹ năng sống, Văn học, Tiểu thuyết, Kinh tế, etc.
- Prices: 50,000 - 200,000 VND
- Stock: 10 - 100 units

## 🐛 Bug Report Template

```markdown
**Bug ID:** BUG-XXX
**Title:** [Short description]
**Severity:** Critical / High / Medium / Low
**Priority:** P0 / P1 / P2 / P3

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
What should happen

**Actual Result:**
What actually happens

**Environment:**
- Browser: Chrome 120
- OS: Windows 11
- Backend: Flask 3.0

**Screenshots:**
[Attach if applicable]

**Logs:**
[Relevant error logs]
```

## 📊 Test Coverage (Planned)

### Backend Unit Tests (Python)

```python
# Example: test_auth_routes.py
import pytest
from app import create_app
from models import db, User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_register_success(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'pass123',
        'full_name': 'Test User'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert data['user']['username'] == 'testuser'

def test_register_duplicate_username(client):
    # First registration
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'pass123',
        'full_name': 'Test User'
    })
    
    # Duplicate registration
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'pass123',
        'full_name': 'Test User 2'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'đã tồn tại' in data['error'].lower()
```

### Frontend Unit Tests (Jest + React Testing Library)

```typescript
// Example: BookCard.test.tsx
import { render, screen } from '@testing-library/react'
import { BookCard } from './BookCard'

test('renders book title', () => {
  const book = {
    id: 1,
    title: 'Test Book',
    author: 'Test Author',
    price: 100000,
    image_url: 'test.jpg'
  }
  
  render(<BookCard book={book} />)
  expect(screen.getByText('Test Book')).toBeInTheDocument()
})
```

## 🚀 Running Tests (Future)

### Backend Tests

```bash
# Run all backend tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=.

# Run specific test file
docker-compose exec backend pytest tests/test_auth_routes.py
```

### Frontend Tests

```bash
# Run all frontend tests
cd frontend
npm run test

# Run with coverage
npm run test:coverage

# Run specific test
npm run test BookCard.test.tsx
```

## ✔️ Test Checklist

### Pre-Release Testing

- [ ] All manual test cases pass
- [ ] No critical bugs
- [ ] Performance acceptable (page load < 3s)
- [ ] Mobile responsive
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Database seeding works
- [ ] Docker deployment works
- [ ] Documentation up-to-date

### Regression Testing

After any code change:
- [ ] Auth still works
- [ ] Cart operations work
- [ ] Order creation works
- [ ] Admin panel accessible
- [ ] No new console errors

---

**📌 Current Status:**
- Manual testing: ✅ Complete
- Unit tests: ⏳ Planned for future
- Integration tests: ⏳ Planned
- E2E tests: ⏳ Planned

