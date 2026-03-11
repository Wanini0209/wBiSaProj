# pickle-io - Requirements Specification

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

本單元旨在封裝標準庫 `pickle` 的操作，提供自動化的檔案資源管理 (Context Manager) 與增強的路徑型別支援。透過提供原子化的讀寫介面，減少重複的 boilerplate code，確保檔案 handle 正確關閉，並提升開發者體驗。

### 1.3 依賴盤點 (Dependencies)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `pickle` | Std | 核心序列化與反序列化邏輯 |
| `pathlib` | Std | 路徑物件型別支援 |
| `typing` | Std | 型別註釋支援 (`Any`, `Union` 等) |

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-12-30 | Initial Release (Basic Dump/Load wrappers) | Feature v1.0.0 |

## 3. 匯出能力 (Exported Capabilities)

### 3.1 匯出清單 (Export List)

```python
__all__ = ["pickle_dump", "pickle_load"]
```

### 3.2 能力定義 (Capability Definitions)

#### 3.2.1 序列化寫入 (pickle_dump)

- **功能目標**: 將 Python 物件序列化並寫入指定檔案路徑。
- **關鍵輸入**: 任意 Python 物件 (`obj`)、目標路徑 (`path`，支援 `str` 或 `pathlib.Path`)、透傳參數 (`**kwargs`)。
- **關鍵輸出**: 無 (檔案寫入成功)。
- **關鍵行為**:
    - 自動使用 `wb` 模式開啟檔案。
    - 確保操作完成後自動關閉檔案資源。
    - 支援將額外參數透傳予 `pickle.dump`。

#### 3.2.2 反序列化讀取 (pickle_load)

- **功能目標**: 從指定檔案路徑讀取並還原 Python 物件。
- **關鍵輸入**: 來源路徑 (`path`，支援 `str` 或 `pathlib.Path`)、透傳參數 (`**kwargs`)。
- **關鍵輸出**: 還原後的 Python 物件。
- **關鍵行為**:
    - 自動使用 `rb` 模式開啟檔案。
    - 確保操作完成後自動關閉檔案資源。
    - 支援將額外參數透傳予 `pickle.load`。

### 3.3 使用範例 (Usage Examples)

```python
from wutils.io import pickle_dump, pickle_load
from pathlib import Path

# Happy Path: 寫入資料 (使用字串路徑)
data = {"user_id": 123, "active": True}
pickle_dump(data, "user_data.pkl")

# Happy Path: 讀取資料 (使用 Path 物件)
file_path = Path("user_data.pkl")
loaded_data = pickle_load(file_path)

# Advanced: 透傳參數 (指定 protocol)
pickle_dump(data, "data_v4.pkl", protocol=4)
```

## 4. 功能需求 (Functional Requirements)

### 4.1 核心邏輯 (Core Logic)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | **自動資源管理寫入**：使用 Context Manager 開啟檔案並執行 `pickle.dump`。 | 呼叫後檔案成功建立，內容為有效的 pickle 格式，且無 File Handle 殘留。 |
| **REQ-LOGIC-02** | **自動資源管理讀取**：使用 Context Manager 開啟檔案並執行 `pickle.load`。 | 能成功讀取有效的 pickle 檔案並還原物件，且無 File Handle 殘留。 |
| **REQ-LOGIC-03** | **多態路徑支援**：`path` 參數必須同時支援 `str` 與 `pathlib.Path` 型別。 | 傳入 `pathlib.Path` 物件時，讀寫操作行為與傳入字串路徑完全一致。 |
| **REQ-LOGIC-04** | **參數透傳機制**：支援透過 `**kwargs` 將參數直接傳遞給底層 `pickle` 函式。 | 當傳入 `protocol` 或 `encoding` 等參數時，生成的檔案或讀取行為應反映該參數的影響。 |

### 4.2 驗證與約束 (Validation)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-VAL-01** | **型別合規性**：介面必須嚴格遵守 Type Hints 定義 (`str | Path`)。 | 透過 Static Type Checker (如 mypy) 檢查時無錯誤；執行時若傳入不支援型別，允許底層 `open` 拋出 `TypeError`。 |

## 5. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy | Ref |
| :--- | :--- | :--- | :--- |
| `FileNotFoundError` | 讀取不存在的檔案路徑 | **透傳 (Propagate)** | **REQ-LOGIC-02** |
| `OSError` | 檔案系統層級錯誤 (如權限不足、無效路徑) | **透傳 (Propagate)** | **REQ-LOGIC-01** |
| `pickle.PickleError` | 物件無法序列化或檔案格式損毀 | **透傳 (Propagate)** | **REQ-LOGIC-01** |

## 6. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Environment | Python 3.12+ Syntax & Runtime support | **Ref: PNFR-ENV-01** |
| **NFR-02** | Type Safety | 100% Type Hint Coverage with Strict Mode | **Ref: PNFR-CDE-01** |
| **NFR-03** | Documentation | NumPy Style Docstrings for all exported functions | **Ref: PNFR-DOC-01** |
| **NFR-04** | Performance | Low Overhead (Thin Wrapper implementation) | **Ref: Feature NFR-04** |

## 7. 架構約束 (Architectural Constraints)

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-01** | **Isolation**: 禁止依賴 `businesssys` 或 `datasource` 層。 | 作為 `wutils` 底層元件，必須保持對業務邏輯的零依賴。 |
| **CONS-02** | **Encapsulation**: 實作檔必須為私有 (`_pickle_io.py`)。 | 僅透過 Container (`__init__.py`) 暴露功能，隱藏實作細節。 |
| **CONS-03** | **Dependency**: 僅依賴標準庫。 | 禁止引入任何第三方套件，以維持輕量化與高相容性。 |
| **CONS-04** | **Stateless**: 函式必須設計為 Pure Function (或接近)。 | 不應保存任何全域狀態，確保執行緒安全與可預測性。 |
