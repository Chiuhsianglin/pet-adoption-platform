# Frontend API Version Switching - Testing Guide

## 測試目標

驗證前端 API 版本切換功能是否正常運作，並確保 V1 和 V2 API 都能正確使用。

## 前置準備

### 1. 確認後端運行

```powershell
# 進入後端目錄
cd C:\project_bmad\pet-adoption-platform\backend

# 啟動後端（確保同時運行 V1 和 V2）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

驗證後端：
- V1: http://localhost:8000/api/v1/docs
- V2: http://localhost:8000/api/v2/docs

### 2. 確認環境變數

檢查 `frontend/.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_V2_ENABLED=true
VITE_API_TIMEOUT=30000
```

### 3. 安裝依賴並啟動前端

```powershell
# 進入前端目錄
cd C:\project_bmad\pet-adoption-platform\frontend

# 安裝依賴（如果還沒安裝）
npm install

# 啟動開發伺服器
npm run dev
```

## 測試案例

### 測試 1: 預設版本檢查

**目標**: 驗證應用啟動時使用正確的預設 API 版本

**步驟**:
1. 清除 localStorage: 開啟開發者工具 Console，執行 `localStorage.clear()`
2. 重新載入頁面
3. 開啟開發者工具 Network 標籤
4. 登入系統
5. 瀏覽寵物列表

**預期結果**:
- ✅ 所有 API 請求 URL 應該是 `http://localhost:8000/api/v1/*`
- ✅ 右上角 API 版本按鈕顯示 "API V1"
- ✅ Console 顯示: `API baseURL updated: http://localhost:8000/api/v1`

**驗證命令**:
```javascript
// 在 Console 執行
console.log('Current version:', localStorage.getItem('api_version')) // 應該是 null
console.log('Axios baseURL:', window.axios?.defaults?.baseURL) // 應該包含 /api/v1
```

---

### 測試 2: 切換到 V2

**目標**: 驗證可以成功切換到 V2 API

**步驟**:
1. 確保已登入
2. 點擊右上角的 "API V1" 按鈕
3. 在下拉選單中選擇 "API V2"
4. 確認成功通知出現
5. 等待頁面重新載入
6. 重新登入（如果需要）
7. 開啟 Network 標籤
8. 瀏覽寵物列表

**預期結果**:
- ✅ 頁面重新載入
- ✅ 按鈕顯示 "API V2"（藍色高亮）
- ✅ 所有 API 請求 URL 變成 `http://localhost:8000/api/v2/*`
- ✅ localStorage 中保存了版本: `localStorage.getItem('api_version') === 'v2'`
- ✅ 功能正常運作（寵物列表正常顯示）

**驗證命令**:
```javascript
// 在 Console 執行
localStorage.getItem('api_version') // 應該是 'v2'
```

---

### 測試 3: V2 功能完整性測試

**目標**: 驗證在 V2 模式下所有核心功能正常運作

**測試場景**:

#### 3.1 寵物瀏覽 (Pets Module)
- [ ] 瀏覽寵物列表
- [ ] 搜尋寵物
- [ ] 使用篩選器
- [ ] 查看寵物詳情
- [ ] 收藏/取消收藏寵物

**驗證 API 端點**:
- GET /api/v2/pets/
- POST /api/v2/pets/search
- GET /api/v2/pets/{id}
- GET /api/v2/pets/filters/options

#### 3.2 申請管理 (Adoptions Module)
- [ ] 建立申請草稿
- [ ] 提交申請
- [ ] 查看申請列表
- [ ] 查看申請詳情
- [ ] 撤回申請

**驗證 API 端點**:
- POST /api/v2/adoptions/applications
- PUT /api/v2/adoptions/applications/{id}
- POST /api/v2/adoptions/applications/{id}/submit
- GET /api/v2/adoptions/applications
- POST /api/v2/adoptions/applications/{id}/withdraw

#### 3.3 通知系統 (Notifications Module)
- [ ] 查看通知列表
- [ ] 標記為已讀
- [ ] 全部標記為已讀
- [ ] 刪除通知
- [ ] 未讀計數正確

**驗證 API 端點**:
- GET /api/v2/notifications/
- PATCH /api/v2/notifications/{id}/read
- POST /api/v2/notifications/mark-all-read
- DELETE /api/v2/notifications/{id}
- GET /api/v2/notifications/unread-count

#### 3.4 即時通訊 (Chat Module)
- [ ] 建立聊天室
- [ ] 查看聊天室列表
- [ ] 發送文字訊息
- [ ] 發送圖片訊息
- [ ] 查看歷史訊息
- [ ] 未讀計數正確

**驗證 API 端點**:
- POST /api/v2/chat/rooms
- GET /api/v2/chat/rooms
- GET /api/v2/chat/rooms/{id}/messages
- POST /api/v2/chat/rooms/{id}/messages/text
- POST /api/v2/chat/rooms/{id}/messages/image

#### 3.5 社群功能 (Community Module)
- [ ] 查看貼文列表
- [ ] 建立貼文
- [ ] 編輯貼文
- [ ] 刪除貼文
- [ ] 留言功能
- [ ] 按讚功能
- [ ] 查看統計資訊

**驗證 API 端點**:
- GET /api/v2/community/posts
- POST /api/v2/community/posts
- PUT /api/v2/community/posts/{id}
- DELETE /api/v2/community/posts/{id}
- POST /api/v2/community/posts/{id}/comments
- POST /api/v2/community/posts/{id}/like

---

### 測試 4: 切換回 V1

**目標**: 驗證可以無縫切換回 V1

**步驟**:
1. 在使用 V2 的狀態下
2. 點擊 "API V2" 按鈕
3. 選擇 "API V1"
4. 確認通知出現
5. 等待頁面重新載入
6. 開啟 Network 標籤
7. 測試功能

**預期結果**:
- ✅ 按鈕顯示 "API V1"（灰色）
- ✅ 所有請求回到 `http://localhost:8000/api/v1/*`
- ✅ localStorage: `localStorage.getItem('api_version') === 'v1'`
- ✅ 所有功能正常

---

### 測試 5: 持久化測試

**目標**: 驗證版本選擇在頁面刷新後保持

**步驟**:
1. 切換到 V2
2. 關閉瀏覽器分頁
3. 重新開啟應用
4. 檢查版本

**預期結果**:
- ✅ 應用自動使用 V2
- ✅ 按鈕顯示 "API V2"
- ✅ 不需要重新切換

---

### 測試 6: 錯誤處理

**目標**: 驗證異常情況的處理

#### 6.1 後端 V2 未啟動
**步驟**:
1. 停止後端
2. 嘗試切換到 V2
3. 啟動只有 V1 的後端

**預期結果**:
- ✅ 顯示適當的錯誤訊息
- ✅ 不會崩潰

#### 6.2 網路錯誤
**步驟**:
1. 使用 V2
2. 關閉後端
3. 嘗試執行操作

**預期結果**:
- ✅ 統一的錯誤處理（"無法連接到伺服器"）
- ✅ UI 保持可用

#### 6.3 禁用 V2
**步驟**:
1. 修改 `.env`: `VITE_V2_ENABLED=false`
2. 重新啟動前端
3. 檢查版本切換器

**預期結果**:
- ✅ V2 選項被禁用或隱藏
- ✅ 無法切換到 V2

---

### 測試 7: 效能比較

**目標**: 比較 V1 和 V2 的效能差異

**步驟**:
1. 開啟 Chrome DevTools Performance 標籤
2. 使用 V1，記錄以下操作的時間：
   - 載入寵物列表
   - 搜尋寵物
   - 載入寵物詳情
3. 切換到 V2，重複相同操作
4. 比較結果

**預期結果**:
- ✅ V2 性能應該相近或更好
- ✅ 沒有明顯的效能退化

---

### 測試 8: 開發者工具檢查

**目標**: 驗證沒有 Console 錯誤或警告

**步驟**:
1. 開啟 Console
2. 清除所有訊息
3. 執行各種操作
4. 切換版本

**預期結果**:
- ✅ 沒有紅色錯誤（除了預期的認證錯誤）
- ✅ 版本切換有清晰的 log 訊息
- ⚠️ 允許的警告：
  - TypeScript 類型檢查警告（開發模式）
  - Vue DevTools 相關訊息

**檢查項目**:
```javascript
// 應該看到這些 log
"API baseURL updated: http://localhost:8000/api/v1"
"API client baseURL updated to: http://localhost:8000/api/v1"
"Switching API from v1 to v2..."
"✅ Switched API from v1 to v2"
```

---

## 自動化測試腳本

可以在 Console 中運行以下腳本進行快速驗證：

```javascript
// 版本切換測試腳本
async function testVersionSwitching() {
  console.log('=== Starting API Version Switching Test ===')
  
  // 1. 檢查當前版本
  const currentVersion = localStorage.getItem('api_version') || 'v1 (default)'
  console.log('1. Current version:', currentVersion)
  
  // 2. 檢查 axios baseURL
  const axiosInstance = window.$axios || axios
  console.log('2. Axios baseURL:', axiosInstance?.defaults?.baseURL)
  
  // 3. 測試切換到 V2
  console.log('3. Switching to V2...')
  localStorage.setItem('api_version', 'v2')
  console.log('   localStorage updated to v2')
  console.log('   Please reload page to apply')
  
  // 4. 驗證 V2 端點可訪問
  try {
    const response = await fetch('http://localhost:8000/api/v2/pets/filters/options')
    console.log('4. V2 API accessible:', response.ok ? '✅ Yes' : '❌ No')
  } catch (error) {
    console.error('4. V2 API check failed:', error)
  }
  
  console.log('=== Test Complete ===')
  console.log('Reload page to see V2 in action')
}

// 執行測試
testVersionSwitching()
```

## 問題排除

### 問題 1: 切換後還是使用舊版本

**解決方法**:
```javascript
// 清除快取並重試
localStorage.clear()
location.reload()
```

### 問題 2: API 請求失敗

**檢查**:
1. 後端是否運行: `curl http://localhost:8000/api/v2/`
2. CORS 設定是否正確
3. 網路面板查看實際請求 URL

### 問題 3: 版本按鈕不顯示

**檢查**:
1. 是否在開發模式: `import.meta.env.DEV === true`
2. 組件是否正確導入
3. Console 是否有錯誤

### 問題 4: TypeScript 編譯錯誤

**暫時解決**:
```typescript
// 在 AppHeader.vue 中，如果 isDevelopment 報錯
// 改用這種方式：
const isDevelopment = import.meta.env.DEV
```

## 測試檢查清單

完成以下檢查清單以確保功能完整：

### 基礎功能
- [ ] ✅ 預設使用 V1
- [ ] ✅ 可以切換到 V2
- [ ] ✅ 可以切換回 V1
- [ ] ✅ 版本持久化（重新載入保持）
- [ ] ✅ UI 正確顯示當前版本

### V2 API 完整性
- [ ] ✅ Pets 模組所有端點工作正常
- [ ] ✅ Adoptions 模組所有端點工作正常
- [ ] ✅ Notifications 模組所有端點工作正常
- [ ] ✅ Chat 模組所有端點工作正常
- [ ] ✅ Community 模組所有端點工作正常

### 錯誤處理
- [ ] ✅ 網路錯誤有適當提示
- [ ] ✅ 認證錯誤正確處理
- [ ] ✅ 切換失敗有錯誤訊息
- [ ] ✅ 後端不可用時不崩潰

### 開發體驗
- [ ] ✅ 沒有 Console 錯誤
- [ ] ✅ 版本切換有清晰的 log
- [ ] ✅ TypeScript 類型檢查通過
- [ ] ✅ 文檔完整清晰

## 測試報告範本

```markdown
# API Version Switching Test Report

**測試日期**: 2025-11-25
**測試人員**: [Your Name]
**環境**: Development

## 測試結果

### 基礎功能測試
- ✅ 預設版本: PASSED
- ✅ 切換到 V2: PASSED
- ✅ 切換回 V1: PASSED
- ✅ 持久化: PASSED

### V2 功能測試
- ✅ Pets: PASSED
- ✅ Adoptions: PASSED
- ✅ Notifications: PASSED
- ✅ Chat: PASSED
- ✅ Community: PASSED

### 發現的問題
1. [描述問題]
   - 嚴重程度: Low/Medium/High
   - 重現步驟: [...]
   - 預期結果: [...]
   - 實際結果: [...]

## 總結
[整體評估和建議]
```

## 下一步

完成測試後：
1. ✅ 記錄所有發現的問題
2. ✅ 更新文檔
3. ✅ 準備生產環境配置
4. ✅ 規劃完整遷移到 V2 的時程

---

**維護者**: Frontend Team  
**最後更新**: 2025-11-25  
**版本**: 1.0
