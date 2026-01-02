# Library Feature Use-Cases - Design Guide

本規範定義 Library Feature 的 `design.md` 撰寫規範。目標是定義 **How**（如何實作），連接業務需求與程式碼實作，關鍵在於 API 簽章設計、任務拆解以及需求的可追溯性。

*供 Generator: Prompt4NewLibFtDesignSpec 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件指導如何將 `requirements.md` 轉化為可執行的技術設計。

### 1.2 設計重點

- **高可用性**：API 介面需直觀且易於測試。
- **高強健性**：明確定義異常處理策略與邊界條件。
- **無狀態性**：原則上應設計為 Pure Function 或 Context Manager。

---

## 2. 檔案路徑標準

`docs/use-cases/<library>/<toolkit>/<feature_name>/design.md`

- `<library>`: 函式庫名稱 (e.g., `wutils`, `wsatools`, `core`, `<system>/core`)
- `<toolkit>`: 功能分類 (e.g., `io`, `validator`, `ds/tree`)
- `<feature_name>`: 功能名稱 (e.g., `pickle-io`)

---

## 3. ID 命名規範

> **⚠️ 重要**：以下 ID 格式為全專案統一規範，必須嚴格遵守。

### 3.1 本文件定義 ID

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `Task N` | 任務編號（數字流水號） | §4 任務分解 |

### 3.2 引用 ID（來自 requirements.md）

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `US-XXX` | User Story | §3.2.1 需求覆蓋檢查 |
| `FR-XX` | Functional Requirement | §4 任務分解 |
| `AC-XX` | Acceptance Criteria | §4 任務分解 |
| `NFR-XX` | Non-Functional Requirement | §4 任務分解 |
| `CONS-XX` | Architectural Constraint | §4 任務分解 |

---

## 4. 內容結構模板

````markdown
# <Feature Name> - Design

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `<feature_name>` |
| **Target Library** | `<library>` |
| **Toolkit Category** | `<toolkit>` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 價值主張 (Value Proposition)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請描述以下兩點：
> - **痛點**：描述現狀的不足（如：Boilerplate code 太多、容易出錯）。
> - **效益**：定義功能的預期效益（如：將操作簡化為一行、統一異常處理機制）。
>
> **💡 範例**：
>
> - **痛點 (Pain Point)**：開發者目前需手動處理檔案開關，且 `open()` 未強制 UTF-8，導致不同作業系統間常出現亂碼。
> - **效益 (Benefit)**：提供 Context Manager 自動管理資源，並內建 UTF-8 強制編碼，確保跨平台一致性。

- **痛點 (Pain Point)**：<填入痛點>
- **效益 (Benefit)**：<填入效益>

### 1.3 設計範圍 (Scope)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請明確劃分本次設計的邊界：
> - **In-Scope**：列出本次實作包含的功能邊界。
> - **Out-of-Scope**：明確列出不包含或延後實作的項目。
>
> **💡 範例**：
>
> - **In-Scope**：Pickle 物件序列化/反序列化、自動備份機制。
> - **Out-of-Scope**：加密功能、跨語言序列化格式 (JSON/YAML) 支援。

- **In-Scope**：<填入範圍>
- **Out-of-Scope**：<填入排除項目>

### 1.4 設計來源 (Design Source)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 連結到對應的 Requirements 文件，並標註版本號以確保追溯性。
>
> **版本號格式**：`vX.Y.Z`（語意化版本）
>
> **💡 範例**：
>
> - **Based on**: `requirements.md` v1.0.0
> - **Source Doc**: `docs/use-cases/wutils/io/pickle-io/requirements.md`

- **Based on**: `requirements.md` vX.Y.Z
- **Source Doc**: `docs/use-cases/<library>/<toolkit>/<feature_name>/requirements.md`

## 2. 變更歷史 (Change History)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 記錄版本變更與變更原因，並追溯到對應的 Requirements 版本。
>
> **版本號格式**：`vX.Y.Z`（語意化版本）
>
> **💡 範例**：
>
> | Version | Date | Description | Source |
> | :--- | :--- | :--- | :--- |
> | v1.0.0 | 2024-01-15 | Initial Design | Based on requirements.md v1.0.0 |
> | v1.1.0 | 2024-02-01 | 新增 pathlib 支援（配合 requirements.md v1.1.0）| Based on requirements.md v1.1.0 |

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | <YYYY-MM-DD> | Initial Design | Based on requirements.md v1.0.0 |

## 3. 高階技術設計 (High-Level Design)

本章節定義 Feature 完成後的「最終樣貌」與「整體架構」。

### 3.1 模組架構 (Module Architecture)

#### 3.1.1 目錄結構 (Directory Structure)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請展示 Library 與 Toolkit 層級的套件結構，以及公開介面 (`__init__.py`)。
> **注意**：在此階段無需列出具體的私有實作檔案 (如 `_impl.py`)。
>
> **💡 範例**：
>
> ```text
> <library>/
> └── <toolkit>/
>     └── __init__.py    # Public Interface
> ```

```text
<填入目錄結構>
```

#### 3.1.2 外部依賴矩陣 (Dependency Matrix)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出本功能所需的所有依賴套件：
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
> | `pathlib` | Std | 路徑物件處理 |

| Package | Type | Purpose |
| :--- | :--- | :--- |
| <套件名稱> | <Std / 3rd-party / Local> | <填入用途> |

### 3.2 公開 API 介面設計 (Public API Interface)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請定義以下內容：
> - **Exports Control**：明確定義 `__init__.py` 中的 `__all__` 內容。
> - **API 簽章**：提供開發者視角的「最終公開介面」設計，需含完整 Type Hints 與 Docstring。
>
> **💡 範例**：
>
> ```python
> def pickle_dump(obj: Any, path: PathLike) -> None:
>     """
>     將物件序列化並寫入指定路徑。
>
>     Args:
>         obj: 要序列化的物件
>         path: 目標檔案路徑
>
>     Raises:
>         PermissionError: 當無寫入權限時
>     """
>     ...
> ```

```python
<填入 API 簽章>
```

#### 3.2.1 需求覆蓋檢查 (Requirement Coverage)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 確保每個 User Story 都有對應的 API 進入點。
> - 引用 `requirements.md` 中的 `US-XXX` ID。
>
> **💡 範例**：
>
> | User Story / Req ID | API Mapping |
> | :--- | :--- |
> | **US-001** | `pickle_dump(obj, path)` |
> | **US-002** | `pickle_load(path)` |

| User Story / Req ID | API Mapping |
| :--- | :--- |
| **US-XXX** | <填入對應 API> |

## 4. 任務分解 (Task Breakdown)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 依據 **Feature → Task → Action** 階層拆解。
> - **原則**：一個 Task 對應一個 Functional Unit (FU) 的新增或修改。
> - **粒度**：Task 的描述需足夠具體，足以作為開發者撰寫該 FU 技術規格（Requirements, Design, Tests Specs）的輸入。
> - **ID 規範**：`Task N`（N 為數字流水號，如 `Task 1`, `Task 2`）。

### Task 1: <任務名稱>

> **💡 範例**：
>
> `實作檔案儲存功能`

#### 1. 功能單元 (Functional Unit, FU)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義此 Task 對應的功能單元 (FU)。
> - **Name**：對應 `<fu_name>`。
> - **Container Path**：對應 `<fu_path>`。
> - **Responsibility**：該單元的主要職責。
>
> **💡 範例**：
>
> | Attribute | Value |
> | :--- | :--- |
> | **Name** | `pickle-io` |
> | **Container Path** | `wutils/io` |
> | **Responsibility** | 負責 pickle 格式的讀寫操作與資源管理 |

| Attribute | Value |
| :--- | :--- |
| **Name** | <fu_name> |
| **Container Path** | <fu_path> |
| **Responsibility** | <填入功能職責摘要> |

#### 2. TDD 策略 (TDD Strategy)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 選擇測試驅動開發策略：
> - **Standard TDD**：適用於邏輯明確的 Library Feature（預設選項）。
> - **Exploratory TDD**：適用於涉及複雜 I/O 或需探索性開發的功能。
>
> **💡 範例**：
>
> | Attribute | Value |
> | :--- | :--- |
> | **Strategy** | Standard TDD |
> | **Reasoning** | 本功能為純粹的 I/O 封裝，邏輯明確且無外部依賴探索需求 |

| Attribute | Value |
| :--- | :--- |
| **Strategy** | <Standard TDD / Exploratory TDD> |
| **Reasoning** | <填入選擇理由> |

#### 3. 實作重點 (Implementation Details)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本區塊子項目採用字母編號 (A, B, C...)，以區別於文件標準章節結構。

##### A. 功能需求對應 (FR Mapping)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 描述程式碼邏輯如何滿足 `requirements.md` 中定義的 FR。
> - 引用 `requirements.md` 中的 `FR-XX` ID。
>
> **💡 範例**：
>
> | ID | Description | Implementation Note |
> | :--- | :--- | :--- |
> | **FR-01** | 寫入操作 | 使用 `with open(path, 'wb')` 並呼叫 `pickle.dump()` |
> | **FR-02** | 讀取操作 | 使用 `with open(path, 'rb')` 並呼叫 `pickle.load()` |

| ID | Description | Implementation Note |
| :--- | :--- | :--- |
| **FR-XX** | <填入摘要> | <填入邏輯描述> |

##### B. 驗收標準對應 (AC Mapping)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 描述測試案例如何驗證 `requirements.md` 中定義的 AC。
> - 引用 `requirements.md` 中的 `AC-XX` ID。
>
> **💡 範例**：
>
> | ID | Scenario | Assertion |
> | :--- | :--- | :--- |
> | **AC-01** | Happy Path | 斷言寫入後檔案存在且內容正確 |
> | **AC-02** | Edge Case | 斷言傳入空路徑時拋出 `ValueError` |
> | **AC-03** | Error Handling | 斷言讀取不存在檔案時拋出 `FileNotFoundError` |

| ID | Scenario | Assertion |
| :--- | :--- | :--- |
| **AC-XX** | <填入情境> | <填入驗證重點> |

##### C. 異常處理 (Exception Handling)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義每種例外情況的處理策略。
>
> **策略選項**：
> - **透傳 (Propagate)**：直接向上傳遞，不做處理。
> - **封裝 (Wrap)**：捕獲後包裝為自訂例外再拋出。
> - **吞噬 (Swallow)**：捕獲後不再拋出（需謹慎使用）。
> - **混合 (Mixed)**：依據不同例外類型採用不同策略。
>
> **💡 範例**：
>
> | Exception | Trigger | Strategy |
> | :--- | :--- | :--- |
> | `FileNotFoundError` | 讀取不存在的檔案 | **透傳 (Propagate)** |
> | `PermissionError` | 無寫入權限 | **透傳 (Propagate)** |
> | `pickle.UnpicklingError` | 檔案格式損壞 | **封裝 (Wrap)** 為 `DataCorruptedError` |

| Exception | Trigger | Strategy |
| :--- | :--- | :--- |
| <例外類型> | <觸發條件> | <處理方式> |

##### D. 架構約束對應 (Architectural Constraints Mapping)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 確認本 Task 符合 `requirements.md` 第 7 章定義的架構約束。
> - 引用 `requirements.md` 中的 `CONS-XX` ID。
> - 說明本 Task 如何滿足該約束。
>
> **💡 範例**：
>
> | ID | Constraint | Compliance Note |
> | :--- | :--- | :--- |
> | **CONS-01** | 僅依賴標準庫 | 本 Task 僅使用 `pickle`, `pathlib` |
> | **CONS-02** | 保持無狀態 | 所有函式皆為 Pure Function，無 Side Effect |
> | **CONS-03** | 封裝私有實作 | 實作檔案命名為 `_pickle_io.py` |

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-XX** | <約束摘要> | <符合性說明> |

##### E. 非功能需求對應 (NFR Mapping) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 僅當 `requirements.md` 第 6 章有定義 NFR 時填寫，否則可省略本區塊。
> - 引用 `requirements.md` 中的 `NFR-XX` ID。
> - 針對 NFR 說明具體的技術實現策略。
>
> **💡 範例**：
>
> | ID | Description | Design Strategy |
> | :--- | :--- | :--- |
> | **NFR-01** | Memory < 100MB | 採用 `yield` 生成器模式逐行讀取，避免一次性載入記憶體 |
> | **NFR-02** | Complexity O(1) | 使用 Hash Map (Dictionary) 建立索引，而非 List 走訪 |

| ID | Description | Design Strategy |
| :--- | :--- | :--- |
| **NFR-XX** | <指標> | <實作策略> |

### Task 2: <任務名稱> [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 僅當 Feature 涉及多個獨立的 Functional Unit 時才需要，否則請省略本章節。
> 結構同 Task 1。

...
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 核心定義與價值

- [ ] **設計邊界**：是否明確劃分了「In-Scope」與「Out-of-Scope」 (對應 §1.3)？
- [ ] **設計來源**：是否正確標註 `requirements.md` 的版本號（格式：`vX.Y.Z`）與路徑 (對應 §1.4)？

### B. 技術架構與介面

- [ ] ⚠️ **依賴合規性**：Dependency Matrix 是否僅包含 Std, 3rd-party 或 Local Library，嚴禁依賴 `businesssys` 或 `datasource` (對應 §3.1.2)？
- [ ] **目錄結構**：是否使用 tree 風格展示實體路徑，且實作檔案名稱符合私有化規範（如 `_pickle.py`） (對應 §3.1.1)？
- [ ] **API 簽章**：公開介面是否包含完整 Type Hints、Docstring，且明確定義了 `__all__` 導出內容 (對應 §3.2)？
- [ ] **需求覆蓋**：是否確保所有 `US-XXX` 都有對應的 API 進入點 (對應 §3.2.1)？

### C. 任務分解與 TDD 策略

- [ ] **Task 粒度**：每個 Task 是否精確對應一個 Functional Unit (FU) (對應 §4)？
- [ ] **映射完整性**：確保已完成 FR Mapping (A)、AC Mapping (B)、CONS Mapping (D)，若有 NFR 需求亦已完成 NFR Mapping (E) (對應 §4)？
- [ ] **異常處理策略**：是否針對每種 Exception 明確定義了處理方式，如透傳、封裝、吞噬或混合 (對應 §4)？
- [ ] **ID 追溯性**：所有引用的 `US/FR/AC/NFR/CONS` ID 是否與 `requirements.md` 完全一致 (對應 §4)？

### D. 格式與命名規範

- [ ] **標記規範**：佔位符變數（如 `<fu_name>`）是否統一使用 `snake_case`？

### E. 最終清理

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
