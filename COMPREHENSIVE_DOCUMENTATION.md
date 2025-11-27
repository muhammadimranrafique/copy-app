# School Copy Manufacturing - Comprehensive Technical Documentation

## Executive Summary

### What is School Copy Manufacturing?

School Copy Manufacturing is a full-stack business management application designed for a manufacturing company that produces school supplies (notebooks, copies, stationery). The application streamlines operations by managing clients (schools and dealers), tracking orders, recording payments, monitoring expenses, and generating financial reports.

### Main Features

- **Client Management (Leaders)**: Manage schools and dealers with contact information and account balances
- **Product Inventory**: Track products with cost/sale prices, stock quantities, and categories
- **Order Management**: Create and track orders with status updates and invoice generation
- **Payment Processing**: Record payments with multiple methods (Cash, Bank Transfer, Cheque, UPI) and generate professional PDF receipts
- **Expense Tracking**: Monitor business expenses across categories (Printing, Delivery, Material, Staff, Utilities, Misc)
- **Dashboard Analytics**: Real-time business metrics including revenue, profit, and recent transactions
- **User Authentication**: Secure JWT-based authentication with role-based access control

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLModel (ORM)
- JWT Authentication
- ReportLab (PDF generation)
- Alembic (Database migrations)

**Frontend:**
- React 18 with TypeScript
- Vite (Build tool)
- TanStack Query (Data fetching)
- React Router (Navigation)
- Tailwind CSS + shadcn/ui (Styling)
- Sonner (Toast notifications)

### Target Users

- Business owners and managers of manufacturing companies
- Staff members handling orders, payments, and inventory
- Accountants tracking expenses and financial reports

---

## Detailed Technical Overview

## 1. Backend Architecture

### 1.1 Project Structure

```
backend/
├── routers/           # API endpoint handlers
│   ├── auth.py       # Authentication endpoints
│   ├── dashboard.py  # Dashboard statistics
│   ├── expenses.py   # Expense management
│   ├── leaders.py    # Client management
│   ├── orders.py     # Order management
│   ├── payments.py   # Payment processing
│   ├── products.py   # Product inventory
│   └── schools.py    # School-specific endpoints
├── services/         # Business logic services
│   ├── invoice_generator.py        # PDF invoice generation
│   └── payment_receipt_generator.py # PDF receipt generation
├── utils/            # Utility functions
│   └── auth.py       # Authentication utilities
├── alembic/          # Database migrations
├── models.py         # Database models
├── database.py       # Database configuration
├── config.py         # Application settings
└── main.py           # Application entry point
```

### 1.2 Core Technologies

**FastAPI Framework:**
- Modern, fast web framework for building APIs
- Automatic OpenAPI documentation at `/docs`
- Built-in request validation using Pydantic
- Async support for high performance

**SQLModel ORM:**
- Combines SQLAlchemy and Pydantic
- Type-safe database operations
- Automatic schema validation

**PostgreSQL Database:**
- Relational database for data persistence
- ACID compliance for transaction safety
- Connection string: `postgresql://user:password@host:port/database`

### 1.3 Database Schema

#### Users Table
```python
class User(SQLModel, table=True):
    id: UUID (Primary Key)
    email: str (Unique)
    full_name: str
    role: str (admin/manager/staff)
    hashed_password: str
    is_active: bool
    created_at: datetime
```

#### Clients Table (Leaders/Schools/Dealers)
```python
class Client(SQLModel, table=True):
    id: UUID (Primary Key)
    name: str
    type: ClientType (School/Dealer)
    contact: str
    address: str
    opening_balance: float
    created_at: datetime
    
    # Relationships
    orders: List[Order]
    payments: List[Payment]
```

#### Products Table
```python
class Product(SQLModel, table=True):
    id: UUID (Primary Key)
    name: str
    category: str
    cost_price: float
    sale_price: float
    stock_quantity: int
    unit: str (default: "pcs")
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

#### Orders Table
```python
class Order(SQLModel, table=True):
    id: UUID (Primary Key)
    order_number: str (Unique)
    client_id: UUID (Foreign Key -> clients.id)
    total_amount: float
    status: OrderStatus (Pending/In Production/Delivered/Paid)
    order_date: datetime
    created_at: datetime
    
    # Relationships
    client: Client (eager loaded)
    payments: List[Payment]
```

#### Payments Table
```python
class Payment(SQLModel, table=True):
    id: UUID (Primary Key)
    amount: float
    mode: PaymentMode (Cash/Bank Transfer/Cheque/UPI)
    status: PaymentStatus (Pending/Partial/Completed)
    reference_number: Optional[str]
    order_id: Optional[UUID] (Foreign Key -> orders.id)
    client_id: UUID (Foreign Key -> clients.id)
    payment_date: datetime
    created_at: datetime
    
    # Relationships
    order: Optional[Order]
    client: Client (eager loaded)
```

#### Expenses Table
```python
class Expense(SQLModel, table=True):
    id: UUID (Primary Key)
    category: ExpenseCategory (PRINTING/DELIVERY/MATERIAL/STAFF/UTILITIES/MISC)
    amount: float
    description: str
    payment_method: Optional[str]
    reference_number: Optional[str]
    expense_date: datetime
    created_at: datetime
```

### 1.4 API Endpoints

#### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `POST /logout` - Logout user
- `GET /me` - Get current user info
- `POST /refresh-token` - Refresh access token
- `GET /verify-token` - Verify token validity

#### Leaders (`/api/v1/leaders`)
- `GET /` - List all leaders (schools/dealers)
- `GET /{leader_id}` - Get specific leader
- `POST /` - Create new leader
- `PUT /{leader_id}` - Update leader
- `DELETE /{leader_id}` - Delete leader (admin only)

#### Products (`/api/v1/products`)
- `GET /` - List all products (with filters)
- `GET /{product_id}` - Get specific product
- `POST /` - Create new product
- `PUT /{product_id}` - Update product
- `DELETE /{product_id}` - Delete product (admin only)
- `GET /category/{category}` - Get products by category

#### Orders (`/api/v1/orders`)
- `GET /` - List all orders (with pagination and filters)
- `GET /{order_id}` - Get specific order
- `POST /` - Create new order
- `PUT /{order_id}` - Update order
- `DELETE /{order_id}` - Delete order (admin/manager only)
- `PATCH /{order_id}/status` - Update order status
- `POST /{order_id}/invoice` - Generate PDF invoice

#### Payments (`/api/v1/payments`)
- `GET /` - List all payments
- `GET /{payment_id}` - Get specific payment
- `POST /` - Record new payment
- `PUT /{payment_id}` - Update payment
- `DELETE /{payment_id}` - Delete payment (admin only)
- `POST /{payment_id}/receipt` - Generate PDF receipt

#### Expenses (`/api/v1/expenses`)
- `GET /` - List all expenses
- `GET /{expense_id}` - Get specific expense
- `POST /` - Add new expense
- `PUT /{expense_id}` - Update expense
- `DELETE /{expense_id}` - Delete expense
- `GET /date/{date_str}` - Get expenses by date
- `GET /category/{category}` - Get expenses by category

#### Dashboard (`/api/v1/dashboard`)
- `GET /stats` - Get dashboard statistics
- `GET /revenue` - Get revenue statistics
- `GET /expenses` - Get expense summary
- `GET /reports/daily` - Daily report
- `GET /reports/weekly` - Weekly report
- `GET /reports/monthly` - Monthly report
- `GET /reports/profit-loss` - Profit & loss statement

### 1.5 Authentication & Authorization

**JWT Token-Based Authentication:**

```python
# Token Creation
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

**Password Hashing:**
- Uses passlib with sha256_crypt (fallback) and bcrypt
- Secure password verification and hashing

**Protected Routes:**
- All API endpoints require valid JWT token
- Token passed in Authorization header: `Bearer <token>`
- Token expires after 30 minutes (configurable)

**Role-Based Access:**
- Admin: Full access to all operations
- Manager: Can manage orders, payments, expenses
- Staff: Limited access to view and create operations

### 1.6 PDF Generation Services

#### Invoice Generator
```python
class InvoiceGenerator:
    def generate_invoice(self, order_data: Dict, client_data: Dict) -> str:
        # Creates professional A4 invoice with:
        # - Company header and branding
        # - Client billing information
        # - Order items table
        # - Totals and tax calculations
        # - QR code for verification
        # - Professional footer
```

#### Payment Receipt Generator
```python
class ProfessionalInvoiceGenerator:
    def generate_receipt(self, payment_data: Dict, client_data: Dict) -> str:
        # Creates eye-catching payment receipt with:
        # - Premium color palette
        # - Payment details spotlight
        # - Client information section
        # - QR code verification
        # - Professional styling
```

### 1.7 Configuration Management

**Environment Variables (.env):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/schoolcopy_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
COMPANY_NAME=School Copy Manufacturing
COMPANY_ADDRESS=123 Business Street, Karachi, Pakistan
COMPANY_PHONE=+92 300 1234567
INVOICE_DIR=./invoices
```

**Settings Class:**
```python
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    company_name: str
    invoice_dir: str
    # ... more settings
    
    class Config:
        env_file = ".env"
```

---

## 2. Frontend Architecture

### 2.1 Project Structure

```
frontend/src/
├── components/
│   ├── ui/              # Reusable UI components (shadcn/ui)
│   ├── ErrorBoundary.tsx
│   ├── Layout.tsx       # Main layout wrapper
│   ├── LoadingSpinner.tsx
│   ├── ProtectedRoute.tsx
│   ├── StatCard.tsx
│   └── WelcomeAlert.tsx
├── hooks/
│   ├── api.ts           # API hooks
│   ├── useAuthenticatedQuery.ts
│   └── useCurrency.ts   # Currency formatting
├── lib/
│   ├── api-client.ts    # API client singleton
│   ├── api-types.ts     # TypeScript types
│   ├── auth-context.ts  # Auth context definition
│   ├── useAuth.ts       # Auth hook
│   └── utils.ts         # Utility functions
├── pages/
│   ├── Dashboard.tsx
│   ├── Leaders.tsx
│   ├── Products.tsx
│   ├── Orders.tsx
│   ├── Payments.tsx
│   ├── Expenses.tsx
│   ├── Login.tsx
│   └── Settings.tsx
├── App.tsx              # Root component
└── main.tsx             # Entry point
```

### 2.2 Core Technologies

**React 18:**
- Modern React with hooks
- Concurrent rendering features
- Improved performance

**TypeScript:**
- Type-safe development
- Better IDE support
- Compile-time error checking

**Vite:**
- Fast development server
- Hot module replacement (HMR)
- Optimized production builds

**TanStack Query (React Query):**
- Server state management
- Automatic caching and refetching
- Optimistic updates
- Background synchronization

**React Router v6:**
- Client-side routing
- Protected routes
- Nested routing support

**Tailwind CSS:**
- Utility-first CSS framework
- Responsive design utilities
- Custom design system

**shadcn/ui:**
- High-quality React components
- Built on Radix UI primitives
- Fully customizable
- Accessible by default

### 2.3 State Management

**Authentication State:**
```typescript
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  loginWithRedirect: (options) => Promise<void>;
  logout: () => Promise<void>;
}
```

**Server State (TanStack Query):**
- Automatic caching with 5-minute stale time
- 30-minute cache retention
- Smart retry logic (skip 401/403/404)
- Exponential backoff for retries

**Local State:**
- Component-level state with useState
- Form state management
- UI state (modals, dialogs)

### 2.4 API Communication

**API Client Architecture:**

```typescript
class ApiClient {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    // Handle 401 -> redirect to login
    // Handle 204 -> return null
    // Parse JSON response
    // Throw ApiError on failure
  }

  private async fetchJson<T>(endpoint: string, init?: RequestInit): Promise<T> {
    // Add auth headers
    // Make fetch request
    // Handle response
  }
}
```

**API Base URL:**
```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
```

**Error Handling:**
```typescript
class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
  }
}
```

### 2.5 Routing Structure

```typescript
<BrowserRouter>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/*" element={
      <ProtectedRoute>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leaders" element={<Leaders />} />
            <Route path="/products" element={<Products />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </ProtectedRoute>
    } />
  </Routes>
</BrowserRouter>
```

**Protected Route Component:**
- Checks for valid authentication token
- Redirects to login if not authenticated
- Shows loading state during auth check

### 2.6 Component Patterns

**Custom Hooks:**

```typescript
// useAuthenticatedQuery - Wrapper for authenticated API calls
function useAuthenticatedQuery<T>(
  queryFn: () => Promise<T>,
  options: {
    isReady: boolean;
    onError?: (error: Error) => void;
  }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (options.isReady) {
      loadData();
    }
  }, [options.isReady]);
  
  return { data, loading, refetch };
}
```

**Currency Formatting:**
```typescript
function useCurrency() {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  };
  
  return { formatCurrency };
}
```

**Error Boundary:**
```typescript
class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

---

## 3. Deployment Guide

### 3.1 Prerequisites

**System Requirements:**
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- PostgreSQL 12+ (database)
- Git (version control)

**Development Tools:**
- Code editor (VS Code recommended)
- Terminal/Command prompt
- Web browser (Chrome/Firefox)

### 3.2 Local Development Setup

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd saleem_copy_app
```

#### Step 2: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Database Setup
```bash
# Install PostgreSQL and create database
psql -U postgres
CREATE DATABASE schoolcopy_db;
CREATE USER schoolcopy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE schoolcopy_db TO schoolcopy_user;
\q
```

#### Step 4: Environment Configuration
```bash
# Create .env file in backend directory
cp .env.example .env

# Edit .env with your settings:
DATABASE_URL=postgresql://schoolcopy_user:your_password@localhost:5432/schoolcopy_db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
COMPANY_NAME=School Copy Manufacturing
COMPANY_ADDRESS=123 Business Street, Karachi, Pakistan
COMPANY_PHONE=+92 300 1234567
INVOICE_DIR=./invoices
```

#### Step 5: Initialize Database
```bash
# Run database migrations
python -m alembic upgrade head

# Create initial admin user (optional)
python create_admin.py
```

#### Step 6: Start Backend Server
```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

#### Step 7: Frontend Setup
```bash
# Open new terminal and navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local:
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

#### Step 8: Start Frontend Development Server
```bash
# Start development server
npm run dev

# Frontend will be available at: http://localhost:5173
```

### 3.3 Production Deployment

#### Option A: Docker Deployment (Recommended)

**1. Create Docker Compose Configuration:**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: schoolcopy_db
      POSTGRES_USER: schoolcopy_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: postgresql://schoolcopy_user:${DB_PASSWORD}@db:5432/schoolcopy_db
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    networks:
      - app-network
    volumes:
      - ./invoices:/app/invoices

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - app-network
    volumes:
      - ./ssl:/etc/nginx/ssl

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

**2. Backend Dockerfile:**

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create invoices directory
RUN mkdir -p invoices

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**3. Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile.prod
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

**4. Nginx Configuration:**

```nginx
# frontend/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
```

**5. Deploy with Docker Compose:**

```bash
# Create production environment file
cp .env.example .env.prod

# Edit .env.prod with production values:
DB_PASSWORD=secure-database-password
SECRET_KEY=super-secure-secret-key-for-production

# Build and start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Option B: Traditional Server Deployment

**1. Server Setup (Ubuntu 20.04+):**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx nodejs npm git

# Install PM2 for process management
sudo npm install -g pm2
```

**2. Database Setup:**

```bash
# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE schoolcopy_db;
CREATE USER schoolcopy_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE schoolcopy_db TO schoolcopy_user;
\q

# Configure PostgreSQL for remote connections (if needed)
sudo nano /etc/postgresql/12/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# Add: local   schoolcopy_db   schoolcopy_user   md5

sudo systemctl restart postgresql
```

**3. Application Deployment:**

```bash
# Clone repository
cd /opt
sudo git clone <repository-url> schoolcopy
sudo chown -R $USER:$USER /opt/schoolcopy
cd /opt/schoolcopy

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run database migrations
python -m alembic upgrade head

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'schoolcopy-backend',
    script: 'venv/bin/uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    cwd: '/opt/schoolcopy/backend',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

# Start backend with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

**4. Frontend Build and Deploy:**

```bash
# Build frontend
cd /opt/schoolcopy/frontend
npm install
npm run build

# Copy build to nginx directory
sudo cp -r dist/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html
```

**5. Nginx Configuration:**

```bash
# Create nginx site configuration
sudo nano /etc/nginx/sites-available/schoolcopy

# Add the nginx configuration from above

# Enable site
sudo ln -s /etc/nginx/sites-available/schoolcopy /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

**6. SSL Certificate:**

```bash
# Get SSL certificate with Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3.4 Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/schoolcopy_db

# Security
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Company Information
COMPANY_NAME=School Copy Manufacturing
COMPANY_ADDRESS=123 Business Street, Karachi, Pakistan
COMPANY_PHONE=+92 300 1234567
COMPANY_EMAIL=info@schoolcopy.com

# File Storage
INVOICE_DIR=./invoices
UPLOAD_DIR=./uploads

# CORS (for production)
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

**Frontend (.env.local):**
```bash
# API Configuration
VITE_API_BASE_URL=https://your-domain.com/api/v1

# App Configuration
VITE_APP_NAME=School Copy Management
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false
```

### 3.5 Monitoring and Maintenance

**Health Check Endpoints:**
```bash
# Backend health
curl https://your-domain.com/api/v1/health

# Database connectivity
curl https://your-domain.com/api/v1/health/db
```

**Log Monitoring:**
```bash
# PM2 logs
pm2 logs schoolcopy-backend

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /opt/schoolcopy/backend/logs/app.log
```

**Backup Strategy:**
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="schoolcopy_db"

# Create backup
pg_dump -U schoolcopy_user -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

# Add to crontab for daily backups:
# 0 2 * * * /opt/scripts/backup.sh
```

**Performance Monitoring:**
```bash
# System resources
htop
df -h
free -h

# Application performance
pm2 monit

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### 3.6 Security Checklist

**Server Security:**
- [ ] Firewall configured (UFW/iptables)
- [ ] SSH key-based authentication
- [ ] Regular security updates
- [ ] Non-root user for applications
- [ ] Fail2ban for intrusion prevention

**Application Security:**
- [ ] Strong SECRET_KEY (32+ characters)
- [ ] HTTPS enabled with valid SSL certificate
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection headers

**Database Security:**
- [ ] Strong database passwords
- [ ] Limited database user privileges
- [ ] Regular database backups
- [ ] Connection encryption (SSL)

### 3.7 Troubleshooting

**Common Issues:**

1. **Backend won't start:**
   ```bash
   # Check logs
   pm2 logs schoolcopy-backend
   
   # Check database connection
   python -c "from database import engine; print('DB OK')"
   ```

2. **Frontend build fails:**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

3. **Database connection issues:**
   ```bash
   # Test connection
   psql -U schoolcopy_user -h localhost -d schoolcopy_db
   
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

4. **SSL certificate issues:**
   ```bash
   # Renew certificate
   sudo certbot renew
   
   # Check certificate status
   sudo certbot certificates
   ```

**Performance Issues:**

1. **Slow API responses:**
   - Check database query performance
   - Monitor server resources
   - Enable database query logging
   - Consider adding database indexes

2. **High memory usage:**
   - Monitor PM2 processes
   - Check for memory leaks
   - Adjust PM2 instance count

3. **Database performance:**
   - Analyze slow queries
   - Update table statistics
   - Consider connection pooling

---

## 4. Maintenance and Updates

### 4.1 Regular Maintenance Tasks

**Daily:**
- Monitor application logs
- Check system resources
- Verify backup completion

**Weekly:**
- Review security logs
- Update system packages
- Check SSL certificate expiry

**Monthly:**
- Database maintenance (VACUUM, ANALYZE)
- Review and rotate logs
- Security audit
- Performance review

### 4.2 Update Procedures

**Application Updates:**
```bash
# Backup current version
cp -r /opt/schoolcopy /opt/schoolcopy.backup

# Pull latest changes
cd /opt/schoolcopy
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head

# Update frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/

# Restart services
pm2 restart schoolcopy-backend
sudo systemctl reload nginx
```

**Database Migrations:**
```bash
# Create migration
cd /opt/schoolcopy/backend
source venv/bin/activate
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

This completes the comprehensive deployment guide for the School Copy Management System. The system is now ready for production deployment with proper security, monitoring, and maintenance procedures.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  };
  
  return { formatCurrency };
}
```

### 2.7 Responsive Design

**Mobile-First Approach:**
- Base styles for mobile devices
- Progressive enhancement for larger screens
- Tailwind breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)

**Responsive Patterns:**
```tsx
// Grid layouts
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

// Flexible spacing
<div className="p-4 sm:p-6 lg:p-8">

// Conditional rendering
<div className="flex flex-col sm:flex-row">
```

---

## 3. Frontend-Backend Communication

### 3.1 Data Flow

**Request Flow:**
1. User interacts with UI component
2. Component calls API function from api-client.ts
3. API client adds authentication headers
4. Request sent to FastAPI backend
5. Backend validates JWT token
6. Backend processes request and queries database
7. Backend returns JSON response
8. Frontend updates UI with response data

**Example: Creating a Payment**

Frontend:
```typescript
async createPayment(data: Partial<Payment>): Promise<ApiResponse<Payment>> {
  const response = await this.fetchJson<Payment>('/payments/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return { success: true, data: response };
}
```

Backend:
```python
@router.post("/", response_model=PaymentRead, status_code=201)
def create_payment(
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verify client exists
    # Create payment record
    # Return payment with client data
```

### 3.2 Field Name Mapping

**Frontend (camelCase) ↔ Backend (snake_case):**

```typescript
// Frontend sends:
{
  orderNumber: "ORD-1001",
  leaderId: "uuid",
  totalAmount: 5000,
  paymentDate: "2025-01-15"
}

// Backend receives and converts:
{
  order_number: "ORD-1001",
  client_id: "uuid",
  total_amount: 5000,
  payment_date: datetime(2025, 1, 15)
}
```

**Pydantic Models Handle Conversion:**
```python
class PaymentRead(SQLModel):
    id: UUID
    amount: float
    method: str = PydanticField(..., alias="mode")
    paymentDate: datetime = PydanticField(..., alias="payment_date")
    
    class Config:
        populate_by_name = True  # Allow both names
```

### 3.3 Authentication Flow

**Login Process:**
1. User submits email/password
2. Frontend sends POST to `/api/v1/auth/login`
3. Backend validates credentials
4. Backend generates JWT token
5. Frontend stores token in localStorage
6. Frontend stores user info in localStorage
7. All subsequent requests include token in Authorization header

**Token Refresh:**
- Token expires after 30 minutes
- Frontend can call `/api/v1/auth/refresh-token` to get new token
- On 401 response, frontend clears storage and redirects to login

### 3.4 Error Handling

**Backend Error Responses:**
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)
```

**Frontend Error Handling:**
```typescript
try {
  const result = await api.createPayment(data);
  toast.success('Payment created successfully');
} catch (error) {
  if (error instanceof ApiError) {
    toast.error(error.message);
  } else {
    toast.error('An unexpected error occurred');
  }
}
```

---

## 4. Key Services & Modules

### 4.1 Authentication Service

**Responsibilities:**
- User registration and login
- Password hashing and verification
- JWT token generation and validation
- Token refresh mechanism
- Current user retrieval

**Key Functions:**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool
def get_password_hash(password: str) -> str
def create_access_token(data: dict, expires_delta: timedelta)
def authenticate_user(session: Session, email: str, password: str) -> User
def get_current_user(token: str) -> User
```

### 4.2 PDF Generation Services

**Invoice Generator:**
- Creates professional A4 invoices
- Includes company branding
- Itemized order details
- QR code for verification
- Saved to `./invoices/` directory

**Payment Receipt Generator:**
- Premium design with color palette
- Payment amount spotlight
- Client information display
- Professional formatting
- QR code verification

### 4.3 Dashboard Service

**Responsibilities:**
- Calculate business metrics
- Aggregate financial data
- Generate reports (daily/weekly/monthly)
- Profit & loss statements
- Revenue and expense analysis

**Key Metrics:**
- Total orders count
- Total revenue
- Total payments received
- Total expenses
- Net profit
- Pending orders

---

## 5. External Integrations

### 5.1 Database (PostgreSQL)

**Connection:**
- SQLModel engine with connection pooling
- Echo mode for SQL logging (development)
- Automatic table creation on startup

**Migrations:**
- Alembic for database schema versioning
- Migration files in `alembic/versions/`
- Commands: `alembic upgrade head`, `alembic revision`

### 5.2 PDF Libraries

**ReportLab:**
- Professional PDF generation
- Custom layouts and styling
- Tables, images, and QR codes
- A4 page size support

**QRCode:**
- Generate verification QR codes
- Embedded in invoices and receipts
- Contains transaction details

### 5.3 Third-Party Services (Planned)

**Google Sheets Integration:**
- Configuration in settings for credentials
- Sync data to Google Sheets
- Currently configured but not implemented

**Email Service:**
- Password reset emails
- Invoice/receipt delivery
- Currently placeholder implementation

---

## 6. Security Considerations

### 6.1 Authentication Security

- JWT tokens with expiration
- Secure password hashing (sha256_crypt/bcrypt)
- Token validation on every request
- Role-based access control

### 6.2 API Security

- CORS middleware configured for allowed origins
- Input validation using Pydantic models
- SQL injection prevention via ORM
- XSS protection through proper escaping

### 6.3 Data Protection

- Passwords never stored in plain text
- Sensitive data not logged
- Environment variables for secrets
- Database credentials in .env file

---

## 7. Development & Deployment

### 7.1 Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

### 7.2 Environment Configuration

**Backend .env:**
```
DATABASE_URL=postgresql://user:password@localhost:5432/schoolcopy_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend .env:**
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_DEBUG=true
```

### 7.3 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 7.4 Production Deployment

**Backend:**
- Use production WSGI server (Gunicorn)
- Set DEBUG=False
- Use strong SECRET_KEY
- Configure production database
- Enable HTTPS

**Frontend:**
```bash
npm run build  # Creates dist/ folder
# Serve with Nginx or similar
```

---

## 8. Code Examples

### 8.1 Creating a New API Endpoint

**Backend (routers/example.py):**
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models import User
from utils.auth import get_current_user

router = APIRouter(prefix="/example", tags=["Example"])

@router.get("/")
def get_examples(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return {"message": "Hello from example endpoint"}
```

**Register in main.py:**
```python
from routers import example
app.include_router(example.router, prefix="/api/v1")
```

### 8.2 Creating a New Frontend Page

**pages/Example.tsx:**
```typescript
import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/useAuth';

export default function Example() {
  const { user } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch data
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Example Page</h1>
      {/* Content */}
    </div>
  );
}
```

**Add to App.tsx:**
```typescript
<Route path="/example" element={<Example />} />
```

### 8.3 Adding a New Database Model

**models.py:**
```python
class NewModel(SQLModel, table=True):
    __tablename__ = "new_models"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Create migration:**
```bash
alembic revision --autogenerate -m "add new_model table"
alembic upgrade head
```

---

## 9. Testing

### 9.1 Backend Testing

**Test Files:**
- `test_db_connection.py` - Database connectivity
- `test_payment_endpoints.py` - Payment API tests
- `test_products_api.py` - Product API tests
- `test_order_number_fix.py` - Order number validation

### 9.2 Frontend Testing

**Manual Testing:**
- Login/logout flow
- CRUD operations for all entities
- Responsive design on different devices
- Error handling and validation

---

## 10. Troubleshooting

### Common Issues

**Backend won't start:**
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running
- Verify all dependencies installed

**Frontend can't connect to backend:**
- Check VITE_API_BASE_URL
- Verify CORS settings in backend
- Ensure backend is running on correct port

**Authentication errors:**
- Clear localStorage
- Check token expiration
- Verify SECRET_KEY matches

**Database errors:**
- Run migrations: `alembic upgrade head`
- Check database permissions
- Verify connection string

---

## Conclusion

This School Copy Manufacturing application provides a complete business management solution with modern architecture, secure authentication, and professional document generation. The separation of concerns between frontend and backend, combined with type-safe development practices, ensures maintainability and scalability for future enhancements.
n prevention through SQLModel ORM
- Request rate limiting (planned)
- HTTPS enforcement in production

### 6.3 Data Protection

- Sensitive data encryption at rest
- Secure token storage in localStorage
- Environment variables for secrets
- Database connection security

---

## 7. Performance Optimizations

### 7.1 Frontend Performance

**React Query Optimizations:**
- 5-minute stale time for cached data
- 30-minute cache retention
- Background refetching
- Optimistic updates for mutations

**Bundle Optimization:**
- Vite for fast development builds
- Tree shaking for unused code elimination
- Code splitting with React.lazy
- Asset optimization

**UI Performance:**
```typescript
// Debounced search
const debouncedSearch = useMemo(
  () => debounce((term: string) => {
    setSearchTerm(term);
  }, 300),
  []
);

// Memoized components
const MemoizedDataTable = memo(DataTable);
```

### 7.2 Backend Performance

**Database Optimizations:**
- Indexed columns for frequent queries
- Connection pooling
- Lazy loading of relationships
- Efficient query patterns

**API Response Optimization:**
- Pagination for large datasets
- Field selection (planned)
- Response compression
- Caching headers

---

## 8. Testing Strategy

### 8.1 Frontend Testing

**Unit Tests:**
- Component testing with React Testing Library
- Hook testing
- Utility function tests
- API client tests

**Integration Tests:**
- User flow testing
- API integration tests
- Authentication flow tests

### 8.2 Backend Testing

**API Tests:**
- Endpoint testing with FastAPI TestClient
- Authentication tests
- Database operation tests
- Error handling tests

**Test Structure:**
```python
def test_create_payment_success(client: TestClient, test_user):
    response = client.post(
        "/api/v1/payments/",
        json={"amount": 1000, "method": "cash"},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 1000
```

---

## 9. Deployment & DevOps

### 9.1 Development Environment

**Frontend Setup:**
```bash
npm install
npm run dev  # Runs on http://localhost:5173
```

**Backend Setup:**
```bash
pip install -r requirements.txt
uvicorn main:app --reload  # Runs on http://127.0.0.1:8000
```

### 9.2 Production Deployment

**Frontend Build:**
```bash
npm run build
# Generates optimized static files in dist/
```

**Backend Deployment:**
- Docker containerization (planned)
- Environment variable configuration
- Database migration on deployment
- Static file serving

### 9.3 Environment Configuration

**Frontend (.env):**
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_APP_TITLE=Saleem Copy App
```

**Backend (.env):**
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 10. Monitoring & Logging

### 10.1 Application Logging

**Backend Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

**Frontend Error Tracking:**
- Console error logging
- API error tracking
- User action logging (planned)

### 10.2 Health Monitoring

**Health Check Endpoint:**
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

---

## 11. Future Enhancements

### 11.1 Planned Features

**Business Features:**
- Multi-currency support
- Advanced reporting and analytics
- Inventory management
- Customer relationship management
- Automated invoice generation
- Payment reminders

**Technical Improvements:**
- Real-time notifications (WebSocket)
- Mobile app development
- Offline capability
- Advanced search and filtering
- Data export/import functionality
- API rate limiting
- Comprehensive audit logging

### 11.2 Scalability Considerations

**Database Scaling:**
- Read replicas for query optimization
- Database sharding for large datasets
- Connection pooling optimization

**Application Scaling:**
- Horizontal scaling with load balancers
- Microservices architecture (future)
- Caching layer (Redis)
- CDN for static assets

---

## 12. Troubleshooting Guide

### 12.1 Common Issues

**Authentication Problems:**
- Clear localStorage and retry login
- Check token expiration
- Verify API endpoint connectivity

**Database Connection Issues:**
- Verify DATABASE_URL environment variable
- Check PostgreSQL service status
- Validate database credentials

**API Communication Errors:**
- Check CORS configuration
- Verify API base URL
- Inspect network requests in browser DevTools

### 12.2 Debug Commands

**Backend Debugging:**
```bash
# Run with debug logging
uvicorn main:app --reload --log-level debug

# Database migrations
alembic upgrade head
alembic current
```

**Frontend Debugging:**
```bash
# Development with source maps
npm run dev

# Build analysis
npm run build -- --analyze
```

---

## 13. API Reference

### 13.1 Authentication Endpoints

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh-token
GET  /api/v1/auth/me
```

### 13.2 Business Endpoints

```
# Leaders (Clients)
GET    /api/v1/leaders/
POST   /api/v1/leaders/
GET    /api/v1/leaders/{id}
PUT    /api/v1/leaders/{id}
DELETE /api/v1/leaders/{id}

# Products
GET    /api/v1/products/
POST   /api/v1/products/
GET    /api/v1/products/{id}
PUT    /api/v1/products/{id}
DELETE /api/v1/products/{id}

# Orders
GET    /api/v1/orders/
POST   /api/v1/orders/
GET    /api/v1/orders/{id}
PUT    /api/v1/orders/{id}
DELETE /api/v1/orders/{id}
GET    /api/v1/orders/{id}/invoice

# Payments
GET    /api/v1/payments/
POST   /api/v1/payments/
GET    /api/v1/payments/{id}
PUT    /api/v1/payments/{id}
DELETE /api/v1/payments/{id}
GET    /api/v1/payments/{id}/receipt

# Expenses
GET    /api/v1/expenses/
POST   /api/v1/expenses/
GET    /api/v1/expenses/{id}
PUT    /api/v1/expenses/{id}
DELETE /api/v1/expenses/{id}

# Dashboard
GET    /api/v1/dashboard/metrics
GET    /api/v1/dashboard/reports
```

---

## 14. Conclusion

The Saleem Copy App is a comprehensive business management solution built with modern web technologies. It provides a solid foundation for managing clients, products, orders, payments, and expenses with a focus on user experience, security, and scalability.

**Key Strengths:**
- Modern, responsive UI with excellent UX
- Robust authentication and authorization
- Comprehensive business logic
- Professional PDF generation
- Clean, maintainable codebase
- Strong type safety with TypeScript

**Areas for Growth:**
- Enhanced reporting and analytics
- Mobile application development
- Advanced integrations
- Performance optimizations
- Comprehensive testing coverage

This documentation serves as a complete reference for developers working on the application and provides insights into the architectural decisions and implementation details that make the system robust and maintainable.