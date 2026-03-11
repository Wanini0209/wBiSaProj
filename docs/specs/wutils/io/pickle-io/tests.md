# pickle-io - Test Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `pickle-io` |
| **Container Path** | `wutils/io` |
| **Parent Feature** | `pickle-io` |
| **Public Interface** | `wutils/io` (`__init__.py`) |
| **Test Type** | Unit Test |
| **Layer** | Library (No Business Dependencies) |

### 1.2 測試範圍 (Test Scope)

本測試規格旨在驗證 `pickle-io` 單元所提供的序列化與反序列化封裝功能。範圍涵蓋：
1.  **核心功能**：驗證 `pickle_dump` 與 `pickle_load` 在不同情境下的資料完整性。
2.  **資源管理**：確保檔案 Handle 在操作後能正確釋放 (Context Manager 行為)。
3.  **多態支援**：驗證路徑參數對 `str` 與 `pathlib.Path` 的支援一致性。
4.  **參數透傳**：驗證額外參數 (如 `protocol`) 能正確傳遞至底層 `pickle` 函式。
5.  **異常處理**：驗證檔案不存在、序列化失敗等異常情境的透傳行為。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-12-30 | Initial Test Spec | Req: v1.0.0, Design: v1.0.0 |

## 3. 測試概述 (Test Overview)

### 3.1 驗證重點 (Verification Focus)

- 驗證 `pickle_dump` 能正確建立檔案並寫入序列化資料
- 驗證 `pickle_load` 能從檔案讀取並還原 Python 物件
- 驗證兩者皆能接受 `str` 與 `pathlib.Path` 型別的路徑參數
- 驗證 `kwargs` 參數能正確影響底層 `pickle` 行為 (例如指定 protocol)
- 驗證在檔案 I/O 錯誤或 Pickle 錯誤時能正確拋出標準例外

### 3.2 測試策略 (Test Strategy)

- **方法**：黑箱測試，針對 Public API 進行功能驗證
- **工具**：`pytest` + `pytest-cov`
- **Mock 策略**：
    - 主要使用 `tmp_path` 進行真實檔案 I/O 測試，不需 Mock 檔案系統。
    - 針對序列化錯誤測試，使用自定義的不可序列化物件 (Unpicklable Object)。

## 4. 測試環境與配置 (Test Environment)

### 4.1 測試標記 (Markers)

- `@pytest.mark.unit`: 必須標記為單元測試。

### 4.2 Fixtures 規劃 (Fixtures Planning)

#### 4.2.1 Pytest 內建 Fixtures (Built-in Fixtures)

| Fixture Name | Scope | Usage |
| :--- | :--- | :--- |
| `tmp_path` | function | 提供獨立的臨時目錄，用於隔離檔案寫入與讀取測試，確保不殘留檔案 |

#### 4.2.2 自定義 Fixtures (Custom Fixtures)

| Fixture Name | Scope | Description |
| :--- | :--- | :--- |
| `sample_dict` | function | 提供標準測試用的字典資料 (`{"key": "value", "num": 123}`) |
| `complex_data` | function | 提供包含巢狀結構的測試資料，用於 Round-Trip 測試 |

### 4.3 測試依賴項 (Test Dependencies)

#### 4.3.1 測試主體 (System Under Test)

| Component | Import Path | Description |
| :--- | :--- | :--- |
| `pickle_dump`, `pickle_load` | `from wutils.io import pickle_dump, pickle_load` | 測試主體 (SUT) |

#### 4.3.2 專案內部輔助依賴 (Internal Dependencies)

無

#### 4.3.3 測試工具套件 (Test Utilities)

無

## 5. 測試案例設計 (Test Cases)

### 5.1 序列化寫入 (pickle_dump)

#### TC-DUMP-HAPPY-001: 基礎字串路徑寫入

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-02** |
| **測試目標** | 驗證傳入字串路徑時，能正確建立檔案並寫入資料 |
| **前置條件** | 1. 準備 `sample_dict` <br> 2. 定義目標路徑字串 `path_str = str(tmp_path / "test.pkl")` |
| **測試步驟** | 呼叫 `pickle_dump(sample_dict, path_str)` |
| **預期結果** | 目標路徑檔案存在，且檔案大小大於 0 |
| **驗證方式 (Assertion)** | `assert os.path.exists(path_str)` |

#### TC-DUMP-HAPPY-002: Path 物件路徑寫入

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-02** |
| **測試目標** | 驗證傳入 `pathlib.Path` 物件時，行為與字串路徑一致 |
| **前置條件** | 1. 準備 `sample_dict` <br> 2. 定義目標路徑物件 `path_obj = tmp_path / "test_path.pkl"` |
| **測試步驟** | 呼叫 `pickle_dump(sample_dict, path_obj)` |
| **預期結果** | 目標路徑檔案存在 |
| **驗證方式 (Assertion)** | `assert path_obj.exists()` |

#### TC-DUMP-HAPPY-003: 參數透傳 (Protocol)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-03** |
| **測試目標** | 驗證 `kwargs` 能正確傳遞給底層 `pickle.dump` (指定 protocol) |
| **前置條件** | 1. 準備 `sample_dict` <br> 2. 指定 `protocol=3` |
| **測試步驟** | 呼叫 `pickle_dump(sample_dict, tmp_path / "proto3.pkl", protocol=3)` |
| **預期結果** | 檔案成功建立，且內容符合指定 protocol 格式 |
| **驗證方式 (Assertion)** | 讀取檔案 bytes 並檢查 pickle header 或嘗試以該 protocol 讀取確認無誤 |

#### TC-DUMP-ERR-001: 寫入不可序列化物件

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01** (Exception Mapping) |
| **測試目標** | 驗證寫入無法序列化的物件時，正確拋出 `pickle.PickleError` 或其子類 |
| **前置條件** | 準備一個含 lambda 或打開的 file handle 的物件 (不可序列化) |
| **測試步驟** | 呼叫 `pickle_dump(unpicklable_obj, tmp_path / "fail.pkl")` |
| **預期結果** | 拋出 `pickle.PickleError` (或 `AttributeError`/`TypeError` 視實作而定，依賴標準庫行為) |
| **驗證方式 (Assertion)** | `pytest.raises((pickle.PickleError, AttributeError, TypeError))` |

### 5.2 反序列化讀取 (pickle_load)

#### TC-LOAD-HAPPY-001: 基礎讀取還原

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-04**, **Rule-05** |
| **測試目標** | 驗證能從現有檔案正確讀取並還原物件 (使用 Path 物件) |
| **前置條件** | 先手動建立一個有效的 pickle 檔案 `valid.pkl` (含 `sample_dict` 內容) |
| **測試步驟** | 呼叫 `result = pickle_load(tmp_path / "valid.pkl")` |
| **預期結果** | `result` 內容與 `sample_dict` 相等 |
| **驗證方式 (Assertion)** | `assert result == sample_dict` |

#### TC-LOAD-HAPPY-002: 參數透傳 (Encoding)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-06** |
| **測試目標** | 驗證 `kwargs` 能正確傳遞給底層 `pickle.load` |
| **前置條件** | 準備一個已存在的 pickle 檔案 |
| **測試步驟** | 呼叫 `pickle_load(path, encoding='ASCII', errors='strict')` |
| **預期結果** | 讀取過程無錯誤 (若資料相容) 或行為受參數影響 |
| **驗證方式 (Assertion)** | 驗證呼叫成功且返回預期物件 |

#### TC-LOAD-ERR-001: 讀取不存在檔案

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-04** (Exception Mapping) |
| **測試目標** | 驗證讀取不存在檔案時拋出 `FileNotFoundError` |
| **前置條件** | 確保路徑 `tmp_path / "ghost.pkl"` 不存在 |
| **測試步驟** | 呼叫 `pickle_load(tmp_path / "ghost.pkl")` |
| **預期結果** | 拋出 `FileNotFoundError` |
| **驗證方式 (Assertion)** | `pytest.raises(FileNotFoundError)` |

### 5.3 整合測試 (Integration Tests)

#### TC-INT-HAPPY-001: 完整讀寫循環 (Round-Trip)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-04** |
| **測試目標** | 驗證物件經過 Dump 後再 Load，資料內容保持一致 (End-to-End) |
| **前置條件** | 準備 `complex_data` (含 List, Dict 等巢狀結構) |
| **測試步驟** | 1. `pickle_dump(complex_data, tmp_path / "cycle.pkl")` <br> 2. `result = pickle_load(tmp_path / "cycle.pkl")` |
| **預期結果** | `result` 與 `complex_data` 內容完全一致 |
| **驗證方式 (Assertion)** | `assert result == complex_data` |

## 6. 測試矩陣 (Test Matrix)

### 6.1 規則覆蓋矩陣 (Rule Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **Rule-01** | **TC-DUMP-HAPPY-001**, **TC-DUMP-HAPPY-002**, **TC-DUMP-ERR-001**, **TC-INT-HAPPY-001** |
| **Rule-02** | **TC-DUMP-HAPPY-001**, **TC-DUMP-HAPPY-002** |
| **Rule-03** | **TC-DUMP-HAPPY-003** |
| **Rule-04** | **TC-LOAD-HAPPY-001**, **TC-LOAD-ERR-001**, **TC-INT-HAPPY-001** |
| **Rule-05** | **TC-LOAD-HAPPY-001** |
| **Rule-06** | **TC-LOAD-HAPPY-002** |

### 6.2 行為驗證覆蓋矩陣 (BV Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **BV-01** | **TC-DUMP-HAPPY-001** |
| **BV-02** | **TC-LOAD-HAPPY-001** |
| **BV-03** | **TC-DUMP-HAPPY-003** |
| **BV-04** | **TC-LOAD-ERR-001** |
| **BV-05** | **TC-DUMP-ERR-001** |

## 7. 實作指引 (Implementation Guide)

### 7.1 檔案位置 (File Location)

- **Target File**: `tests/wutils/io/pickle-io/test_pickle_io.py`

### 7.2 測試程式骨架 (Skeleton)

```python
import pytest
import pickle
import os
from pathlib import Path

# === 測試主體 (SUT) ===
# ⚠️ 必須從 FU Container 導入，禁止導入私有實作
from wutils.io import pickle_dump, pickle_load

@pytest.mark.unit
class TestPickleIO:
    """Test suite for pickle-io."""

    # --- 自定義 Fixtures ---

    @pytest.fixture
    def sample_dict(self):
        """提供標準測試用的字典資料。"""
        ...

    @pytest.fixture
    def complex_data(self):
        """提供包含巢狀結構的測試資料，用於 Round-Trip 測試。"""
        ...

    # === Happy Path (主流程) ===

    def test_tc_dump_happy_001_basic_str_path(self, tmp_path, sample_dict):
        """TC-DUMP-HAPPY-001: 基礎字串路徑寫入。

        測試目標: 驗證傳入字串路徑時，能正確建立檔案並寫入資料
        預期結果: 目標路徑檔案存在，且檔案大小大於 0
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_dump_happy_002_path_obj_write(self, tmp_path, sample_dict):
        """TC-DUMP-HAPPY-002: Path 物件路徑寫入。

        測試目標: 驗證傳入 pathlib.Path 物件時，行為與字串路徑一致
        預期結果: 目標路徑檔案存在
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_dump_happy_003_kwargs_protocol(self, tmp_path, sample_dict):
        """TC-DUMP-HAPPY-003: 參數透傳 (Protocol)。

        測試目標: 驗證 kwargs 能正確傳遞給底層 pickle.dump (指定 protocol)
        預期結果: 檔案成功建立，且內容符合指定 protocol 格式
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_load_happy_001_basic_read(self, tmp_path, sample_dict):
        """TC-LOAD-HAPPY-001: 基礎讀取還原。

        測試目標: 驗證能從現有檔案正確讀取並還原物件 (使用 Path 物件)
        預期結果: result 內容與 sample_dict 相等
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_load_happy_002_kwargs_encoding(self, tmp_path, sample_dict):
        """TC-LOAD-HAPPY-002: 參數透傳 (Encoding)。

        測試目標: 驗證 kwargs 能正確傳遞給底層 pickle.load
        預期結果: 讀取過程無錯誤 (若資料相容) 或行為受參數影響
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    # === Error Handling (錯誤處理) ===

    def test_tc_dump_err_001_unpicklable(self, tmp_path):
        """TC-DUMP-ERR-001: 寫入不可序列化物件。

        測試目標: 驗證寫入無法序列化的物件時，正確拋出 pickle.PickleError 或其子類
        預期結果: 拋出 pickle.PickleError
        """
        # Arrange
        ...
        # Act & Assert
        ...

    def test_tc_load_err_001_file_not_found(self, tmp_path):
        """TC-LOAD-ERR-001: 讀取不存在檔案。

        測試目標: 驗證讀取不存在檔案時拋出 FileNotFoundError
        預期結果: 拋出 FileNotFoundError
        """
        # Arrange
        ...
        # Act & Assert
        ...

    # === Integration Tests (整合測試) ===

    def test_tc_int_happy_001_round_trip(self, tmp_path, complex_data):
        """TC-INT-HAPPY-001: 完整讀寫循環 (Round-Trip)。

        測試目標: 驗證物件經過 Dump 後再 Load，資料內容保持一致 (End-to-End)
        預期結果: result 與 complex_data 內容完全一致
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...
```

### 7.3 執行指令 (Execution Commands)

```bash
# 執行本 FU 的單元測試
pytest tests/wutils/io/pickle-io/test_pickle_io.py -v -m unit

# 執行並產生覆蓋率報告
pytest tests/wutils/io/pickle-io/test_pickle_io.py -v --cov=wutils/io --cov-report=term-missing
```

### 7.4 注意事項 (Implementation Notes)

- **跨平台相容性**：檔案路徑操作請務必依賴 `pathlib` 與 `tmp_path` fixture，避免使用 OS 相關的路徑分隔符。
- **異常模擬**：在測試 `TC-DUMP-ERR-001` 時，可使用含有 `lambda` 的字典作為不可序列化輸入。
- **資源清理**：`tmp_path` 會自動清理，不需手動刪除測試產生的檔案。

## 8. 驗收標準 (Acceptance Criteria)

- [ ] **覆蓋完整性**：所有定義的 TC (Test Cases) 均已轉化為測試程式碼，且完整覆蓋 `design.md` 中的所有 `Rule-XX`。
- [ ] **導入路徑合規 (架構紅線)**：
    - [ ] **SUT 導入**：測試主體 (System Under Test) 必須嚴格從 FU Container (`__init__.py`) 導入。
    - [ ] **私有禁令**：嚴格禁止直接導入 `_` 開頭的私有實作模組。
- [ ] **測試執行品質**：
    - [ ] `pytest` 執行全數通過 (Green Light)。
    - [ ] 測試標記正確：所有單元測試均已加上 `@pytest.mark.unit`。
- [ ] **環境與隔離**：
    - [ ] **資源隔離**：檔案 I/O 必須使用 `tmp_path`，且測試後不留下任何殘留檔案。
    - [ ] **無副作用**：測試不依賴也不會修改全域狀態或外部環境。
- [ ] **結構一致性**：測試檔案存放路徑嚴格遵循「結構對應性原則」(`tests/wutils/io/pickle-io/`)。
