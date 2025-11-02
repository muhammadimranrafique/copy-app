# School Copy Backend API

FastAPI-based backend system for School Copy Manufacturing Business Management.

## 🚀 Features

- **RESTful API** with FastAPI
- **PostgreSQL Database** with SQLModel ORM
- **JWT Authentication** with role-based access
- **Google Sheets Integration** for bi-directional sync
- **PDF Invoice Generation** using ReportLab
- **Celery Task Queue** for async operations
- **Comprehensive CRUD** for all business entities

## 📋 Requirements

- Python 3.12+
- PostgreSQL 14+
- Redis (for Celery)
- Google Cloud credentials file

## 🔧 Installation

1. **Clone the repository**
```bash
cd backend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Set up PostgreSQL database**
```bash
createdb schoolcopy_db
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start the development server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── models.py               # SQLModel database models
├── database.py             # Database configuration
├── routers/                # API route handlers
│   ├── clients.py
│   ├── products.py
│   ├── orders.py
│   ├── payments.py
│   ├── expenses.py
│   ├── invoices.py
│   └── reports.py
├── services/               # Business logic
│   ├── google_sheets.py    # Google Sheets integration
│   └── invoice_generator.py # PDF generation
├── utils/                  # Utility functions
│   ├── auth.py             # JWT authentication
│   └── permissions.py      # Role-based access
├── requirements.txt        # Python dependencies
└── env.example            # Environment variables template
```

## 🔐 Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. **Register/Login** at `/api/v1/auth/login`
2. **Receive a token** in the response
3. **Include the token** in subsequent requests:
```
Authorization: Bearer <your-token>
```

## 🔄 Google Sheets Integration

The backend automatically syncs data with Google Sheets:

1. **Set up Google Cloud** and create a service account
2. **Download credentials** as `credentials.json`
3. **Configure** `GOOGLE_SHEET_ID` in `.env`
4. Enable automatic sync on CRUD operations

## 📄 PDF Invoice Generation

Generate invoices for orders:
```bash
POST /api/v1/orders/{order_id}/invoice
```

Features:
- Professional invoice layout
- Company branding
- QR code verification
- Itemized breakdown
- Automatic calculations

## 📊 API Endpoints

### Clients
- `GET /api/v1/clients` - List all clients
- `POST /api/v1/clients` - Create a client
- `GET /api/v1/clients/{id}` - Get client details
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Products
- `GET /api/v1/products` - List all products
- `POST /api/v1/products` - Create a product
- `GET /api/v1/products/{id}` - Get product details
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Orders
- `GET /api/v1/orders` - List all orders
- `POST /api/v1/orders` - Create an order
- `GET /api/v1/orders/{id}` - Get order details
- `POST /api/v1/orders/{id}/invoice` - Generate invoice
- `PUT /api/v1/orders/{id}` - Update order
- `DELETE /api/v1/orders/{id}` - Delete order

### Payments
- `GET /api/v1/payments` - List all payments
- `POST /api/v1/payments` - Record a payment
- `GET /api/v1/payments/{id}` - Get payment details

### Expenses
- `GET /api/v1/expenses` - List all expenses
- `POST /api/v1/expenses` - Add an expense
- `GET /api/v1/expenses/{id}` - Get expense details

### Reports
- `GET /api/v1/reports/profit-loss` - Get profit/loss report
- `GET /api/v1/reports/monthly` - Get monthly report
- `GET /api/v1/reports/yearly` - Get yearly report

## 🐳 Docker Deployment

```bash
docker build -t school-copy-backend .
docker run -p 8000:8000 school-copy-backend
```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

This project is licensed under the MIT License.
