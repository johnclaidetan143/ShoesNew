# Quick Start Guide - PharmaQuick API

Get the PharmaQuick API running in 5 minutes!

## Prerequisites
- Python 3.8+
- pip

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python seed.py
```

This creates:
- SQLite database
- Admin account (admin@pharmaquick.com / admin@123)
- Sample customer (customer@example.com / customer@123)
- 16 sample products

### 3. Start Server
```bash
python run.py
```

Server runs at: `http://localhost:5000`

## Test the API

### 1. Login as Admin
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pharmaquick.com",
    "password": "admin@123"
  }'
```

Response includes `access_token` - copy this!

### 2. Get Products
```bash
curl http://localhost:5000/api/products
```

### 3. Get User Profile (Replace TOKEN with your access_token)
```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### 4. Create Product (Admin only)
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin 500mg",
    "description": "Pain relief",
    "price": 4.99,
    "stock": 200,
    "category": "general"
  }'
```

### 5. Add to Cart
```bash
curl -X POST http://localhost:5000/api/cart \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### 6. View Cart
```bash
curl http://localhost:5000/api/cart \
  -H "Authorization: Bearer TOKEN"
```

### 7. Checkout
```bash
curl -X POST http://localhost:5000/api/orders/checkout \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Key Features to Explore

| Feature | Endpoint |
|---------|----------|
| Register | POST /api/auth/register |
| Login | POST /api/auth/login |
| Products | GET/POST /api/products |
| Cart | GET/POST/PUT/DELETE /api/cart |
| Orders | POST /api/orders/checkout, GET /api/orders |
| Profile | GET/PUT /api/user/profile |
| Addresses | GET/POST/PUT/DELETE /api/user/addresses |
| Notifications | GET /api/user/notifications |
| Admin Users | GET /api/user/admin/users |

## Environment Variables

Edit `.env` to customize:
```
FLASK_ENV=development
FLASK_PORT=5000
DATABASE_URL=sqlite:///pharmaquick.db
```

## Switch to Production

```bash
FLASK_ENV=production FLASK_DEBUG=False python run.py
```

## Database Reset

```bash
# Delete database and reseed
rm pharmaquick.db
python seed.py
```

## Common Issues

**Port already in use?**
```bash
FLASK_PORT=5001 python run.py
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Database locked?**
```bash
rm pharmaquick.db
python seed.py
```

## Next Steps

1. Customize product categories in `app/models.py`
2. Add email notifications
3. Implement payment processing
4. Add more validation rules
5. Deploy to production

## Full Documentation

See `README.md` for complete API documentation.

---

**Enjoy building with PharmaQuick! 🚀**
