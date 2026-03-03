# FU Overview: wutils/wthread

## 1. Context (上下文)

- **Library**: `wutils` (Project-Level Library)
- **Layer**: `Toolkit`
- **Scope**: `wthread`
- **FU-Container Path**: `wutils/wthread`

## 2. Layer Constraints (層級限制)

- **Allowed Dependencies**: Python Standard Library (`threading`, `sys`, `typing` etc.)
- **Prohibited Dependencies**: `core`, All Business Systems (`businesssys`), All Data Source Systems (`datasource`)
- **Special Rules**:
    - 嚴禁包含任何與特定業務流程編排相關的邏輯。
    - 必須防止 Thread 內部的 Exception 導致 Silent Failure。

## 3. FU Inventory (功能單元清單)

### `future-thread`
- **Responsibility**: 提供增強型的執行緒類別，封裝執行結果獲取與例外跨執行緒傳遞機制
- **Components**:
  - `FutureThread`
- **Spec**: [→](./future-thread/)

## 4. Decision Guide (決策指引)

### 4.1 擴充既有 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 增加執行緒名稱的自動生成規則 | 擴充 `future-thread` FU |
| 調整執行結果獲取的超時 (Timeout) 預設行為 | 擴充 `future-thread` FU |
| 增加執行緒狀態的回調 (Callback) 機制 | 擴充 `future-thread` FU |

### 4.2 需要新增 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| 提供基於 `concurrent.futures` 的執行緒池封裝 | 新增 `wthread-pool` FU |
| 提供執行緒安全的鎖定機制或同步原語 (如 RWLock) | 新增 `safe-lock` FU |
| 提供週期性的背景任務執行器 | 新增 `periodic-task` FU |

### 4.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| 「實作一個股票報價的即時更新執行緒」 | ❌ 業務系統 | 具體的業務邏輯執行緒應位於 `<system>/service` 或 `<system>/etl`，而非通用工具庫 |
| 「實作分佈式鎖 (Distributed Lock)」 | ❌ 禁止 | `wutils` 關注單機 Python 環境。分佈式鎖涉及外部基礎設施 (Redis/Zookeeper)，應屬於 System Core 或特定 Library |

## 5. Related Resources (相關資源)

- **Architecture Overview**: [→ wutils_overview.md](../../../architecture/wutils_overview.md)
- **Feature Overview**: [→ use-cases/wutils/wthread/overview.md](../../../use-cases/wutils/wthread/overview.md)
