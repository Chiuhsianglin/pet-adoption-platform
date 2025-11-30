# API Version Switching Guide

## 概述

本專案前端支援動態切換 API 版本（V1 和 V2），讓開發者和測試人員可以輕鬆在兩個版本之間切換，以便進行測試、比較和逐步遷移。

## 架構說明

### V1 API（穩定版本）
- **路徑**: `/api/v1/*`
- **架構**: 原始 Active Record 模式
- **狀態**: 穩定運行，所有功能完整

### V2 API（新架構）
- **路徬**: `/api/v2/*`
- **架構**: Controller → Service → Repository 三層架構
- **優勢**: 
  - 程式碼量減少 82%
  - 更好的可維護性
  - 清晰的關注點分離
  - 更容易測試

## 功能特性

### 1. 自動版本管理
- ✅ 從環境變數讀取預設版本
- ✅ 支援 localStorage 持久化用戶選擇
- ✅ 自動更新 Axios baseURL
- ✅ 頁面重新載入時保持版本設定

### 2. UI 切換組件
- ✅ 視覺化版本切換按鈕
- ✅ 顯示當前使用版本
- ✅ 顯示當前 API baseURL
- ✅ 切換時自動重新載入頁面

### 3. 程式化 API
- ✅ `useApiVersion()` composable
- ✅ 版本切換監聽器
- ✅ 完整的 TypeScript 類型支援

## 安裝與配置

### 1. 環境變數設定

在專案根目錄建立 `.env` 文件：

```bash
# API 基礎 URL（不包含版本號）
VITE_API_BASE_URL=http://localhost:8000

# 預設 API 版本 (v1 或 v2)
VITE_API_VERSION=v1

# 是否啟用 V2 API 選項
VITE_V2_ENABLED=true

# API 請求超時時間（毫秒）
VITE_API_TIMEOUT=30000
```

### 2. 配置優先順序

系統按以下優先順序決定使用哪個 API 版本：

1. **localStorage** - 用戶手動切換的版本（最高優先級）
2. **環境變數** - `VITE_API_VERSION` 設定
3. **預設值** - V1（如果以上都未設定）

## 使用方法

### 方法 1：使用 UI 組件切換

1. 在需要的地方引入 `ApiVersionSwitcher` 組件：

```vue
<template>
  <v-app-bar>
    <!-- 其他內容 -->
    <ApiVersionSwitcher />
  </v-app-bar>
</template>

<script setup lang="ts">
import ApiVersionSwitcher from '@/components/ApiVersionSwitcher.vue'
</script>
```

2. 點擊按鈕即可在 V1 和 V2 之間切換
3. 切換後頁面會自動重新載入

### 方法 2：程式化切換

在任何組件中使用 `useApiVersion` composable：

```typescript
import { useApiVersion } from '@/composables/useApiVersion'

// 在 setup 中
const { 
  currentVersion,   // 當前版本 (reactive)
  apiBaseURL,       // 當前 API URL (computed)
  isV2,             // 是否使用 V2 (computed)
  v2Supported,      // 是否支援 V2 (computed)
  isSwitching,      // 是否正在切換 (reactive)
  switchToV1,       // 切換到 V1
  switchToV2,       // 切換到 V2
  switchVersion,    // 切換到指定版本
} = useApiVersion()

// 切換到 V2
await switchToV2()

// 切換到 V1
await switchToV1()

// 或指定版本
await switchVersion('v2')
```

### 方法 3：監聽版本切換事件

```typescript
import { useApiVersion } from '@/composables/useApiVersion'

const { onVersionSwitch } = useApiVersion()

// 註冊監聽器
const unregister = onVersionSwitch(async (newVersion) => {
  console.log(`API version changed to: ${newVersion}`)
  // 執行版本切換後的操作
  // 例如：清除快取、重新載入數據等
})

// 在組件卸載時取消註冊
onUnmounted(() => {
  unregister()
})
```

## 開發指南

### 1. 新增 API 端點時的考量

當新增或修改 API 端點時：

```typescript
// ❌ 不要硬編碼版本號
const response = await api.get('/api/v1/pets')

// ✅ 使用相對路徑，讓系統自動添加版本
const response = await api.get('/pets')

// baseURL 會自動根據當前版本變成：
// V1: http://localhost:8000/api/v1/pets
// V2: http://localhost:8000/api/v2/pets
```

### 2. 測試不同版本

```bash
# 測試 V1
localStorage.setItem('api_version', 'v1')
# 重新載入頁面

# 測試 V2
localStorage.setItem('api_version', 'v2')
# 重新載入頁面
```

### 3. 在開發工具中檢查

打開瀏覽器開發者工具 Console：

```javascript
// 查看當前版本資訊
console.log(localStorage.getItem('api_version'))

// 查看完整配置
import { useApiVersion } from '@/composables/useApiVersion'
const { getVersionInfo } = useApiVersion()
console.log(getVersionInfo())
```

## 架構說明

### 核心文件

1. **`src/config/api.ts`**
   - API 版本配置管理
   - baseURL 計算邏輯
   - 版本檢查函數

2. **`src/composables/useApiVersion.ts`**
   - 版本狀態管理
   - 切換邏輯
   - 事件監聽系統

3. **`src/services/api.ts`**
   - Axios 實例配置
   - `updateApiBaseURL()` 函數用於動態更新

4. **`src/components/ApiVersionSwitcher.vue`**
   - UI 切換組件
   - 視覺化版本指示器

5. **`src/main.ts`**
   - 初始化 API 版本監聽
   - 連接版本系統與 Axios 實例

### 工作流程

```
用戶點擊切換按鈕
    ↓
switchToV2() / switchToV1()
    ↓
setApiVersion('v2') → localStorage
    ↓
currentVersion.value = 'v2'
    ↓
watch(apiBaseURL) 觸發
    ↓
updateApiBaseURL() 更新 axios.defaults.baseURL
    ↓
通知所有監聽器
    ↓
頁面重新載入（可選）
```

## 最佳實踐

### 1. 逐步遷移策略

建議按模組逐步從 V1 遷移到 V2：

```typescript
// 階段 1: 只切換 Pets 模組到 V2
// 前端保持 V1，手動測試 Pets V2 端點

// 階段 2: 切換 Adoptions 模組到 V2
// 繼續測試和驗證

// 階段 3: 全面切換到 V2
// 設定 VITE_API_VERSION=v2
```

### 2. 測試檢查清單

- [ ] V1 所有功能正常運作
- [ ] V2 所有功能正常運作
- [ ] 切換過程流暢無錯誤
- [ ] localStorage 持久化正常
- [ ] 頁面重新載入後版本保持
- [ ] 錯誤處理正確
- [ ] 性能無明顯差異

### 3. 除錯提示

如果遇到問題：

```typescript
// 檢查當前配置
import { getApiConfig, getCurrentApiVersion } from '@/config/api'
console.log('Current version:', getCurrentApiVersion())
console.log('API config:', getApiConfig())

// 檢查 axios baseURL
import api from '@/services/api'
console.log('Axios baseURL:', api.defaults.baseURL)

// 清除 localStorage 重置版本
localStorage.removeItem('api_version')
```

## 常見問題

### Q1: 切換版本後某些功能不工作？

**A**: 確認該功能在目標版本中已經實現。V2 API 可能還在開發中，某些端點可能尚未完成。

### Q2: 如何在生產環境禁用版本切換？

**A**: 設定環境變數 `VITE_V2_ENABLED=false`，UI 組件會自動隱藏 V2 選項。

### Q3: 版本切換需要重新登入嗎？

**A**: 不需要。JWT token 儲存在 Pinia store 中，切換版本不會影響認證狀態。

### Q4: 如何知道當前使用的是哪個版本？

**A**: 
1. 查看 UI 切換按鈕的顯示
2. 開啟 Network 工具查看請求 URL
3. Console 輸入 `localStorage.getItem('api_version')`

### Q5: 能否為不同模組使用不同版本？

**A**: 目前不支援。整個應用使用統一的 API 版本。如需此功能，可以擴展 `useApiVersion` composable。

## 效能考量

- **切換成本**: 需要重新載入頁面（~1-2 秒）
- **運行成本**: 無額外性能開銷
- **儲存空間**: localStorage 僅存 2 字節（'v1' 或 'v2'）

## 未來計劃

- [ ] 支援 A/B 測試（部分用戶使用 V2）
- [ ] 版本切換不重新載入頁面（熱切換）
- [ ] 模組級別版本控制
- [ ] 版本使用統計和監控
- [ ] 自動回退機制（V2 失敗時自動切回 V1）

## 參考資料

- [V2 API 開發進度](../backend/V2_API_STATUS.md)
- [後端重構進度](../backend/REFACTORING_PROGRESS.md)
- [V2 API 測試指南](../backend/V2_API_TESTING.md)

## 更新日誌

### 2025-11-25
- ✅ 建立完整的 API 版本切換系統
- ✅ 實現 `useApiVersion` composable
- ✅ 建立 `ApiVersionSwitcher` UI 組件
- ✅ 更新環境變數配置
- ✅ 撰寫完整文檔

---

**維護者**: Backend Team  
**最後更新**: 2025-11-25  
**狀態**: ✅ 完成並可用
