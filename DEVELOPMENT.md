# Development Notes & Architecture

## System Architecture

### Three-Tier Architecture
```
┌─────────────────┐
│   Flask API     │  (Routes & Business Logic)
├─────────────────┤
│  SQLAlchemy     │  (ORM & Database Abstraction)
├─────────────────┤
│  SQLite/PgSQL   │  (Persistent Data Store)
└─────────────────┘
```

### Request Flow
```
Client Request
    ↓
Authentication (JWT)
    ↓
Authorization Check (Role-based)
    ↓
Route Handler
    ↓
Database Query/Operation
    ↓
Response (JSON)
```

## Key Design Patterns

### 1. Application Factory Pattern
- `create_app()` in `app/__init__.py`
- Enables multiple app instances for testing
- Configuration-based environment setup

### 2. Blueprint Architecture
- Modular route organization
- Separate concerns (auth, products, cart, orders, user)
- Easy to scale and maintain

### 3. Database Models
- SQLAlchemy ORM for database abstraction
- Relationships defined at model level
- Cascading deletes for data integrity

### 4. Extensions Pattern
- Centralized initialization in `extensions.py`
- Clean separation of library setup
- Easy dependency management

## Extension Overview

| Extension | Purpose | Config |
|-----------|---------|--------|
| SQLAlchemy | ORM & Database | `SQLALCHEMY_*` |
| Flask-JWT-Extended | Token Auth | `JWT_*` |
| Flask-Bcrypt | Password Hashing | None needed |

## Authentication Flow

```
1. User Registration
   └─→ Password hashed with bcrypt
   └─→ User stored in database
   └─→ Return user data

2. User Login
   └─→ Verify email exists
   └─→ Check password hash
   └─→ Generate JWT token (includes role)
   └─→ Return access & refresh tokens

3. Protected Request
   └─→ Extract token from header
   └─→ Verify signature
   └─→ Extract identity & role
   └─→ Process request
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(256),
    role VARCHAR(20),  -- 'admin' | 'customer'
    phone VARCHAR(20),
    created_at DATETIME
);
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150),
    description TEXT,
    price FLOAT,
    stock INTEGER,
    category VARCHAR(50),
    image_url VARCHAR(300),
    is_active BOOLEAN,
    created_at DATETIME
);
```

### Relationships
- User → Addresses (1:many)
- User → CartItems (1:many)
- User → Orders (1:many)
- User → Notifications (1:many)
- Product → CartItems (1:many)
- Product → OrderItems (1:many)
- Order → OrderItems (1:many)

## Error Handling Strategy

### HTTP Status Codes
- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST (new resource)
- `400 Bad Request`: Invalid input validation failed
- `401 Unauthorized`: Authentication required/failed
- `403 Forbidden`: Authorization failed (insufficient role)
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource already exists (email duplicate)
- `500 Internal Server Error`: Unexpected server error

### Error Response Format
```json
{
  "error": "Descriptive error message"
}
```

## Security Features

### 1. Password Security
- Bcrypt hashing with salt rounds
- Minimum 6 character requirement
- Confirmation on change

### 2. Token Security
- JWT tokens with expiration
- Refresh token rotation
- Role-based claims in token

### 3. Authorization
- Admin-only endpoints protected
- User can only access own resources
- Role verification on sensitive operations

### 4. Data Validation
- Required field checking
- Type validation (int, float, string)
- Email uniqueness constraint
- Category whitelist enforcement

### 5. Database Integrity
- Foreign key constraints
- Cascade deletes to prevent orphans
- Transaction rollback on errors

## Performance Optimizations

### Implemented
- Pagination for list endpoints (20 items/page)
- Eager loading of relationships
- Query optimization with filters
- Database indexing on foreign keys

### Recommended for Future
- Caching (Redis) for frequently accessed products
- Database query optimization
- Async task queue for notifications (Celery)
- API rate limiting
- Response compression (gzip)

## Configuration Management

### Environment-Based
```python
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
```

### Settings by Environment
| Setting | Dev | Test | Prod |
|---------|-----|------|------|
| DEBUG | True | True | False |
| Database | SQLite | :memory: | PostgreSQL |
| JWT Expiry | 24h | 24h | 24h |

## Database Migrations

For production, consider using Flask-Migrate:

```bash
pip install Flask-Migrate
flask db init
flask db migrate
flask db upgrade
```

## API Rate Limiting

Consider adding for production:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Logging

Add logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## Testing Strategy

### Unit Tests Example
```python
def test_register_user(client):
    response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'test@test.com',
        'password': 'test123'
    })
    assert response.status_code == 201
```

### Integration Tests Example
```python
def test_order_flow(client, admin_token):
    # Create product
    # Add to cart
    # Checkout
    # Verify order created
    pass
```

## Common Customizations

### Add New Product Category
Edit `app/routes/products.py`:
```python
VALID_CATEGORIES = {
    "general",
    "newborn",
    "vitamins",
    "your_category",  # Add here
}
```

### Change JWT Expiry
Edit `.env`:
```
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
```

### Add New User Role
Edit `app/routes/auth.py`:
```python
VALID_ROLES = {"admin", "customer", "moderator"}
```

## Deployment Checklist

- [ ] Update SECRET_KEY and JWT_SECRET_KEY
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=False
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS headers
- [ ] Set up logging to file/service
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring/alerting
- [ ] Use environment variables for sensitive data
- [ ] Implement API versioning
- [ ] Add request validation middleware
- [ ] Configure WSGI server (Gunicorn)
- [ ] Set up reverse proxy (Nginx)

## Useful Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- JWT: https://jwt.io/
- Bcrypt: https://github.com/pyca/bcrypt
- REST Best Practices: https://restfulapi.net/

## Future Enhancements

1. **Payment Integration**
   - Stripe/PayPal API
   - Transaction logging
   - Refund handling

2. **Email Notifications**
   - Order confirmation emails
   - Shipping updates
   - Marketing newsletters

3. **Advanced Search**
   - Full-text search
   - Elasticsearch integration
   - Search analytics

4. **Mobile Analytics**
   - User behavior tracking
   - Product popularity metrics
   - Sales analytics

5. **Loyalty Program**
   - Points system
   - Discount coupons
   - VIP tiers

6. **Real-time Features**
   - WebSocket for live updates
   - Push notifications
   - Live chat support

---

For questions or issues, refer to README.md or QUICKSTART.md
