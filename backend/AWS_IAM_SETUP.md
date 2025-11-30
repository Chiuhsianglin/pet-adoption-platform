# AWS IAM 權限設定指南

## 當前問題

您的 AWS IAM 用戶 `uploader` (arn:aws:iam::672408958278:user/uploader) 缺少以下 S3 權限：
- ❌ `s3:ListBucket` - 列出儲存桶內容
- ❌ `s3:PutObject` - 上傳檔案
- ❌ `s3:GetObject` - 下載檔案
- ❌ `s3:DeleteObject` - 刪除檔案

## 解決方案

### 選項 1: 使用 AWS Console（推薦）

#### 步驟 1: 登入 AWS Console
1. 前往 https://console.aws.amazon.com/
2. 使用您的 AWS 帳號登入
3. 確認右上角區域為 **ap-southeast-2** (Sydney)

#### 步驟 2: 進入 IAM 服務
1. 在搜尋欄輸入 "IAM"
2. 點擊 **IAM** 服務

#### 步驟 3: 找到 uploader 用戶
1. 左側選單點擊 **Users**
2. 搜尋並點擊 **uploader** 用戶
3. 點擊 **Add permissions** 按鈕
4. 選擇 **Attach policies directly**

#### 步驟 4: 添加 S3 權限策略
1. 點擊 **Create policy** 按鈕（新標籤頁開啟）
2. 選擇 **JSON** 標籤
3. 複製貼上以下策略（也保存在 `aws-iam-policy.json`）:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::pet-adoption-files"
    },
    {
      "Sid": "S3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::pet-adoption-files/*"
    }
  ]
}
```

5. 點擊 **Next: Tags** (可跳過)
6. 點擊 **Next: Review**
7. 輸入策略名稱: **PetAdoptionS3UploaderPolicy**
8. 輸入描述: **S3 access for pet adoption file uploads**
9. 點擊 **Create policy**

#### 步驟 5: 將策略附加到用戶
1. 回到 uploader 用戶的 **Add permissions** 頁面
2. 刷新策略列表
3. 搜尋 **PetAdoptionS3UploaderPolicy**
4. 勾選該策略
5. 點擊 **Next: Review**
6. 點擊 **Add permissions**

#### 步驟 6: 驗證權限
在 PowerShell 執行以下命令測試：

```powershell
cd c:\project_bmad\pet-adoption-platform\backend
python test_s3_upload.py
```

---

### 選項 2: 使用 AWS CLI

如果您已安裝並設定 AWS CLI：

#### 1. 創建策略
```bash
aws iam create-policy \
  --policy-name PetAdoptionS3UploaderPolicy \
  --policy-document file://aws-iam-policy.json \
  --description "S3 access for pet adoption file uploads"
```

#### 2. 附加策略到用戶
```bash
aws iam attach-user-policy \
  --user-name uploader \
  --policy-arn arn:aws:iam::672408958278:policy/PetAdoptionS3UploaderPolicy
```

#### 3. 驗證權限
```bash
aws iam list-attached-user-policies --user-name uploader
```

---

## 權限說明

### Bucket 層級權限 (pet-adoption-files)
- **s3:ListBucket** - 允許列出儲存桶中的物件
- **s3:GetBucketLocation** - 允許取得儲存桶位置資訊

### Object 層級權限 (pet-adoption-files/*)
- **s3:PutObject** - 允許上傳檔案
- **s3:GetObject** - 允許讀取/下載檔案
- **s3:DeleteObject** - 允許刪除檔案
- **s3:PutObjectAcl** - 允許設定檔案存取權限（用於公開/私有設定）

---

## 安全性建議

### ✅ 當前策略的優點
- **最小權限原則** - 只授予必要的操作權限
- **資源限制** - 僅限於 `pet-adoption-files` 儲存桶
- **細粒度控制** - 明確指定允許的操作

### 🔒 額外安全措施（可選）
如果想進一步限制權限，可以添加條件：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::pet-adoption-files/*",
      "Condition": {
        "StringLike": {
          "s3:prefix": ["pets/*", "documents/*", "avatars/*"]
        }
      }
    }
  ]
}
```

---

## 驗證測試

### 測試 1: S3 連線
```powershell
python -c "import boto3; from app.core.config import settings; s3 = boto3.client('s3', region_name=settings.AWS_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY); s3.list_objects_v2(Bucket=settings.AWS_S3_BUCKET, MaxKeys=1); print('✅ S3 連線成功')"
```

### 測試 2: 檔案上傳
```powershell
python -c "import boto3; from app.core.config import settings; from io import BytesIO; from PIL import Image; img = Image.new('RGB', (100, 100), 'red'); buf = BytesIO(); img.save(buf, 'JPEG'); buf.seek(0); s3 = boto3.client('s3', region_name=settings.AWS_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY); s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key='test/test.jpg', Body=buf.getvalue()); print('✅ 檔案上傳成功')"
```

### 測試 3: 完整測試套件
```powershell
cd c:\project_bmad\pet-adoption-platform\backend
python test_s3_upload.py
```

---

## 常見問題

### Q: 更新權限後多久生效？
**A:** 通常在 1-2 分鐘內生效，某些情況可能需要 5 分鐘。

### Q: 如果測試還是失敗怎麼辦？
**A:** 
1. 確認策略已正確附加到 uploader 用戶
2. 等待 2-3 分鐘讓權限傳播
3. 檢查 AWS CloudTrail 查看被拒絕的請求詳情

### Q: 是否需要重啟應用程式？
**A:** 不需要。AWS 權限更新後，boto3 客戶端會自動使用新權限。

### Q: 可以用現有的 AWS 管理策略嗎？
**A:** 可以使用 `AmazonS3FullAccess` 但不建議，因為它授予所有 S3 儲存桶的完整權限。建議使用上述自訂策略來限制權限範圍。

---

## 檔案位置

- **策略 JSON**: `backend/aws-iam-policy.json`
- **測試腳本**: `backend/test_s3_upload.py`
- **環境設定**: `backend/.env`

---

## 下一步

1. ✅ 完成 IAM 權限設定
2. ⏳ 執行 S3 測試腳本
3. ⏳ 驗證 API 服務器啟動
4. ⏳ 執行完整的整合測試

完成權限設定後，請告訴我，我會協助您執行測試！
