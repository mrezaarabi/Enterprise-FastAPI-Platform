# Enterprise-Level FastAPI Application

This is an enterprise-level RESTful API built with FastAPI, providing a robust foundation for building secure, maintainable, and scalable web applications.

## Features

- **Modern Python**: Using Python 3.11+ features  
- **FastAPI Framework**: High-performance, easy to learn, fast to code  
- **Comprehensive Authentication**: JWT token authentication with OAuth2  
- **Role-Based Access Control**: Fine-grained permissions  
- **SQLAlchemy ORM**: With PostgreSQL  
- **Alembic Migrations**: Database versioning  
- **Pydantic Models**: For data validation  
- **Docker Integration**: Docker and Docker Compose setup  
- **Comprehensive Logging**: Structured logging with JSON output  
- **Sentry Integration**: For error tracking  
- **Health Check Endpoint**: For monitoring  
- **Testing**: Pytest with fixtures  
- **Documentation**: Auto-generated via OpenAPI (Swagger)  
- **Code Formatting**: Black, isort, and flake8 configuration  
- **Type Checking**: With mypy  

## Project Structure

The project follows a **layered architecture**, ensuring separation of concerns and maintainability:

- **Controllers**: API endpoints (`app/api`)
- **Service Layer**: Business logic (`app/services`)
- **Repository Layer**: CRUD operations (`app/crud`)
- **Data Layer**: Models and schemas (`app/models`, `app/schemas`)

Each layer plays a distinct role, making the application modular and scalable.

### **Directory Overview**
- **app/api**: API endpoints  
- **app/core**: Core modules and configuration  
- **app/crud**: Database access operations  
- **app/db**: Database setup and session  
- **app/models**: Database models  
- **app/schemas**: Pydantic schemas  
- **app/services**: Business logic  
- **app/utils**: Utility functions  

## Getting Started

### Prerequisites

- Docker and Docker Compose  
- Python 3.11+  
- Poetry (for local development)  

---

## Running with Docker

1. **Copy `.env.example` to `.env` and adjust variables**:
   ```bash
   cp .env.example .env
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API** at [http://localhost:8000](http://localhost:8000).  
4. **API documentation** is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).


## **Database Migrations & Alembic Setup**

### **Initialize Alembic**
When setting up the database migrations for the first time, initialize Alembic:

```bash
docker-compose run --rm api alembic init alembic
```

### **Modify `alembic/env.py`**
After running the Alembic initialization command, Alembic generates a default `alembic/env.py` file, which **does not correctly load our FastAPI database settings**. To fix this, open `alembic/env.py` and **make the following changes**:

#### **1️⃣ Ensure the app's modules are accessible**  
Add the following at the top:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Move up one level
```

#### **2️⃣ Load the database URL dynamically**  
Find this line:

```python
url = config.get_main_option("sqlalchemy.url")
```

Replace it with:

```python
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
```

#### **3️⃣ Ensure Alembic detects our database models**  
Find this line:

```python
target_metadata = None
```

Replace it with:

```python
from app.db.base_class import Base
from app.core.config import settings
from app.models import user  # Import at least one model to trigger autogeneration

target_metadata = Base.metadata
```

### **Final `env.py` File After Modification**
After making the changes, your modified `alembic/env.py` should look like this:

```python
import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure the app modules can be found
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the project's database models and settings
from app.db.base_class import Base
from app.core.config import settings  # Load database URL from settings
from app.models import user  # Ensure the User model is imported

# This is the Alembic Config object, providing access to config values
config = context.config

# Set up logging from Alembic's config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load the correct database URL dynamically
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# Use SQLAlchemy metadata to detect model changes
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## **Applying Migrations**

After modifying `env.py`, you can now create and apply migrations:

1. **Stamp the current DB** (mark the database as up-to-date without running migrations):
   ```bash
   docker-compose run --rm api alembic stamp head
   ```

2. **Autogenerate a new migration** (based on model changes):
   ```bash
   docker-compose run --rm api alembic revision --autogenerate -m "Create users table"
   ```

3. **Apply migrations**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

## **Interacting with PostgreSQL**
To interact with the database inside the `db` container using `psql`:

```bash
docker-compose exec db psql -U postgres -d app
```
   - **List tables**: `\dt`
   - **Select all users**: `SELECT * FROM users;`

## **Using pgAdmin**
If you prefer a graphical interface for PostgreSQL, pgAdmin is included in the Docker Compose file.

1. Open [http://localhost:5050](http://localhost:5050) in your browser.

2. Log in using the credentials from your `.env` file (e.g., `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`).

3. Add a new server with the following details:

   - **Host**: `db`
   - **Port**: `5432`
   - **Database**: `app`
   - **Username**: `postgres`
   - **Password**: whatever you set in `.env` for `POSTGRES_PASSWORD`

Now you can view tables, run queries, and manage the database without the command line.

### **Creating a Superuser**
Some API endpoints require **superuser permissions** to be accessed.

By default, users are created with `is_superuser = False` for security reasons. To make a user a superuser, update their database record:

```sql
UPDATE users SET is_superuser = true WHERE email = 'your_email@example.com';
```

Once this is done, the user will have access to **admin-only endpoints**, such as:

```
GET /api/v1/users/
```

## **Run specific tests in Docker**:

```bash
# Authentication tests
docker-compose run --rm api pytest tests/test_api/test_auth.py -v

# User tests
docker-compose run --rm api pytest tests/test_api/test_users.py -v

# All tests with coverage
docker-compose run --rm api pytest --cov=app
```

## Common Commands & Troubleshooting

Below are commonly used Docker-based commands for managing migrations, databases, and troubleshooting issues:

1. **Drop the Alembic version table** (if you need to reset migrations):
   ```bash
   docker-compose exec db psql -U postgres -d app -c "DROP TABLE IF EXISTS alembic_version;"
   ```
   *Use with caution—this can break migration consistency if done unintentionally.*

### **Step-by-Step “Rebuild & Run” Flow**

A. **Shut down running containers**:
   ```bash
   docker-compose down
   ```
   Stops and removes all running containers, freeing up ports.

B. **Rebuild containers without cache** (useful if Docker build steps get stuck):
   ```bash
   docker-compose build --no-cache
   ```

C. **Start containers in detached mode**:
   ```bash
   docker-compose up -d
   ```
   Runs containers in the background.

D. **Check API container logs**:
   ```bash
   docker-compose logs -f api
   ```
   Streams real-time logs for the API service.

---

## Local Development

1. **Install dependencies** (using Poetry):
   ```bash
   poetry install
   ```
2. **Set up the database** (locally with Alembic):
   ```bash
   alembic upgrade head
   ```
3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

- **Create a new migration**:
  ```bash
  alembic revision --autogenerate -m "description"
  ```
- **Apply migrations**:
  ```bash
  alembic upgrade head
  ```

## Testing

- **Run tests**:
  ```bash
  pytest
  ```
- **With coverage**:
  ```bash
  pytest --cov=app
  ```

---

## API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Extending the API

You can extend this foundation by:

1. Adding more resource endpoints (products, orders, etc.)
2. Implementing caching with Redis (already configured)
3. Setting up CI/CD pipelines
4. Adding rate limiting
5. Implementing background tasks with Celery

The modular structure makes it easy to add new features while maintaining separation of concerns and testability.

## Contributing

1. Fork the repository  
2. Create a feature branch: `git checkout -b feature-name`  
3. Commit changes: `git commit -am 'Add feature'`  
4. Push to branch: `git push origin feature-name`  
5. Submit a pull request  

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
