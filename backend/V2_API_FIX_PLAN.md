# V2 API 修復計劃

## 問題分析

V2 API 無法啟動，原因：
- `PetCreate`, `PetUpdate`, `PetResponse` 等schema未定義
- V1 API 使用直接序列化dict，不使用Pydantic models
- refactored 檔案是基於假設的schema結構建立的

## 解決方案

### 方案 1：簡化 V2 API（推薦）
將 V2 API 改為使用 dict 而非 Pydantic models，與 V1 保持一致：
- 移除所有 `response_model` 參數
- 使用 `Dict[str, Any]` 作為返回類型
- 參數使用 `dict` 或現有的簡單schema

**優勢**：
- 快速部署
- 與現有V1 API完全兼容
- 不需要建立大量schema

### 方案 2：完整建立所有schema
為每個模組建立完整的Pydantic schema：
- PetCreate, PetUpdate for pets
- AdoptionCreate, AdoptionUpdate for adoptions
- 等等...

**劣勢**：
- 耗時
- 需要與V1保持同步
- 可能引入更多bugs

## 立即行動

採用方案1，步驟：
1. 重寫 v2 API 檔案，移除Pydantic schema依賴
2. 使用 service 層返回的 ORM objects直接序列化
3. 保持 service 層不變（已經完成且正確）

## 快速修復腳本

建立一個簡化的 v2 pets API：
- 只保留核心端點（list, get, search）
- 使用 dict 返回
- 驗證 service 層工作正常

然後逐步擴展到其他模組。
