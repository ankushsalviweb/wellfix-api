# WellFix - Laptop Repair Service Platform

A comprehensive FastAPI-based backend service for managing laptop repair operations, including customer requests, engineer assignments, and admin workflows.

## Features

- **User Management**
  - Role-based access (Customer, Engineer, Admin)
  - Secure authentication with JWT
  - Profile and address management

- **Job Management**
  - Complete repair job lifecycle
  - Status tracking and updates
  - On-site and lab repair workflows
  - Quote management and approvals

- **Service Area Management**
  - Pincode-based service area definition
  - Automated serviceability checks

- **Admin Features**
  - Engineer assignment
  - Service area management
  - Pricing configuration
  - Performance reporting

- **Rating System**
  - Customer feedback
  - Engineer performance tracking

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based token authentication
- **Testing**: pytest
- **Load Testing**: Locust
- **Documentation**: OpenAPI/Swagger

## Project Structure

```
wellfix_api/
├── api/            # API endpoints and routers
├── core/           # Core functionality (config, db, security)
├── crud/           # Database CRUD operations
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
└── services/       # Business logic services

tests/              # Test suites
docs/               # Documentation
alembic/            # Database migrations
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ankushsalviweb/wellfix-api.git
   cd wellfix-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn wellfix_api.main:app --reload
   ```

## Testing

Run the test suite:
```bash
python -m pytest
```

Run with coverage:
```bash
python run_coverage.py
```

## API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 