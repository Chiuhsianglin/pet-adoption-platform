# ContactModal 端到端測試 - 快速參考

## 已完成 

### 前端 (ContactModal.vue - ~420 lines)
- 7 種諮詢類型 (一般諮詢、領養相關、預約參觀等)
- 4 種聯絡方式 (電子郵件、電話、LINE、簡訊)
- 完整表單驗證 (必填、Email、電話格式)
- 預約參觀功能 (日期 + 時段選擇)
- 自動填充已登入用戶資料
- 成功訊息 + 2 秒自動關閉

### 後端 (Inquiry API - ~325 lines)
- POST /api/v1/inquiries - 建立諮詢
- GET /api/v1/inquiries - 列表查詢 (分頁、篩選)
- GET /api/v1/inquiries/{id} - 單一諮詢
- 可選認證 (匿名 + 已登入用戶)
- Pydantic 驗證
- 中文錯誤訊息

### 資料庫
- inquiries 表 (17 columns, 2 indexes)
- 5 筆測試記錄
- 時間戳自動設定

## 測試結果 

| 測試項目 | 狀態 | 說明 |
|---------|------|------|
| 匿名用戶諮詢 |  PASS | Status 201, 記錄建立 |
| 預約參觀功能 |  PASS | 日期時段正確儲存 |
| 查詢諮詢列表 |  PASS | Status 200, 總數 5 |
| 資料庫整合 |  PASS | 所有欄位正確 |
| API 通信 |  PASS | CORS 設定正常 |

## 服務管理

### 檢查服務狀態
`powershell
# 檢查後端
python -c "import requests; print(requests.get('http://localhost:8000/').json())"

# 檢查前端 (瀏覽器訪問)
http://localhost:3001

# 檢查資料庫記錄
python -c "import requests; r=requests.get('http://localhost:8000/api/v1/inquiries'); print('總數:', r.json()['data']['total'])"
`

### 查看 Job 狀態
`powershell
Get-Job | Format-Table -AutoSize
`

### 停止所有服務
`powershell
Get-Job | Stop-Job
Get-Job | Remove-Job
`

## 手動測試

### 1. 訪問前端
http://localhost:3001/pets/1

### 2. 點擊「聯繫機構」按鈕

### 3. 填寫表單
- 姓名: 測試用戶
- Email: test@example.com
- 電話: 0912345678
- 聯絡方式: 電子郵件
- 諮詢類型: 一般諮詢
- 訊息: 我想了解更多關於這隻寵物的資訊...
- 隱私政策: 

### 4. 點擊送出
- 應該看到綠色成功訊息
- 2 秒後自動關閉

### 5. 驗證資料庫
`powershell
python -c "import requests; items=requests.get('http://localhost:8000/api/v1/inquiries').json()['data']['items']; [print(f'{i}. {item[\"name\"]} - {item[\"inquiry_type\"]}') for i,item in enumerate(items[:5],1)]"
`

## 快速命令

### 重啟後端
`powershell
Get-Job -Name Job7 | Stop-Job
Get-Job -Name Job7 | Remove-Job
Start-Job -Name Backend -ScriptBlock { cd "C:\project_bmad\pet-adoption-platform\backend"; $env:PYTHONPATH=$PWD; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 }
`

### 測試 API
`powershell
# 建立諮詢
python -c "import requests,json; r=requests.post('http://localhost:8000/api/v1/inquiries', json={'name':'測試','email':'test@example.com','phone':'0912345678','contact_method':'電子郵件','inquiry_type':'一般諮詢','message':'測試訊息測試訊息測試訊息','pet_id':1,'shelter_id':1}); print(r.status_code, r.json()['message'])"

# 查詢列表
python -c "import requests; r=requests.get('http://localhost:8000/api/v1/inquiries'); print('總數:', r.json()['data']['total'])"
`

## 進度

- **Story 2.5**: 60% Complete
- **完成**: ContactModal + Inquiry API + E2E Testing
- **下一步**: VaccinationTimeline 組件

## 文檔

- Story: docs/stories/epic-2/2.5-pet-details.md
- 測試腳本: ackend/test_inquiry_e2e.py
- 前端組件: rontend/src/components/pet/ContactModal.vue
- 後端 API: ackend/app/api/v1/inquiries.py

---
更新日期: 2025-11-07
開發者: James (Full Stack Developer)
