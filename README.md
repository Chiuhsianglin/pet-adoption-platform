# 🐾 Pet Adoption Platform

![Backend Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Frontend%20Tests/badge.svg)
![Integration Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Integration%20Tests/badge.svg)
![Code Quality](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Code%20Quality/badge.svg)
[![codecov](https://codecov.io/gh/Chiuhsianglin/pet-adoption-platform/branch/main/graph/badge.svg)](https://codecov.io/gh/Chiuhsianglin/pet-adoption-platform)

A comprehensive pet adoption management system built with Vue.js frontend and FastAPI backend, designed to streamline the pet adoption process and connect loving homes with pets in need.

## 📋 Project Overview

The Pet Adoption Platform is a full-stack web application that facilitates pet adoption by providing:

- **Pet Management**: Shelters can post and manage pet profiles
- **Adoption Applications**: Streamlined application process for potential adopters
- **Real-time Communication**: Chat system for adopters and shelters
- **User Management**: Secure authentication and user profiles
- **File Upload**: Photo and document management system

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- Vue.js 3 with Composition API
- TypeScript for type safety
- Vuetify for UI components
- Pinia for state management
- Vite for fast development and building

**Backend:**
- FastAPI (Python) for high-performance API
- SQLAlchemy ORM with MySQL database
- Redis for caching and real-time features
- JWT authentication
- WebSocket for real-time communication

**Infrastructure:**
- Docker for containerization
- Docker Compose for local development
- GitHub Actions for CI/CD
- AWS S3 for file storage

### Project Structure

```
pet-adoption-platform/
├── frontend/                 # Vue.js frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── backend/                  # FastAPI backend application
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── main.py
│   └── Dockerfile
├── docs/                     # Project documentation
├── docker-compose.yml        # Development environment
├── .github/workflows/        # CI/CD configurations
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **MySQL** 8.0+ (or use Docker)
- **Redis** (or use Docker)

### Option 1: Docker Development (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pet-adoption-platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database Admin: http://localhost:8080 (phpMyAdmin)

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   # Create database
   mysql -u root -p -e "CREATE DATABASE pet_adoption;"
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## 🧪 Testing

### Backend Testing

```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend Testing

```bash
cd frontend
npm run test
npm run test:coverage
```

### Run All Tests

```bash
# Using Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🔧 Development Tools

### Code Quality

**Frontend:**
```bash
npm run lint        # ESLint checking
npm run format      # Prettier formatting
npm run type-check  # TypeScript checking
```

**Backend:**
```bash
black .            # Code formatting
isort .            # Import sorting
flake8 .           # Linting
mypy app/          # Type checking
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing

### Test Coverage

- **Backend Tests**: 564 tests (Unit: 337, Integration: 139, E2E: 88)
- **Frontend Tests**: 23 tests
- **Overall Coverage**: ~80%

### Running Tests Locally

#### Backend Tests

```bash
cd backend

# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test types
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/e2e/                     # E2E tests only

# Run tests in parallel
pytest -n auto --cov=app

# Generate detailed coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

#### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui
```

### CI/CD Automation

All tests are automatically run on:
- Every push to `main` branch
- All pull requests
- Daily integration tests at 2 AM UTC

See [`.github/workflows/README.md`](.github/workflows/README.md) for detailed CI/CD documentation.

## 📊 Database Schema

### Core Tables

- **users**: User accounts and profiles
- **pets**: Pet information and status
- **adoption_applications**: Adoption requests and status
- **chat_rooms**: Communication channels
- **messages**: Chat messages
- **notifications**: User notifications
- **pet_photos**: Pet image management

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable rounds
- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Pydantic models for API validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **File Upload Security**: Type and size validation
- **Rate Limiting**: API request throttling

## 🌐 API Documentation

When running the backend server, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

```
Authentication:
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh

Pets:
GET    /api/v1/pets
POST   /api/v1/pets
GET    /api/v1/pets/{pet_id}
PUT    /api/v1/pets/{pet_id}

Adoptions:
POST   /api/v1/adoptions
GET    /api/v1/adoptions/{app_id}
PUT    /api/v1/adoptions/{app_id}/review

Chat:
GET    /api/v1/chat/rooms
POST   /api/v1/chat/rooms
WebSocket: /ws/chat/{room_id}
```

## 🚀 Deployment

### Production Environment Variables

Key environment variables for production:

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=mysql+aiomysql://user:pass@host:port/db
JWT_SECRET_KEY=very-secure-production-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Monitoring and Logging

### Health Checks

- **API Health**: GET /health
- **Database Connection**: Included in health check
- **Redis Connection**: Included in health check

### Logging

Structured logging with configurable levels:
- **Development**: Console output with DEBUG level
- **Production**: JSON format with INFO level
- **Log Files**: Rotating file handler with size limits

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make changes and test**
4. **Run quality checks**
   ```bash
   pre-commit run --all-files
   ```
5. **Commit and push**
   ```bash
   git commit -m 'Add amazing feature'
   git push origin feature/amazing-feature
   ```
6. **Create Pull Request**

### Code Standards

- **Frontend**: ESLint + Prettier + TypeScript
- **Backend**: Black + isort + flake8 + mypy
- **Commit Messages**: Conventional Commits format
- **Testing**: Minimum 80% code coverage

## 📝 Documentation

- **Project Requirements**: `/docs/prd.md`
- **UI/UX Specifications**: `/docs/front-end-spec.md`
- **Architecture Design**: `/docs/architecture.md`
- **Epic & Story Documentation**: `/docs/epics/` and `/docs/stories/`

## 🆘 Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check MySQL service
docker-compose ps mysql

# Check database logs
docker-compose logs mysql
```

**Frontend Build Issues:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Backend Import Issues:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PWD/backend
```

### Getting Help

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `/docs` directory
- **API Docs**: http://localhost:8000/docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Product Manager**: Product strategy and requirements
- **UX Designer**: User experience and interface design
- **Backend Developer**: API and database development
- **Frontend Developer**: User interface implementation
- **DevOps Engineer**: Infrastructure and deployment

---

## 🎯 Project Status

This project is currently in development. See the [project board](https://github.com/yourorg/pet-adoption-platform/projects) for current progress and upcoming features.

### Completed Features ✅
- [x] Project setup and configuration
- [x] Database schema design
- [x] Authentication system
- [x] Docker containerization
- [x] CI/CD pipeline

### In Progress 🚧
- [ ] Pet management system
- [ ] Adoption application workflow
- [ ] Real-time chat implementation
- [ ] File upload system

### Planned Features 📋
- [ ] Email notifications
- [ ] Advanced search and filtering
- [ ] Mobile app development
- [ ] Admin dashboard
- [ ] Analytics and reporting

---

**Happy coding! 🐾**#   C I / C D   T e s t  
 