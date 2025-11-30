# 聊天系統部署指南

## 1. 執行資料庫遷移

```bash
cd backend

# 連接到 MySQL
mysql -u your_username -p your_database_name < create_chat_tables.sql
```

或使用 Python 腳本：

```python
# create_chat_db.py
import mysql.connector
import os

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'your_username'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME', 'pet_adoption')
)

cursor = conn.cursor()

with open('create_chat_tables.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()
    
for statement in sql_script.split(';'):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
cursor.close()
conn.close()

print("✅ Chat tables created successfully!")
```

執行：
```bash
python create_chat_db.py
```

## 2. 環境變數設置

確保 `.env` 檔案包含以下設定：

```env
# S3 Configuration (檔案上傳)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# WebSocket URL (前端)
VITE_WS_URL=ws://localhost:8000
```

## 3. 啟動後端

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## 4. 啟動前端

```bash
cd frontend
npm run dev
```

## 5. 測試流程

### A. 建立聊天室
1. 訪問 http://localhost:3000/pets
2. 選擇一隻寵物
3. 點擊「聯繫機構」按鈕
4. 系統自動建立聊天室並插入寵物卡片

### B. 發送訊息
1. 在聊天室輸入文字訊息
2. 按 Enter 或點擊發送按鈕
3. 訊息應即時顯示在聊天室中

### C. 上傳檔案
1. 點擊「📎」按鈕
2. 選擇圖片或檔案（支援：jpg, png, pdf, doc, docx 等）
3. 檔案上傳到 S3 後顯示在聊天室

### D. WebSocket 即時推送
1. 開啟兩個瀏覽器視窗
2. 一個視窗登入為申請者，另一個登入為收容所
3. 在任一視窗發送訊息
4. 另一視窗應即時收到訊息

### E. 未讀訊息
1. 在聊天列表中檢查未讀數量
2. 進入聊天室後未讀數應清零

## 6. API 測試

使用 Postman 或 curl 測試：

### 建立聊天室
```bash
curl -X POST http://localhost:8000/api/v1/chat/rooms \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": 1}'
```

### 獲取聊天室列表
```bash
curl http://localhost:8000/api/v1/chat/rooms \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 發送訊息
```bash
curl -X POST http://localhost:8000/api/v1/chat/rooms/1/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "content": "你好！",
    "message_type": "text"
  }'
```

### 上傳檔案
```bash
curl -X POST http://localhost:8000/api/v1/chat/rooms/1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/your/file.jpg"
```

## 7. WebSocket 連接測試

前端自動連接 WebSocket：
- 連接 URL: `ws://localhost:8000/api/v1/chat/ws?token=YOUR_TOKEN`
- 心跳：每 30 秒自動發送 ping
- 自動重連：斷線後 5 秒重連

檢查瀏覽器控制台：
- ✅ 成功：`WebSocket connected`
- 📢 訂閱：`Subscribed to room X`
- 📨 收到訊息：`WebSocket message: {...}`

## 8. 常見問題排查

### 問題 1: WebSocket 無法連接
- 檢查後端是否啟動
- 檢查 CORS 設定
- 確認 token 有效

### 問題 2: 檔案上傳失敗
- 檢查 S3 設定（AWS 憑證、bucket 名稱）
- 確認檔案大小限制（圖片 5MB，檔案 10MB）
- 檢查檔案類型是否允許

### 問題 3: 寵物卡片不顯示
- 檢查是否首次建立聊天室
- 確認寵物資料完整（名稱、照片）
- 查看資料庫 chat_pet_cards 表

### 問題 4: 未讀數不更新
- 檢查 WebSocket 連接狀態
- 確認 mark_messages_as_read API 被調用
- 查看資料庫 chat_messages.is_read 欄位

## 9. 資料庫查詢示例

```sql
-- 查看所有聊天室
SELECT * FROM chat_rooms;

-- 查看特定聊天室的訊息
SELECT * FROM chat_messages WHERE room_id = 1 ORDER BY created_at DESC;

-- 查看未讀訊息數
SELECT room_id, COUNT(*) as unread_count 
FROM chat_messages 
WHERE is_read = FALSE AND sender_id != YOUR_USER_ID
GROUP BY room_id;

-- 查看寵物卡片
SELECT * FROM chat_pet_cards;
```

## 10. 生產環境注意事項

1. **WebSocket URL**: 改為 `wss://` (HTTPS)
2. **S3 CORS**: 設定允許來源
3. **檔案大小**: 根據需求調整限制
4. **連接池**: 調整資料庫連接池大小
5. **監控**: 添加 WebSocket 連接數監控
6. **日誌**: 記錄聊天訊息審計日誌

## 完成！🎉

聊天系統已完整實作，包含：
- ✅ WebSocket 即時通訊
- ✅ 寵物卡片自動插入
- ✅ 檔案上傳 (S3)
- ✅ 未讀訊息管理
- ✅ 分頁載入歷史訊息
- ✅ 自動重連機制
