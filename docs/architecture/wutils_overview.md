# Library Architecture Overview

## 1. Library Identity (函式庫識別)

### 1.1 基本資料 (Basic Info)

- **Library Name**: `wutils`
- **Library Full Name**: `Wanini's Python Utilities`
- **Library Type**: `Project-Level Library`

### 1.2 願景與邊界 (Vision & Scope)

- **Core Vision (核心願景)**:
    作為專案的「基礎建設隔離層 (Infrastructure Isolation Layer)」，封裝具有副作用 (Side Effects) 的底層操作（如 I/O、執行緒、網絡），提供統一、安全且易於測試的標準介面，以實現「測試接縫 (Test Seam)」與「升級防火牆 (Upgrade Firewall)」。
- **Out of Scope (非目標範圍)**:
    - **不涉及業務邏輯**：嚴禁包含任何與特定業務領域 (`User`, `Market` 等) 相關的邏輯。
    - **不定義領域模型**：不應定義複雜的資料結構或 Schema。
    - **不依賴上層系統**：嚴禁依賴 `core`、`businesssys` 或 `datasource`。
- **Dependency Position (依賴定位)**:
    位於專案依賴鏈的最底層 (Level 0)，不依賴專案內任何其他套件。

## 2. Toolkit Structure (工具集結構)

> **快速導覽**：本函式庫包含以下 Toolkit：
>
> ```text
> wutils/
> ├── io/         → 提供統一的 I/O 操作介面，封裝資源管理與編碼處理。
> └── wthread/    → 提供增強型的並發原語，解決原生執行緒的結果回傳與異常處理問題。
> ```

### 2.1 Toolkit: `io`

- **Structure**:
    ```text
    io/
    └── (No Sub-toolkits, Flat Structure)
    ```
- **Responsibility**: 提供原子化 (Atomic) 且安全的文件與 I/O 操作介面，強制執行資源管理 (Context Manager) 與編碼規範 (UTF-8)，消除樣板程式碼 (Boilerplate)。
- **Boundary Rules**:
    - **Includes**: 檔案讀寫 (JSON, Pickle, Text)、路徑正規化 (Path/str 兼容)、自動資源釋放。
    - **Excludes**: 業務資料的解析邏輯、資料庫連線、複雜的資料轉換 (Data Transformation)。
- **Sub-toolkits**: (無)

### 2.2 Toolkit: `wthread`

- **Structure**:
    ```text
    wthread/
    └── (No Sub-toolkits, Flat Structure)
    ```
- **Responsibility**: 增強 Python 標準並發庫的功能，提供更安全的執行緒生命週期管理、結果獲取與例外傳遞機制，防止並發環境下的靜默失敗 (Silent Failure)。
- **Boundary Rules**:
    - **Includes**: 執行緒封裝 (FutureThread)、並發結果獲取、跨執行緒例外傳遞。
    - **Excludes**: 複雜的任務排程 (Job Scheduling)、分散式鎖 (Distributed Lock)、業務流程編排。
- **Sub-toolkits**: (無)

## 3. Technology Constraints (技術限制)

- **Python Version**: `>=3.12`
- **Internal Dependencies (專案內依賴)**:
    - **Allowed**: (無) - `wutils` 為最底層函式庫。
    - **Prohibited**: `core`, 所有業務系統 (`businesssys`), 所有資料源系統 (`datasource`)。
- **External Dependencies (第三方依賴)**:
    - **Allowed**: Python 標準庫 (`json`, `pickle`, `threading`, `pathlib`, `typing` 等)。
    - **Approval Required**: 涉及 I/O、網絡或系統操作的第三方套件 (如 `boto3`, `requests`) 必須經過架構審查，且必須被完整封裝，嚴禁洩漏底層型別。
- **Type Safety**: 100% Type Hint Coverage (Strict Mode)

## 4. Internal Toolkit Dependencies (庫內工具集依賴)

| 依賴關係 | 說明 |
|:---------|:-----|
| (無) | 本函式庫目前的 Toolkit (`io`, `wthread`) 之間無相互依賴。 |
