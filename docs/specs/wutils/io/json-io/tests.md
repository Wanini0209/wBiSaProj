# json-io - Test Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `json-io` |
| **Container Path** | `wutils/io` |
| **Parent Feature** | `json-io` |
| **Public Interface** | `wutils/io` (`__init__.py`) |
| **Test Type** | Unit Test |
| **Layer** | Library (No Business Dependencies) |

### 1.2 測試範圍 (Test Scope)

驗證 `json-io` 模組中的 `json_dump` 與 `json_load` 函式。重點在於確保跨平台的 UTF-8 編碼強制性、對 `pathlib.Path` 與 `str` 路徑型別的支援、底層資源的正確管理（Context Manager），以及標準庫 `json` 異常的正確透傳。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-02 | Initial Test Spec | Req: v1.0.0, Design: v1.0.0 |

## 3. 測試概述 (Test Overview)

### 3.1 驗證重點 (Verification Focus)

- 驗證寫入與讀取時是否強制使用 UTF-8 編碼 (包含非 ASCII 字元處理)。
- 驗證是否同時支援 `str` 與 `pathlib.Path` 路徑物件。
- 驗證資源管理機制 (確保檔案 Handle 被關閉)。
- 驗證參數透傳機制 (`kwargs` 傳遞至底層 `json` 函式)。
- 驗證異常情況下的透傳行為 (檔案不存在、格式錯誤、序列化失敗)。

### 3.2 測試策略 (Test Strategy)

- **方法**：黑箱測試，針對 Public API 進行功能驗證。
- **工具**：`pytest` + `pytest-cov`。
- **Mock 策略**：無需 Mock，使用 `tmp_path` 進行真實檔案 I/O 測試，以確保實際檔案操作行為符合預期。

## 4. 測試環境與配置 (Test Environment)

### 4.1 測試標記 (Markers)

- `@pytest.mark.unit`: 必須標記為單元測試。

### 4.2 Fixtures 規劃 (Fixtures Planning)

#### 4.2.1 Pytest 內建 Fixtures (Built-in Fixtures)

| Fixture Name | Scope | Usage |
| :--- | :--- | :--- |
| `tmp_path` | function | 提供獨立的臨時目錄，用於隔離檔案寫入與讀取測試 |

#### 4.2.2 自定義 Fixtures (Custom Fixtures)

| Fixture Name | Scope | Description |
| :--- | :--- | :--- |
| `sample_data` | function | 提供包含中文字元與巢狀結構的標準測試用字典物件 |

### 4.3 測試依賴項 (Test Dependencies)

#### 4.3.1 測試主體 (System Under Test)

| Component | Import Path | Description |
| :--- | :--- | :--- |
| `json_dump`, `json_load` | `from wutils.io import json_dump, json_load` | 測試主體 (SUT) |

#### 4.3.2 專案內部輔助依賴 (Internal Dependencies) [Optional]

無

#### 4.3.3 測試工具套件 (Test Utilities) [Optional]

無

## 5. 測試案例設計 (Test Cases)

### 5.1 json_dump 測試 (Dump Test Cases)

#### TC-DUMP-HAPPY-001: 強制 UTF-8 寫入

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-03** |
| **測試目標** | 驗證寫入包含非 ASCII (如中文) 的資料時，檔案以 UTF-8 編碼建立 |
| **前置條件** | 1. 準備包含中文的字典 `sample_data` <br> 2. 取得 `tmp_path` |
| **測試步驟** | 1. 定義目標路徑 `file_path = tmp_path / "utf8.json"` <br> 2. 呼叫 `json_dump(sample_data, file_path)` <br> 3. 使用 `pathlib` 讀取檔案 bytes 並解碼驗證 |
| **預期結果** | 檔案成功建立，且內容可被 UTF-8 正確解碼並包含預期中文字元 |
| **驗證方式 (Assertion)** | `assert file_path.read_text(encoding="utf-8") == json.dumps(...)` |

#### TC-DUMP-HAPPY-002: 支援字串路徑

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-02** |
| **測試目標** | 驗證 `json_dump` 接受 `str` 型別的路徑參數 |
| **前置條件** | 1. 準備簡單字典 `{"k": "v"}` <br> 2. 取得 `tmp_path` |
| **測試步驟** | 1. 定義字串路徑 `str_path = str(tmp_path / "str_path.json")` <br> 2. 呼叫 `json_dump(data, str_path)` |
| **預期結果** | 函式執行成功，且檔案存在於指定路徑 |
| **驗證方式 (Assertion)** | `assert Path(str_path).exists()` |

#### TC-DUMP-HAPPY-003: 參數透傳 (Indent)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-04** |
| **測試目標** | 驗證 `kwargs` (如 `indent`) 能正確傳遞給底層 `json.dump` |
| **前置條件** | 準備字典 `{"a": 1, "b": 2}` |
| **測試步驟** | 呼叫 `json_dump(data, path, indent=4)` |
| **預期結果** | 生成的檔案內容包含換行符號 `\n` 與縮排空格 |
| **驗證方式 (Assertion)** | `assert "\n    " in file_content` |

#### TC-DUMP-ERR-001: 不可序列化物件

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-05** |
| **測試目標** | 驗證傳入不可序列化物件 (如 `set`) 時，透傳底層的 `TypeError` |
| **前置條件** | 準備包含 `set` 的資料 `data = {"s": {1, 2}}` |
| **測試步驟** | 呼叫 `json_dump(data, path)` |
| **預期結果** | 拋出 `TypeError` |
| **驗證方式 (Assertion)** | `pytest.raises(TypeError)` |

### 5.2 json_load 測試 (Load Test Cases)

#### TC-LOAD-HAPPY-001: 強制 UTF-8 讀取

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-06**, **Rule-08** |
| **測試目標** | 驗證能正確讀取 UTF-8 編碼且包含中文字元的 JSON 檔案 |
| **前置條件** | 1. 建立檔案並寫入 UTF-8 JSON 字串 (含中文) |
| **測試步驟** | 呼叫 `loaded_data = json_load(file_path)` |
| **預期結果** | 讀回的 `loaded_data` 與原始資料一致，無亂碼 |
| **驗證方式 (Assertion)** | `assert loaded_data == original_data` |

#### TC-LOAD-HAPPY-002: 支援字串路徑

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-07** |
| **測試目標** | 驗證 `json_load` 接受 `str` 型別的路徑參數 |
| **前置條件** | 建立有效 JSON 檔案 |
| **測試步驟** | 呼叫 `json_load(str(file_path))` |
| **預期結果** | 成功讀取並回傳資料 |
| **驗證方式 (Assertion)** | `assert result is not None` |

#### TC-LOAD-ERR-001: 檔案不存在

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-08** |
| **測試目標** | 驗證讀取不存在檔案時，透傳 `FileNotFoundError` |
| **前置條件** | 確保路徑不存在 |
| **測試步驟** | 呼叫 `json_load(non_existent_path)` |
| **預期結果** | 拋出 `FileNotFoundError` |
| **驗證方式 (Assertion)** | `pytest.raises(FileNotFoundError)` |

#### TC-LOAD-ERR-002: JSON 格式錯誤

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-06** |
| **測試目標** | 驗證讀取非有效 JSON 格式檔案時，透傳 `json.JSONDecodeError` |
| **前置條件** | 建立內容為 `{invalid-json` 的檔案 |
| **測試步驟** | 呼叫 `json_load(invalid_file_path)` |
| **預期結果** | 拋出 `json.JSONDecodeError` |
| **驗證方式 (Assertion)** | `pytest.raises(json.JSONDecodeError)` |

### 5.3 整合測試 (Integration Tests)

#### TC-INT-HAPPY-001: 完整讀寫循環 (Round-Trip)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-02**, **Rule-06**, **Rule-07** |
| **測試目標** | 驗證 `dump` 寫入的複雜物件可被 `load` 無誤地讀回 |
| **前置條件** | 準備 `sample_data` 與 `tmp_path` |
| **測試步驟** | 1. `json_dump(sample_data, path)` <br> 2. `result = json_load(path)` |
| **預期結果** | `result` 與 `sample_data` 完全相等 (`==`) |
| **驗證方式 (Assertion)** | `assert result == sample_data` |

## 6. 測試矩陣 (Test Matrix)

### 6.1 規則覆蓋矩陣 (Rule Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **Rule-01** | **TC-DUMP-HAPPY-001**, **TC-INT-HAPPY-001** |
| **Rule-02** | **TC-DUMP-HAPPY-002**, **TC-INT-HAPPY-001** |
| **Rule-03** | **TC-DUMP-HAPPY-001** |
| **Rule-04** | **TC-DUMP-HAPPY-003** |
| **Rule-05** | **TC-DUMP-ERR-001** |
| **Rule-06** | **TC-LOAD-HAPPY-001**, **TC-LOAD-ERR-002**, **TC-INT-HAPPY-001** |
| **Rule-07** | **TC-LOAD-HAPPY-002**, **TC-INT-HAPPY-001** |
| **Rule-08** | **TC-LOAD-HAPPY-001**, **TC-LOAD-ERR-001** |
| **Rule-09** | **TC-INT-HAPPY-001** (隱含驗證) |

### 6.2 行為驗證覆蓋矩陣 (BV Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **BV-01** | **TC-DUMP-HAPPY-001** |
| **BV-02** | **TC-LOAD-HAPPY-001** |
| **BV-03** | **TC-DUMP-HAPPY-002**, **TC-LOAD-HAPPY-002** |
| **BV-04** | **TC-DUMP-HAPPY-003** |
| **BV-05** | **TC-DUMP-ERR-001** |
| **BV-06** | **TC-LOAD-ERR-001** |
| **BV-07** | **TC-LOAD-ERR-002** |

## 7. 實作指引 (Implementation Guide)

### 7.1 檔案位置 (File Location)

- **Target File**: `tests/wutils/io/json-io/test_json_io.py`

### 7.2 測試程式骨架 (Skeleton)

```python
import pytest
import json
from pathlib import Path
from typing import Any

# === 測試主體 (SUT) ===
# ⚠️ 必須從 FU Container 導入，禁止導入私有實作
from wutils.io import json_dump, json_load

@pytest.mark.unit
class TestJsonIO:
    """Test suite for json-io."""

    # --- 自定義 Fixtures ---

    @pytest.fixture
    def sample_data(self) -> dict[str, Any]:
        """提供包含中文字元與巢狀結構的標準測試用字典物件。"""
        ...

    # === json_dump Tests ===

    def test_tc_dump_happy_001_utf8_encoding(self, tmp_path, sample_data):
        """TC-DUMP-HAPPY-001: 強制 UTF-8 寫入。

        測試目標: 驗證寫入包含非 ASCII (如中文) 的資料時，檔案以 UTF-8 編碼建立
        預期結果: 檔案成功建立，且內容可被 UTF-8 正確解碼並包含預期中文字元
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_dump_happy_002_str_path(self, tmp_path):
        """TC-DUMP-HAPPY-002: 支援字串路徑。

        測試目標: 驗證 json_dump 接受 str 型別的路徑參數
        預期結果: 函式執行成功，且檔案存在於指定路徑
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_dump_happy_003_indent_passthrough(self, tmp_path):
        """TC-DUMP-HAPPY-003: 參數透傳 (Indent)。

        測試目標: 驗證 kwargs (如 indent) 能正確傳遞給底層 json.dump
        預期結果: 生成的檔案內容包含換行符號 \n 與縮排空格
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_dump_err_001_unserializable(self, tmp_path):
        """TC-DUMP-ERR-001: 不可序列化物件。

        測試目標: 驗證傳入不可序列化物件 (如 set) 時，透傳底層的 TypeError
        預期結果: 拋出 TypeError
        """
        # Arrange
        ...
        # Act & Assert
        ...

    # === json_load Tests ===

    def test_tc_load_happy_001_utf8_read(self, tmp_path, sample_data):
        """TC-LOAD-HAPPY-001: 強制 UTF-8 讀取。

        測試目標: 驗證能正確讀取 UTF-8 編碼且包含中文字元的 JSON 檔案
        預期結果: 讀回的 loaded_data 與原始資料一致，無亂碼
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_load_happy_002_str_path(self, tmp_path):
        """TC-LOAD-HAPPY-002: 支援字串路徑。

        測試目標: 驗證 json_load 接受 str 型別的路徑參數
        預期結果: 成功讀取並回傳資料
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_load_err_001_file_not_found(self, tmp_path):
        """TC-LOAD-ERR-001: 檔案不存在。

        測試目標: 驗證讀取不存在檔案時，透傳 FileNotFoundError
        預期結果: 拋出 FileNotFoundError
        """
        # Arrange
        ...
        # Act & Assert
        ...

    def test_tc_load_err_002_invalid_json(self, tmp_path):
        """TC-LOAD-ERR-002: JSON 格式錯誤。

        測試目標: 驗證讀取非有效 JSON 格式檔案時，透傳 json.JSONDecodeError
        預期結果: 拋出 json.JSONDecodeError
        """
        # Arrange
        ...
        # Act & Assert
        ...

    # === Integration Tests ===

    def test_tc_int_happy_001_round_trip(self, tmp_path, sample_data):
        """TC-INT-HAPPY-001: 完整讀寫循環 (Round-Trip)。

        測試目標: 驗證 dump 寫入的複雜物件可被 load 無誤地讀回
        預期結果: result 與 sample_data 完全相等 (==)
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
pytest tests/wutils/io/json-io/test_json_io.py -v -m unit

# 執行並產生覆蓋率報告
pytest tests/wutils/io/json-io/test_json_io.py -v --cov=wutils/io --cov-report=term-missing
```

### 7.4 注意事項 (Implementation Notes)

- **跨平台相容性**：所有檔案 I/O 測試必須使用 `tmp_path` fixture，嚴禁硬編碼路徑。
- **編碼驗證**：驗證 `json_dump` 的 UTF-8 行為時，建議使用 `path.read_text(encoding="utf-8")` 讀取並檢查內容。

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
- [ ] **結構一致性**：測試檔案存放路徑嚴格遵循「結構對應性原則」(`tests/wutils/io/json-io/`)。
