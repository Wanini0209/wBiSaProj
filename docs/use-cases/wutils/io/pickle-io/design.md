# pickle-io - Design

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `pickle-io` |
| **Target Library** | `wutils` |
| **Toolkit Category** | `io` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 價值主張 (Value Proposition)

- **痛點 (Pain Point)**：開發者目前需重複撰寫 `with open(...)` 樣板程式碼來處理檔案資源管理，且需手動處理路徑物件 (`Path`) 轉字串的問題，不僅繁瑣且容易因忘記關閉檔案導致資源洩漏。
- **效益 (Benefit)**：提供單一行程的原子化操作介面，自動處理檔案開關與資源釋放，並原生支援 `pathlib.Path` 與參數透傳，大幅簡化程式碼並提升安全性。

### 1.3 設計範圍 (Scope)

- **In-Scope**：
    - 封裝 `pickle` 的序列化 (`dump`) 與反序列化 (`load`) 操作。
    - 自動化檔案資源管理 (Context Manager)。
    - 支援 `str` 與 `pathlib.Path` 路徑格式。
    - 支援 `pickle` 底層參數透傳 (如 `protocol`, `encoding`)。
- **Out-of-Scope**：
    - JSON、YAML 或其他序列化格式的支援。
    - 資料加密或壓縮機制。
    - 遠端檔案系統 (如 S3) 的直接支援。

### 1.4 設計來源 (Design Source)

- **Based on**: `requirements.md` v1.0.0
- **Source Doc**: `docs/use-cases/wutils/io/pickle-io/requirements.md`

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-12-30 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 高階技術設計 (High-Level Design)

### 3.1 模組架構 (Module Architecture)

#### 3.1.1 目錄結構 (Directory Structure)

```text
wutils/
└── io/
    ├── __init__.py      # Public Interface (Exposes pickle_dump, pickle_load)
    └── _pickle_io/      # pickle-io Feature 的私有實作空間
        └── _pickle.py   # Private Implementation
```

#### 3.1.2 外部依賴矩陣 (Dependency Matrix)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `pickle` | Std | 核心序列化與反序列化邏輯 |
| `pathlib` | Std | 路徑物件型別支援 |
| `typing` | Std | 型別註釋支援 (`Any`, `Union` 等) |

### 3.2 公開 API 介面設計 (Public API Interface)

```python
from typing import Any, Union
from pathlib import Path

__all__ = ["pickle_dump", "pickle_load"]

def pickle_dump(obj: Any, path: Union[str, Path], **kwargs: Any) -> None:
    """
    將物件序列化並寫入指定路徑。

    封裝了標準的 `pickle.dump` 操作與檔案資源管理。

    Args:
        obj: 要序列化的 Python 物件。
        path: 目標檔案路徑，支援字串或 pathlib.Path 物件。
        **kwargs: 透傳給 `pickle.dump` 的額外參數 (如 protocol, fix_imports)。

    Raises:
        OSError: 當檔案寫入失敗或路徑無效時。
        pickle.PickleError: 當物件無法被序列化時。
    """
    ...

def pickle_load(path: Union[str, Path], **kwargs: Any) -> Any:
    """
    從指定路徑讀取並反序列化物件。

    封裝了標準的 `pickle.load` 操作與檔案資源管理。

    Args:
        path: 來源檔案路徑，支援字串或 pathlib.Path 物件。
        **kwargs: 透傳給 `pickle.load` 的額外參數 (如 encoding, errors)。

    Returns:
        Any: 反序列化後的 Python 物件。

    Raises:
        FileNotFoundError: 當指定檔案不存在時。
        OSError: 當檔案讀取失敗或權限不足時。
        pickle.UnpicklingError: 當檔案內容格式損壞或非 pickle 格式時。
    """
    ...
```

#### 3.2.1 需求覆蓋檢查 (Requirement Coverage)

| User Story / Req ID | API Mapping |
| :--- | :--- |
| **US-001** | `pickle_dump(obj, path, **kwargs)` |
| **US-002** | `pickle_load(path, **kwargs)` |
| **US-003** | `pickle_dump` 與 `pickle_load` 的 `**kwargs` 參數 |

## 4. 功能單元劃分 (FU Decomposition)

### 4.1 FU: `pickle-io`

#### 1. FU 屬性與整體職責 (Attributes & Responsibility)

| Attribute | Value |
| :--- | :--- |
| **Container Path** | `wutils/io` |
| **Responsibility** | 提供自動管理資源的 Pickle 序列化與反序列化函式 |

#### 2. 核心公開元件指派與契約 (Assigned Components & Contracts)

| Component | Type | Expected Contract / Responsibility |
| :--- | :--- | :--- |
| `pickle_dump` | Function | 實作物件序列化並寫入檔案的邏輯，必須以 `wb` 模式封裝 Context Manager 確保資源釋放，支援 `str` 與 `Path` 雙路徑型別，並透傳 `**kwargs`（如 `protocol`）至底層 `pickle.dump`。 |
| `pickle_load` | Function | 實作從檔案讀取並反序列化的邏輯，必須以 `rb` 模式封裝 Context Manager，支援雙路徑型別，若檔案不存在需透傳 `FileNotFoundError`，序列化失敗需透傳 `pickle.PickleError`。 |

#### 3. TDD 策略指示 (TDD Strategy Directive)

| Attribute | Value |
| :--- | :--- |
| **Strategy** | Standard TDD |
| **Reasoning** | 本功能為標準庫的薄層封裝 (Thin Wrapper)，邏輯單純且邊界明確，適合使用標準 TDD 流程進行驗證。 |

#### 4. 實作設計約定 (Implementation Design)

##### A. 功能需求對應 (FR Mapping)

| ID | Description | Implementation Note |
| :--- | :--- | :--- |
| **FR-01** | 序列化寫入函式 | 實作 `pickle_dump`，內部使用 `with open(path, 'wb')` |
| **FR-02** | 反序列化讀取函式 | 實作 `pickle_load`，內部使用 `with open(path, 'rb')` |
| **FR-03** | 參數透傳 | 接收 `**kwargs` 並直接傳遞給 `pickle.dump` / `pickle.load` |
| **FR-04** | 自動資源管理 | 利用 `with` 陳述式 (Context Manager) 確保檔案 handle 關閉 |
| **FR-05** | 完整型別註釋 | 所有參數與回傳值皆需標註型別，通過 Strict Mode 檢查 |

##### B. 驗收標準對應 (AC Mapping)

| ID | Scenario | Assertion |
| :--- | :--- | :--- |
| **AC-01** | Happy Path - 寫入與讀回 | 斷言寫入後的物件經讀取後，與原物件相等 (`assertEqual`) |
| **AC-02** | Edge Case - Pathlib 支援 | 傳入 `pathlib.Path` 物件，斷言操作成功且無 TypeError |
| **AC-03** | Edge Case - 參數透傳 | 寫入時指定 `protocol`，斷言生成的檔案格式符合預期 |
| **AC-04** | Error Handling - 檔案不存在 | 讀取不存在路徑，斷言拋出 `FileNotFoundError` |
| **AC-05** | Error Handling - 無效路徑 | 寫入至無權限或無效路徑，斷言拋出 `OSError` 或其子類別 |

##### C. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy |
| :--- | :--- | :--- |
| `FileNotFoundError` | 讀取不存在的檔案 | **透傳 (Propagate)** - 這是預期且具語意的標準例外 |
| `OSError` / `PermissionError` | 檔案系統層級錯誤 (如權限不足) | **透傳 (Propagate)** - 讓呼叫者依據環境決定如何處理 |
| `pickle.PickleError` | 序列化/反序列化失敗 | **透傳 (Propagate)** - 保持對底層錯誤的透明度 |

##### D. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | 僅依賴標準庫 | 僅使用 `pickle`, `pathlib`, `typing`，無第三方依賴 |
| **CONS-02** | 無業務依賴 | 位於 `wutils` 底層，完全獨立於業務與資料層 |
| **CONS-03** | 無狀態性 | `pickle_dump` 與 `pickle_load` 實作為 Pure Function |
| **CONS-04** | 內聚性 | 兩者皆定義於 Feature 級私有目錄 `_pickle_io/` 內，並透過 `__init__.py` 匯出 |

##### E. 非功能需求對應 (NFR Mapping)

| ID | Description | Design Strategy |
| :--- | :--- | :--- |
| **NFR-01** | Python 3.12+ | 確保語法相容性，不使用已棄用的 API |
| **NFR-02** | 100% Type Hints | 使用 `mypy --strict` 標準進行型別標註 |
| **NFR-03** | NumPy Docstrings | 依照 NumPy 風格撰寫函式說明文件 |
| **NFR-04** | Low Overhead | 僅做簡單的 `with open` 封裝，不引入額外邏輯運算 |
