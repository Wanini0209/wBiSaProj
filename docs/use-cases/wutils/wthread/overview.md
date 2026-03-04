# Feature Overview: wutils/wthread

## 1. Context (上下文)

- **Library**: `wutils` (Project-Level Library)
- **Scope Type**: `Toolkit`
- **Scope Name**: `wthread`
- **Description**: 增強 Python 標準並發庫的功能，提供更安全的執行緒生命週期管理、結果獲取與例外傳遞機制，防止並發環境下的靜默失敗 (Silent Failure)。

## 2. Feature Catalog (功能清單)

| Feature Name | Value / Goal | Status | Link |
|:-------------|:-------------|:-------|:-----|
| `future-thread` | 提供可獲取回傳值並自動傳遞子執行緒例外的增強版 Thread 類別 | Released | [→](./future-thread/) |

## 3. Decision Guide (決策指引)

### 3.1 修改既有 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 調整 `FutureThread` 的狀態檢查邏輯 (Guard Clauses) | 修改 `future-thread` Feature |
| 增加 `FutureThread` 的屬性 (如執行時間統計) | 修改 `future-thread` Feature |
| 調整 `get_result` 的超時 (Timeout) 行為 | 修改 `future-thread` Feature |

### 3.2 需要新增 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 管理一組執行緒的資源池 (Thread Pool) | 新增 `thread-pool` Feature |
| 實作讀寫鎖 (Read-Write Lock) 機制 | 新增 `rw-lock` Feature |
| 實作跨執行緒的事件發布/訂閱機制 | 新增 `event-bus` Feature |

### 3.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| 「在背景執行定時任務 (Cron Job)」 | **業務系統的 ETL 或 Scheduler** | `wthread` 僅提供底層並發原語 (Primitives)，不包含任務排程與業務流程編排。 |
| 「使用 Process 進行平行運算」 | 新增 `wprocess` Toolkit | `wthread` 專注於執行緒 (Thread) 層級，跨進程 (Process) 屬於不同的技術範疇。 |
