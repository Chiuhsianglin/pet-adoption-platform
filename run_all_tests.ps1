#!/usr/bin/env pwsh
# 執行所有測試並生成報告
# Run all tests and generate reports

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$NoCoverage,
    [switch]$Parallel
)

$ErrorActionPreference = "Continue"
$totalFailures = 0

Write-Host "🧪 Pet Adoption Platform - Test Runner" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Backend Tests
if (-not $SkipBackend) {
    Write-Host "📦 Running Backend Tests..." -ForegroundColor Yellow
    Push-Location backend
    
    try {
        if ($NoCoverage) {
            if ($Parallel) {
                pytest -n auto -v
            } else {
                pytest -v
            }
        } else {
            if ($Parallel) {
                pytest -n auto --cov=app --cov-report=html --cov-report=term --cov-report=xml -v
            } else {
                pytest --cov=app --cov-report=html --cov-report=term --cov-report=xml -v
            }
        }
        
        if ($LASTEXITCODE -ne 0) {
            $totalFailures++
            Write-Host "❌ Backend tests failed!" -ForegroundColor Red
        } else {
            Write-Host "✅ Backend tests passed!" -ForegroundColor Green
        }
        
        if (-not $NoCoverage) {
            Write-Host "`n📊 Backend coverage report: backend/htmlcov/index.html" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "❌ Error running backend tests: $_" -ForegroundColor Red
        $totalFailures++
    } finally {
        Pop-Location
    }
    
    Write-Host "`n" -ForegroundColor Gray
}

# Frontend Tests
if (-not $SkipFrontend) {
    Write-Host "🎨 Running Frontend Tests..." -ForegroundColor Yellow
    Push-Location frontend
    
    try {
        if ($NoCoverage) {
            npm test -- --run
        } else {
            npm run test:coverage
        }
        
        if ($LASTEXITCODE -ne 0) {
            $totalFailures++
            Write-Host "❌ Frontend tests failed!" -ForegroundColor Red
        } else {
            Write-Host "✅ Frontend tests passed!" -ForegroundColor Green
        }
        
        if (-not $NoCoverage) {
            Write-Host "`n📊 Frontend coverage report: frontend/coverage/index.html" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "❌ Error running frontend tests: $_" -ForegroundColor Red
        $totalFailures++
    } finally {
        Pop-Location
    }
    
    Write-Host "`n" -ForegroundColor Gray
}

# Summary
Write-Host "======================================" -ForegroundColor Cyan
if ($totalFailures -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ $totalFailures test suite(s) failed" -ForegroundColor Red
    exit 1
}
