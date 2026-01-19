# Project-Level Library Architecture Overview - Documentation Guide

本規範定義 **Project-Level Library (專案級函式庫)** 的 `LIBRARY_OVERVIEW.md` 撰寫規範。目標是定義函式庫的 **邊界 (Boundaries)**、**工具集職責 (Toolkit Responsibilities)** 與 **架構限制 (Constraints)**，作為 System Analyst (LLM) 執行需求分析與架構設計時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範適用於 **專案級函式庫** (如 `wutils`, `core`)。業務系統請參閱 `sys-biz-overview.md`，資料源系統請參閱 `sys-ds-overview.md`。

*供 Generator: Prompt4LibraryOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是專案級函式庫的「憲法」。它不描述具體功能的實作細節，而是定義「提供什麼能力」、「不提供什麼」、以及「各工具集的職責劃分」。

### 1.2 關鍵特性

- **單一真理來源 (SSOT)**：所有 Toolkit 的歸屬判定與技術選型均以此文件為最高指導原則。
- **邊界優先 (Boundary First)**：必須明確定義「非目標範圍 (Out of Scope)」與「排除規則 (Excludes)」，以防止架構腐化。
- **能力導向 (Capability Oriented)**：以「提供什麼能力」而非「如何實作」來組織 Toolkit。

### 1.3 與 System Core 的差異

| 面向 | System Core (`<system>/core`) | Project-Level Library |
|:-----|:-------------------------|:----------------------|
| **範圍** | 單一系統專用 | 全專案共用 |
| **典型深度** | 1-3 層 | 1-4 層 |
| **結構複雜度** | 較簡單，通常扁平 | 較複雜，可能有深層巢狀 |
| **文件結構** | 全部使用縮排清單 | 前兩層使用標題，第三層以下使用縮排清單 |

> **設計原則**：由於專案級函式庫的範圍較大、結構較深，前兩層 Toolkit 使用 `##`/`###` 標題提供明確的導航錨點，第三層以下則使用縮排清單保持文件可讀性。

---

## 2. 檔案路徑標準

`docs/architecture/<library>_overview.md`

- `<library>`: 函式庫名稱 (e.g., `wutils`, `core`)。

---

## 3. 命名規範 (Naming Conventions)

> **⚠️ 重要**：請嚴格遵守以下命名規範，以確保 Python 套件結構的合法性與一致性。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 5.3 & 8.2*

### 3.1 函式庫與結構命名

| 屬性 | 格式規範 | 說明 | 範例 |
|:-----|:---------|:-----|:-----|
| **Library Name** | `[a-z0-9]+` | **函式庫 ID**。全小寫，無任何分隔符號。保持頂層 Namespace 簡潔。 | `wutils`, `core` |
| **Toolkit Name** | `snake_case` | **技術分類名稱**。全小寫，使用底線分隔，嚴禁連字號 (-)。<br>必須是合法的 Python Package Name。<br>必須反映技術解決方案領域。 | ✅ `io`, `data_transform`, `file_io`<br>❌ `file-io` (非法套件名)<br>❌ `common`, `utils` (禁止模糊命名) |
| **Sub-toolkit Name** | `snake_case` | 同 Toolkit Name 規範。 | `csv`, `parquet`, `network` |

---

## 4. 內容結構模板

````markdown
# Library Architecture Overview

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本文件將被用作 Prompt Input 餵給 LLM 進行分析。請確保內容精簡、無歧義，並專注於「定義規則」。

## 1. Library Identity (函式庫識別)

### 1.1 基本資料 (Basic Info)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **Library Name**: 函式庫 ID (對應目錄名稱)。
> - **Library Full Name**: 函式庫全名。
> - **Library Type**: 固定填寫 `Project-Level Library`。
>
> **💡 範例**：
>
> - **Library Name**: `wutils`
> - **Library Full Name**: `W-Project Utilities`
> - **Library Type**: `Project-Level Library`

- **Library Name**: `<library_name>`
- **Library Full Name**: `<library_full_name>`
- **Library Type**: `Project-Level Library`

### 1.2 願景與邊界 (Vision & Scope)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **Core Vision**: 一句話描述函式庫價值，作為功能是否屬於本函式庫的最終判斷依據。
> - **Out of Scope**: **(關鍵)** 明確列出「不做」什麼。這能有效防止 LLM 產生超出函式庫職責的幻覺 (Hallucination)。
> - **Dependency Position**: 說明此函式庫在依賴鏈中的位置與限制。
>
> **💡 範例**：
>
> - **Core Vision**: 提供通用的 Python 開發工具集，簡化常見的 I/O、資料處理與日誌記錄任務。
> - **Out of Scope**:
>     - 不涉及業務邏輯實作。
>     - 不涉及特定系統的領域概念。
>     - 不依賴專案內其他任何套件。
> - **Dependency Position**: 位於依賴鏈最底層，不依賴專案內任何其他套件。

- **Core Vision (核心願景)**:
    <一句話描述函式庫的核心價值與定位>
- **Out of Scope (非目標範圍)**:
    - <明確列出不做的功能>
- **Dependency Position (依賴定位)**:
    <說明此函式庫在依賴鏈中的位置>

## 2. Toolkit Structure (工具集結構)

> **📝 總體撰寫指引**（請勿保留本指引文字）：
> 本節定義了函式庫的工具集邊界與職責。這是 **System Analyst (LLM)** 執行 **「工具集歸屬判定 (Toolkit Ownership Check)」** 時的 **唯一真理來源 (SSOT)**。
>
> **⚠️ 結構層級處理原則**：
>
> | 層級 | 處理方式 | 說明 |
> |:-----|:---------|:-----|
> | **L1 Toolkit** (頂層) | `## 2.x Toolkit: xxx` | 作為主要導航錨點 |
> | **L2 Sub-toolkit** (次層) | `### 2.x.x Sub-toolkit: xxx` | 保持視覺層級一致性 |
> | **L3+ Sub-toolkit** (深層) | 縮排清單 | 避免標題層級過深，保持可讀性 |
>
> **⚠️ 每個 Toolkit 區塊必須包含**：
> 1. **Structure**: 該 Toolkit 的目錄結構圖 (ASCII Tree)
> 2. **Responsibility**: 核心職責與關鍵能力描述
> 3. **Boundary Rules**: 包含 (Includes) 與排除 (Excludes) 規則
> 4. **Sub-toolkits**: 若有子工具集，列出其職責定義

> **快速導覽**：本函式庫包含以下 Toolkit：
>
> ```text
> <library>/
> ├── <toolkit_A>/    → <一句話職責描述>
> ├── <toolkit_B>/    → <一句話職責描述>
> └── <toolkit_C>/    → <一句話職責描述>
> ```

### 2.1 Toolkit: `<toolkit_name>`

> **📝 撰寫指引**：
> - **Structure**: 展示該 Toolkit 的完整目錄結構。
> - **Responsibility**: 應具體描述其提供的**關鍵能力 (Key Capabilities)**，例如：「提供 CSV/Parquet 格式的讀寫與 Schema 驗證能力」而非僅寫「負責檔案處理」。
> - **Boundary Rules**: 明確定義包含與排除範圍，協助判斷新功能歸屬。
> - **Sub-toolkits**: 若有子工具集，依層級深度使用 `###` 標題或縮排清單。
>
> **💡 範例 (淺層結構，1-2 層)**：
>
> ### 2.1 Toolkit: `logging`
>
> - **Structure**:
>     ```text
>     logging/
>     ├── formatters/
>     └── handlers/
>     ```
> - **Responsibility**: 提供統一的日誌記錄框架，支援多種輸出格式與目標。
> - **Boundary Rules**:
>     - **Includes**: 日誌格式化、日誌處理器、日誌等級管理。
>     - **Excludes**: 應用層的日誌策略配置（應由各系統自行定義）。
> - **Sub-toolkits**:
>     - `formatters` - 日誌格式化器 (JSON, Plain Text, etc.)
>     - `handlers` - 日誌處理器 (Console, File, Remote, etc.)
>
> **💡 範例 (深層結構，3-4 層)**：
>
> ### 2.2 Toolkit: `io`
>
> - **Structure**:
>     ```text
>     io/
>     ├── file/
>     │   ├── csv/
>     │   └── parquet/
>     └── network/
>         ├── http/
>         └── ftp/
>     ```
> - **Responsibility**: 提供統一的 I/O 操作介面，封裝檔案與網路存取的複雜度。
> - **Boundary Rules**:
>     - **Includes**: 檔案讀寫、網路請求、格式轉換。
>     - **Excludes**: 業務資料的 Schema 定義（應由各系統定義）。
> - **Sub-toolkits**:
>     - **Sub-toolkit**: `file`
>         - **Responsibility**: 檔案讀寫操作的統一介面。
>         - **Sub-toolkits**:
>             - `csv` - CSV 格式的讀寫與驗證
>             - `parquet` - Parquet 格式的讀寫與 Schema 管理
>     - **Sub-toolkit**: `network`
>         - **Responsibility**: 網路請求的封裝與重試機制。
>         - **Sub-toolkits**:
>             - `http` - HTTP/HTTPS 請求封裝
>             - `ftp` - FTP 檔案傳輸封裝

- **Structure**:
    ```text
    <toolkit_name>/
    ├── <sub_toolkit_A>/
    │   └── <sub_sub_toolkit>/
    └── <sub_toolkit_B>/
    ```
- **Responsibility**: <定義核心職責與關鍵能力>
- **Boundary Rules**:
    - **Includes**: <明確定義包含的範圍>
    - **Excludes**: <明確定義排除的範圍>
- **Sub-toolkits**:
    - **Sub-toolkit**: `<sub_toolkit_name>`
        - **Responsibility**: <定義子工具集職責與關鍵能力>
        - **Sub-toolkits** (若有第三層以下):
            - `<sub_sub_toolkit>` - <一句話職責描述>

### 2.2 Toolkit: `<toolkit_name>`

> **📝 撰寫指引**：
> 請完整複製 2.1 的結構進行定義。

- **Structure**:
    ```text
    <toolkit_name>/
    └── ...
    ```
- **Responsibility**: <定義核心職責與關鍵能力>
- **Boundary Rules**:
    - **Includes**: ...
    - **Excludes**: ...
- **Sub-toolkits**: (若無子工具集可省略)
    - ...

## 3. Technology Constraints (技術限制)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節定義函式庫的技術限制與依賴規則。**依賴限制是防止架構腐化的關鍵防線**，必須明確區分「專案內依賴」與「外部依賴」。
>
> **⚠️ 依賴方向原則**：
> - 依賴只能**向下**流動（高層依賴低層），嚴禁反向依賴。
> - 專案依賴鏈：`業務系統` → `core` → `wutils` → (無專案內依賴)
>
> **💡 範例 (wutils)**：
>
> - **Python Version**: `>=3.12`
> - **Internal Dependencies (專案內依賴)**:
>     - **Allowed**: (無，`wutils` 位於依賴鏈最底層)
>     - **Prohibited**: `core`, 任何業務系統, 任何資料源系統
> - **External Dependencies (第三方依賴)**:
>     - **Allowed**: Python 標準庫、已核准清單 (見 `pyproject.toml`)
>     - **Approval Required**: 新增第三方依賴需經架構審查
> - **Type Safety**: 100% Type Hint Coverage (Strict Mode)
>
> **💡 範例 (core)**：
>
> - **Python Version**: `>=3.12`
> - **Internal Dependencies (專案內依賴)**:
>     - **Allowed**: `wutils`
>     - **Prohibited**: 任何業務系統, 任何資料源系統
> - **External Dependencies (第三方依賴)**:
>     - **Allowed**: Python 標準庫、`pydantic`、已核准清單
>     - **Approval Required**: 新增第三方依賴需經架構審查
> - **Type Safety**: 100% Type Hint Coverage (Strict Mode)

- **Python Version**: `<version_requirement>`
- **Internal Dependencies (專案內依賴)**:
    - **Allowed**: <列出允許依賴的專案內套件，若無則填「無」>
    - **Prohibited**: <明確列出禁止依賴的套件，防止循環依賴>
- **External Dependencies (第三方依賴)**:
    - **Allowed**: <列出允許使用的第三方套件類別或清單>
    - **Approval Required**: <說明新增依賴的審查流程>
- **Type Safety**: <Type Hint 要求>

## 4. Internal Toolkit Dependencies (庫內工具集依賴)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節描述函式庫**內部**各 Toolkit 之間的依賴關係。這能顯性化內部耦合，協助 SA 評估變更影響範圍，並在設計新功能時避免引入不當依賴。
>
> **撰寫原則**：
> 1. **聚焦實質依賴**：僅記錄具有實際 import 關係的 Toolkit 組合。
> 2. **標註方向性**：使用箭頭 (`→`) 標示依賴方向，A → B 表示 A 依賴 B。
> 3. **說明依賴原因**：簡述為何需要此依賴，協助後續重構評估。
>
> **⚠️ 設計目標**：
> - 理想狀態是 Toolkit 之間**零耦合**或**單向依賴**。
> - 若出現**雙向依賴 (↔)**，應視為架構 Smell，需評估是否重構。
>
> **💡 範例**：
>
> | 依賴關係 | 說明 |
> |:---------|:-----|
> | `network` → `security` | `network` 的 HTTPS 請求依賴 `security` 提供的 SSL 憑證驗證能力。 |
> | `io/file` → `data_transform` | 檔案讀取後需使用 `data_transform` 進行格式標準化。 |
> | (無) | 本函式庫各 Toolkit 之間無內部依賴。 |
>
> **⚠️ 注意**：
> - 若函式庫各 Toolkit 之間無內部依賴，請明確標註「無」，而非省略此區塊。
> - 此處描述的是 **Toolkit 層級**的依賴，非個別 FU 層級。

| 依賴關係 | 說明 |
|:---------|:-----|
| `<toolkit_a>` → `<toolkit_b>` | <描述 A 依賴 B 的原因與用途> |
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 命名與結構合規性

- [ ] **命名檢查**：Library Name 是否全小寫無分隔？Toolkit/Sub-toolkit 是否為合法 `snake_case`？
- [ ] **結構層級**：是否正確使用 `##`/`###` 標題處理前兩層，第三層以下使用縮排清單？
- [ ] **結構圖一致性**：每個 Toolkit 區塊的 Structure 結構圖是否與 Sub-toolkits 清單一致？

### B. 核心與邊界

- [ ] **快速導覽**：Section 2 開頭是否有頂層結構的快速導覽圖？
- [ ] **職責定義**：每個 Toolkit 的 Responsibility 是否包含具體的「關鍵能力」描述？
- [ ] **邊界規則**：每個 Toolkit 是否都有明確的 Includes 與 Excludes？
- [ ] **負面表列**：Section 1.2 的 `Out of Scope` 是否已明確填寫？

### C. 依賴管理 (防禦性架構)

- [ ] **內部依賴**：Section 3 是否已明確列出 `Allowed` 與 `Prohibited` 的專案內套件？
- [ ] **外部依賴**：是否已定義第三方依賴的審查流程？
- [ ] **庫內依賴**：Section 4 是否已列出 Toolkit 之間的依賴關係？（若無依賴，是否明確標註「無」？）
- [ ] **雙向依賴檢查**：是否有 `↔` 雙向依賴？若有，是否已評估重構必要性？

### D. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的函式庫資訊？
