# FU Overview: wutils/io

## 1. Context (上下文)

- **Library**: `wutils` (Project-Level Library)
- **Layer**: `Toolkit`
- **Scope**: `io`
- **FU-Container Path**: `wutils/io`

## 2. FU Inventory (功能單元清單)

### `json-io`
- **Parent Feature**: `json-io`
- **Responsibility**: 提供原子化的 JSON 檔案讀寫介面，強制 UTF-8 編碼與自動資源管理
- **Components**:
  - `json_dump`
  - `json_load`

### `pickle-io`
- **Parent Feature**: `pickle-io`
- **Responsibility**: 提供原子化的 Pickle 檔案讀寫介面，支援多態路徑處理與自動資源管理
- **Components**:
  - `pickle_dump`
  - `pickle_load`

## 3. Decision Guide (決策指引)

### 3.1 擴充既有 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 新增 JSON 讀寫時的特殊參數支援 (如 `cls` encoder) | 擴充 `json-io` FU (利用 `**kwargs` 透傳) |
| 新增 Pickle 讀寫時的 Protocol 強制性設定 | 擴充 `pickle-io` FU |
| 調整預設的檔案開啟模式或權限設定 | 擴充對應的 IO FU (`json-io` 或 `pickle-io`) |

### 3.2 需要新增 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 提供 CSV 檔案的讀寫與驗證能力 | 新增 `csv-processing` FU |
| 提供 YAML 檔案的讀寫能力 | 新增 `yaml-io` FU |
| 提供純文字檔案 (Text/Log) 的原子化讀寫 | 新增 `text-io` FU |
| 提供二進位檔案 (Binary) 的串流處理 | 新增 `stream-io` FU |

### 3.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| 「在 json-io 中加入特定的 Data Schema 驗證」 | ❌ 禁止 | `wutils/io` 僅負責 I/O 與格式處理，資料驗證邏輯應屬於 `core/validator` 或業務系統層級 |
| 「讀取 S3 上的 JSON 檔案」 | 新增 `network-io` Toolkit 或類似 FU | `wutils/io` 預設關注本地檔案系統操作，涉及網路副作用的操作應隔離 |
