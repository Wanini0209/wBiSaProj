# pickle-io - Design Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `pickle-io` |
| **Container Path** | `wutils/io` |
| **Parent Feature** | `pickle-io` |
| **Public Interface** | `wutils/io` (`__init__.py`) |
| **Exports** | `pickle_dump`, `pickle_load` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 目的 (Purpose)

本單元旨在封裝標準庫 `pickle` 的操作，提供自動化的檔案資源管理 (Context Manager) 與增強的路徑型別支援 (`str` 與 `Path`)。透過提供原子化的讀寫介面，確保檔案 Handle 正確關閉，減少重複的 boilerplate code，並提升開發者體驗。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-12-30 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 檔案組織 (File Organization)

```text
wutils/io/
├── __init__.py      # Public Container
└── _pickle_io/      # pickle-io Feature 的私有實作空間
    └── _pickle.py   # Private Implementation
```

### 3.1 公開介面 (Public Interface)

**檔案**: `wutils/io/__init__.py`

```python
from ._pickle_io._pickle import pickle_dump, pickle_load

__all__ = ["pickle_dump", "pickle_load"]
```

### 3.2 私有實作 (Private Implementation)

| File Path | Responsibility |
| :--- | :--- |
| `_pickle_io/_pickle.py` | 實作 `pickle` 的序列化與反序列化封裝邏輯，包含資源管理與路徑處理。 |

## 4. 依賴項 (Dependencies)

| Package | Type | Import Statement | Purpose |
| :--- | :--- | :--- | :--- |
| `pickle` | Std | `import pickle` | 核心序列化與反序列化邏輯 |
| `pathlib` | Std | `from pathlib import Path` | 路徑物件型別支援 |
| `typing` | Std | `from typing import Any, Union` | Type Hints |

## 5. 介面設計與行為 (Interface Design & Rules)

### 5.1 `pickle_dump`

#### 5.1.1 函式簽章 (Function Signature)

```python
def pickle_dump(obj: Any, path: Union[str, Path], **kwargs: Any) -> None:
    """
    將 Python 物件序列化並寫入指定檔案路徑。

    Parameters
    ----------
    obj : Any
        欲序列化的 Python 物件。
    path : Union[str, Path]
        目標檔案路徑，支援字串或 Path 物件。
    **kwargs : Any
        透傳給 pickle.dump 的額外參數 (如 protocol)。

    Returns
    -------
    None
    """
    ...
```

#### 5.1.2 行為規則 (Behavioral Rules)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-01** | 自動資源管理寫入 | 必須使用 Context Manager (`with open(...)`) 以 `wb` 模式開啟檔案，確保操作後資源釋放。 |
| **Rule-02** | 多態路徑支援 | 若傳入 `pathlib.Path` 物件，必須能正確轉換或直接使用，行為需與 `str` 路徑一致。 |
| **Rule-03** | 參數透傳機制 | 必須將 `**kwargs` 完整傳遞給底層 `pickle.dump` 函式。 |

### 5.2 `pickle_load`

#### 5.2.1 函式簽章 (Function Signature)

```python
def pickle_load(path: Union[str, Path], **kwargs: Any) -> Any:
    """
    從指定檔案路徑讀取並還原 Python 物件。

    Parameters
    ----------
    path : Union[str, Path]
        來源檔案路徑，支援字串或 Path 物件。
    **kwargs : Any
        透傳給 pickle.load 的額外參數 (如 encoding)。

    Returns
    -------
    Any
        還原後的 Python 物件。
    """
    ...
```

#### 5.2.2 行為規則 (Behavioral Rules)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-04** | 自動資源管理讀取 | 必須使用 Context Manager (`with open(...)`) 以 `rb` 模式開啟檔案，確保操作後資源釋放。 |
| **Rule-05** | 多態路徑支援 | 若傳入 `pathlib.Path` 物件，必須能正確轉換或直接使用，行為需與 `str` 路徑一致。 |
| **Rule-06** | 參數透傳機制 | 必須將 `**kwargs` 完整傳遞給底層 `pickle.load` 函式。 |

## 6. 異常處理 (Exception Handling)

### 6.1 異常傳播策略 (Propagation Strategy)

- **策略**: 透傳 (Propagate)
- **理由**: 作為底層 IO 工具，應保留原始錯誤資訊 (如檔案不存在、權限錯誤、序列化失敗)，讓上層呼叫者依據業務場景決定如何處理。

### 6.2 異常對照表 (Exception Mapping Table)

| Exception | Trigger | Function | Ref |
| :--- | :--- | :--- | :--- |
| `FileNotFoundError` | 讀取不存在的檔案路徑 | `pickle_load` | **Rule-04** |
| `OSError` | 檔案系統層級錯誤 (如權限不足、無效路徑) | `pickle_dump`, `pickle_load` | **Rule-01**, **Rule-04** |
| `pickle.PickleError` | 物件無法序列化或檔案格式損毀 | `pickle_dump`, `pickle_load` | **Rule-01**, **Rule-04** |
| `TypeError` | 傳入不支援的路徑型別 (非 str/Path) | `pickle_dump`, `pickle_load` | **Rule-02**, **Rule-05** |

## 7. 行為驗證 (Behavior Verification)

| BV ID | Scenario | Expected Behavior | Ref |
| :--- | :--- | :--- | :--- |
| **BV-01** | Happy Path: 正常寫入物件 (str Path) | 檔案成功建立，無異常拋出。 | **Rule-01**, **Rule-02** |
| **BV-02** | Happy Path: 正常讀取物件 (Path Object) | 成功還原原始物件內容。 | **Rule-04**, **Rule-05** |
| **BV-03** | Advanced: 透傳參數 (protocol) | 產生的檔案應符合指定 protocol 版本。 | **Rule-03** |
| **BV-04** | Error: 讀取不存在的檔案 | 拋出 `FileNotFoundError`。 | **Rule-04** |
| **BV-05** | Error: 寫入不可序列化物件 | 拋出 `pickle.PickleError` 或其子類。 | **Rule-01** |

## 8. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Environment | Python 3.12+ Syntax & Runtime support | **Req: NFR-01** |
| **NFR-02** | Type Safety | 100% Type Hint Coverage with Strict Mode | **Req: NFR-02** |
| **NFR-03** | Documentation | NumPy Style Docstrings for all exported functions | **Req: NFR-03** |
| **NFR-04** | Performance | Low Overhead (Thin Wrapper implementation) | **Req: NFR-04** |

## 9. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | Isolation | 依賴項表格 (§4) 確認僅依賴標準庫，無 Business 層依賴。 |
| **CONS-02** | Encapsulation | 實作檔位於 Feature 級私有目錄 `_pickle_io/_pickle.py` (見 §3.2)，且僅透過 `__init__.py` 匯出功能。 |
| **CONS-03** | Dependency | 依賴項表格 (§4) 確認所有 Imports 皆為 `Std` 類型。 |
| **CONS-04** | Stateless | 函式設計為 Pure Function (§5.1, §5.2)，無保存全域狀態。 |

## 10. 需求追溯矩陣 (Traceability Matrix)

| Requirement (REQ) | Design Element (Rules) | Verification (BV) |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | **Rule-01** | **BV-01**, **BV-05** |
| **REQ-LOGIC-02** | **Rule-04** | **BV-02**, **BV-04** |
| **REQ-LOGIC-03** | **Rule-02**, **Rule-05** | **BV-01**, **BV-02** |
| **REQ-LOGIC-04** | **Rule-03**, **Rule-06** | **BV-03** |
| **REQ-VAL-01** | **Function Signatures (§5)** | **Static Analysis (mypy)** |

## 11. 驗收標準 (Acceptance Criteria)

- [ ] **介面一致性**：實作的 Function/Class Signature 與本設計文件 (§5) 100% 一致。
- [ ] **行為完整性**：實作程式碼已完整涵蓋並符合所有定義的行為規則 (`Rule-01` 至 `Rule-06`)。
- [ ] **型別安全**：符合 **PNFR-CDE-01**，實作具備 100% Type Hint 覆蓋率（Strict Mode）。
- [ ] **文件規範**：符合 **PNFR-DOC-01**，所有公開介面均具備完整的 NumPy Style Docstrings。
- [ ] **架構紅線 (DIP)**：
    - [ ] **封裝性**：所有具體實作皆存放於 Feature 級私有目錄 `_pickle_io/` 中。
    - [ ] **導入規範**：本單元無 Local 依賴，符合規範。
