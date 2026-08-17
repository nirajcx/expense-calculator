# 📖 Core Concepts Explained

This document explains the key concepts used in this project in **simple, beginner-friendly language**. If you've never worked with a Python backend before, start here.

---

## Table of Contents

1. [Pydantic Schemas vs SQLAlchemy Models — What's the Difference?](#1-pydantic-schemas-vs-sqlalchemy-models)
2. [Dependency Injection (Depends) in FastAPI](#2-dependency-injection-depends-in-fastapi)
3. [JWT Authentication — Access Tokens & Refresh Tokens](#3-jwt-authentication)
4. [Why We Hash Passwords (and Never Store Them in Plain Text)](#4-why-we-hash-passwords)
5. [Alembic Migrations — What They Are and Why We Need Them](#5-alembic-migrations)
6. [Request/Response Lifecycle — How a Request Flows Through the App](#6-requestresponse-lifecycle)

---

## 1. Pydantic Schemas vs SQLAlchemy Models

### The Problem

When building an API, you deal with data in two very different places:

1. **The Database** — where data is permanently stored (tables, rows, columns)
2. **The API** — where data goes in (requests) and comes out (responses)

These two "shapes" of data are often **different**. For example:

- The database stores a `hashed_password` column — but you should **NEVER** send that to the client
- The client sends a `password` when registering — but you **NEVER** store that directly in the database
- The database has auto-generated fields like `id`, `created_at` — the client doesn't send those

### The Solution: Two Different Classes

| | SQLAlchemy Model | Pydantic Schema |
|---|---|---|
| **What it does** | Defines the database table structure | Defines the API data shape |
| **Lives in** | `app/models/` | `app/schemas/` |
| **Example** | `User` model with `hashed_password` | `UserResponse` without any password field |
| **Used for** | Reading from / writing to the database | Validating request data & shaping response data |

### Example

```python
# models/user.py — Database table (what's STORED)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)        # ← Stored in DB, but NEVER sent to client
    full_name = Column(String)
    created_at = Column(DateTime)

# schemas/user.py — API response (what's SENT to client)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    created_at: datetime
    # Notice: NO password field! The client never sees it.

# schemas/user.py — API request (what the CLIENT SENDS)
class UserCreate(BaseModel):
    email: EmailStr
    password: str               # ← Client sends plain password (we hash it before storing)
    full_name: str | None
    # Notice: NO id or created_at! Those are auto-generated.
```

### Think of it Like a Restaurant

- **SQLAlchemy Model** = The kitchen's recipe book (the full, internal data)
- **Pydantic Schema (Response)** = The menu shown to customers (only what they need to see)
- **Pydantic Schema (Request)** = The order form (what the customer fills out)

---

## 2. Dependency Injection (Depends) in FastAPI

### What Is It?

**Dependency injection** sounds scary, but it's a simple idea:

> Instead of an endpoint **creating** the things it needs (like a database session or user authentication), those things are **provided to it** automatically.

### A Real-World Analogy

Imagine you're a chef in a restaurant:

- **Without dependency injection**: You have to go to the market, buy ingredients, bring them back, THEN start cooking. Every. Single. Order.
- **With dependency injection**: The ingredients magically appear on your counter when you need them. You just cook.

### How It Works in This Project

```python
# WITHOUT dependency injection (BAD — repetitive and messy):
@router.get("/expenses")
def get_expenses():
    # You'd have to create a DB session manually every time
    db = SessionLocal()
    try:
        # And check authentication manually every time
        token = extract_token_from_header()
        user = validate_token(token)
        lookup_user_in_db(user)
        # THEN do the actual work
        expenses = db.query(Expense).filter(Expense.owner_id == user.id).all()
        return expenses
    finally:
        db.close()

# WITH dependency injection (GOOD — clean and reusable):
@router.get("/expenses")
def get_expenses(
    db: Session = Depends(get_db),                    # ← DB session provided automatically
    current_user: User = Depends(get_current_user),   # ← Auth checked automatically
):
    # Just do the actual work — everything else is handled!
    expenses = db.query(Expense).filter(Expense.owner_id == current_user.id).all()
    return expenses
```

### What `Depends()` Does Step by Step

1. FastAPI sees `Depends(get_db)` in the function signature
2. It calls `get_db()` — which creates a database session
3. It passes the result (the session) as the `db` parameter to your endpoint
4. When the request finishes, `get_db()` cleans up (closes the session)

### Why Use It?

- **DRY (Don't Repeat Yourself)** — Write auth logic once, reuse everywhere
- **Clean code** — Endpoints focus on business logic, not boilerplate
- **Testable** — In tests, you can swap `get_db` with a test database
- **Composable** — Dependencies can depend on other dependencies

---

## 3. JWT Authentication

### What Is a JWT?

**JWT (JSON Web Token)** is like a digital ID card. When you log in, the server gives you a signed token that proves who you are. You show this token on every subsequent request instead of sending your password each time.

### What's Inside a JWT?

A JWT has three parts (separated by dots):

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiIsImV4cCI6MTcyMTcwMDAwMH0.abc123signature
│          HEADER          │              PAYLOAD              │    SIGNATURE    │
```

- **Header**: Algorithm info (e.g., HS256)
- **Payload**: The actual data (user ID, expiration time)
- **Signature**: A cryptographic proof that the token hasn't been tampered with

> ⚠️ **Important**: JWTs are **signed**, not **encrypted**. Anyone can read the payload. That's why we only put the user ID in it — never sensitive data like passwords.

### Access Token vs Refresh Token

We use **two** tokens because of a security tradeoff:

| | Access Token | Refresh Token |
|---|---|---|
| **Purpose** | Proves who you are on each API request | Gets you a new access token without re-logging in |
| **Lifetime** | Short (30 minutes) | Long (7 days) |
| **Sent with** | Every API request (in Authorization header) | Only sent to the /refresh endpoint |
| **If stolen** | Attacker has access for max 30 min | More dangerous — should be stored securely |

### The Flow

```
1. User logs in with email + password
   └─→ Server returns: { access_token, refresh_token }

2. User makes API requests with access token
   └─→ Authorization: Bearer <access_token>
   └─→ Server validates token → returns data

3. Access token expires (after 30 min)
   └─→ Client sends refresh token to /auth/refresh
   └─→ Server returns: { new_access_token, new_refresh_token }

4. Refresh token expires (after 7 days)
   └─→ User must log in again with email + password
```

### Why Not Just Use Long-Lived Access Tokens?

If someone steals a long-lived token, they have access for a long time. With short-lived access tokens, the damage window is small. The refresh token is only sent to one specific endpoint, reducing its exposure.

---

## 4. Why We Hash Passwords

### The Problem with Storing Plain-Text Passwords

If your database gets hacked (it happens to even big companies), and passwords are stored as:

```
| email              | password       |
|--------------------|----------------|
| alice@example.com  | ilovecats123   |  ← Attacker can see this!
| bob@example.com    | qwerty456      |  ← And this!
```

Every user's password is immediately compromised. Many people reuse passwords across sites, so this is catastrophic.

### How Hashing Works

**Hashing** is a one-way transformation. You can turn a password INTO a hash, but you can never turn a hash BACK into a password.

```
"ilovecats123"  →  hash()  →  "$2b$12$LJ3m4ysX8Rn2K.mXg..."
                              (this is what we store in the database)
```

When a user logs in:
1. They send their plain password: `"ilovecats123"`
2. We hash it: `hash("ilovecats123")` → `"$2b$12$LJ3m4ys..."`
3. We compare the result with the stored hash
4. If they match → login successful!

### Why bcrypt?

We use **bcrypt** specifically because it's designed to be **slow**. Yes, slow is good here!

- Regular hashing (SHA-256): Can compute billions of hashes per second → easy to brute-force
- bcrypt: Intentionally slow → takes ~100ms per hash → brute-forcing would take centuries

```python
# In our code (app/core/security.py):
import bcrypt

# Hash a password (when user registers)
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
# Example output: "$2b$12$LJ3m4ysX8Rn2K.mXg..."

# Verify a password (when user logs in)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
# Result: True if they match, False otherwise
```

---

## 5. Alembic Migrations

### The Problem

When you change your SQLAlchemy models (e.g., add a new column to the User table), the database doesn't automatically update. You need a way to evolve the database schema over time without losing data.

### Why Not Just Auto-Create Tables?

SQLAlchemy has `Base.metadata.create_all()` which creates tables from your models. But:

| Scenario | `create_all()` | Alembic Migrations |
|----------|----------------|-------------------|
| Create new tables | ✅ Works | ✅ Works |
| Add a new column | ❌ Ignores it | ✅ Adds the column |
| Rename a column | ❌ Can't do it | ✅ Renames it |
| Remove a column | ❌ Leaves old data | ✅ Drops the column |
| Team collaboration | ❌ "Works on my machine" | ✅ Everyone runs same migrations |
| Rollback a mistake | ❌ Impossible | ✅ `alembic downgrade -1` |
| Track history | ❌ No record | ✅ Full version history |

### Think of It Like Git, but for Your Database

- **Git** tracks changes to your **code** over time
- **Alembic** tracks changes to your **database schema** over time

Each migration file is like a commit — it describes what changed and how to undo it.

### How It Works

```bash
# Step 1: You change a model (e.g., add a "phone" column to User)
# In models/user.py:
# phone = Column(String(20), nullable=True)   ← add this line

# Step 2: Generate a migration file (Alembic compares models to the DB and figures out what changed)
alembic revision --autogenerate -m "Add phone column to users"
# This creates a file in alembic/versions/ with upgrade() and downgrade() functions

# Step 3: Apply the migration (actually alter the database table)
alembic upgrade head

# Step 4: If something went wrong, rollback:
alembic downgrade -1
```

### What a Migration File Looks Like

```python
# alembic/versions/abc123_add_phone_column.py

def upgrade():
    """What to do when applying this migration."""
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    """What to do when rolling back this migration."""
    op.drop_column('users', 'phone')
```

---

## 6. Request/Response Lifecycle

Here's what happens when a client sends a request to this API, step by step:

```
CLIENT (browser, React app, mobile app, cURL, Postman)
  │
  │  Sends HTTP request:
  │  POST /api/v1/expenses/
  │  Authorization: Bearer eyJhbG...
  │  Body: {"amount": 25.50, "description": "Lunch", "date": "2025-07-23"}
  │
  ▼
┌─────────────────────────────────────────────────┐
│  1. FASTAPI RECEIVES THE REQUEST                │
│     - Matches URL to the correct router/endpoint│
│     - Runs middleware (CORS, etc.)              │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  2. DEPENDENCIES RUN (Depends)                   │
│     a. get_db() → Creates a database session    │
│     b. get_current_user() →                     │
│        - Extracts Bearer token from header      │
│        - Decodes JWT token                      │
│        - Looks up user in DB                    │
│        - Returns User object                    │
│     (If token is invalid → 401 Unauthorized)    │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  3. PYDANTIC SCHEMA VALIDATION                   │
│     - Parses the request body                   │
│     - Validates against ExpenseCreate schema    │
│       ✓ amount > 0? ✓ date is valid? etc.      │
│     (If validation fails → 422 Unprocessable)   │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  4. ROUTER (endpoint function)                   │
│     - Receives validated data + authenticated   │
│       user + DB session                         │
│     - Calls the service layer                   │
│                                                 │
│     def create_new_expense(                     │
│         expense_data: ExpenseCreate,  ← step 3  │
│         db: Session,                  ← step 2a │
│         current_user: User,           ← step 2b │
│     ):                                          │
│         return create_expense(db, expense_data, │
│                               current_user.id)  │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  5. SERVICE (business logic)                     │
│     - Validates category ownership              │
│     - Creates the Expense ORM object            │
│     - Saves to database (db.add + db.commit)    │
│     - Returns the created Expense               │
│     (If business rule fails → raises exception) │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  6. DATABASE (SQLAlchemy + PostgreSQL)          │
│     - INSERT INTO expenses (amount, ...) ...    │
│     - Returns the new row with auto-gen id      │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  7. RESPONSE                                     │
│     - FastAPI serializes the result using        │
│       ExpenseResponse schema                    │
│     - Only includes fields defined in the schema│
│     - Sends JSON response with status 201       │
└────────────────────┬────────────────────────────┘
                     ▼
CLIENT receives:
{
    "id": 1,
    "amount": 25.50,
    "description": "Lunch",
    "date": "2025-07-23",
    "category_id": null,
    "category": null,
    "owner_id": 1,
    "created_at": "2025-07-23T12:00:00",
    "updated_at": "2025-07-23T12:00:00"
}
```

### Summary of the Flow

```
Client → FastAPI → Dependencies (auth + DB) → Schema Validation → Router → Service → Database
                                                                                        │
Client ← FastAPI ← Response Schema (serialization) ← Router ← Service ← Database ──────┘
```

### Where Errors Are Caught

| Step | What Can Go Wrong | HTTP Status |
|------|-------------------|-------------|
| Dependencies | Invalid/expired token | 401 Unauthorized |
| Schema Validation | Missing field, wrong type, invalid value | 422 Unprocessable Entity |
| Service | Business rule violation (e.g., duplicate email) | 409 Conflict |
| Service | Resource not found (with ownership check) | 404 Not Found |
| Database | Connection error, constraint violation | 500 Internal Server Error |

---

## 🎓 What to Learn Next

1. **FastAPI Official Tutorial**: [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)
2. **SQLAlchemy ORM Tutorial**: [https://docs.sqlalchemy.org/en/20/tutorial/](https://docs.sqlalchemy.org/en/20/tutorial/)
3. **Pydantic v2 Docs**: [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)
4. **JWT.io** (play with tokens): [https://jwt.io/](https://jwt.io/)
5. **Alembic Tutorial**: [https://alembic.sqlalchemy.org/en/latest/tutorial.html](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
