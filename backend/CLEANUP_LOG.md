# 資料表清理記錄

## 第一階段清理（已執行）
執行日期：2025-11-29

### 已刪除的表（無模型定義）
1. **user_behaviors** - 用戶行為記錄
   - 原因：代碼中無對應模型
   - 狀態：✅ 已刪除

2. **pet_statistics** - 寵物統計
   - 原因：代碼中無對應模型
   - 狀態：✅ 已刪除

3. **vaccinations** - 疫苗表
   - 原因：與 vaccination_records 重複，代碼中無對應模型
   - 狀態：✅ 已刪除

---

## 第二階段清理（待評估）
以下表格有模型定義但無 API 實現，建議在確認不需要後再刪除：

### 分析功能相關表
- **daily_metrics** - 每日指標
- **application_timeline** - 申請時間軸  
- **status_transitions** - 狀態轉換記錄
- **audit_logs** - 審計日誌
- **pet_view_logs** - 寵物瀏覽記錄

### 建議
如果確定未來不需要實現以下功能，可以刪除對應的表：
- ❌ 平台數據統計和分析功能 → 刪除分析相關表
- ✅ 保留以便未來擴展 → 保留這些表

---

## 保留的表（有使用中）

### 核心功能表
- ✅ **inquiries** - 詢問功能（V2 已實現）
- ✅ **chat_pet_cards** - 聊天寵物卡片（V2 WebSocket）
- ✅ **password_history** - 密碼歷史（安全功能）
- ✅ **pet_history** - 寵物歷史記錄

### 領養流程相關表（模型存在）
- ⚠️ **vaccination_records** - 預防接種記錄
- ⚠️ **adoption_confirmations** - 領養確認
- ⚠️ **document_requests** - 文件請求
- ⚠️ **application_reviewers** - 申請審核人員
- ⚠️ **application_status_history** - 申請狀態歷史
- ⚠️ **review_comments** - 審核評論
- ⚠️ **review_decisions** - 審核決定

註：⚠️ 標記的表有模型但無 V2 API 實現，建議保留以便未來擴展
