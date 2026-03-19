# json-io - Design Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `json-io` |
| **Container Path** | `wutils/io` |
| **Parent Feature** | `json-io` |
| **Public Interface** | `wutils/io` (`__init__.py`) |
| **Exports** | `json_dump`, `json_load` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 目的 (Purpose)

本單元旨在封裝 Python 標準庫 `json` 的檔案讀寫操作，提供一致性的原子化介面。核心目的是強制統一使用 UTF-8 編碼以避免跨平台亂碼問題，並透過內建的 Context Manager 自動管理檔案資源，減少重複的樣板程式碼 (Boilerplate) 與潛在的資源洩漏風險。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-02 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 檔案組織 (File Organization)

```text
wutils/io/
├── __init__.py      # Public Container
└── _json_io/        # json-io Feature 的私有實作空間
    └── _json.py     # Private Implementation: JSON 讀寫邏輯
```

### 3.1 公開介面 (Public Interface)

**檔案**: `wutils/io/__init__.py`

```python
from ._json_io._json import json_dump, json_load

__all__ = ["json_dump", "json_load"]
```

### 3.2 私有實作 (Private Implementation)

| File Path | Responsibility |
| :--- | :--- |
| `_json_io/_json.py` | 實作 `json_dump` 與 `json_load` 函式，處理檔案開啟、編碼強制與異常透傳邏輯 |

## 4. 依賴項 (Dependencies)

| Package | Type | Import Statement | Purpose |
| :--- | :--- | :--- | :--- |
| `json` | Std | `import json` | 核心 JSON 序列化與反序列化邏輯 |
| `pathlib` | Std | `from pathlib import Path` | 檔案路徑物件處理 |
| `typing` | Std | `from typing import Any, Union` | Type Hints |

## 5. 介面設計與行為 (Interface Design & Rules)

### 5.1 `json_dump`

#### 5.1.1 函式簽章 (Function Signature)

```python
def json_dump(obj: Any, path: Union[str, Path], **kwargs: Any) -> None:
    """
    將 Python 物件序列化為 JSON 格式並寫入指定檔案，強制使用 UTF-8 編碼。

    Parameters
    ----------
    obj : Any
        待序列化的 Python 物件。
    path : Union[str, Path]
        目標檔案路徑。
    **kwargs : Any
        透傳給 json.dump 的額外關鍵字參數 (如 indent, sort_keys)。

    Returns
    -------
    None
    """
    ...
```

#### 5.1.2 行為規則 (Behavioral Rules)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-01** | 強制 UTF-8 編碼寫入 | 呼叫 `open` 時必須指定 `encoding='utf-8'`，寫入非 ASCII 字元應正確保留 |
| **Rule-02** | 支援多種路徑型別 | 接受 `str` 或 `pathlib.Path` 物件，並能正確處理 |
| **Rule-03** | 自動資源管理 | 使用 Context Manager (`with open(...)`) 確保檔案 Handle 在操作後關閉 |
| **Rule-04** | 參數透傳 | 將 `kwargs` 直接傳遞給底層 `json.dump`，如 `indent=4` 應產生格式化輸出 |
| **Rule-05** | 序列化檢查 | 若 `obj` 無法序列化，應透傳底層 `TypeError` |

### 5.2 `json_load`

#### 5.2.1 函式簽章 (Function Signature)

```python
def json_load(path: Union[str, Path], **kwargs: Any) -> Any:
    """
    從指定檔案讀取 JSON 內容並反序列化為 Python 物件，強制使用 UTF-8 編碼。

    Parameters
    ----------
    path : Union[str, Path]
        來源檔案路徑。
    **kwargs : Any
        透傳給 json.load 的額外關鍵字參數。

    Returns
    -------
    Any
        反序列化後的 Python 物件 (通常為 dict 或 list)。
    """
    ...
```

#### 5.2.2 行為規則 (Behavioral Rules)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-06** | 強制 UTF-8 編碼讀取 | 呼叫 `open` 時必須指定 `encoding='utf-8'`，能正確讀取包含非 ASCII 字元的檔案 |
| **Rule-07** | 支援多種路徑型別 | 接受 `str` 或 `pathlib.Path` 物件，並能正確處理 |
| **Rule-08** | 自動資源管理 | 使用 Context Manager (`with open(...)`) 確保檔案 Handle 在操作後關閉 |
| **Rule-09** | 參數透傳 | 將 `kwargs` 直接傳遞給底層 `json.load` |

## 6. 異常處理 (Exception Handling)

### 6.1 異常傳播策略 (Propagation Strategy)

- **策略**: 透傳 (Propagate)
- **理由**: 作為底層 IO 工具，應保留原始錯誤資訊（如檔案不存在、權限不足、JSON 格式錯誤），不應過度包裝隱藏底層細節，讓上層呼叫者決定如何處理特定錯誤。

### 6.2 異常對照表 (Exception Mapping Table)

| Exception | Trigger | Function | Ref |
| :--- | :--- | :--- | :--- |
| `FileNotFoundError` | 讀取不存在的檔案路徑 | `json_load` | **Rule-08** |
| `PermissionError` | 無權限讀取或寫入指定路徑 | `json_dump`, `json_load` | **Rule-03**, **Rule-08** |
| `json.JSONDecodeError` | 檔案內容非有效 JSON 格式 | `json_load` | **Rule-06** |
| `TypeError` | 傳入不可序列化的物件 (如 `set`) | `json_dump` | **Rule-05** |

## 7. 行為驗證 (Behavior Verification)

| BV ID | Scenario | Expected Behavior | Ref |
| :--- | :--- | :--- | :--- |
| **BV-01** | Happy Path: 寫入包含中文的物件 (UTF-8) | 檔案成功建立，且內容為正確 UTF-8 編碼 | **Rule-01**, **Rule-03** |
| **BV-02** | Happy Path: 讀取 UTF-8 JSON 檔案 | 正確還原 Python 物件，中文字元無亂碼 | **Rule-06**, **Rule-08** |
| **BV-03** | Happy Path: 使用 `Path` 物件與 `str` 路徑 | 兩種類型輸入皆能正常執行讀寫 | **Rule-02**, **Rule-07** |
| **BV-04** | Feature: 傳入 `indent` 參數至 dump | 生成的 JSON 檔案具備縮排格式 | **Rule-04** |
| **BV-05** | Error: 嘗試 dump 不可序列化物件 (如 set) | 拋出 `TypeError` | **Rule-05** |
| **BV-06** | Error: load 不存在的檔案 | 拋出 `FileNotFoundError` | **Rule-08** |
| **BV-07** | Error: load 格式錯誤的 JSON 檔 | 拋出 `json.JSONDecodeError` | **Rule-06** |

## 8. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Encoding | 讀寫操作皆強制指定 `encoding='utf-8'` | **NFR-01** |
| **NFR-02** | Type Safety | 100% Type Hint 覆蓋率 (Strict Mode) | **NFR-02** |
| **NFR-03** | Compatibility | 支援標準庫 `json` 的關鍵字參數 (`**kwargs`) | **NFR-03** |

## 9. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | 僅依賴標準庫 | 依賴項表格 (§4) 已確認僅使用 `json`, `pathlib`, `typing` (Std) |
| **CONS-02** | 無狀態設計 | 所有函式設計為 Pure Function，無全域變數 (見 §5 介面設計) |
| **CONS-03** | 實作檔為私有 | 實作邏輯位於 Feature 級私有目錄 `_json_io/_json.py`，僅透過 `__init__.py` 匯出 (見 §3) |
| **CONS-04** | 禁止依賴業務層 | 本 FU 位於 Library 層，未引入任何上層依賴 |

## 10. 需求追溯矩陣 (Traceability Matrix)

| Requirement (REQ) | Design Element (Rules) | Verification (BV) |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | **Rule-01** | **BV-01** |
| **REQ-LOGIC-02** | **Rule-06** | **BV-02**, **BV-07** |
| **REQ-LOGIC-03** | **Rule-02**, **Rule-07** | **BV-03** |
| **REQ-LOGIC-04** | **Rule-03**, **Rule-08** | **BV-01**, **BV-02**, **BV-06** |
| **REQ-LOGIC-05** | **Rule-04**, **Rule-09** | **BV-04** |
| **REQ-VAL-01** | **Rule-05** | **BV-05** |

## 11. 驗收標準 (Acceptance Criteria)

- [ ] **介面一致性**：實作的 Function Signature 與本設計文件 (§5) 100% 一致。
- [ ] **行為完整性**：實作程式碼已完整涵蓋並符合所有定義的行為規則 (`Rule-01` 至 `Rule-09`)。
- [ ] **型別安全**：符合 **PNFR-CDE-01**，實作具備 100% Type Hint 覆蓋率（Strict Mode）。
- [ ] **文件規範**：符合 **PNFR-DOC-01**，所有公開介面均具備完整的 NumPy Style Docstrings。
- [ ] **架構紅線 (DIP)**：
    - [ ] **封裝性**：具體實作存放於 Feature 級私有目錄 `_json_io/` 中。
    - [ ] **導入規範**：本模組無 Local 依賴，符合依賴原則。
