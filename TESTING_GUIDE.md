# 🎯 照片上傳系統測試指南

## ✅ 系統狀態

### 後端伺服器
- ✅ 運行中: http://localhost:8000
- ✅ API 文件: http://localhost:8000/api/v1/docs
- ✅ 資料庫連線: 正常
- ✅ S3 連線: 正常
- ✅ pet_photos 資料表: 已建立

### 前端伺服器
- ✅ 運行中: http://localhost:3000
- ✅ API 連線: http://localhost:8000/api/v1

### 測試帳號
- Email: `test@example.com`
- Password: `Test123456!`
- Role: `shelter` (可以上傳寵物照片)

## 📋 測試步驟

### 方法 1: 前端手動測試（推薦）

1. **登入系統**
   ```
   網址: http://localhost:3000
   Email: test@example.com
   Password: Test123456!
   ```

2. **創建新寵物（如果沒有）**
   - 點選「寵物管理」
   - 點選「新增寵物」
   - 填寫基本資訊並儲存

3. **測試照片上傳**
   - 在寵物管理頁面，找到你的寵物
   - 點選「照片管理」或「編輯」
   - 找到照片上傳區域
   - 選擇一張圖片上傳
   - 確認照片顯示在列表中

4. **驗證功能**
   - ✅ 照片成功上傳
   - ✅ 照片 URL 格式正確（來自 S3）
   - ✅ 第一張照片自動設為主照片
   - ✅ 可以設定其他照片為主照片
   - ✅ 可以刪除照片
   - ✅ 照片顯示在寵物列表
   - ✅ 照片顯示在寵物詳情頁

### 方法 2: API 測試（使用 curl）

1. **取得 Token**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "Test123456!"
     }'
   ```
   複製回應中的 `access_token`

2. **創建測試寵物**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/pets" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "測試寵物",
       "species": "dog",
       "breed": "混種",
       "gender": "male",
       "age_years": 2,
       "status": "available",
       "description": "用於測試照片上傳"
     }'
   ```
   記下回應中的寵物 `id`

3. **上傳照片**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/pets/PET_ID/photos" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "files=@test_image.jpg" \
     -F "caption=測試照片"
   ```

4. **查看寵物資料**
   ```bash
   curl "http://localhost:8000/api/v1/pets/PET_ID" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```
   檢查 `photos` 陣列和 `primary_photo_url`

### 方法 3: Swagger UI 測試

1. 開啟 API 文件: http://localhost:8000/api/v1/docs

2. 點選右上角「Authorize」並輸入 Bearer Token

3. 測試以下 endpoints:
   - `POST /api/v1/auth/login` - 登入
   - `POST /api/v1/pets` - 創建寵物
   - `POST /api/v1/pets/{pet_id}/photos` - 上傳照片
   - `GET /api/v1/pets/{pet_id}` - 查看寵物資料
   - `DELETE /api/v1/pets/{pet_id}/photos/{photo_id}` - 刪除照片

## 🔍 驗證清單

### 照片上傳
- [ ] 可以選擇圖片檔案
- [ ] 支援 JPG、PNG、WebP 格式
- [ ] 自動壓縮和優化圖片
- [ ] 顯示上傳進度（如果有）
- [ ] 上傳成功後顯示預覽

### 照片儲存
- [ ] 照片儲存到 AWS S3
- [ ] URL 格式: `https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/pets/{pet_id}/photos/...`
- [ ] MySQL 中有照片記錄（file_url, file_key）
- [ ] 第一張照片自動設為 is_primary=true

### 照片顯示
- [ ] 寵物列表顯示主照片
- [ ] 寵物詳情頁顯示完整照片庫
- [ ] 照片可以點擊放大
- [ ] 照片載入速度正常

### 照片管理
- [ ] 可以上傳多張照片
- [ ] 可以設定主照片
- [ ] 可以刪除照片
- [ ] 刪除照片時同時從 S3 刪除
- [ ] 有權限控制（只有擁有者可操作）

## 🐛 常見問題

### 問題 1: 403 Permission Denied
**原因**: 嘗試上傳照片到不屬於自己的寵物
**解決**: 使用自己創建的寵物進行測試

### 問題 2: 照片無法顯示
**檢查**:
1. 瀏覽器開發者工具 > Network tab
2. 確認照片 URL 是否正確
3. 確認 S3 bucket CORS 設定
4. 確認照片確實上傳到 S3

### 問題 3: 上傳失敗 "Upload failed"
**檢查**:
1. AWS credentials 是否正確（.env 檔案）
2. S3 bucket 是否存在
3. IAM 權限是否包含 s3:PutObject
4. 檔案大小是否超過限制（10MB）

## 📊 預期結果

成功測試後，你應該能看到：

1. **資料庫（MySQL）**
   ```sql
   SELECT * FROM pet_photos;
   ```
   顯示照片記錄，包含 file_url 和 file_key

2. **S3 Bucket**
   - 路徑: `pets/{pet_id}/photos/`
   - 檔案格式: `20251112_061855_37f68ccc.jpg`

3. **前端顯示**
   - 寵物列表：顯示主照片
   - 寵物詳情：顯示完整照片庫
   - 照片管理：可以上傳、刪除、設定主照片

4. **API 回應**
   ```json
   {
     "message": "Successfully uploaded 1 photo(s)",
     "photos": [
       {
         "file_url": "https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/...",
         "file_key": "pets/2/photos/20251112_061855_37f68ccc.jpg",
         "is_primary": true
       }
     ]
   }
   ```

## 🚀 下一步

測試完成後：
1. ✅ 系統運作正常
2. 🎨 可以開始使用真實資料
3. 🔧 如需優化，參考 PHOTO_UPLOAD_CHECKLIST.md
4. 📸 享受完整的照片上傳功能！
