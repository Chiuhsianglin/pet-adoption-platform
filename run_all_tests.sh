#!/bin/bash
# 執行所有測試並生成報告
# Run all tests and generate reports

set -e

SKIP_BACKEND=false
SKIP_FRONTEND=false
NO_COVERAGE=false
PARALLEL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --no-coverage)
            NO_COVERAGE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-backend] [--skip-frontend] [--no-coverage] [--parallel]"
            exit 1
            ;;
    esac
done

total_failures=0

echo "🧪 Pet Adoption Platform - Test Runner"
echo "======================================"
echo ""

# Backend Tests
if [ "$SKIP_BACKEND" = false ]; then
    echo "📦 Running Backend Tests..."
    cd backend
    
    if [ "$NO_COVERAGE" = true ]; then
        if [ "$PARALLEL" = true ]; then
            pytest -n auto -v || total_failures=$((total_failures + 1))
        else
            pytest -v || total_failures=$((total_failures + 1))
        fi
    else
        if [ "$PARALLEL" = true ]; then
            pytest -n auto --cov=app --cov-report=html --cov-report=term --cov-report=xml -v || total_failures=$((total_failures + 1))
        else
            pytest --cov=app --cov-report=html --cov-report=term --cov-report=xml -v || total_failures=$((total_failures + 1))
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Backend tests passed!"
    else
        echo "❌ Backend tests failed!"
    fi
    
    if [ "$NO_COVERAGE" = false ]; then
        echo ""
        echo "📊 Backend coverage report: backend/htmlcov/index.html"
    fi
    
    cd ..
    echo ""
fi

# Frontend Tests
if [ "$SKIP_FRONTEND" = false ]; then
    echo "🎨 Running Frontend Tests..."
    cd frontend
    
    if [ "$NO_COVERAGE" = true ]; then
        npm test -- --run || total_failures=$((total_failures + 1))
    else
        npm run test:coverage || total_failures=$((total_failures + 1))
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Frontend tests passed!"
    else
        echo "❌ Frontend tests failed!"
    fi
    
    if [ "$NO_COVERAGE" = false ]; then
        echo ""
        echo "📊 Frontend coverage report: frontend/coverage/index.html"
    fi
    
    cd ..
    echo ""
fi

# Summary
echo "======================================"
if [ $total_failures -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ $total_failures test suite(s) failed"
    exit 1
fi
