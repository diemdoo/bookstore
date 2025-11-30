# 13 - Chatbot Documentation

> Tài liệu chi tiết về tính năng Chatbot thông minh với Google Gemini AI

## 📋 Tổng Quan

Chatbot là một tính năng hỗ trợ khách hàng thông minh được tích hợp vào hệ thống Bookstore. Chatbot sử dụng **Google Gemini 2.5 Flash API** để cung cấp phản hồi tự nhiên và thông minh dựa trên dữ liệu thực tế từ database.

### Mục Đích

- Hỗ trợ khách hàng 24/7 với phản hồi tự động
- Trả lời câu hỏi về sách, danh mục, giá cả, tác giả
- Gợi ý sách dựa trên sở thích và danh mục
- Hướng dẫn về quy trình mua hàng, thanh toán, giao hàng
- Giải đáp thắc mắc về chính sách đổi trả, vận chuyển

### Tính Năng Chính

- ✅ **AI-Powered Responses**: Sử dụng Google Gemini 2.5 Flash để tạo phản hồi thông minh
- ✅ **Real-time Database Integration**: Lấy dữ liệu thực tế từ database (bestsellers, categories, book details)
- ✅ **Smart Book Detection**: Tự động nhận diện tên sách trong câu hỏi và query thông tin chi tiết
- ✅ **Book Quality Assessment**: Đánh giá chất lượng sách dựa trên description, sold count, author, publisher, pages
- ✅ **Similar Books Recommendations**: Gợi ý sách tương tự (cùng tác giả, cùng category)
- ✅ **FAQ Fallback**: Hệ thống FAQ đơn giản làm fallback khi API không khả dụng
- ✅ **Context-Aware**: Hiểu context về bookstore và có thể trả lời câu hỏi cụ thể
- ✅ **User-Friendly UI**: Giao diện chat đẹp, dễ sử dụng với floating button

## 🏗 Kiến Trúc

### Technology Stack

- **Backend**: Flask (Python)
- **AI Engine**: Google Gemini 2.5 Flash API
- **Library**: `google-genai` (new SDK, replaces deprecated `google-generativeai`)
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: PostgreSQL (để lấy context data)

### Component Structure

```
Backend:
├── routes/chatbot.py          # Chatbot API endpoint
│   ├── get_bookstore_context()        # Lấy context tổng quát từ database
│   ├── detect_and_get_book_info()     # Detect và query thông tin sách cụ thể
│   ├── format_book_context()          # Format thông tin sách thành text
│   ├── build_system_prompt()          # Tạo system prompt cho Gemini
│   ├── query_gemini()                 # Gọi Gemini API
│   └── chatbot()                      # Main route handler
│
Frontend:
└── components/shared/Chatbot.tsx  # Chatbot UI component
    ├── Floating button
    ├── Chat modal
    └── Message list
```

## 🔄 Cách Hoạt Động

### Flow Diagram

```
User Input
    ↓
Frontend: Chatbot.tsx
    ↓
POST /api/chatbot
    ↓
Backend: routes/chatbot.py
    ↓
1. Validate question
    ↓
2. Check GEMINI_API_KEY
    ↓
3. Build context from database
    ├── Categories
    ├── Bestsellers (top 10)
    └── Category books (sample)
    ↓
4. Detect book in question (if any)
    ├── Extract book title using Gemini
    ├── Search in database
    ├── Query book details
    └── Query similar books
    ↓
5. Build system prompt
    ├── Role definition
    ├── Bookstore context
    ├── Book-specific context (if detected)
    ├── AI instructions for book assessment
    └── Policies & services
    ↓
6. Call Gemini API
    ├── Model: gemini-2.5-flash
    ├── System instruction
    └── User question
    ↓
7. Return response
    ├── Success → Gemini answer
    └── Fail → FAQ fallback
    ↓
Frontend: Display answer
```

### Chi Tiết Từng Bước

#### 1. Context Building (`get_bookstore_context()`)

Hàm này query database để lấy thông tin về bookstore:

- **Categories**: Danh sách các danh mục sách (active only)
- **Total Books**: Tổng số sách trong hệ thống
- **Bestsellers**: Top 10 sách bán chạy nhất (dựa trên số lượng đã bán từ orders completed)
- **Category Books**: Sample books từ mỗi category (top 3-5 sách với số lượng đã bán)

**Query Logic**:
```python
# Bestsellers query
bestsellers = db.session.query(
    Book,
    func.sum(OrderItem.quantity).label('total_sold')
).join(OrderItem).join(Order).filter(
    Order.status == 'completed'
).group_by(Book.id).order_by(desc('total_sold')).limit(10).all()
```

#### 2. Book Detection (`detect_and_get_book_info()`)

Nếu user hỏi về một cuốn sách cụ thể, chatbot sẽ:
- **Extract Book Title**: Sử dụng Gemini để extract tên sách từ câu hỏi
- **Search Database**: Tìm sách khớp với title (fuzzy match)
- **Query Details**: Lấy thông tin chi tiết: description, author, publisher, pages, price, sold count, category
- **Find Similar Books**: Query sách tương tự (cùng tác giả, cùng category)

**Example**:
```python
# User: "Sách Harry Potter có hay không?"
# → Detect: "Harry Potter"
# → Query: Book details + similar books
# → Add to context
```

#### 3. System Prompt Building (`build_system_prompt(question=None)`)

Tạo system prompt với:
- **Role**: Trợ lý AI của cửa hàng sách trực tuyến
- **Tasks**: Trả lời câu hỏi, gợi ý sách, hướng dẫn mua hàng, đánh giá chất lượng sách
- **Context**: 
  - Thông tin tổng quát về bookstore (categories, bestsellers, category books)
  - Thông tin sách cụ thể (nếu detected): description, author, publisher, pages, price, sold count, similar books
- **AI Instructions**: Hướng dẫn cách đánh giá sách dựa trên:
  - Description (nội dung, thể loại, đối tượng độc giả)
  - Sold count (sách bán chạy thường được yêu thích)
  - Author (tác giả nổi tiếng thường viết sách chất lượng)
  - Publisher (NXB uy tín)
  - Pages (độ dài và chi tiết nội dung)
  - Similar books (so sánh tương đối)
- **Policies**: Thanh toán, giao hàng, đổi trả, đăng ký/đăng nhập

#### 4. Gemini API Call (`query_gemini()`)

- **Model**: `gemini-2.5-flash` (latest, fast, suitable for chatbot)
- **Client**: Lazy initialization, reused across requests
- **Config**: System instruction + user question
- **Error Handling**: Catches `errors.APIError` and generic exceptions

#### 5. Response Handling

- **Success**: Trả về answer từ Gemini
- **Failure**: Fallback về FAQ matching
- **No API Key**: Sử dụng FAQ only

## 📊 Context Information

### Dữ Liệu Được Bao Gồm

Context được build từ database bao gồm:

1. **Categories List**
   ```
   Cửa hàng có {total_books} cuốn sách trong các danh mục sau:
   - Sách Tiếng Việt, Truyện Tranh, Đồ Trang Trí, Văn Phòng Phẩm
   ```

2. **Top 10 Bestsellers**
   ```
   Top 10 sách bán chạy nhất:
   1. {title} - {author} (Đã bán: {sold_count})
   2. {title} - {author} (Đã bán: {sold_count})
   ...
   ```

3. **Category Books (Sample)**
   ```
   Sách theo danh mục:
   - Sách Tiếng Việt: {book1}, {book2}, {book3}
   - Truyện Tranh: {book1}, {book2}, {book3}
   ...
   ```

### Context Format

Context được format như một text string, dễ đọc cho AI model:

**General Context** (luôn có):
```
Cửa hàng có 60 cuốn sách trong các danh mục sau:
- Sách Tiếng Việt, Truyện Tranh, Đồ Trang Trí, Văn Phòng Phẩm

Top 10 sách bán chạy nhất:
1. Sách A - Tác giả A (Đã bán: 15)
2. Sách B - Tác giả B (Đã bán: 12)
...

Sách theo danh mục:
- Sách Tiếng Việt: Sách A - Tác giả A (Đã bán: 15), Sách B - Tác giả B (Đã bán: 12)
- Truyện Tranh: Sách C - Tác giả C (Đã bán: 8), Sách D - Tác giả D (Đã bán: 6)
...
```

**Book-Specific Context** (nếu user hỏi về sách cụ thể):
```
[Thông tin sách cụ thể:]
Sách: Harry Potter và Hòn đá Phù thủy
- Tác giả: J.K. Rowling
- Mô tả: Câu chuyện về cậu bé phù thủy trẻ tuổi...
- Nhà xuất bản: Nhà xuất bản Trẻ
- Số trang: 320
- Giá: 150,000 VNĐ
- Đã bán: 25 cuốn
- Danh mục: Sách Tiếng Việt

Sách tương tự:
- Harry Potter và Phòng chứa Bí mật - J.K. Rowling (Đã bán: 20)
- Harry Potter và Tù nhân Azkaban - J.K. Rowling (Đã bán: 18)
- Percy Jackson và Kẻ trộm tia chớp - Rick Riordan (Đã bán: 15)
```

## 🔌 API Endpoint

### POST /api/chatbot

**Mô tả**: Xử lý câu hỏi từ chatbot và trả về câu trả lời

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "question": "Tìm sách nào bán chạy nhất"
}
```

**Response: 200 OK**
```json
{
  "answer": "Dựa trên dữ liệu bán hàng, top 3 sách bán chạy nhất hiện tại là:\n\n1. Sách A - Tác giả A (Đã bán: 15 cuốn)\n2. Sách B - Tác giả B (Đã bán: 12 cuốn)\n3. Sách C - Tác giả C (Đã bán: 8 cuốn)\n\nBạn có muốn xem chi tiết về cuốn sách nào không?",
  "source": "gemini"
}
```

**Response Fields**:
- `answer` (string): Câu trả lời từ chatbot
- `source` (string): Nguồn của câu trả lời (`gemini`, `faq`, `faq_default`, `error`)

**Error: 400 Bad Request**
```json
{
  "error": "Vui lòng nhập câu hỏi"
}
```

**Error Handling**:
- Nếu Gemini API fail → Fallback về FAQ
- Nếu không có API key → Sử dụng FAQ only
- Nếu có exception → Trả về FAQ default message

## 🎨 Frontend Integration

### Chatbot Component

**Location**: `frontend/src/components/shared/Chatbot.tsx`

**Features**:
- Floating button ở góc dưới bên phải
- Modal chat interface với animation
- Message history (user + bot messages)
- Loading state khi đang gọi API
- Auto-scroll to bottom khi có message mới
- Input validation và error handling

**UI Components**:
- Floating button với icon MessageCircle
- Chat modal với header "Chatbot hỗ trợ"
- Messages area (scrollable)
- Input field với send button
- Loading indicator

**Styling**:
- Tailwind CSS
- Icons từ lucide-react
- Primary color scheme
- Smooth animations

### Integration

Chatbot component được tích hợp vào `App.tsx` để hiển thị trên tất cả các trang public:

```tsx
import { Chatbot } from './components/shared/Chatbot'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        ...
      </Routes>
      <Chatbot /> {/* Global chatbot component */}
    </Router>
  )
}
```

## ⚙️ Configuration

### Environment Variables

**Backend** (`.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Location**: `backend/config.py`
```python
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

### Model Configuration

**Model**: `gemini-2.5-flash`
- Latest model from Google
- Fast response time
- Suitable for chatbot use cases
- Supports system instructions

**Client Initialization**:
- Lazy initialization (first request)
- Module-level client (reused across requests)
- Error handling for missing API key

### Dependencies

**Backend** (`requirements.txt`):
```
google-genai==1.52.0
```

**Frontend** (`package.json`):
- React hooks (useState, useEffect, useRef)
- lucide-react (icons)
- Tailwind CSS (styling)

## 📝 Examples

### Câu Hỏi Mẫu và Phản Hồi

#### 1. Câu hỏi về bestsellers
**User**: "Tìm sách nào bán chạy nhất"

**Bot**: "Dựa trên dữ liệu bán hàng, top 3 sách bán chạy nhất hiện tại là:
1. Sách A - Tác giả A (Đã bán: 15 cuốn)
2. Sách B - Tác giả B (Đã bán: 12 cuốn)
3. Sách C - Tác giả C (Đã bán: 8 cuốn)

Bạn có muốn xem chi tiết về cuốn sách nào không?"

#### 2. Câu hỏi về category
**User**: "Sách nào trong danh mục Truyen Tranh bán chạy?"

**Bot**: "Trong danh mục Truyện Tranh, các sách bán chạy nhất là:
- Sách C - Tác giả C (Đã bán: 8 cuốn)
- Sách D - Tác giả D (Đã bán: 6 cuốn)
- Sách E - Tác giả E (Đã bán: 4 cuốn)

Bạn có muốn tìm hiểu thêm về cuốn nào không?"

#### 3. Câu hỏi về chính sách
**User**: "Thanh toán như thế nào?"

**Bot**: "Chúng tôi hỗ trợ thanh toán khi nhận hàng (COD). Bạn sẽ thanh toán khi nhận được sách. Đây là phương thức thanh toán tiện lợi và an toàn cho khách hàng."

#### 4. Câu hỏi về sách cụ thể
**User**: "Sách Harry Potter có hay không?"

**Bot**: "Dựa trên thông tin về sách 'Harry Potter và Hòn đá Phù thủy':

- **Tác giả**: J.K. Rowling - một tác giả nổi tiếng thế giới
- **Đã bán**: 25 cuốn - đây là một con số khá tốt, cho thấy sách được nhiều người yêu thích
- **Mô tả**: Câu chuyện về cậu bé phù thủy trẻ tuổi... (phân tích nội dung)
- **Số trang**: 320 trang - độ dài vừa phải, phù hợp cho độc giả trẻ

Đây là một cuốn sách rất hay, phù hợp cho trẻ em và thanh thiếu niên yêu thích thể loại fantasy. Bạn có thể tham khảo thêm các cuốn khác trong series như 'Harry Potter và Phòng chứa Bí mật' (đã bán 20 cuốn)."

#### 5. Câu hỏi về chất lượng sách
**User**: "Sách này phù hợp với ai?"

**Bot**: "Dựa trên mô tả và thông tin về sách, cuốn sách này phù hợp với:
- Trẻ em và thanh thiếu niên (8-16 tuổi)
- Người yêu thích thể loại fantasy, phiêu lưu
- Người mới bắt đầu đọc sách (số trang vừa phải, nội dung dễ hiểu)

Bạn có thể đọc thử mô tả để xem có phù hợp với sở thích của mình không."

#### 6. Câu hỏi chào hỏi
**User**: "Xin chào"

**Bot**: "Xin chào! Tôi có thể giúp gì cho bạn? Bạn có thể hỏi về sách, danh mục, giá cả, hoặc bất kỳ thắc mắc nào về cửa hàng của chúng tôi."

### Use Cases

1. **Product Discovery**: Khách hàng hỏi về sách, tác giả, danh mục
2. **Book Quality Assessment**: Đánh giá chất lượng sách dựa trên description, sold count, author, publisher
3. **Book Recommendations**: Chatbot gợi ý sách dựa trên sở thích và sách tương tự
4. **Book Comparison**: So sánh sách với sách tương tự (cùng tác giả, cùng category)
5. **Target Audience Analysis**: Phân tích sách phù hợp với đối tượng nào
6. **Policy Information**: Giải đáp về thanh toán, giao hàng, đổi trả
7. **Order Support**: Hướng dẫn về quy trình mua hàng
8. **General Questions**: Trả lời các câu hỏi chung về cửa hàng

## 🔍 Logging

Chatbot có logging chi tiết để debug và monitor:

**Log Levels**:
- `INFO`: Normal operations (question received, API called, response received)
- `WARNING`: Fallback to FAQ, missing API key
- `ERROR`: API errors, exceptions

**Log Format**:
```
[CHATBOT] 📨 Received question: {question}
[CHATBOT] 🔑 API Key found, calling Gemini...
[CHATBOT] 📝 System prompt built (length: {length} chars)
[CHATBOT] 📤 Calling Gemini API with question: {question}...
[CHATBOT] ✅ Gemini response received: {response}...
[CHATBOT] 📤 Response source: {source}
```

**View Logs**:
```bash
docker-compose logs -f bookstore_backend | grep CHATBOT
```

## 🚀 Future Enhancements

### Potential Improvements

1. **Multi-Book Detection**
   - Detect và so sánh nhiều sách trong một câu hỏi
   - "So sánh sách A với sách B"

2. **Conversation History**
   - Lưu conversation history trong session
   - Context-aware follow-up questions
   - Multi-turn conversations

3. **Enhanced Book Matching**
   - Cải thiện độ chính xác khi match tên sách
   - Fuzzy matching với điểm số
   - Xử lý tên sách viết tắt hoặc không chính xác

4. **Analytics**
   - Track popular questions
   - Monitor response quality
   - User satisfaction metrics

5. **Multi-language Support**
   - Support English questions
   - Auto-detect language

6. **Rich Responses**
   - Book cards trong chat
   - Links to product pages
   - Images and formatting

### Planned Features

- [x] Book detail search trong context ✅
- [x] Book quality assessment ✅
- [x] Similar books recommendations ✅
- [ ] Multi-book comparison trong một câu hỏi
- [ ] Conversation memory
- [ ] Book recommendations based on preferences
- [ ] Integration với order tracking
- [ ] Admin dashboard cho chatbot analytics

## 📚 Related Documentation

- [Backend Architecture](05-BACKEND_ARCHITECTURE.md) - Kiến trúc backend
- [API Documentation](04-API_DOCUMENTATION.md) - Tài liệu API endpoints
- [Frontend Architecture](06-FRONTEND_ARCHITECTURE.md) - Kiến trúc frontend
- [Database Design](03-DATABASE_DESIGN.md) - Thiết kế database

## 🔗 References

- [Google Gen AI SDK Documentation](https://github.com/googleapis/python-genai)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini 2.5 Flash Model](https://ai.google.dev/models/gemini)

---

**Last Updated**: 2025-01-29
**Version**: 2.0.0

### Changelog

#### Version 2.0.0 (2025-01-29)
- ✅ Added smart book detection: Tự động nhận diện tên sách trong câu hỏi
- ✅ Added book detail context: Query và hiển thị thông tin chi tiết sách (description, author, publisher, pages, price, sold count)
- ✅ Added similar books: Gợi ý sách tương tự (cùng tác giả, cùng category)
- ✅ Enhanced AI instructions: Hướng dẫn AI cách đánh giá chất lượng sách dựa trên nhiều tiêu chí
- ✅ Improved context building: Context động dựa trên câu hỏi của user

#### Version 1.0.0 (2025-11-29)
- ✅ Initial release với Gemini 2.5 Flash integration
- ✅ Basic context từ database (categories, bestsellers, category books)
- ✅ FAQ fallback system


