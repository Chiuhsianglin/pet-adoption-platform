# CloudFront CDN 設定指南

## 🎯 目標
設置 CloudFront CDN 來加速 S3 圖片載入，預期速度提升 50-80%

---

## 📋 步驟 1：AWS Console 創建 CloudFront Distribution

### 1.1 前往 CloudFront 控制台
- 登入 AWS Console
- 搜尋並進入 **CloudFront** 服務
- 點擊 **Create Distribution**

### 1.2 Origin 設定
```
Origin Domain: 選擇你的 S3 Bucket
  - 例如：pet-adoption-files.s3.us-east-1.amazonaws.com

Origin Path: (留空)

Origin Access: 
  ✅ 如果 S3 是公開存取：選擇 "Public"
  ✅ 如果 S3 是私有：選擇 "Origin Access Control (OAC)" 並設定權限
```

### 1.3 Default Cache Behavior 設定
```
Viewer Protocol Policy: Redirect HTTP to HTTPS

Allowed HTTP Methods: GET, HEAD (只讀操作)

Cache Policy: CachingOptimized
  - 或自訂：TTL 設為 7 天 (604800 秒)

Compress Objects Automatically: Yes (建議開啟)
```

### 1.4 其他設定
```
Price Class: 
  - Use all edge locations (最快，但較貴)
  - Use only North America and Europe (平衡)

Alternate Domain Names (CNAMEs): (選填，如果要用自己的域名)

SSL Certificate: Default CloudFront Certificate
```

### 1.5 建立 Distribution
- 點擊 **Create Distribution**
- 等待狀態從 "Deploying" 變為 "Enabled"（約 5-15 分鐘）
- **記下 Distribution Domain Name**
  - 例如：`d1234567890abc.cloudfront.net`

---

## 📋 步驟 2：設定環境變數

編輯 `backend/.env` 檔案，添加：

```env
# CloudFront CDN 設定
AWS_CLOUDFRONT_DOMAIN=https://d1234567890abc.cloudfront.net
```

> ⚠️ 注意：請將 `d1234567890abc.cloudfront.net` 替換為你的實際 Distribution Domain Name

---

## 📋 步驟 3：重啟後端服務

```powershell
# 停止目前的後端進程
Get-Process -Name "python" | Where-Object {$_.Path -like "*project_bmad*"} | Stop-Process -Force

# 重新啟動後端
cd C:\project_bmad\pet-adoption-platform\backend
.\start_backend.ps1
```

---

## ✅ 驗證 CloudFront 是否生效

### 檢查 1：後端啟動日誌
應該看到：
```
🔧 S3Service 初始化:
   USE_S3: True
   Bucket: pet-adoption-files
   Region: us-east-1
   CloudFront: https://d1234567890abc.cloudfront.net  ✅
```

### 檢查 2：瀏覽器開發者工具
1. 打開前端頁面（例如社群、寵物列表）
2. 按 F12 開啟開發者工具
3. 切換到 **Network** 標籤
4. 重新載入頁面
5. 查看圖片請求的 URL：
   - ✅ 正確：`https://d1234567890abc.cloudfront.net/pet_photo/xxx.jpg`
   - ❌ 錯誤：`https://pet-adoption-files.s3.amazonaws.com/...?X-Amz-Signature=...`

### 檢查 3：載入速度
- **之前**（S3 直接載入）：通常 500ms - 2000ms
- **現在**（CloudFront）：應該在 50ms - 300ms

---

## 🔧 進階優化（可選）

### 選項 1：S3 Bucket 權限設定
如果使用 OAC（私有 S3），需要更新 S3 Bucket Policy：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::pet-adoption-files/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

### 選項 2：自訂 Cache Key
在 CloudFront > Cache Policies 中設定：
- Cache based on: Query strings (All)
- TTL: Min=0, Max=31536000, Default=604800

### 選項 3：前端圖片懶加載
安裝 `vue3-lazyload` 套件，減少初始載入量。

---

## 📊 預期效果

| 項目 | 優化前 | 優化後 |
|------|--------|--------|
| 圖片載入速度 | 500-2000ms | 50-300ms |
| 首頁載入時間 | 3-5 秒 | 1-2 秒 |
| S3 API 呼叫 | 每次請求 | 快取 7 天 |
| 用戶體驗 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## ❓ 常見問題

### Q1: CloudFront 顯示 403 錯誤？
**A:** 檢查 S3 Bucket 權限，確保 CloudFront OAC 有讀取權限。

### Q2: 圖片更新後，CloudFront 還顯示舊圖片？
**A:** 需要手動清除快取（Invalidation）：
```
CloudFront > Distributions > Invalidations > Create Invalidation
Object Paths: /pet_photo/*
```

### Q3: 開發環境想跳過 CloudFront？
**A:** 在 `backend/.env` 中移除或註解掉：
```env
# AWS_CLOUDFRONT_DOMAIN=https://d1234567890abc.cloudfront.net
```

### Q4: CloudFront 會增加成本嗎？
**A:** 
- CloudFront 前 1TB/月流量：約 $0.085/GB
- S3 出站流量：約 $0.09/GB
- 實際上可能**降低成本**（減少 S3 API 呼叫）

---

## 🎉 完成！

設置完成後，你的寵物領養平台圖片載入速度將顯著提升！

如有問題，請檢查：
1. CloudFront Distribution 狀態是否為 "Enabled"
2. `.env` 中的 `AWS_CLOUDFRONT_DOMAIN` 是否正確
3. 後端啟動日誌中 CloudFront 配置是否顯示

---

**上次更新**: 2025-11-30
