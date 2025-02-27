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

The project follows a modular architecture:

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

### Running with Docker

1. Copy `.env.example` to `.env` and adjust variables:
   ```bash
   cp .env.example .env
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. API will be available at http://localhost:8000
4. API documentation at http://localhost:8000/docs

### Local Development

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up the database:
   ```bash
   alembic upgrade head
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.