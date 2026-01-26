# Project Core Architecture Overview

## 1. Library Identity (函式庫識別)

### 1.1 基本資料 (Basic Info)

- **Library Name**: `core`
- **Library Full Name**: `Project-Level Core Library`
- **Library Type**: `Project-Level Library`

### 1.2 願景與邊界 (Vision & Scope)

- **Core Vision (核心願景)**:
    作為專案的「契約定義層 (Contract Definition Layer)」與「共用語言層」，提供跨系統共用的抽象介面 (Interfaces)、資料模型 (Schemas) 與常數 (Constants)，確保業務系統與資料源系統之間的解耦與標準化通訊。
- **Out of Scope (非目標範圍)**:
    - **不包含通用工具**：與專案業務無關的通用邏輯（如字串處理、檔案 I/O、通用驗證規則）應歸屬於 `wutils`。
    - **不包含實作細節**：嚴禁包含任何 Repository 或 Service 的具體實作邏輯（應位於各系統中）。
    - **不依賴上層系統**：嚴禁依賴任何 `businesssys` 或 `datasource`。
- **Dependency Position (依賴定位)**:
    位於依賴鏈的 Level 1，僅依賴 `wutils`，並被專案中所有業務系統與資料源系統依賴。

## 2. Toolkit Structure (工具集結構)

> **快速導覽**：本函式庫包含以下 Toolkit：
>
> ```text
> core/
> ├── interfaces/ → 定義 Repository 與 Provider 的抽象契約，實現依賴反轉 (DIP)。
> ├── schemas/    → 定義跨系統共用的 Pydantic Models、DTOs 與結構化資料容器。
> └── constants/  → 定義跨系統共用的純粹常數與 Enums。
> ```

### 2.1 Toolkit: `interfaces`

- **Structure**:

    ```text
    interfaces/
    └── (No Sub-toolkits, Flat Structure)
    ```

- **Responsibility**: 定義所有跨系統交互的抽象契約 (Abstract Base Classes / Protocols)，作為業務系統與資料源系統之間的解耦介面。
- **Boundary Rules**:
    - **Includes**: Repository 介面定義 (e.g., `IStockPriceRepository`)、資料提供者介面 (e.g., `IMarketDataProvider`)、跨系統服務介面。
    - **Excludes**: 任何具體的函式實作、資料庫連線邏輯、外部 API 呼叫邏輯。
- **Sub-toolkits**: (無)

### 2.2 Toolkit: `schemas`

- **Structure**:

    ```text
    schemas/
    └── (No Sub-toolkits, Flat Structure)
    ```

- **Responsibility**: 提供專案級標準化的資料模型與基礎型別，確保跨系統資料交換時的格式一致性與型別安全。
- **Boundary Rules**:
    - **Includes**: 跨系統共用的 Pydantic Models、dataclass / frozen dataclass、NamedTuple、以及與結構緊密耦合的靜態實例容器 (Static Instance Containers)。
    - **Excludes**: 僅在單一系統內部使用的資料模型（應位於 `<system>/core/schemas` 或 FU 內部）、通用資料類型的驗證邏輯（應位於 `wutils`）。
- **Sub-toolkits**: (無)

### 2.3 Toolkit: `constants`

- **Structure**:

    ```text
    constants/
    └── (No Sub-toolkits, Flat Structure)
    ```

- **Responsibility**: 集中管理跨系統共用的常數定義，避免魔術數字 (Magic Numbers) 與字串硬編碼 (Hard-coding)。
- **Boundary Rules**:
    - **Includes**: 跨系統共用的 Enums (如 `MarketType`, `Currency`)、格式字串 (如日期格式模板)、全域數值常數。
    - **Excludes**: 包含複雜邏輯的方法、特定系統內部的設定值 (Config)。
- **Sub-toolkits**: (無)

## 3. Technology Constraints (技術限制)

- **Python Version**: `>=3.12`
- **Internal Dependencies (專案內依賴)**:
    - **Allowed**: `wutils`。
    - **Prohibited**: 所有業務系統 (`businesssys`)、所有資料源系統 (`datasource`)，以防止循環依賴。
- **External Dependencies (第三方依賴)**:
    - **Allowed**: Python 標準庫、`pydantic` (用於定義 Schemas)。
    - **Approval Required**: 任何其他第三方套件需經嚴格審查，原則上 `core` 應保持依賴極簡。
- **Type Safety**: 100% Type Hint Coverage (Strict Mode)

## 4. Internal Toolkit Dependencies (庫內工具集依賴)

| 依賴關係 | 說明 |
|:---------|:-----|
| `interfaces` → `schemas` | 抽象介面中的方法簽章 (Method Signatures) 需要參照 `schemas` 中定義的標準資料模型作為輸入參數或回傳值型別。 |
| `interfaces` → `constants` | 抽象介面可能直接使用 `constants` 中的 Enum 作為參數（例如指定市場類型）。 |
| `schemas` → `constants` | 資料模型的欄位可能使用 `constants` 中的 Enum 作為型別；靜態實例容器可能使用 Enum 值或其他常數作為建構參數。 |
