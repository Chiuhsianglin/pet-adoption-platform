# GitHub Actions CI/CD Workflows

This directory contains the automated CI/CD workflows for the Pet Adoption Platform.

## 📋 Workflows Overview

### 1. Backend Tests (`backend-tests.yml`)
**Triggers**: Push/PR to `main` or `develop` branches (when backend files change)

**What it does**:
- Runs on Python 3.11 and 3.12 (matrix testing)
- Sets up MySQL 8.0 and Redis 7 services
- Executes all backend tests:
  - Unit tests (337 tests)
  - Integration tests (139 tests)
  - E2E tests (88 tests)
- Generates coverage reports
- Uploads coverage to Codecov

**Services**:
- MySQL 8.0 (port 3306)
- Redis 7-alpine (port 6379)

---

### 2. Frontend Tests (`frontend-tests.yml`)
**Triggers**: Push/PR to `main` or `develop` branches (when frontend files change)

**What it does**:
- Runs on Node.js 18.x and 20.x (matrix testing)
- Installs npm dependencies
- Executes frontend tests (23 tests)
- Runs tests with coverage
- Builds the frontend application
- Uploads build artifacts

---

### 3. Integration Tests (`integration-tests.yml`)
**Triggers**: 
- Push to `main` branch
- Pull requests to `main`
- Daily at 2 AM UTC (scheduled)
- Manual trigger (workflow_dispatch)

**What it does**:
- Full stack integration testing
- Runs backend E2E tests with real MySQL and Redis
- Health checks for all services
- Generates comprehensive test reports
- Uploads artifacts with 30-day retention

---

### 4. Code Quality (`code-quality.yml`)
**Triggers**: Push/PR to `main` or `develop` branches

**What it does**:

**Backend Quality Checks**:
- Black (code formatting)
- isort (import sorting)
- Flake8 (linting)
- MyPy (type checking)

**Frontend Quality Checks**:
- ESLint (linting)
- Prettier (formatting)
- Vue-tsc (TypeScript type checking)

All checks use `continue-on-error: true` for informational purposes.

---

### 5. PR Checks (`pr-checks.yml`)
**Triggers**: Pull requests to `main` or `develop` branches

**What it does**:
- Detects changed files (backend/frontend)
- Runs only relevant tests based on changes
- Provides intelligent test execution
- Posts automated comment on PR with results
- Shows ✅ for passed tests, ❌ for failures, ⏭️ for skipped

---

## 📊 Test Coverage

| Test Type | Count | Coverage |
|-----------|-------|----------|
| Backend Unit | 337 | ~85% |
| Backend Integration | 139 | ~80% |
| Backend E2E | 88 | ~75% |
| Frontend Unit | 23 | ~74% |
| **Total** | **587** | **~80%** |

---

## 🔐 Required Secrets

Configure these secrets in GitHub Repository Settings → Secrets and variables → Actions:

### Required
- `JWT_SECRET_KEY`: Secret key for JWT token generation
  ```bash
  # Generate with Python
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- `DATABASE_URL`: Database connection string (used in workflows)
  ```
  mysql+aiomysql://root:root@127.0.0.1:3306/pet_adoption_test
  ```

### Optional
- `CODECOV_TOKEN`: Token for uploading coverage to Codecov (required for private repositories)

---

## 🚀 Local Testing

You can run the same tests locally before pushing:

### Backend Tests
```bash
cd backend

# Run all tests
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test types
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with parallel execution
pytest -n auto --cov=app
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Full Test Suite
```powershell
# Windows
.\run_all_tests.ps1

# With options
.\run_all_tests.ps1 -Parallel -NoCoverage
```

```bash
# Linux/Mac
./run_all_tests.sh

# With options
./run_all_tests.sh --parallel --no-coverage
```

---

## 🔧 Troubleshooting

### MySQL Connection Timeout
If MySQL health checks fail:
- Increase health check retries in workflow
- Check MySQL service configuration
- Verify DATABASE_URL format

### Node Version Issues
If tests fail on specific Node version:
- Check package-lock.json compatibility
- Update dependencies: `npm ci` vs `npm install`
- Verify node version in matrix matches local development

### Coverage Upload Fails
If Codecov upload fails:
- Set `fail_ci_if_error: false` to prevent CI failure
- Check CODECOV_TOKEN secret configuration
- Verify repository is added to Codecov

### Workflow Not Triggering
If workflows don't run:
- Check path filters match changed files
- Verify branch names in workflow triggers
- Ensure workflows are in `.github/workflows/` directory

---

## 📈 Status Badges

Add these badges to your README.md:

```markdown
![Backend Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Frontend%20Tests/badge.svg)
![Integration Tests](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Integration%20Tests/badge.svg)
![Code Quality](https://github.com/Chiuhsianglin/pet-adoption-platform/workflows/Code%20Quality/badge.svg)
[![codecov](https://codecov.io/gh/Chiuhsianglin/pet-adoption-platform/branch/main/graph/badge.svg)](https://codecov.io/gh/Chiuhsianglin/pet-adoption-platform)
```

---

## 🎯 Best Practices

1. **Always run tests locally before pushing**
2. **Keep workflows fast**: Use caching, parallel execution
3. **Use path filters**: Don't run unnecessary tests
4. **Monitor workflow execution time**: Optimize slow tests
5. **Review failed workflows promptly**: Fix issues quickly
6. **Keep dependencies updated**: Regular maintenance
7. **Use matrix testing**: Ensure compatibility across versions

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Codecov Documentation](https://docs.codecov.com/)
