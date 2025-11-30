# 07 - Luồng Xác Thực (Authentication Flow)

## 🔐 Tổng Quan

Hệ thống sử dụng **Session-based Authentication** với:
- **Backend**: Flask-Session với server-side session storage
- **Frontend**: React Context để quản lý auth state
- **Security**: bcrypt password hashing, httpOnly cookies

## 🎯 Authentication Methods

| Method | Endpoint | Cho ai | Redirect |
|--------|----------|--------|----------|
| **Customer Register** | `/api/register` | Guest | Homepage (auto login) |
| **Customer Login** | `/api/login` | Guest | Homepage |
| **Admin Login** | `/api/login` | Admin | `/admin` dashboard |
| **Logout** | `/api/logout` | All | Tùy role |

## 📋 Flow Diagrams

### 1. Customer Registration Flow

```mermaid
sequenceDiagram
    participant U as User (Guest)
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    
    Note over U,DB: Customer Registration Flow
    
    U->>FE: Visit /register
    FE->>FE: Show RegisterPage
    U->>FE: Fill form:<br/>username, email, password, full_name
    U->>FE: Click "Đăng Ký"
    
    FE->>FE: Client-side validation:<br/>- All fields filled?<br/>- Email valid format?<br/>- Password min 6 chars?
    
    alt Validation Failed
        FE-->>U: Show error messages
    end
    
    FE->>BE: POST /api/register<br/>{username, email, password, full_name}
    
    Note over BE: Backend Processing
    BE->>BE: Validate input data
    BE->>DB: Check username exists?
    DB-->>BE: Query result
    
    alt Username exists
        BE-->>FE: 400 Bad Request<br/>{error: "Username đã tồn tại"}
        FE->>FE: Toast.error()
        FE-->>U: Show error toast
    end
    
    BE->>DB: Check email exists?
    DB-->>BE: Query result
    
    alt Email exists
        BE-->>FE: 400 Bad Request<br/>{error: "Email đã tồn tại"}
        FE->>FE: Toast.error()
        FE-->>U: Show error toast
    end
    
    Note over BE: All validations passed
    BE->>BE: Hash password (bcrypt, cost=12)
    BE->>BE: Generate customer_code (KH001, KH002, ...)
    
    BE->>DB: INSERT INTO users<br/>(username, password_hash, email,<br/>full_name, role='customer',<br/>customer_code, is_active=true)
    DB-->>BE: User created (user_id)
    
    Note over BE: Auto-login after registration
    BE->>BE: Create session<br/>session['user_id'] = new_user_id
    
    BE-->>FE: 201 Created<br/>{message: "Đăng ký thành công",<br/>user: {...}}
    
    FE->>FE: AuthContext.setUser(user)
    FE->>FE: Toast.success("Đăng ký thành công!")
    FE->>FE: Navigate to '/'
    
    FE-->>U: Redirect to Homepage<br/>(Logged in as customer)
```

### 2. Customer Login Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    
    Note over U,DB: Customer Login Flow
    
    U->>FE: Visit /login
    FE->>FE: Show LoginPage
    U->>FE: Enter username & password
    U->>FE: Click "Đăng Nhập"
    
    FE->>FE: Client validation:<br/>- Username not empty?<br/>- Password not empty?
    
    FE->>BE: POST /api/login<br/>{username, password}
    
    BE->>DB: SELECT * FROM users<br/>WHERE username = ?
    DB-->>BE: User data or NULL
    
    alt User not found
        BE-->>FE: 401 Unauthorized<br/>{error: "Tài khoản không tồn tại"}
        FE->>FE: Toast.error()
        FE-->>U: Show error
    end
    
    Note over BE: User found, check password
    BE->>BE: check_password(<br/>  stored_hash,<br/>  input_password<br/>)
    
    alt Password incorrect
        BE-->>FE: 401 Unauthorized<br/>{error: "Mật khẩu không đúng"}
        FE->>FE: Toast.error()
        FE-->>U: Show error
    end
    
    Note over BE: Check if account is active
    alt Account inactive (is_active=false)
        BE-->>FE: 401 Unauthorized<br/>{error: "Tài khoản đã bị khóa"}
        FE->>FE: Toast.error()
        FE-->>U: Show error
    end
    
    Note over BE: All checks passed
    BE->>BE: Create session<br/>session['user_id'] = user.id
    BE->>BE: Set session cookie<br/>(httpOnly=true, secure=true in prod)
    
    BE-->>FE: 200 OK<br/>{message: "Đăng nhập thành công",<br/>user: {...}}
    
    FE->>FE: AuthContext.setUser(user)
    FE->>FE: Toast.success("Đăng nhập thành công!")
    FE->>FE: Navigate to '/'
    
    FE-->>U: Redirect to Homepage<br/>(Logged in)
```

### 3. Admin Login Flow

```mermaid
sequenceDiagram
    participant A as Admin
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    
    Note over A,DB: Admin Login Flow
    
    A->>FE: Visit /admin/login
    FE->>FE: Show AdminLoginPage<br/>(Special styling)
    A->>FE: Enter admin credentials
    A->>FE: Click "Đăng Nhập"
    
    FE->>BE: POST /api/login<br/>{username, password}
    
    Note over BE: Same endpoint as customer login
    BE->>DB: SELECT * FROM users<br/>WHERE username = ?
    DB-->>BE: User data
    
    BE->>BE: Validate password
    BE->>BE: Check is_active
    
    alt Not admin
        Note over BE: role !== 'admin'
        BE-->>FE: 200 OK but role=customer
        FE->>FE: Check user.role
        FE-->>A: Toast.error("Không có quyền truy cập")
        FE->>FE: Stay on /admin/login
    end
    
    Note over BE: Admin validation passed
    BE->>BE: Create session<br/>session['user_id'] = admin.id
    
    BE-->>FE: 200 OK<br/>{user: {role: 'admin', ...}}
    
    FE->>FE: AuthContext.setUser(admin_user)
    FE->>FE: Toast.success("Đăng nhập thành công!")
    FE->>FE: Navigate to '/admin'
    
    FE-->>A: Redirect to Admin Dashboard
```

### 4. Protected Route Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant PR as ProtectedRoute
    participant AC as AuthContext
    participant BE as Backend
    
    Note over U,BE: Accessing Protected Route
    
    U->>FE: Navigate to /profile or /admin
    FE->>PR: Route matches, render ProtectedRoute
    
    PR->>AC: Get auth state<br/>{user, loading}
    
    alt Loading = true
        PR-->>U: Show loading spinner
    end
    
    alt User = null (not authenticated)
        PR->>FE: <Navigate to="/admin/login" />
        FE-->>U: Redirect to login page
    end
    
    Note over PR: User authenticated
    PR->>PR: Check route requires admin?
    
    alt Admin route & user.role !== 'admin'
        PR-->>U: 403 Forbidden or redirect
    end
    
    Note over PR: All checks passed
    PR->>FE: Render {children}
    FE-->>U: Show protected content
```

### 5. Session Check on App Load

```mermaid
sequenceDiagram
    participant B as Browser
    participant FE as Frontend
    participant AC as AuthContext
    participant BE as Backend
    participant DB as Database
    
    Note over B,DB: App Initialization
    
    B->>FE: Load application
    FE->>AC: AuthProvider mounted
    AC->>AC: useEffect(() => checkAuth())
    
    AC->>BE: GET /api/me<br/>(with session cookie)
    
    alt No session cookie or invalid session
        BE-->>AC: 401 Unauthorized
        AC->>AC: setUser(null)<br/>setLoading(false)
        FE-->>B: Show as guest
    end
    
    Note over BE: Valid session exists
    BE->>BE: Get user_id from session
    BE->>DB: SELECT * FROM users<br/>WHERE id = session['user_id']
    DB-->>BE: User data
    
    alt User not found or inactive
        BE->>BE: Clear session
        BE-->>AC: 401 Unauthorized
        AC->>AC: setUser(null)
    end
    
    Note over BE: User found and active
    BE-->>AC: 200 OK<br/>{user: {...}}
    
    AC->>AC: setUser(user)<br/>setLoading(false)
    FE-->>B: Render with user logged in
```

### 6. Logout Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant AC as AuthContext
    participant BE as Backend
    
    Note over U,BE: Logout Flow
    
    U->>FE: Click "Đăng xuất"
    FE->>AC: Call logout()
    
    AC->>BE: POST /api/logout
    BE->>BE: Clear session<br/>session.clear()
    BE-->>AC: 200 OK
    
    AC->>AC: setUser(null)
    AC->>FE: CartContext.clearCart()
    FE->>FE: Toast.success("Đã đăng xuất")
    
    alt Customer logout
        FE->>FE: Navigate to '/'
        FE-->>U: Redirect to Homepage
    end
    
    alt Admin logout
        FE->>FE: Navigate to '/admin/login'
        FE-->>U: Redirect to Admin Login
    end
```

## 🔒 Security Features

### 1. Password Security

```python
# Backend: utils/helpers.py
import bcrypt

def hash_password(password: str) -> str:
    """Hash password với bcrypt cost factor 12"""
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

def check_password(hashed: str, plain: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )
```

**Security Properties:**
- **Slow hashing**: Cost factor 12 = 2^12 iterations (secure but reasonable)
- **Unique salt**: Mỗi password có salt riêng (tự động)
- **No plain text**: Không bao giờ lưu plain password
- **Rainbow table resistant**: Salt prevents rainbow table attacks

### 2. Session Security

```python
# Backend: app.py
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Không thể access từ JS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only (production)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
```

**Security Properties:**
- **httpOnly**: Prevents XSS attacks (JS cannot read cookie)
- **SameSite**: Prevents CSRF attacks
- **Secure**: HTTPS only in production
- **Expiration**: 7-day timeout

### 3. Input Validation

```python
# Backend: routes/auth.py
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    
    # Validation rules
    if not username or len(username) < 4:
        return jsonify({'error': 'Username phải có ít nhất 4 ký tự'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Email không hợp lệ'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400
    
    if not full_name:
        return jsonify({'error': 'Họ tên không được để trống'}), 400
    
    # Check uniqueness - Query User model trực tiếp
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username đã tồn tại'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email đã tồn tại'}), 400
    
    # Proceed with registration...
    password_hash = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role='customer',
        is_active=True,
        customer_code=User.generate_customer_code()
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Auto-login
    session['user_id'] = new_user.id
    return jsonify({'message': 'Đăng ký thành công', 'user': new_user.to_dict()}), 201
```

### 4. Rate Limiting (Future Enhancement)

```python
# Recommended: Add Flask-Limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    # ...
```

## 🎯 Frontend Implementation

### AuthContext.tsx

```typescript
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Check auth on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
    } catch (error) {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const user = await authService.login({ username, password })
    setUser(user)
  }

  const register = async (data: RegisterRequest) => {
    const user = await authService.register(data)
    setUser(user)
  }

  const logout = async () => {
    await authService.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, setUser, login, register, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}
```

### ProtectedRoute.tsx

```typescript
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/admin/login" replace />
  }

  return <>{children}</>
}
```

## 📊 Authentication States

| State | user | loading | Action |
|-------|------|---------|--------|
| **Initial** | null | true | Check auth |
| **Guest** | null | false | Show login/register |
| **Customer** | {..., role:'customer'} | false | Full access |
| **Admin** | {..., role:'admin'} | false | Admin access |
| **Checking** | null/user | true | Show spinner |

## 🔍 Troubleshooting

### Issue: "Yêu cầu đăng nhập" after login

**Cause**: Session cookie không được gửi

**Solution:**
```typescript
// Frontend: api.ts
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // ← Must be true!
})
```

```python
# Backend: app.py
CORS(app, 
     supports_credentials=True,  # ← Must be true!
     origins=['http://localhost:5173'])
```

### Issue: Admin cannot login

**Check:**
1. User role = 'admin' in database?
2. is_active = true?
3. Correct redirect logic after login?

### Issue: Session expires too fast

**Adjust:**
```python
# Backend: app.py
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Longer session
```

---

## 📋 Summary

### Authentication Flow Summary

✅ **Registration**: Validate → Hash password → Generate code → Save → Auto-login  
✅ **Login**: Validate credentials → Check active → Create session → Return user  
✅ **Protected Routes**: Check session → Verify role → Render or redirect  
✅ **Logout**: Clear session → Clear frontend state → Redirect  

### Security Checklist

✅ Passwords hashed với bcrypt (cost=12)  
✅ Session cookies với httpOnly  
✅ Input validation (frontend + backend)  
✅ Unique username & email constraints  
✅ Account active check  
✅ Role-based access control  
⚠️ Rate limiting (recommended addition)  
⚠️ Two-factor authentication (future)  

---

**📌 Authentication system đơn giản nhưng secure, phù hợp cho đồ án tốt nghiệp!**

