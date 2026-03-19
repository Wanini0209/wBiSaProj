# Library Functional Unit (FU) Specs - Design Guide

本規範定義 Library 型 **Functional Unit (FU)** 在 `specs` 層級的 `design.md` 撰寫規範。目標是將需求轉化為可實作的介面設計，作為 TDD 流程中實作與測試的單一真理來源。

*供 Generator: Prompt4NewLibFuDesignSpec 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件指導如何將 `requirements.md` 的需求轉化為可實作的介面設計，是 TDD 流程中「測試先行」的設計依據。

### 1.2 TDD 導向的契約設計

- **介面即契約**：設計文件必須將 Function/Method Signature 與其「行為規則 (Rules)」綁定，作為實作與測試的單一真理來源 (SSOT)。
- **實作黑箱化**：**嚴禁**包含函數本體程式碼，僅保留介面定義。實作細節應使用 `...` 或 `pass` 帶過。

### 1.3 高度結構化

- **表格優先**：依賴項、規則、異常、非功能需求必須以表格呈現，確保可讀性 (Scannability)。
- **完全追溯**：必須提供需求 (Requirements) 到設計 (Design) 再到驗證 (Verification) 的雙向追溯能力。

---

## 2. 檔案路徑標準

`docs/specs/<fu_path>/<fu_name>/design.md`

- `<fu_path>`: FU Container 路徑 (e.g., `wutils/io`)
- `<fu_name>`: FU 名稱 (e.g., `pickle-io`)

---

## 3. ID 命名規範

> **⚠️ 重要**：以下 ID 格式為全專案統一規範，必須嚴格遵守。

### 3.1 本文件定義 ID

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `Rule-XX` | Behavioral Rule（兩位數流水號） | §5 介面設計與行為 |
| `BV-XX` | Behavior Verification（兩位數流水號） | §7 行為驗證 |

### 3.2 引用 ID（來自 requirements.md）

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `REQ-LOGIC-XX` | Core Logic Requirement | §10 需求追溯矩陣 |
| `REQ-VAL-XX` | Validation Requirement | §10 需求追溯矩陣 |
| `NFR-XX` | Non-Functional Requirement | §8 非功能需求 |
| `CONS-XX` | Architectural Constraint | §9 架構約束對應 |

---

## 4. 內容結構模板

````markdown
# <FU Name> - Design Specification

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
> 簡述此 FU 解決什麼問題，以及為何需要它（避免樣板代碼、統一行為等）。
>
> **💡 範例**：
>
> 「封裝 pickle 序列化操作，提供類型安全的介面並確保資源正確釋放，減少重複的 boilerplate code。」

<填入目的描述>

## 2. 變更歷史 (Change History)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 記錄版本變更，並在 Source 欄位明確指出是對應哪個版本的需求文件。
>
> **Source 格式**：`Based on requirements.md vX.Y.Z`
> **版本號格式**：`vX.Y.Z`（語意化版本）
>
> **💡 範例**：
>
> | Version | Date | Description | Source |
> | :--- | :--- | :--- | :--- |
> | v1.0.0 | 2024-01-15 | Initial Design | Based on requirements.md v1.0.0 |
> | v1.1.0 | 2024-02-01 | 新增 pathlib 支援 | Based on requirements.md v1.1.0 |

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | <YYYY-MM-DD> | Initial Design | Based on requirements.md v<Req_Version> |

## 3. 檔案組織 (File Organization)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 使用 tree 格式展示 FU Container 的實體檔案結構，包含公開介面與 Feature 級私有實作目錄的位置。
> 私有實作檔案必須位於以 Feature name 命名的私有目錄內（`_` 前綴 + `snake_case`）。
>
> **💡 範例**：
>
> ```text
> wutils/io/
> ├── __init__.py          # Public Container: 匯出 pickle_dump, pickle_load
> └── _pickle_io/          # pickle-io Feature 的私有實作空間
>     └── _pickle.py       # Private Implementation: 序列化邏輯
> ```

```text
<fu_path>/
├── __init__.py                    # Public Container
└── _<feature_snake_name>/         # Feature 的私有實作空間
    ├── <impl_file>                # Private Implementation
    └── ...
```

### 3.1 公開介面 (Public Interface)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義 Container 的匯出內容，必須與 Requirements 的 Export List 一致。
> 注意：import 路徑需包含 Feature 級私有目錄。
>
> **💡 範例**：
>
> **檔案**: `wutils/io/__init__.py`
>
> ```python
> from ._pickle_io._pickle import pickle_dump, pickle_load
>
> __all__ = ["pickle_dump", "pickle_load"]
> ```

**檔案**: `<fu_path>/__init__.py`

```python
from ._<feature_snake_name>.<impl_file> import <Component_1>, <Component_2>, ...

__all__ = ["<Component_1>", "<Component_2>", "..."]
```

### 3.2 私有實作 (Private Implementation)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出所有私有實作檔案及其職責。
>
> **⚠️ 重要路徑規範**：
> - **必須** 使用 **相對路徑** (Relative Path)，相對於 FU Container (`<fu_path>`)。
> - **必須** 包含 Feature 級私有目錄前綴。
> - **嚴禁** 使用絕對路徑或重複包含 Container Path 的完整路徑。
>
> **💡 範例**：
>
> 若 Container Path 為 `wutils/io`，Feature Name 為 `pickle-io`：
>
> | File Path | Responsibility |
> | :--- | :--- |
> | `_pickle_io/_pickle.py` | **(O) 正確**：相對於 `wutils/io`，位於 Feature 級目錄內 |
> | `_pickle.py` | **(X) 錯誤**：私有檔案未放入 Feature 級目錄 |
> | `wutils/io/_pickle_io/_pickle.py` | **(X) 錯誤**：請勿包含 Container Path |

| File Path | Responsibility |
| :--- | :--- |
| `_<feature_snake_name>/<impl_file>` | <填入職責> |

## 4. 依賴項 (Dependencies)

> **📝 撰寫指引**（請勿保留本指引文字）：
> Library FU 應盡量減少依賴，但允許為了重用性引用底層 Library。必須列出所有 Import 及其用途。
> - **Type**：
>   - `Std` (標準庫)
>   - `3rd-party` (第三方套件)
>   - **`Local` (專案內其他 Library/FU)**
> - **Import Statement**：完整的 import 語句。對於 `Local` 依賴，必須指向目標 FU 的**公開介面** (`__init__.py`)。
> - **Purpose**：說明此依賴的用途。
>
> **⚠️ 架構紅線**：若 Type 為 `Local`，嚴禁導入目標的私有模組 (如 `from wutils.io._pickle_io import ...`)，必須透過 Container (`__init__.py`) 導入。
>
> **💡 範例**：
>
> | Package | Type | Import Statement | Purpose |
> | :--- | :--- | :--- | :--- |
> | `typing` | Std | `from typing import Any, Union` | Type Hints |
> | `pydantic` | 3rd-party | `from pydantic import BaseModel` | 資料驗證 |
> | `wutils` | **Local** | `from wutils.common import StringHelper` | **重用字串處理邏輯** |

| Package | Type | Import Statement | Purpose |
| :--- | :--- | :--- | :--- |
| <套件名稱> | <Std / 3rd-party / Local> | <import 語句> | <用途> |

## 5. 介面設計與行為 (Interface Design & Rules)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 這是 TDD 的核心。針對每個公開 Class/Function，依序提供 Signature 與 Behavioral Rules。
> - **ID 規範**：`Rule-XX`，須全文件唯一，連續編號 (`Rule-01`, `Rule-02`, ...)。

### 5.1 `<函數/類別名稱>`

#### 5.1.1 函式簽章 (Function Signature)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 提供完整的 Type Hints 與 NumPy Style Docstring。函數本體僅使用 `...` 或 `pass`。
>
> **💡 範例**：
>
> ```python
> def pickle_dump(obj: Any, path: Union[str, Path]) -> None:
>     """
>     將物件序列化並寫入指定檔案路徑。
>
>     Parameters
>     ----------
>     obj : Any
>         欲序列化的 Python 物件。
>     path : Union[str, Path]
>         目標檔案路徑。
>
>     Returns
>     -------
>     None
>     """
>     ...
> ```

```python
def <function_name>(<params with type hints>) -> <return_type>:
    """
    <填入功能描述>

    Parameters
    ----------
    <param> : <type>
        <填入參數說明>

    Returns
    -------
    <type>
        <填入回傳值說明>
    """
    ...
```

#### 5.1.2 行為規則 (Behavioral Rules)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義此函數的具體行為規則，每條規則須有明確的驗收條件。
>
> **💡 範例**：
>
> | ID | Description | Acceptance Criteria |
> | :--- | :--- | :--- |
> | **Rule-01** | 使用 Context Manager 管理檔案資源 | 檔案操作後資源必須正確釋放 |
> | **Rule-02** | 支援 `str` 與 `Path` 兩種路徑類型 | 兩種類型輸入皆能正常處理 |

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-XX** | <填入規則簡述> | <填入驗收標準> |

### 5.2 `<下一個函數/類別名稱>`

*(重複 5.1 結構)*

## 6. 異常處理 (Exception Handling)

### 6.1 異常傳播策略 (Propagation Strategy)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 說明處理策略的整體設計方針，並解釋原因。
>
> **策略選項**：
> - **透傳 (Propagate)**：直接向上傳遞，不做處理。
> - **封裝 (Wrap)**：捕獲後包裝為自訂例外再拋出。
> - **吞噬 (Swallow)**：捕獲後不再拋出（需謹慎使用）。
> - **混合 (Mixed)**：依據不同例外類型採用不同策略。
>
> **💡 範例**：
>
> - **策略**: 透傳 (Propagate)
> - **理由**: 作為底層 IO 工具，應保留原始錯誤資訊，讓上層決定如何處理。

- **策略**: <填入策略選擇：透傳 / 封裝 / 吞噬 / 混合>
- **理由**: <填入設計理由>

### 6.2 異常對照表 (Exception Mapping Table)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出所有可能的異常及其觸發情境，並追溯到對應的 Rule。
>
> **💡 範例**：
>
> | Exception | Trigger | Function | Ref |
> | :--- | :--- | :--- | :--- |
> | `ValueError` | 傳入空字串路徑 | `pickle_dump`, `pickle_load` | **Rule-03** |
> | `TypeError` | 傳入不可序列化物件 | `pickle_dump` | **Rule-04** |
> | `FileNotFoundError` | 讀取不存在的檔案 | `pickle_load` | **Rule-05** |

| Exception | Trigger | Function | Ref |
| :--- | :--- | :--- | :--- |
| <例外類型> | <觸發條件> | <函式名稱> | **Rule-XX** |

## 7. 行為驗證 (Behavior Verification)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義高層次的測試情境 (Scenarios)，作為 `tests.md` 的輸入。
> 包含 Happy Path (主流程) 與 Edge Case (邊界案例/錯誤流)。
>
> **💡 範例**：
>
> | ID | Scenario | Expected Behavior | Ref |
> | :--- | :--- | :--- | :--- |
> | **BV-01** | Happy Path: 正常寫入物件到檔案 | 檔案成功建立且內容可還原 | **Rule-01**, **Rule-02** |
> | **BV-02** | Happy Path: 使用 Path 物件讀取 | 正確還原物件 | **Rule-02** |
> | **BV-03** | Edge Case: 傳入空字串路徑 | 拋出 `ValueError` | **Rule-03** |
> | **BV-04** | Error: 讀取不存在的檔案 | 拋出 `FileNotFoundError` | **Rule-05** |

| BV ID | Scenario | Expected Behavior | Ref |
| :--- | :--- | :--- | :--- |
| **BV-XX** | <Happy Path / Edge Case / Error>: <情境描述> | <預期結果> | **Rule-XX** |

## 8. 非功能需求 (Non-Functional Requirements) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義效能、型別安全等非功能需求，並追溯到 Requirements 的 NFR。若無特殊需求，可省略本章節。
>
> **💡 範例**：
>
> | ID | Category | Description | Traceability |
> | :--- | :--- | :--- | :--- |
> | **NFR-01** | Type Safety | 100% Type Hint 覆蓋率 (Strict Mode) | **NFR-02** |
> | **NFR-02** | Performance | 單檔處理時間 < 100ms (1MB 以下) | **NFR-03** |

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-XX** | <類別> | <需求描述> | **NFR-XX** |

## 9. 架構約束對應 (Architectural Constraints Mapping)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 確認本 Design 符合 `requirements.md` 第 8 章定義的架構約束。
> - 引用 `requirements.md` 中的 `CONS-XX` ID。
> - 說明本 Design 如何滿足該約束，並指向文件中的相關章節作為佐證。
>
> **💡 範例**：
>
> | ID | Constraint | Compliance Note |
> | :--- | :--- | :--- |
> | **CONS-01** | 僅依賴標準庫與 Core | 依賴項表格 (§4) 已確認僅使用 `Std` 類型 |
> | **CONS-02** | 無狀態設計 | 所有函式設計為 Pure Function，無全域變數 (見 §5 介面設計) |
> | **CONS-03** | 實作檔為私有 | 檔案組織 (§3.2) 所有實作檔皆以 `_` 開頭 |

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-XX** | <填入約束摘要> | <填入符合性說明，指向相關章節> |

## 10. 需求追溯矩陣 (Traceability Matrix)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 確保每個 Requirement 都有對應的 Rule 和 Verification。
>
> **💡 範例**：
>
> | Requirement (REQ) | Design Element (Rules) | Verification (BV) |
> | :--- | :--- | :--- |
> | **REQ-LOGIC-01** | **Rule-01** | **BV-01** |
> | **REQ-LOGIC-02** | **Rule-02** | **BV-01**, **BV-02** |
> | **REQ-VAL-01** | **Rule-03** | **BV-03** |

| Requirement (REQ) | Design Element (Rules) | Verification (BV) |
| :--- | :--- | :--- |
| **REQ-XX** | **Rule-XX** | **BV-XX** |

## 11. 驗收標準 (Acceptance Criteria)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義功能實作完成時的「完工定義 (DoD)」。此清單結合了專案的非功能性需求 (PNFR) 與架構約束，確保實作代碼符合專案工程標準。

- [ ] **介面一致性**：實作的 Function/Class Signature 與本設計文件 (§5.1) 100% 一致。
- [ ] **行為完整性**：實作程式碼已完整涵蓋並符合所有定義的行為規則 (`Rule-XX`)。
- [ ] **型別安全**：符合 **PNFR-CDE-01**，實作具備 100% Type Hint 覆蓋率（Strict Mode）。
- [ ] **文件規範**：符合 **PNFR-DOC-01**，所有公開介面均具備完整的 NumPy Style Docstrings。
- [ ] **架構紅線 (DIP)**：
    - [ ] **封裝性**：所有具體實作皆存放於 Feature 級私有目錄（`_<feature_snake_name>/`）中。
    - [ ] **導入規範**：對專案內其他 Library 的依賴，嚴格僅透過目標容器的 `__init__.py` 導入，禁止穿透存取私有實作。
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 文件追溯性與定位

- [ ] **變更歷史**：是否詳實記錄，且 Source 欄位追溯到對應的 Requirements 版本 (對應 §2)？

### B. 結構與依賴規範

- [ ] **檔案組織樹狀圖**：是否清晰呈現 Public/Private 結構，且私有實作檔案位於 Feature 級私有目錄內 (對應 §3)？
- [ ] ⚠️ **路徑規範**：私有實作路徑是否嚴格使用「相對路徑」（含 Feature 級目錄前綴），且嚴禁包含 Container Path 或絕對路徑 (對應 §3.2)？
- [ ] ⚠️ **Local 依賴紅線**：若依賴專案內其他 FU，是否僅透過 Container (`__init__.py`) 導入，嚴禁穿透導入私有模組 (對應 §4)？

### C. 介面設計與 TDD 核心

- [ ] ⚠️ **實作黑箱化**：Function Body 是否僅保留 `...` 或 `pass` (對應 §5)？
- [ ] **介面品質**：Docstring 符合 NumPy Style、參數與回傳值具備 100% Type Hints、每個 `Rule-XX` 具備明確的 Acceptance Criteria (對應 §5)？

### D. 異常處理與行為驗證

- [ ] **異常處理策略**：策略是否明確（如透傳、封裝等），並提供了具體的設計理由 (對應 §6)？
- [ ] **映射完整性**：每個 Requirement 均對應到 Rule 設計，每個設計 Rule 均有對應的 BV 驗證場景 (對應 §10)？

### E. 格式與命名規範

- [ ] **標記規範**：所有自定義 ID (`Rule`, `BV`) 是否為兩位數流水號，如 `Rule-01` (對應 §5, §7)？

### F. 最終清理

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
