# CI/CD 部署指南
# CI/CD Deployment Guide

## 📋 部署檢查清單 / Deployment Checklist

### 1️⃣ 提交 CI/CD 配置文件
Commit CI/CD configuration files

```powershell
# 檢查狀態
git status

# 添加所有 workflow 文件
git add .github/workflows/*.yml
git add .github/workflows/README.md

# 添加測試腳本和更新的 README
git add run_all_tests.ps1 run_all_tests.sh
git add README.md

# 提交
git commit -m "feat: Add comprehensive CI/CD workflows with automated testing

- Add backend testing workflow (564 tests, Python 3.11/3.12)
- Add frontend testing workflow (23 tests, Node 18.x/20.x)
- Add integration testing workflow (daily E2E tests)
- Add code quality checks (linting, formatting, type checking)
- Add PR automation with intelligent filtering
- Add test runner scripts for local testing
- Update README with badges and testing documentation
- Total: 587 automated tests with ~80% coverage"

# 推送到 GitHub
git push origin main
```

### 2️⃣ 配置 GitHub Repository Secrets
Configure GitHub Repository Secrets

前往 GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

#### 必需的 Secrets (Required)

1. **DATABASE_URL**
   ```
   Name: DATABASE_URL
   Value: mysql+aiomysql://user:password@localhost:3306/pet_adoption_test
   ```

2. **JWT_SECRET_KEY**
   ```powershell
   # 生成安全的密鑰 / Generate secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # 將輸出複製到 GitHub Secret
   Name: JWT_SECRET_KEY
   Value: <your-generated-secret-key>
   ```

#### 可選的 Secrets (Optional)

3. **CODECOV_TOKEN** (用於私有倉庫 / For private repositories)
   ```
   - 前往 https://codecov.io
   - 登錄並連接 GitHub
   - 添加你的倉庫
   - 複製 Upload Token
   
   Name: CODECOV_TOKEN
   Value: <your-codecov-token>
   ```

### 3️⃣ 更新 README Badges
Update README Badges

在 `README.md` 中替換 `YOUR_USERNAME` 為你的 GitHub 用戶名：

```markdown
![Backend Tests](https://github.com/YOUR_USERNAME/pet-adoption-platform/workflows/Backend%20Tests/badge.svg)
```

替換為：

```markdown
![Backend Tests](https://github.com/your-actual-username/pet-adoption-platform/workflows/Backend%20Tests/badge.svg)
```

### 4️⃣ 驗證 Workflows
Verify Workflows

1. **檢查 Actions 標籤**
   - 前往 GitHub Repository → Actions
   - 確認所有 5 個 workflows 都出現在列表中：
     - ✅ Backend Tests
     - ✅ Frontend Tests
     - ✅ Integration Tests
     - ✅ Code Quality
     - ✅ PR Checks

2. **觸發第一次運行**
   ```powershell
   # 創建測試分支
   git checkout -b test/ci-cd-verification
   
   # 進行微小更改
   echo "# CI/CD Test" >> .github/workflows/README.md
   
   # 提交並推送
   git add .github/workflows/README.md
   git commit -m "test: Verify CI/CD workflows"
   git push origin test/ci-cd-verification
   
   # 創建 Pull Request
   # 前往 GitHub 網頁創建 PR
   ```

3. **監控執行結果**
   - 檢查 Actions 標籤中的運行狀態
   - 確認所有測試通過
   - 查看 PR 上的自動評論

### 5️⃣ 驗證 Coverage Reports
Verify Coverage Reports

1. **Codecov 集成**
   - 前往 https://codecov.io/gh/YOUR_USERNAME/pet-adoption-platform
   - 檢查覆蓋率報告是否上傳
   - 確認 badge 顯示正確的覆蓋率百分比

2. **Artifacts 下載**
   - 在 Actions → Workflow Run → Artifacts
   - 下載 coverage reports 和 test reports
   - 在本地瀏覽器中打開 HTML 報告

## 🔧 故障排除 / Troubleshooting

### Workflow 未觸發
Workflow Not Triggered

**問題**: 推送代碼後沒有 workflow 運行

**解決方案**:
```powershell
# 檢查路徑過濾器
# 確保你修改的文件匹配 workflow 的 paths 條件

# 手動觸發 workflow
# 前往 Actions → 選擇 workflow → Run workflow
```

### MySQL 連接失敗
MySQL Connection Failed

**問題**: Tests fail with "Can't connect to MySQL server"

**解決方案**:
1. 確認 `DATABASE_URL` secret 格式正確
2. 檢查 workflow 中的 MySQL service 配置
3. 增加 health check 超時時間（已在配置中設置）

### Coverage 上傳失敗
Coverage Upload Failed

**問題**: Codecov upload returns error

**解決方案**:
```yaml
# 在 workflow 中添加 fail_ci_if_error: false
- uses: codecov/codecov-action@v4
  with:
    fail_ci_if_error: false  # 不因上傳失敗而中斷 CI
```

### Node/Python 版本問題
Node/Python Version Issues

**問題**: Tests fail on specific version in matrix

**解決方案**:
```yaml
# 調整 matrix 配置，移除有問題的版本
strategy:
  matrix:
    python-version: ["3.11"]  # 暫時移除 3.12
```

## 📊 監控和維護 / Monitoring and Maintenance

### 每日檢查
Daily Checks

1. 檢查 GitHub Actions 標籤的 workflow 狀態
2. 查看 Codecov 覆蓋率趨勢
3. 審查失敗的測試並修復

### 每週維護
Weekly Maintenance

1. 更新依賴版本
2. 審查 workflow 執行時間，優化慢速測試
3. 檢查 artifact 存儲使用情況

### 優化建議
Optimization Tips

```yaml
# 使用緩存加速安裝
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# 並行運行測試
pytest -n auto

# 使用 fail-fast 策略快速失敗
strategy:
  fail-fast: true
```

## 🎯 下一步 / Next Steps

- [ ] 設置 GitHub 通知（失敗時發送郵件）
- [ ] 配置 Slack/Discord 集成
- [ ] 添加部署 workflows（staging, production）
- [ ] 設置性能測試 workflow
- [ ] 添加安全掃描（OWASP Dependency Check）
- [ ] 配置自動版本號和 changelog 生成

## 📚 相關文檔 / Related Documentation

- [GitHub Actions 文檔](https://docs.github.com/en/actions)
- [Codecov 文檔](https://docs.codecov.com/)
- [Pytest 文檔](https://docs.pytest.org/)
- [Vitest 文檔](https://vitest.dev/)
- [項目 CI/CD 詳細說明](.github/workflows/README.md)
