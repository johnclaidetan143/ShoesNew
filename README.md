# PharmaQuick - Pharmacy Management Backend API

A production-ready Flask REST API for a mobile pharmacy application with complete CRUD operations, user authentication, cart management, order processing, and admin panel.

## Features

### 🔐 Authentication & Authorization
- User registration and login with JWT tokens
- Refresh token mechanism for extended sessions
- Role-based access control (Admin & Customer)
- Password hashing with bcrypt

### 📦 Product Management
- Full CRUD operations for medicines
- Category filtering (general, newborn, vitamins, antibiotics, skincare, supplements, equipment)
- Stock management
- Product images support
- Pagination for large datasets

### 🛒 Shopping Cart
- Add/remove items from cart
- Update item quantities
- Real-time stock validation
- Cart total calculation

### 📋 Order Management
- Checkout from cart
- Order status tracking (pending, processing, completed, cancelled)
- Order history with filtering
- Order cancellation with stock restoration
- Address selection during checkout

### 👤 User Profile Management
- Profile information updates
- Password change functionality
- Multiple address management
- Default address setting

### 🔔 Notifications
- Order status updates
- Real-time notification system
- Mark notifications as read

### 🛡️ Admin Panel (API Endpoints)
- User management and role assignment
- Product administration
- Order monitoring and status updates
- System statistics

## Tech Stack

- **Backend Framework**: Flask 3.0.3
- **Database ORM**: SQLAlchemy 2.0.30
- **Authentication**: Flask-JWT-Extended 4.6.0
- **Password Hashing**: Flask-Bcrypt 1.0.1
- **Environment Management**: python-dotenv 1.0.1
- **Database**: SQLite (default) / PostgreSQL (configurable)

## Project Structure

```
pharmaquick/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # Flask extensions (db, jwt, bcrypt)
│   ├── models.py            # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── products.py      # Product management routes
│   │   ├── cart.py          # Shopping cart routes
│   │   ├── orders.py        # Order management routes
│   │   └── user.py          # User profile & admin routes
│
├── config.py                # Configuration management
├── run.py                   # Application entry point
├── seed.py                  # Database seeding script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Clone/Setup Project

```bash
cd pharmaquick
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

The `.env` file contains all configuration. Update if needed:

```env
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///pharmaquick.db
```

### Step 5: Initialize Database

```bash
# Option 1: Seed with sample data
python seed.py

# Option 2: Fresh database without seed
python -c "from app import create_app; from app.extensions import db; app = create_app(); db.create_all()"
```

### Step 6: Run Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "+1234567890",
  "role": "customer"  # Optional, defaults to "customer"
}
```

**Response**: `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "customer",
    "phone": "+1234567890",
    "created_at": "2024-04-18T10:30:00"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response**: `200 OK`
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user": { ... }
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGc..."
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Product Endpoints

#### List Products
```http
GET /api/products?category=vitamins&page=1&limit=20
```

#### Get Product by ID
```http
GET /api/products/1
```

#### Create Product (Admin)
```http
POST /api/products
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Vitamin C 1000mg",
  "description": "Immune booster",
  "price": 12.50,
  "stock": 100,
  "category": "vitamins",
  "image_url": "https://..."
}
```

#### Update Product (Admin)
```http
PUT /api/products/1
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "price": 11.99,
  "stock": 95
}
```

#### Delete Product (Admin)
```http
DELETE /api/products/1
Authorization: Bearer <admin_token>
```

### Cart Endpoints

#### View Cart
```http
GET /api/cart
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "product": { ... },
      "quantity": 2,
      "subtotal": 25.00
    }
  ],
  "total": 25.00,
  "item_count": 1
}
```

#### Add to Cart
```http
POST /api/cart
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/cart/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove from Cart
```http
DELETE /api/cart/1
Authorization: Bearer <access_token>
```

#### Clear Cart
```http
DELETE /api/cart/clear
Authorization: Bearer <access_token>
```

### Order Endpoints

#### Checkout
```http
POST /api/orders/checkout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "address_id": 1  # Optional
}
```

#### Get Order History
```http
GET /api/orders
Authorization: Bearer <access_token>
```

#### Get Order Details
```http
GET /api/orders/1
Authorization: Bearer <access_token>
```

#### Update Order Status (Admin)
```http
PUT /api/orders/1/status
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "status": "processing"  # pending, processing, completed, cancelled
}
```

#### Cancel Order
```http
POST /api/orders/1/cancel
Authorization: Bearer <access_token>
```

### User Profile Endpoints

#### Get Profile
```http
GET /api/user/profile
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/user/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "phone": "+9876543210"
}
```

#### Change Password
```http
PUT /api/user/password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword",
  "confirm_password": "newpassword"
}
```

### Address Endpoints

#### List Addresses
```http
GET /api/user/addresses
Authorization: Bearer <access_token>
```

#### Add Address
```http
POST /api/user/addresses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "label": "Home",
  "street": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "is_default": true
}
```

#### Update Address
```http
PUT /api/user/addresses/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "street": "456 Oak Avenue"
}
```

#### Delete Address
```http
DELETE /api/user/addresses/1
Authorization: Bearer <access_token>
```

### Notification Endpoints

#### Get Notifications
```http
GET /api/user/notifications
Authorization: Bearer <access_token>
```

#### Mark Notification as Read
```http
PUT /api/user/notifications/1/read
Authorization: Bearer <access_token>
```

#### Mark All as Read
```http
PUT /api/user/notifications/read-all
Authorization: Bearer <access_token>
```

### Admin Endpoints

#### List All Users
```http
GET /api/user/admin/users?page=1&limit=20
Authorization: Bearer <admin_token>
```

#### Update User Role
```http
PUT /api/user/admin/users/1/role
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "admin"  # or "customer"
}
```

#### Delete User
```http
DELETE /api/user/admin/users/1
Authorization: Bearer <admin_token>
```

## Default Credentials

After running the seed script:

### Admin Account
- **Email**: `admin@pharmaquick.com`
- **Password**: `admin@123`
- **Role**: admin

### Sample Customer
- **Email**: `customer@example.com`
- **Password**: `customer@123`
- **Role**: customer

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message here"
}
```

HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | Environment mode |
| `FLASK_DEBUG` | True | Debug mode |
| `FLASK_PORT` | 5000 | Server port |
| `SECRET_KEY` | - | Flask secret key |
| `JWT_SECRET_KEY` | - | JWT signing key |
| `DATABASE_URL` | sqlite:///pharmaquick.db | Database connection |

## Database Models

### User
- id, name, email, password_hash, role, phone, created_at
- Relationships: addresses, cart_items, orders, notifications

### Product
- id, name, description, price, stock, category, image_url, is_active, created_at

### CartItem
- id, user_id, product_id, quantity
- Relationship: product

### Order
- id, user_id, total, status, address_id, created_at
- Relationships: items, address

### OrderItem
- id, order_id, product_id, quantity, unit_price

### Address
- id, user_id, label, street, city, state, zip_code, is_default

### Notification
- id, user_id, message, is_read, created_at

## Security Best Practices

1. **Environment Variables**: Never commit `.env` with real secrets
2. **Password Hashing**: All passwords are hashed with bcrypt
3. **JWT Tokens**: Use strong secret keys in production
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS appropriately for your frontend
6. **Rate Limiting**: Consider adding rate limiting for production

## Deployment

### Production Checklist

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Use a production database (PostgreSQL recommended)
4. Change `SECRET_KEY` and `JWT_SECRET_KEY`
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Enable HTTPS/SSL
7. Set up proper logging
8. Configure CORS headers

### Gunicorn Example

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Testing

Create a test request:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@pharmaquick.com","password":"admin@123"}'
```

## Troubleshooting

### Database Lock Error
- Delete `pharmaquick.db` and run `python seed.py` again

### Port Already in Use
- Change `FLASK_PORT` in `.env` or run on different port:
  ```bash
  FLASK_PORT=5001 python run.py
  ```

### JWT Token Errors
- Ensure `Authorization: Bearer <token>` header format is correct
- Token may have expired, use refresh endpoint

## Contributing

This is a starter template. Feel free to extend with:
- Payment integration
- Email notifications
- Advanced search and filters
- Order tracking in real-time
- Review and rating system
- Loyalty program
- Multi-language support

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify database configuration

---

**Made with ❤️ for pharmacy management**
"# shoes" 
"# ShoesNew" 
