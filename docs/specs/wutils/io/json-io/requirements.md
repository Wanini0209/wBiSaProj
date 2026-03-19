# json-io - Requirements Specification

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

本單元旨在封裝 Python 標準庫 `json` 的檔案讀寫操作，提供原子化的函式介面。其主要目的是強制統一使用 UTF-8 編碼以避免跨平台亂碼問題，並透過內建的 Context Manager 自動管理檔案資源，減少重複的樣板程式碼 (Boilerplate) 與潛在的資源洩漏風險。

### 1.3 依賴盤點 (Dependencies)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `json` | Std | 核心 JSON 序列化與反序列化邏輯 |
| `pathlib` | Std | 檔案路徑物件處理與正規化 |
| `typing` | Std | 型別提示支援 |

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-02 | Initial Release (Basic Dump/Load with UTF-8 support) | Feature v1.0.0 |

## 3. 匯出能力 (Exported Capabilities)

### 3.1 匯出清單 (Export List)

```python
__all__ = ["json_dump", "json_load"]
```

### 3.2 能力定義 (Capability Definitions)

#### 3.2.1 JSON 寫入 (json_dump)

- **功能目標**: 將 Python 物件序列化為 JSON 格式並寫入指定檔案，強制使用 UTF-8 編碼。
- **關鍵輸入**: 待序列化物件 (Any)、目標路徑 (支援 `str` 或 `pathlib.Path`)、透傳參數 (如 `indent`, `sort_keys`)。
- **關鍵輸出**: 無 (副作用為檔案建立或覆寫)。
- **關鍵行為**:
    - 自動開啟與關閉檔案 (Context Manager)。
    - 強制指定 `encoding='utf-8'`。
    - 支援標準庫 `json.dump` 的所有關鍵字參數。

#### 3.2.2 JSON 讀取 (json_load)

- **功能目標**: 從指定檔案讀取 JSON 內容並反序列化為 Python 物件，強制使用 UTF-8 編碼。
- **關鍵輸入**: 來源路徑 (支援 `str` 或 `pathlib.Path`)、透傳參數。
- **關鍵輸出**: 反序列化後的 Python 物件 (通常為 `dict` 或 `list`)。
- **關鍵行為**:
    - 自動開啟與關閉檔案 (Context Manager)。
    - 強制以 `encoding='utf-8'` 讀取。
    - 支援標準庫 `json.load` 的所有關鍵字參數。

### 3.3 使用範例 (Usage Examples)

```python
from pathlib import Path
from typing import Any
from wutils.io import json_dump, json_load

# 準備資料與路徑
data: dict[str, Any] = {"key": "value", "numbers": [1, 2, 3]}
file_path = Path("data.json")

# Happy Path: 寫入 (支援 Path 物件與額外參數)
json_dump(data, file_path, indent=4)

# Happy Path: 讀取
loaded_data = json_load(file_path)
assert loaded_data == data

# Happy Path: 使用字串路徑
json_dump(data, "data_str.json")
```

## 4. 功能需求 (Functional Requirements)

### 4.1 核心邏輯 (Core Logic)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | `json_dump` 必須強制使用 UTF-8 編碼寫入檔案 | 寫入包含非 ASCII 字元 (如中文) 的資料後，檔案內容編碼正確且可被標準 UTF-8 編輯器讀取 |
| **REQ-LOGIC-02** | `json_load` 必須強制使用 UTF-8 編碼讀取檔案 | 能夠正確讀取 UTF-8 編碼的 JSON 檔案，且還原的字串內容正確無亂碼 |
| **REQ-LOGIC-03** | 支援 `str` 與 `pathlib.Path` 類型的路徑輸入 | 傳入 `str` 路徑或 `Path` 物件時，`dump` 與 `load` 皆能正常執行無錯誤 |
| **REQ-LOGIC-04** | 自動資源管理 (Resource Management) | 函式執行完畢或發生錯誤後，檔案 Handle 必須被關閉 (無 Resource Leak) |
| **REQ-LOGIC-05** | 參數透傳 (Parameter Passthrough) | 傳入 `kwargs` (如 `indent=4`) 至 `dump` 時，生成的檔案內容必須具備對應的格式 (如縮排) |

### 4.2 驗證與約束 (Validation)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-VAL-01** | 輸入物件序列化檢查 | 若傳入無法被 JSON 序列化的物件 (如 `set`) 至 `dump`，應觸發底層錯誤而不被吞噬 |

## 5. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy | Ref |
| :--- | :--- | :--- | :--- |
| `FileNotFoundError` | 呼叫 `load` 時檔案路徑不存在 | **透傳 (Propagate)** | **REQ-LOGIC-04** |
| `PermissionError` | 無權限讀取或寫入指定路徑 | **透傳 (Propagate)** | **REQ-LOGIC-04** |
| `json.JSONDecodeError` | 呼叫 `load` 時檔案內容非有效 JSON 格式 | **透傳 (Propagate)** | **REQ-LOGIC-02** |
| `TypeError` | 呼叫 `dump` 時物件無法序列化 | **透傳 (Propagate)** | **REQ-VAL-01** |

## 6. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Encoding | 強制 UTF-8 編碼，不依賴作業系統預設值 | **Ref: Feature NFR-01** |
| **NFR-02** | Type Safety | 100% Type Hint Coverage (Strict Mode) | **Ref: PNFR-CDE-01** |
| **NFR-03** | Compatibility | 介面參數設計需最大程度相容標準庫 `json` 模組 | **Ref: Feature NFR-03** |

## 7. 架構約束 (Architectural Constraints)

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-01** | **Dependency**: 僅依賴標準庫 | 禁止引入任何第三方套件，確保輕量化與高移植性 |
| **CONS-02** | **Stateless**: 保持無狀態設計 | 實作為 Module-level functions，禁止使用 Global Variables 保存狀態 |
| **CONS-03** | **Cohesion**: 單一 Feature 目錄實作 | `dump` 與 `load` 邏輯應實作於同一 Feature 級私有目錄 (`_json_io/`) 內的私有模組中 |
| **CONS-04** | **Isolation**: 禁止依賴業務層 | 嚴禁 import `businesssys` 或 `datasource` 等上層模組 |
