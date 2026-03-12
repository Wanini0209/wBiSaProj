# Feature Overview: wutils/io

## 1. Context (上下文)

- **Library**: `wutils` (Project-Level Library)
- **Scope Type**: `Toolkit`
- **Scope Name**: `io`
- **Description**: 提供原子化 (Atomic) 且安全的文件 I/O 操作介面，強制執行資源管理 (Context Manager) 與編碼規範 (UTF-8)，消除樣板程式碼 (Boilerplate) 並作為 I/O 操作的基礎建設隔離層。

## 2. Feature Catalog (功能清單)

### `json-io`
- **Value / Goal**: 提供標準化的 JSON 讀寫能力，內建 UTF-8 強制編碼與自動資源釋放
- **Owned FUs**: `json-io`
- **Status**: Released

### `pickle-io`
- **Value / Goal**: 提供安全的 Pickle 序列化與反序列化能力，封裝檔案開關與路徑處理細節
- **Owned FUs**: `pickle-io`
- **Status**: Released

## 3. Decision Guide (決策指引)

### 3.1 修改既有 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 調整 JSON 讀寫的預設參數 (如縮排規則) | 修改 `json-io` Feature |
| 調整 Pickle 序列化的預設 Protocol 版本 | 修改 `pickle-io` Feature |
| 擴充現有 I/O 工具對特殊路徑物件的支援 | 修改對應的 `json-io` 或 `pickle-io` Feature |

### 3.2 需要新增 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 讀寫 CSV 檔案並進行基礎格式處理 | 新增 `csv-io` (或 `csv-processing`) Feature |
| 讀寫 Yaml 設定檔 | 新增 `yaml-io` Feature |
| 進行純文字 (Plain Text) 的標準化讀寫 | 新增 `text-io` Feature |
| 處理遠端檔案系統 (如 S3/MinIO) 的存取 | 新增 `s3-io` Feature (需遵循 `wutils` 邊界規則) |

### 3.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| 「解析 JSON 內容並轉換為 Domain Model」 | **業務系統的 Service/Core** | `wutils.io` 僅負責「檔案到記憶體 (Dict/List)」的物理 I/O，不涉及業務邏輯或模型轉換。 |
| 「驗證 JSON 是否符合特定 Schema」 | `wutils/core/validator` (假設存在) | I/O Toolkit 專注於讀寫，資料驗證屬於 Validator Toolkit 的職責。 |
