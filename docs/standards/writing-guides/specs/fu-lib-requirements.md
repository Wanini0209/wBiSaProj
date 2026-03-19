# Library Functional Unit (FU) Specs - Requirements Guide

本規範定義 Library 型 **Functional Unit (FU)** 在 `specs` 層級的 `requirements.md` 撰寫規範。目標是定義 Functional Unit 的能力、行為與驗收標準，作為驗收測試的依據。

*供 Generator: Prompt4NewLibFuReqSpec 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

僅定義能力、行為與驗收標準，不包含具體 API 簽章 (Signature) 或實作檔名 (這些屬於 `design.md`)。此文件是驗收測試 (Acceptance Testing) 的唯一依據。

### 1.2 關鍵特性

- **結構對應 (Structural Correspondence)**：路徑必須為 `docs/specs/<fu_path>/<fu_name>/requirements.md`。
- **依賴邊界 (Boundary Control)**：必須明確列出允許使用的外部依賴，防止依賴膨脹。
- **可追溯性 (Traceability)**：必須連結回 Design 文件與 Feature。
- **可測試性 (Testability)**：每個需求都必須有對應的驗收條件與測試案例 ID。

---

## 2. 檔案路徑標準

`docs/specs/<fu_path>/<fu_name>/requirements.md`

- `<fu_path>`: FU Container 路徑 (e.g., `wutils/io`)
- `<fu_name>`: FU 名稱 (e.g., `pickle-io`)

---

## 3. ID 命名規範

> **⚠️ 重要**：以下 ID 格式為全專案統一規範，必須嚴格遵守。

### 3.1 本文件定義 ID

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `REQ-LOGIC-XX` | Core Logic Requirement（兩位數流水號） | §4.1 核心邏輯 |
| `REQ-VAL-XX` | Validation Requirement（兩位數流水號） | §4.2 驗證與約束 |
| `NFR-XX` | Non-Functional Requirement（兩位數流水號） | §6 非功能需求 |
| `CONS-XX` | Architectural Constraint（兩位數流水號） | §7 架構約束 |

### 3.2 引用 ID（來自 Feature design.md）

本文件引用上游 Feature 設計文件的版本號進行追溯，不直接引用其內部 ID。

---

## 4. 內容結構模板

````markdown
# <FU Name> - Requirements Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `<fu_name>` |
| **Container Path** | `<fu_path>` |
| **Parent Feature** | `<feature_name>` |
| **Public Interface** | `<fu_path>` (`__init__.py`) |
| **Exports** | `<Component_1>`, `<Component_2>`, ... |
| **Layer** | Library (No Business Dependencies) |

### 1.2 目的 (Purpose)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 簡述此 FU 的技術職責與價值主張。
>
> **💡 範例**：
>
> 「封裝 pickle 操作以確保資源安全並減少 boilerplate code。」

<填入目的描述>

### 1.3 依賴盤點 (Dependencies)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 明確列出本 FU 所需的標準庫與第三方套件依賴。
> - **Type**：
>   - `Std` (標準庫)
>   - `3rd-party` (第三方套件，需標註是否已審核)
>   - **`Local` (專案內其他 Library 或同 Library 內的 FU)**
>
> - **Local 限制**：若使用 `Local`，僅限依賴同級或更底層的 Library (如 `core` 可依賴 `wutils`)，**嚴禁** 依賴 `businesssys` 或 `datasource` 層。
>
> **💡 範例**：
>
> | Package | Type | Purpose |
> | :--- | :--- | :--- |
> | `pickle` | Std | 核心序列化邏輯 |
> | `pathlib` | Std | 路徑物件支援 |
> | `pydantic` | 3rd-party | (需審核) 用於複雜資料驗證 |

| Package | Type | Purpose |
| :--- | :--- | :--- |
| <套件名稱> | <Std / 3rd-party / Local> | <填入用途> |

## 2. 變更歷史 (Change History)

> **📝 撰寫指引**：
> 記錄版本變更。基於「FU 單一驅動原則」，此 FU 永遠隸屬於 Metadata 中定義的 `Parent Feature`。
> 因此，此處的 `Source` 欄位不需重複填寫 Feature 名稱，而是明確指出是該 Parent Feature 的**哪一個版本 (Version)** 或是哪一個具體的 **Task ID** 驅動了此次變更。
>
> **Source 格式**：`Feature vX.Y.Z` 或 `Task: <Task_ID>`
>
> **💡 範例**：
>
> | Version | Date | Description | Source |
> | :--- | :--- | :--- | :--- |
> | v1.0.0 | 2024-01-15 | Initial Release (Basic Dump/Load) | Feature v1.0.0 |
> | v1.1.0 | 2024-02-01 | Add pathlib support | Feature v1.1.0 |
> | v1.1.1 | 2024-02-10 | Fix file handle leak | Task: TASK-452 |

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | <YYYY-MM-DD> | <變更描述> | <填入 Feature 版本或 Task ID> |

## 3. 匯出能力 (Exported Capabilities)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義本單元必須透過 Container (`__init__.py`) 公開的功能。
> - 描述**功能目標**而非實作細節（API 簽章應在 Design 階段定義）。
> - 必須示範從 Container 導入 (`from <fu_path> import ...`)。
> - 禁止導入私有模組 (`_module.py`)。

### 3.1 匯出清單 (Export List)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出 `__init__.py` 中的 `__all__` 預期匯出項目，這是 FU Container 對外公開的完整清單。
>
> **💡 範例**：
>
> ```python
> __all__ = ["pickle_dump", "pickle_load"]
> ```

```python
__all__ = ["<Component_1>", "<Component_2>", "..."]
```

### 3.2 能力定義 (Capability Definitions)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 以描述性方式定義每個匯出能力的目標與關鍵行為。
>
> **💡 範例**：
>
> #### 3.2.1 序列化寫入 (Dump)
>
> - **功能目標**: 將 Python 物件序列化並寫入檔案。
> - **關鍵輸入**: 任意 Python 物件、目標路徑 (支援 `str` 與 `Path`)。
> - **關鍵輸出**: 無 (檔案寫入成功)。
> - **關鍵行為**: 自動管理檔案開關 (Context Manager)。
>
> #### 3.2.2 反序列化讀取 (Load)
>
> - **功能目標**: 從檔案讀取並還原 Python 物件。
> - **關鍵輸入**: 來源路徑 (支援 `str` 與 `Path`)。
> - **關鍵輸出**: 還原的 Python 物件。
> - **關鍵行為**: 自動管理檔案開關 (Context Manager)。

#### 3.2.1 [能力名稱]

- **功能目標**: <填入此能力要達成的目標>
- **關鍵輸入**: <填入輸入參數與支援的類型>
- **關鍵輸出**: <填入回傳值或副作用>
- **關鍵行為**: <填入重要的行為特性>

### 3.3 使用範例 (Usage Examples)

> **📝 撰寫指引**（請勿保留本指引文字）：
> **Developer Experience First**：展示如何使用。**注意：此處僅展示「預期的呼叫方式」，參數名稱與型別若非關鍵需求，應保留彈性給 Design 階段決定。**
>
> **💡 範例**：
>
> ```python
> from wutils.io import pickle_dump, pickle_load
>
> # Happy Path: 寫入
> pickle_dump({"key": "value"}, "data.pkl")
>
> # Happy Path: 讀取
> data = pickle_load("data.pkl")
> ```

```python
from <fu_path> import <ExportedClass>, <exported_function>

# <填入使用情境描述>
<填入使用範例>
```

## 4. 功能需求 (Functional Requirements)

### 4.1 核心邏輯 (Core Logic)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 描述核心業務或技術邏輯。
> - **ID 規範**：`REQ-LOGIC-XX`（兩位數流水號）。
> - 每個需求必須有明確的驗收條件。
>
> **💡 範例**：
>
> | ID | Description | Acceptance Criteria |
> | :--- | :--- | :--- |
> | **REQ-LOGIC-01** | 使用 Context Manager 開啟檔案進行寫入操作 | 檔案成功寫入且資源已正確釋放 |
> | **REQ-LOGIC-02** | 支援 `str` 與 `Path` 兩種路徑類型 | 兩種類型輸入皆能正常處理 |

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-LOGIC-XX** | <填入描述> | <填入驗收條件> |

### 4.2 驗證與約束 (Validation)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 描述輸入驗證邏輯與約束條件。
> - **ID 規範**：`REQ-VAL-XX`（兩位數流水號）。
>
> **💡 範例**：
>
> | ID | Description | Acceptance Criteria |
> | :--- | :--- | :--- |
> | **REQ-VAL-01** | 檢查路徑參數不得為空字串 | 傳入空字串時拋出 `ValueError` |
> | **REQ-VAL-02** | 檢查物件必須可序列化 | 傳入不可序列化物件時拋出 `TypeError` |

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-VAL-XX** | <填入驗證規則> | <填入驗收條件> |

## 5. 異常處理 (Exception Handling)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義例外類型與處理策略。
>
> **策略選項**：
> - **透傳 (Propagate)**：Library 不應吞噬此錯誤，直接向上傳遞。
> - **封裝 (Wrap)**：捕獲後包裝為自訂例外再拋出。
> - **吞噬 (Swallow)**：捕獲後不再拋出（需謹慎使用）。
> - **混合 (Mixed)**：依據不同例外類型採用不同策略。
>
> **追溯要求**：
> - **關聯需求 (REQ Ref)**：追溯到對應的 REQ ID，確保錯誤行為可驗收。
>
> **💡 範例**：
>
> | Exception | Trigger | Strategy | Ref |
> | :--- | :--- | :--- | :--- |
> | `FileNotFoundError` | 讀取不存在的路徑 | **透傳 (Propagate)** | **REQ-LOGIC-02** |
> | `TypeError` | 輸入不可序列化物件 | **透傳 (Propagate)** | **REQ-VAL-02** |
> | `PermissionError` | 無檔案寫入權限 | **透傳 (Propagate)** | **REQ-LOGIC-01** |

| Exception | Trigger | Strategy | Ref |
| :--- | :--- | :--- | :--- |
| <例外類型> | <觸發情境> | <處理策略> | **REQ-XX** |

## 6. 非功能需求 (Non-Functional Requirements) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義效能、環境、型別安全等非功能需求。若無特殊需求，可省略本章節。
> - **ID 規範**：`NFR-XX`（兩位數流水號）。
> - 需追溯到專案級 NFR (PNFR) 或 Feature 級 NFR。
>
> **💡 範例**：
>
> | ID | Category | Description | Traceability |
> | :--- | :--- | :--- | :--- |
> | **NFR-01** | Environment | Python 3.12+ | **Ref: PNFR-ENV-01** |
> | **NFR-02** | Type Safety | 100% Type Hint Coverage | **Ref: PNFR-CDE-01** |
> | **NFR-03** | Complexity | Core algorithm: O(1) | **Ref: Feature NFR-01** |

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-XX** | <類別> | <填入需求描述> | <來源> |

## 7. 架構約束 (Architectural Constraints)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義實作時必須遵守的架構限制。
> - **ID 規範**：`CONS-XX`（兩位數流水號）。
> - **合規說明 (Compliance Note)**：補充說明該約束在本 FU 的具體意義。
>
> **💡 範例**：
>
> | ID | Constraint | Notes |
> | :--- | :--- | :--- |
> | **CONS-01** | **Isolation**: 禁止依賴 `businesssys` 或 `datasource` 層。 | 本工具為 Library 元件，嚴禁反向依賴業務邏輯 |
> | **CONS-02** | **Encapsulation**: 實作檔必須位於 Feature 級私有目錄 (`_<feature_snake_name>/`) 內。 | 強制透過 Container 匯出，避免直接依賴實作細節，並確保私有檔案與 Feature 的歸屬關係 |
> | **CONS-03** | **Dependency**: 僅依賴標準庫。 | 本工具定位為底層 IO，禁止引入任何第三方依賴 |

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-XX** | <填入約束描述> | <填入合規說明> |
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 文件追溯性與元數據
- [ ] **Metadata 一致性**：`Container Path` 與 `Public Interface` 格式正確，且 `Exports` 清單與 §3 定義完全一致？
- [ ] ⚠️ **依賴合規性**：Local 依賴是否嚴格遵守禁止依賴 `businesssys` 或 `datasource` 層的紅線？
- [ ] **變更歷史追溯**：§2 Change History 的 `Source` 欄位是否僅填寫 Parent Feature 的版本號或 Task ID (e.g., `Feature v1.1.0` 或 `Task: TASK-xxx`)，且未冗餘重複 Feature 名稱？

### B. 需求定義品質

- [ ] **匯出能力非實作化**：`Capability Definitions` 是否僅描述「做什麼 (What)」，而非具體的函數簽章 (對應 §3.2)？
- [ ] ⚠️ **封裝導入檢查**：`Usage Examples` 是否完全透過 `<fu_path>` 導入，嚴禁出現導入私有模組 (`_*.py`) 的程式碼 (對應 §3.3)？
- [ ] **驗收條件可測性**：每個 `REQ-LOGIC` 與 `REQ-VAL` 是否都具備具體、可觀察、可驗證的 `Acceptance Criteria` (對應 §4)？

### C. 異常、約束與標準

- [ ] **異常策略標準化**：`Strategy` 描述是否僅限於透傳、封裝、吞噬或混合，並正確追溯至 `REQ-ID` (對應 §5)？
- [ ] **非功能需求追溯**：所有的 `NFR` 是否正確追溯至專案級標準，如 `Ref: PNFR-ENV-01` (對應 §6)？
- [ ] **架構約束具體化**：每個 `CONS` 需求是否都有填寫「合規說明 (Notes)」，而非僅有標題 (對應 §7)？

### D. 格式與命名規範

- [ ] **ID 命名規範**：所有 ID（`REQ-LOGIC`, `REQ-VAL`, `NFR`, `CONS`）是否嚴格遵守兩位數流水號 (`-XX`) 格式 (對應 §4, §5, §6, §7)？

### E. 最終清理

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
