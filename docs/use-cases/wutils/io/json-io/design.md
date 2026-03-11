# json-io - Design

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `json-io` |
| **Target Library** | `wutils` |
| **Toolkit Category** | `io` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 價值主張 (Value Proposition)

- **痛點 (Pain Point)**：目前開發者需重複撰寫 `with open(...)` 樣板程式碼，且容易因遺漏 `encoding='utf-8'` 導致跨平台亂碼，或因忘記關閉檔案造成資源洩漏。
- **效益 (Benefit)**：提供單行呼叫的原子化函式，內建強制 UTF-8 編碼與自動資源管理，大幅減少 Boilerplate 並提升程式碼安全性與可讀性。

### 1.3 設計範圍 (Scope)

- **In-Scope**：
    - JSON 檔案的寫入 (`dump`) 與讀取 (`load`)。
    - 支援 `str` 與 `pathlib.Path` 路徑格式。
    - 強制 UTF-8 編碼處理。
    - 透傳標準庫 `json` 的額外參數 (如 `indent`, `sort_keys`)。
- **Out-of-Scope**：
    - JSON Schema 驗證功能 (屬於 Validator Toolkit)。
    - 非標準 JSON 格式支援 (如 JSON5, Comments)。
    - 非同步 I/O (Async I/O) 支援。

### 1.4 設計來源 (Design Source)

- **Based on**: `requirements.md` v1.0.0
- **Source Doc**: `docs/use-cases/wutils/io/json-io/requirements.md`

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-02 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 高階技術設計 (High-Level Design)

本章節定義 Feature 完成後的「最終樣貌」與「整體架構」。

### 3.1 模組架構 (Module Architecture)

#### 3.1.1 目錄結構 (Directory Structure)

```text
wutils/
└── io/
    ├── __init__.py      # Public Interface (Exports json_dump, json_load)
    └── _json_io.py      # Private Implementation
```

#### 3.1.2 外部依賴矩陣 (Dependency Matrix)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `json` | Std | 核心 JSON 序列化與反序列化邏輯 |
| `pathlib` | Std | 檔案路徑物件處理與正規化 |
| `typing` | Std | 型別提示支援 (`Any`, `Union` 等) |

### 3.2 公開 API 介面設計 (Public API Interface)

```python
from typing import Any, Union
from pathlib import Path

__all__ = ["json_dump", "json_load"]

def json_dump(obj: Any, path: Union[str, Path], **kwargs: Any) -> None:
    """
    將物件序列化為 JSON 格式並寫入指定路徑 (強制 UTF-8)。

    Args:
        obj: 要序列化的 Python 物件。
        path: 目標檔案路徑 (支援 str 或 pathlib.Path)。
        **kwargs: 透傳至 json.dump 的額外參數 (如 indent, sort_keys)。

    Raises:
        TypeError: 當物件無法序列化時。
        PermissionError: 當無寫入權限時。
        OSError: 其他檔案系統錯誤。
    """
    ...

def json_load(path: Union[str, Path], **kwargs: Any) -> Any:
    """
    從指定路徑讀取並反序列化 JSON 檔案 (強制 UTF-8)。

    Args:
        path: 來源檔案路徑 (支援 str 或 pathlib.Path)。
        **kwargs: 透傳至 json.load 的額外參數。

    Returns:
        Any: 反序列化後的 Python 物件 (通常為 dict 或 list)。

    Raises:
        FileNotFoundError: 當檔案不存在時。
        json.JSONDecodeError: 當檔案內容非有效 JSON 格式時。
        PermissionError: 當無讀取權限時。
    """
    ...
```

#### 3.2.1 需求覆蓋檢查 (Requirement Coverage)

| User Story / Req ID | API Mapping |
| :--- | :--- |
| **US-001** | `json_dump(obj, path, **kwargs)` |
| **US-002** | `json_load(path, **kwargs)` |
| **US-003** | `json_dump` 與 `json_load` 的 `path` 參數型別設計 |
| **US-004** | `json_dump` 與 `json_load` 的 `**kwargs` 參數設計 |

## 4. 功能單元劃分 (FU Decomposition)

### 4.1 FU: `json-io`

#### 1. FU 屬性與整體職責 (Attributes & Responsibility)

| Attribute | Value |
| :--- | :--- |
| **Container Path** | `wutils/io` |
| **Responsibility** | 封裝標準庫 json 操作，提供統一的資源管理與編碼設定。 |

#### 2. 核心公開元件指派與契約 (Assigned Components & Contracts)

| Component | Type | Expected Contract / Responsibility |
| :--- | :--- | :--- |
| `json_dump` | Function | 實作物件序列化為 JSON 並寫入檔案的邏輯，必須強制 UTF-8 編碼、封裝 Context Manager 確保資源釋放，支援 `str` 與 `Path` 雙路徑型別，並透傳 `**kwargs` 至底層 `json.dump`。 |
| `json_load` | Function | 實作從檔案讀取並反序列化 JSON 的邏輯，必須強制 UTF-8 編碼、封裝 Context Manager，支援雙路徑型別，若檔案不存在需透傳 `FileNotFoundError`，若格式錯誤需透傳 `json.JSONDecodeError`。 |

#### 3. TDD 策略指示 (TDD Strategy Directive)

| Attribute | Value |
| :--- | :--- |
| **Strategy** | Standard TDD |
| **Reasoning** | 本功能邏輯單純，主要依賴 Python 標準庫，行為預期明確，適合標準紅綠重構流程。 |

#### 4. 實作設計約定 (Implementation Design)

##### A. 功能需求對應 (FR Mapping)

| ID | Description | Implementation Note |
| :--- | :--- | :--- |
| **FR-01** | `json_dump` 寫入功能 | 使用 `with open(path, 'w', encoding='utf-8')` 包覆 `json.dump(obj, f, **kwargs)`。 |
| **FR-02** | `json_load` 讀取功能 | 使用 `with open(path, 'r', encoding='utf-8')` 包覆 `json.load(f, **kwargs)`。 |
| **FR-03** | Path 支援 | 在函式入口處檢查 `path`，若為 `str` 則轉換為 `pathlib.Path` 物件，或直接由 `open` 處理 (Python 3.6+ `open` 原生支援 PathLike)。 |
| **FR-04** | 資源管理 | 利用 `with` statement (Context Manager) 確保區塊結束後自動關閉檔案 handle。 |
| **FR-05** | 讀寫對稱性 | 確保 `dump` 預設參數與 `load` 預設行為匹配，不進行額外的資料轉換。 |

##### B. 驗收標準對應 (AC Mapping)

| ID | Scenario | Assertion |
| :--- | :--- | :--- |
| **AC-01** | Happy Path (Read/Write) | 寫入複雜 Dict，讀回後 `assert data_in == data_out`，且確認檔案存在。 |
| **AC-02** | Happy Path (Params) | 呼叫 `dump(..., indent=4)`，讀取檔案 raw content，斷言包含換行符 `\n` 與縮排空格。 |
| **AC-03** | Edge Case (Path Object) | 傳入 `pathlib.Path` 物件至 `dump/load`，斷言執行成功無 TypeError。 |
| **AC-04** | Error Handling (Missing File) | 對不存在路徑呼叫 `load`，斷言拋出 `FileNotFoundError`。 |
| **AC-05** | Error Handling (Invalid JSON) | 建立含亂碼檔案呼叫 `load`，斷言拋出 `json.JSONDecodeError`。 |

##### C. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy |
| :--- | :--- | :--- |
| `FileNotFoundError` | 讀取不存在的檔案 | **透傳 (Propagate)**：這是標準庫預期行為，讓呼叫端決定如何處理。 |
| `PermissionError` | 權限不足導致無法讀寫 | **透傳 (Propagate)**：屬於環境問題，應向上拋出。 |
| `json.JSONDecodeError` | 檔案內容損毀或格式錯誤 | **透傳 (Propagate)**：保留原始錯誤訊息以利除錯。 |
| `TypeError` | 傳入無法序列化的物件 | **透傳 (Propagate)**：標準 `json.dump` 行為。 |

##### D. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | 僅依賴標準庫 | 檢查 import 區段，僅包含 `json`, `pathlib`, `typing`。 |
| **CONS-02** | 保持無狀態 | 實作為 Module-level functions，無 class state 或 global variables。 |
| **CONS-03** | 同一 FU | `dump` 與 `load` 實作於同一檔案 `_json_io.py` 並由同一個 `__init__.py` 導出。 |
| **CONS-04** | 無業務依賴 | 確保不 import 任何 `businesssys` 或 `datasource` 模組。 |

##### E. 非功能需求對應 (NFR Mapping)

| ID | Description | Design Strategy |
| :--- | :--- | :--- |
| **NFR-01** | 強制 UTF-8 | 在 `open()` 函式中明確指定 `encoding='utf-8'` 參數，不依賴 OS Default。 |
| **NFR-02** | 100% Type Hints | 所有函式參數與回傳值皆標註型別，並使用 `mypy` 驗證。 |
| **NFR-03** | 相容 std json 介面 | 使用 `**kwargs` 接收所有未定義參數並傳遞給底層 `json` 函式。 |
