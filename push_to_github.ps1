# ========================================
# 快速推送到 GitHub 腳本
# ========================================
# 使用說明：
# 1. 打開此文件
# 2. 修改下方的用戶資訊
# 3. 複製所有命令到 PowerShell 執行
# ========================================

# ⚠️ 請先在 GitHub 創建 repository 並取得 URL
# ⚠️ 請先取得 Personal Access Token（見 GITHUB_PUSH_GUIDE.md）

# ========================================
# 步驟 1: 設定 Git 用戶資訊（僅針對此專案）
# ========================================
Write-Host "📝 設定 Git 用戶資訊..." -ForegroundColor Cyan
git config user.name "Chiuhsianglin"        # ← 修改這裡
git config user.email "lily12253410@gmail.com"  # ← 修改這裡

# ========================================
# 步驟 2: 檢查並清理 Git 狀態
# ========================================
Write-Host "`n🔍 檢查 Git 狀態..." -ForegroundColor Cyan
git status

# ========================================
# 步驟 3: 添加所有文件
# ========================================
Write-Host "`n➕ 添加所有文件..." -ForegroundColor Cyan
git add .

# ========================================
# 步驟 4: 確認要提交的文件
# ========================================
Write-Host "`n📋 將要提交的文件：" -ForegroundColor Yellow
git status

Write-Host "`n⚠️  請檢查上方列表，確認：" -ForegroundColor Yellow
Write-Host "   1. 沒有 .env 文件" -ForegroundColor Yellow
Write-Host "   2. 沒有敏感資訊" -ForegroundColor Yellow
Write-Host "`n按 Enter 繼續，或 Ctrl+C 取消..." -ForegroundColor Yellow
Read-Host

# ========================================
# 步驟 5: 創建提交
# ========================================
Write-Host "`n💾 創建提交..." -ForegroundColor Cyan

$commitMessage = @"
Initial commit: Pet Adoption Platform

Features:
- Pet browsing and search with filters
- User authentication (shelter/adopter)
- Adoption application system
- Community posts comments and likes
- Real-time chat with WebSocket
- Notification system
- Favorite pets
- Photo upload with AWS S3 and CloudFront CDN
- RESTful API with FastAPI V2
- Vue 3 and Vuetify frontend
- MySQL database
"@

git commit -m $commitMessage

# ========================================
# 步驟 6: 設定遠端 repository
# ========================================
Write-Host "`n🔗 設定遠端 repository..." -ForegroundColor Cyan

# 檢查是否已有 origin
$hasOrigin = git remote | Select-String "origin"

if ($hasOrigin) {
    Write-Host "⚠️  已存在 origin，移除舊的..." -ForegroundColor Yellow
    git remote remove origin
}

# ⚠️ 修改下方的 URL 為你的 GitHub repository URL
git remote add origin https://github.com/Chiuhsianglin/pet-adoption-platform.git  # ← 修改這裡

Write-Host "✅ 遠端 repository 已設定" -ForegroundColor Green

# ========================================
# 步驟 7: 推送到 GitHub
# ========================================
Write-Host "`n🚀 準備推送到 GitHub..." -ForegroundColor Cyan
Write-Host "⚠️  等等會要求輸入認證資訊：" -ForegroundColor Yellow
Write-Host "   - Username: 你的 GitHub 用戶名" -ForegroundColor Yellow
Write-Host "   - Password: 你的 Personal Access Token（不是登入密碼！）" -ForegroundColor Yellow
Write-Host "`n按 Enter 開始推送..." -ForegroundColor Yellow
Read-Host

git branch -M main
git push -u origin main

# ========================================
# 完成！
# ========================================
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 推送成功！" -ForegroundColor Green
    Write-Host "🎉 你的專案已上傳到 GitHub" -ForegroundColor Green
    Write-Host "`n📝 下一步：" -ForegroundColor Cyan
    Write-Host "   1. 前往 GitHub 查看你的 repository" -ForegroundColor White
    Write-Host "   2. 可以考慮添加 README.md 來說明專案" -ForegroundColor White
    Write-Host "   3. 設定 repository 的 visibility (Public/Private)" -ForegroundColor White
} else {
    Write-Host "`n❌ 推送失敗" -ForegroundColor Red
    Write-Host "💡 常見問題：" -ForegroundColor Yellow
    Write-Host "   1. Personal Access Token 是否正確？" -ForegroundColor White
    Write-Host "   2. Repository URL 是否正確？" -ForegroundColor White
    Write-Host "   3. Token 權限是否包含 'repo'？" -ForegroundColor White
    Write-Host "`n請參考 GITHUB_PUSH_GUIDE.md 取得詳細說明" -ForegroundColor Cyan
}
