# 💰 Expense Tracker API

A **production-grade Personal Finance & Expense Tracker** backend API built with FastAPI. Track your daily expenses, organize them into categories, and manage your financial data securely.

This project follows **industry-standard backend architecture** — the kind a backend engineer with 5-6 years of experience would set up — with clean separation of concerns, proper authentication, and a structure that scales.

---

## ✨ Features (Current)

| Feature                       | Description                                               |
| ----------------------------- | --------------------------------------------------------- |
| 🔐 **JWT Authentication**     | Signup, login, logout with access + refresh token flow    |
| 🔒 **Password Security**      | Passwords hashed with bcrypt — never stored in plain text |
| 💸 **Expense CRUD**           | Create, read, update, delete expenses                     |
| 🏷️ **Category Management**    | Organize expenses into custom categories                  |
| 👤 **Ownership Enforcement**  | Users can ONLY see/edit their own data                    |
| 📄 **Pagination & Filtering** | Filter expenses by date range and category                |
| ⚠️ **Error Handling**         | Consistent error response format across all endpoints     |
| ⚙️ **Environment Config**     | Secrets and settings managed via `.env` file              |
| 🐘 **Dual DB Support**        | Works with PostgreSQL (production) and SQLite (local dev) |

## 🚀 Future Plans

- [ ] 🐳 **Docker** — Containerize the app with Docker & Docker Compose
- [ ] ☸️ **Kubernetes** — Deploy to a K8s cluster with Helm charts
- [ ] 🤖 **AI Expense Categorization** — Auto-categorize expenses using ML/LLMs
- [ ] 📊 **Spending Insights** — AI-powered monthly spending analysis and budgeting tips
- [ ] 📧 **Email Notifications** — Weekly spending summaries and budget alerts
- [ ] 📈 **Analytics Dashboard** — Spending trends, charts, and breakdowns
- [ ] 🔄 **CI/CD Pipeline** — Automated testing and deployment with GitHub Actions
- [ ] 📱 **React Frontend** — Full-featured web UI to complement the API
- [ ] 💱 **Multi-currency Support** — Track expenses in different currencies
- [ ] 📤 **CSV/PDF Export** — Export expense reports

---

## 🛠️ Tech Stack

| Technology                                                                        | Purpose           | Why This?                                 |
| --------------------------------------------------------------------------------- | ----------------- | ----------------------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/)                                          | Web framework     | Async, auto-docs, type-safe, blazing fast |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/)                                     | ORM               | Industry standard, supports multiple DBs  |
| [Alembic](https://alembic.sqlalchemy.org/)                                        | DB migrations     | Safe, versioned schema changes            |
| [Pydantic v2](https://docs.pydantic.dev/)                                         | Data validation   | Auto-validates request/response data      |
| [PostgreSQL](https://www.postgresql.org/)                                         | Primary database  | Battle-tested, scalable relational DB     |
| [SQLite](https://www.sqlite.org/)                                                 | Dev database      | Zero setup, works out of the box          |
| [bcrypt](https://github.com/pyca/bcrypt/)                                         | Password hashing  | Secure, slow-by-design hashing            |
| [python-jose](https://github.com/mpdavis/python-jose)                             | JWT tokens        | Create and verify JSON Web Tokens         |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Config management | Type-safe env var loading                 |
| [Uvicorn](https://www.uvicorn.org/)                                               | ASGI server       | Lightning-fast async server               |

---

## 📁 Project Structure

```
expense-calculator/
│
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # 🚀 App entry point — creates FastAPI app, includes routers
│   │
│   ├── core/                   # ⚙️ Core utilities (used across the entire app)
│   │   ├── config.py           #    App settings loaded from .env (DB URL, JWT secret, etc.)
│   │   ├── security.py         #    Password hashing & JWT token creation/verification
│   │   └── exceptions.py       #    Custom exception classes & error response format
│   │
│   ├── db/                     # 🗄️ Database configuration
│   │   ├── base.py             #    SQLAlchemy Base class (all models inherit from this)
│   │   └── session.py          #    DB engine, session factory, and get_db() dependency
│   │
│   ├── models/                 # 📦 SQLAlchemy models (database table definitions)
│   │   ├── user.py             #    User table (email, hashed_password, etc.)
│   │   ├── category.py         #    Category table (name, description, owner)
│   │   └── expense.py          #    Expense table (amount, date, category, owner)
│   │
│   ├── schemas/                # 📋 Pydantic schemas (request/response data shapes)
│   │   ├── user.py             #    UserCreate, UserLogin, UserResponse
│   │   ├── token.py            #    TokenResponse, TokenRefreshRequest
│   │   ├── category.py         #    CategoryCreate, CategoryUpdate, CategoryResponse
│   │   └── expense.py          #    ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   │
│   ├── routers/                # 🛣️ API route handlers (HTTP layer)
│   │   ├── auth.py             #    /auth/register, /auth/login, /auth/refresh, etc.
│   │   ├── categories.py       #    /categories/ CRUD endpoints
│   │   └── expenses.py         #    /expenses/ CRUD endpoints with filters
│   │
│   ├── services/               # 🧠 Business logic (the "brains" of the app)
│   │   ├── auth.py             #    Registration, authentication, token creation logic
│   │   ├── category.py         #    Category CRUD logic with ownership checks
│   │   └── expense.py          #    Expense CRUD logic with pagination & filtering
│   │
│   └── dependencies/           # 🔌 FastAPI dependencies (reusable injected functions)
│       └── auth.py             #    get_current_user — extracts & validates JWT from header
│
├── alembic/                    # 🔄 Database migration files
│   ├── env.py                  #    Migration environment config
│   ├── script.py.mako          #    Template for new migration files
│   └── versions/               #    Individual migration scripts (auto-generated)
│
├── docs/                       # 📚 Documentation
│   └── CONCEPTS.md             #    Beginner-friendly explanation of core concepts
│
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables (copy to .env)
├── .gitignore                  # Files to exclude from git
└── README.md                   # You are here!
```

### Why This Structure?

| Folder          | Responsibility                     | Why Separate?                                                                           |
| --------------- | ---------------------------------- | --------------------------------------------------------------------------------------- |
| `core/`         | Config, security, exceptions       | Shared utilities — used by everything else                                              |
| `db/`           | Database connection & base class   | Isolates DB setup from business logic                                                   |
| `models/`       | Database table definitions         | Maps Python classes to DB tables (SQLAlchemy)                                           |
| `schemas/`      | API data shapes (request/response) | Validates & filters data (Pydantic) — separate from DB models to control what's exposed |
| `routers/`      | HTTP endpoint definitions          | Handles HTTP concerns (status codes, headers) — delegates logic to services             |
| `services/`     | Business logic                     | The actual "work" — reusable, testable, doesn't know about HTTP                         |
| `dependencies/` | Reusable injected functions        | Auth checks, DB sessions — injected into endpoints via `Depends()`                      |

> **The key principle:** Each layer only knows about the layer below it.
> `Router → Service → Database`. Routers don't touch the database directly. Services don't know about HTTP status codes.

---

## 🏁 Getting Started (Step by Step)

### Prerequisites

- **Python 3.11+** installed ([download here](https://www.python.org/downloads/))
- **Git** installed
- **PostgreSQL** (optional — SQLite works for local development with zero setup)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/expense-calculator.git
cd expense-calculator
```

### 2. Create a Virtual Environment

A virtual environment keeps this project's packages isolated from your global Python installation.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On macOS/Linux:
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of your terminal prompt — that means it's active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example .env file
cp .env.example .env    # On macOS/Linux
copy .env.example .env  # On Windows
```

Open `.env` and update the values:

- **`JWT_SECRET_KEY`**: Generate a random secret:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **`DATABASE_URL`**: Leave as SQLite for local dev, or set your PostgreSQL URL

### 5. Run Database Migrations

```bash
# Generate the initial migration (reads your models and creates the migration script)
alembic revision --autogenerate -m "Initial tables: users, categories, expenses"

# Apply the migration (actually creates the tables in the database)
alembic upgrade head
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
.\expensesvenv\Scripts\python.exe -m uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 7. Explore the API

Open your browser:

- 📖 **Interactive Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 **Alternative Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- ❤️ **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint                | Description                         | Auth Required |
| ------ | ----------------------- | ----------------------------------- | :-----------: |
| `POST` | `/api/v1/auth/register` | Create a new user account           |      ❌       |
| `POST` | `/api/v1/auth/login`    | Login and get JWT tokens            |      ❌       |
| `POST` | `/api/v1/auth/refresh`  | Refresh access token                |      ❌       |
| `POST` | `/api/v1/auth/logout`   | Logout (discard tokens client-side) |      ✅       |
| `GET`  | `/api/v1/auth/me`       | Get current user profile            |      ✅       |

### Expenses

| Method   | Endpoint                | Description                          | Auth Required |
| -------- | ----------------------- | ------------------------------------ | :-----------: |
| `POST`   | `/api/v1/expenses/`     | Create a new expense                 |      ✅       |
| `GET`    | `/api/v1/expenses/`     | List expenses (paginated + filtered) |      ✅       |
| `GET`    | `/api/v1/expenses/{id}` | Get a single expense                 |      ✅       |
| `PUT`    | `/api/v1/expenses/{id}` | Update an expense                    |      ✅       |
| `DELETE` | `/api/v1/expenses/{id}` | Delete an expense                    |      ✅       |

**Query Parameters for `GET /expenses/`:**

| Parameter     | Type | Default | Description                             |
| ------------- | ---- | ------- | --------------------------------------- |
| `page`        | int  | 1       | Page number                             |
| `per_page`    | int  | 20      | Items per page (max 100)                |
| `date_from`   | date | —       | Filter: expenses on or after this date  |
| `date_to`     | date | —       | Filter: expenses on or before this date |
| `category_id` | int  | —       | Filter: expenses in this category       |

### Categories

| Method   | Endpoint                  | Description              | Auth Required |
| -------- | ------------------------- | ------------------------ | :-----------: |
| `POST`   | `/api/v1/categories/`     | Create a new category    |      ✅       |
| `GET`    | `/api/v1/categories/`     | List all your categories |      ✅       |
| `GET`    | `/api/v1/categories/{id}` | Get a single category    |      ✅       |
| `PUT`    | `/api/v1/categories/{id}` | Update a category        |      ✅       |
| `DELETE` | `/api/v1/categories/{id}` | Delete a category        |      ✅       |

### Health

| Method | Endpoint  | Description           | Auth Required |
| ------ | --------- | --------------------- | :-----------: |
| `GET`  | `/`       | Root health check     |      ❌       |
| `GET`  | `/health` | Detailed health check |      ❌       |

---

## 🧪 Quick Test with cURL

### Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "MySecureP@ss123", "full_name": "Test User"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=MySecureP@ss123"
```

### Create an expense (use the access_token from login response)

```bash
curl -X POST http://localhost:8000/api/v1/expenses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 25.50, "description": "Lunch at Subway", "date": "2025-07-23"}'
```

---

## 📚 Learn More

- **[docs/CONCEPTS.md](docs/CONCEPTS.md)** — Beginner-friendly explanations of Pydantic, JWT, Depends, Alembic, and more
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** — Official FastAPI docs
- **[SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)** — Official SQLAlchemy tutorial

---

## 📄 License

This project is for learning purposes. Feel free to use it however you like.
