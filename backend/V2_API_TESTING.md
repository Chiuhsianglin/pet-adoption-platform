# V2 API 測試指南

## 🎯 測試 V2 端點

V2 API 已部署在 `/api/v2/` 路徑下，使用新的三層架構。

## 📋 可用端點

### 1. Pets (寵物管理)
```bash
# 獲取寵物列表
curl http://localhost:8000/api/v2/pets

# 獲取單個寵物
curl http://localhost:8000/api/v2/pets/{pet_id}

# 搜尋寵物
curl -X POST http://localhost:8000/api/v2/pets/search \
  -H "Content-Type: application/json" \
  -d '{"species": "dog", "size": "medium"}'

# 獲取篩選選項
curl http://localhost:8000/api/v2/pets/filters/options

# 收藏寵物（需要認證）
curl -X POST http://localhost:8000/api/v2/pets/{pet_id}/favorite \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Adoptions (領養申請)
```bash
# 創建草稿
curl -X POST http://localhost:8000/api/v2/adoptions/applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": 1}'

# 提交申請
curl -X PUT http://localhost:8000/api/v2/adoptions/applications/{id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"living_space": "house", ...}'

# 獲取我的申請
curl http://localhost:8000/api/v2/adoptions/applications \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Notifications (通知)
```bash
# 獲取通知列表
curl http://localhost:8000/api/v2/notifications \
  -H "Authorization: Bearer YOUR_TOKEN"

# 獲取未讀數量
curl http://localhost:8000/api/v2/notifications/unread-count \
  -H "Authorization: Bearer YOUR_TOKEN"

# 標記已讀
curl -X PATCH http://localhost:8000/api/v2/notifications/{id}/read \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Chat (聊天)
```bash
# 創建或獲取聊天室
curl -X POST http://localhost:8000/api/v2/chat/rooms \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shelter_id": 1, "pet_id": 1}'

# 獲取聊天室訊息
curl http://localhost:8000/api/v2/chat/rooms/{room_id}/messages \
  -H "Authorization: Bearer YOUR_TOKEN"

# 發送文字訊息
curl -X POST http://localhost:8000/api/v2/chat/rooms/{room_id}/messages/text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello!"}'
```

### 5. Community (社群)
```bash
# 獲取貼文列表
curl http://localhost:8000/api/v2/community/posts

# 創建貼文
curl -X POST http://localhost:8000/api/v2/community/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "我的寵物故事", "content": "...", "post_type": "share"}'

# 按讚
curl -X POST http://localhost:8000/api/v2/community/posts/{id}/like \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 與 V1 對比測試

### 測試相同請求的回應
```bash
# V1 端點
curl http://localhost:8000/api/v1/pets

# V2 端點
curl http://localhost:8000/api/v2/pets

# 比較回應格式和內容是否一致
```

## 📊 API 文件

訪問 Swagger 文件：
- V1: http://localhost:8000/api/v1/docs
- V2: http://localhost:8000/api/v2/docs (將自動包含 v2 端點)

## ✅ 檢查清單

測試時請確認：
- [ ] 回應格式與 V1 一致
- [ ] HTTP 狀態碼正確
- [ ] 錯誤訊息清晰
- [ ] 分頁功能正常
- [ ] 權限驗證正確
- [ ] 資料庫查詢效率（檢查日誌中的 SQL）

## 🐛 如果遇到問題

1. 查看後端日誌
2. 檢查 `/api/v2/` 路由是否正確註冊
3. 確認 Service 和 Repository 層正常工作
4. 使用 `python test_architecture.py` 驗證基礎架構

## 🔄 前端整合

前端可以通過環境變數切換：
```javascript
// .env.development
VITE_API_VERSION=v2
VITE_API_BASE_URL=http://localhost:8000/api/v2

// 或在代碼中切換
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'
const API_BASE = `http://localhost:8000/api/${API_VERSION}`
```
