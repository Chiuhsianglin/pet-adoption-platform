# GitHub 推送指南

## 📋 前置準備（已完成）

✅ `.env` 文件已在 `.gitignore` 中
✅ 敏感資訊不會被推送
✅ 專案結構完整

---

## 🚀 推送步驟

### 方法 1：使用新的 GitHub 帳號

#### Step 1: 創建新的 GitHub 帳號
1. 前往 https://github.com/signup
2. 註冊新帳號

#### Step 2: 創建新的 Repository
1. 登入新的 GitHub 帳號
2. 點擊右上角 "+" → "New repository"
3. 填寫：
   - **Repository name**: `pet-adoption-platform`
   - **Description**: 寵物領養平台 - 提供寵物瀏覽、收藏、領養申請、社群互動等功能
   - **Visibility**: Public 或 Private（看你的需求）
   - ⚠️ **不要**勾選 "Initialize this repository with a README"
4. 點擊 "Create repository"
5. **記下你的 repository URL**（例如：`https://github.com/你的用戶名/pet-adoption-platform.git`）

#### Step 3: 在本地執行推送命令

打開 PowerShell，複製以下命令（**記得替換成你的實際資訊**）：

```powershell
# 1. 進入專案目錄
cd C:\project_bmad\pet-adoption-platform

# 2. 設定此專案的 Git 用戶資訊（僅針對此專案）
git config user.name "你的新GitHub用戶名"
git config user.email "你的新GitHub註冊email"

# 3. 檢查是否已經初始化 Git（如果顯示錯誤就執行下一步）
git status

# 4. 如果還沒初始化，執行：
git init

# 5. 添加所有文件
git add .

# 6. 查看將要提交的文件（確認沒有 .env）
git status

# 7. 創建第一次提交
git commit -m "Initial commit: Pet Adoption Platform

Features:
- Pet browsing and search with filters
- User authentication (shelter/adopter)
- Adoption application system
- Community posts, comments, and likes
- Real-time chat with WebSocket
- Notification system
- Favorite pets
- Photo upload with AWS S3 + CloudFront CDN
- RESTful API with FastAPI (V2)
- Vue 3 + Vuetify frontend
- MySQL database
"

# 8. 連接到你的 GitHub repository（替換成你的 URL）
git remote add origin https://github.com/你的用戶名/pet-adoption-platform.git

# 9. 推送到 GitHub
git branch -M main
git push -u origin main
```

#### Step 4: 輸入認證資訊
- GitHub 會要求你輸入用戶名和密碼
- **注意**：密碼需要使用 **Personal Access Token**（不是你的 GitHub 登入密碼）

---

### 如何取得 Personal Access Token

1. 登入 GitHub
2. 點擊右上角頭像 → **Settings**
3. 左側選單最底部 → **Developer settings**
4. 點擊 **Personal access tokens** → **Tokens (classic)**
5. 點擊 **Generate new token** → **Generate new token (classic)**
6. 填寫：
   - **Note**: `pet-adoption-platform`
   - **Expiration**: 選擇有效期限
   - **Select scopes**: 勾選 `repo`（完整存取權限）
7. 點擊 **Generate token**
8. **立即複製 token**（只會顯示一次！）
9. 在推送時，密碼處貼上這個 token

---

## 🔐 推送後的環境變數設定

推送到 GitHub 後，其他人（或你在其他電腦）需要創建自己的 `.env` 文件：

### Backend `.env` 範本
創建 `backend/.env` 文件並填入：

```env
# Application Settings
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=你的秘密金鑰（請更換）
APP_NAME=Pet Adoption Platform API
APP_VERSION=1.0.0

# Database Settings
DATABASE_URL=mysql+aiomysql://用戶名:密碼@localhost:3306/pet_adoption

# JWT Settings
JWT_SECRET_KEY=你的JWT秘密金鑰（請更換）
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Settings
PASSWORD_BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# AWS S3 Settings
USE_S3=true
AWS_ACCESS_KEY_ID=你的AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=你的AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET=你的S3_BUCKET名稱
AWS_REGION=ap-southeast-2
AWS_CLOUDFRONT_DOMAIN=https://你的CloudFront域名.cloudfront.net
BACKEND_URL=http://localhost:8000
```

### Frontend `.env` 範本
創建 `frontend/.env` 文件並填入：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

---

## 📝 建議的 README.md 內容

推送後，建議在 GitHub 上添加一個 README.md 來說明專案。我已經為你準備好了內容（見下一個文件）。

---

## ⚠️ 重要提醒

### 已排除的敏感文件（不會被推送）：
- ✅ `.env` 文件
- ✅ `node_modules/`
- ✅ `__pycache__/`
- ✅ `.venv/`
- ✅ 資料庫文件

### 如果不小心推送了敏感資訊：
1. 立即更換所有密鑰和 token
2. 使用 `git filter-branch` 或 BFG Repo-Cleaner 清除歷史記錄
3. Force push: `git push origin main --force`

---

## 🎉 完成後

推送成功後，你可以：
1. 在 GitHub 上查看你的專案
2. 分享 repository URL 給他人
3. 設定 GitHub Actions 進行 CI/CD（可選）
4. 添加 LICENSE 文件（建議使用 MIT License）

---

**需要協助？** 
- GitHub 文檔: https://docs.github.com/
- Git 基礎教學: https://git-scm.com/book/zh-tw/v2
