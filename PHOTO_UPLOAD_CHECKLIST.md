# 照片上傳系統檢查清單

## ✅ 已完成的工作

### 1. 後端儲存服務 (`backend/app/services/storage_service.py`)
- ✅ 建立 `StorageService` 類別
- ✅ 實作檔案驗證功能（檔案大小、類型、真實性）
- ✅ 實作圖片優化功能（壓縮、調整大小）
- ✅ 實作 S3 上傳功能 (`upload_pet_photo`)
- ✅ 實作 S3 刪除功能 (`delete_file`)
- ✅ 實作 Presigned URL 生成（用於私有檔案）

### 2. 後端 API Endpoints (`backend/app/api/v1/pets.py`)
- ✅ 更新 `POST /pets/{pet_id}/photos` 接受 `multipart/form-data`
  - 接收多個檔案上傳
  - 驗證用戶權限（只有寵物所有者可以上傳）
  - 上傳到 S3 並儲存 URL 到 MySQL
  - 自動設定第一張照片為主要照片
- ✅ 更新 `DELETE /pets/{pet_id}/photos/{photo_id}` 
  - 從 S3 刪除檔案
  - 從 MySQL 刪除記錄
  - 驗證用戶權限

### 3. 資料庫模型 (`backend/app/models/pet.py`)
- ✅ `PetPhoto` 模型已定義
  - `id`: Primary key
  - `pet_id`: Foreign key to pets
  - `file_url`: S3 完整 URL
  - `file_key`: S3 object key
  - `is_primary`: 是否為主要照片
  - `caption`: 照片說明
  - `upload_order`: 排序順序
  - `created_at`: 建立時間

### 4. 前端元件
- ✅ `PhotoEditor.vue` 已存在
  - 照片上傳介面
  - 照片管理（排序、設定主照片、刪除）
  - 照片說明編輯
- ✅ `PetCard.vue` 顯示主要照片
- ✅ `PetDetailPage.vue` 顯示完整照片庫

### 5. API 序列化
- ✅ `_serialize_pet` 函數已包含 `primary_photo_url`
- ✅ `/pets/{id}` endpoint 回傳照片陣列
- ✅ `/pets/favorites` endpoint 包含照片 URL

## 🔧 需要檢查的項目

### 1. 環境設定檢查

```bash
# 檢查 .env 檔案是否包含正確的 AWS 設定
AWS_ACCESS_KEY_ID=你的_access_key
AWS_SECRET_ACCESS_KEY=你的_secret_key
AWS_REGION=ap-northeast-1
AWS_S3_BUCKET=pet-adoption-files
```

### 2. 安裝必要套件

```bash
cd backend
pip install -r requirements.txt
# 特別確認這些套件：
# - boto3==1.34.0
# - pillow==10.1.0  
# - python-magic-bin==0.4.14 (Windows) 或 python-magic (Linux/Mac)
```

### 3. 資料庫表結構檢查

```bash
# 在 MySQL 中執行
cd backend
mysql -u your_user -p pet_adoption < verify_pet_photos_table.sql
```

或手動檢查：
```sql
DESC pet_photos;
-- 應該看到：id, pet_id, file_url, file_key, is_primary, caption, upload_order, created_at
```

### 4. S3 權限測試

```bash
cd backend
python test/test_s3_simple.py
# 應該看到所有 5 個測試都通過
```

### 5. 照片上傳流程測試

```bash
cd backend
python test_photo_upload.py
# 應該看到 4 個步驟都成功
```

## 📋 測試步驟

### 後端測試

1. **啟動後端伺服器**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **使用 curl 測試上傳**
```bash
# 1. 先登入取得 token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"your_password"}'

# 2. 上傳照片（替換 YOUR_TOKEN 和 PET_ID）
curl -X POST "http://localhost:8000/api/v1/pets/PET_ID/photos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@test_image.jpg" \
  -F "caption=測試照片"
```

### 前端測試

1. **啟動前端**
```bash
cd frontend
npm run dev
```

2. **手動測試流程**
   - [ ] 登入系統
   - [ ] 進入寵物管理頁面
   - [ ] 點擊「照片管理」
   - [ ] 上傳一張照片（應該成功上傳到 S3）
   - [ ] 檢查照片是否顯示（應該從 S3 載入）
   - [ ] 上傳多張照片
   - [ ] 設定主要照片
   - [ ] 刪除照片（應該從 S3 和資料庫都刪除）
   - [ ] 檢查寵物列表頁的照片顯示
   - [ ] 檢查寵物詳情頁的照片庫

3. **瀏覽器開發者工具檢查**
   - [ ] Network tab: 確認照片從 S3 URL 載入
   - [ ] Console: 無錯誤訊息
   - [ ] 照片 URL 格式：`https://pet-adoption-files.s3.ap-northeast-1.amazonaws.com/pets/{pet_id}/photos/...`

## 🐛 常見問題排除

### 問題 1: 上傳失敗 "S3 上傳失敗"
**解決方案：**
1. 檢查 AWS credentials 是否正確
2. 檢查 S3 bucket 是否存在
3. 檢查 IAM 權限是否包含 `s3:PutObject`

### 問題 2: 照片無法顯示
**解決方案：**
1. 檢查 S3 bucket 的 CORS 設定
2. 確認照片 URL 格式正確
3. 檢查 bucket 的公開存取設定

### 問題 3: "python-magic" 錯誤
**解決方案：**
- Windows: `pip install python-magic-bin`
- Linux/Mac: `pip install python-magic` 並安裝 libmagic
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libmagic1
  
  # macOS
  brew install libmagic
  ```

### 問題 4: 資料庫錯誤 "pet_photos table doesn't exist"
**解決方案：**
```bash
# 執行建表 SQL
mysql -u your_user -p pet_adoption < backend/verify_pet_photos_table.sql
```

## 📊 驗證結果

完成所有測試後，應該能看到：

1. ✅ 照片成功上傳到 S3
2. ✅ MySQL 中有照片記錄（包含 file_url 和 file_key）
3. ✅ 前端正確顯示照片
4. ✅ 可以設定主要照片
5. ✅ 可以刪除照片（S3 和資料庫都刪除）
6. ✅ 照片顯示速度快（使用 CDN/CloudFront 更佳）

## 🚀 下一步優化建議

1. **效能優化**
   - 設定 CloudFront CDN
   - 實作圖片 lazy loading
   - 加入圖片預覽縮圖

2. **功能增強**
   - 批次上傳進度顯示
   - 拖放上傳
   - 照片編輯功能（裁切、旋轉）

3. **安全性**
   - 檔案病毒掃描
   - 更嚴格的檔案類型驗證
   - Rate limiting

4. **監控**
   - S3 上傳/刪除日誌
   - 錯誤追蹤
   - 使用量統計
