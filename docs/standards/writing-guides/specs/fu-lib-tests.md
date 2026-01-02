# Library Functional Unit (FU) Specs - Tests Guide

本規範定義 Library 型 **Functional Unit (FU)** 在 `specs` 層級的 `tests.md` 撰寫規範。目標是定義測試規格，指導開發者撰寫具體的測試程式碼，作為 TDD 流程的關鍵輸入。

*供 Generator: Prompt4NewLibFuTestSpec 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件定義測試規格，指導開發者撰寫具體的測試程式碼，是 TDD 流程的關鍵輸入。

### 1.2 測試策略

> 對於 Library FU，我們採用 **標準 TDD (Standard TDD)** 策略。

- **測試對象**：針對 FU Container 的 **公開介面 (Public Interface)** 進行黑箱測試。
- **隔離性**：單元測試應獨立執行，不依賴外部環境（如真實資料庫、網路），必要時使用 Mock。
- **覆蓋率**：Library 元件通常被廣泛引用，要求高覆蓋率（通常 > 90%）。

### 1.3 結構對應性原則

測試規格書必須明確指引測試程式碼的實體位置，嚴格遵循專案的結構對應規則：

- **Spec**: `docs/specs/<fu_path>/<fu_name>/tests.md`
- **Test Code**: `tests/<fu_path>/<fu_name>/test_<name>.py`

---

## 2. 檔案路徑標準

`docs/specs/<fu_path>/<fu_name>/tests.md`

- `<fu_path>`: FU Container 路徑 (e.g., `core/utils`)
- `<fu_name>`: FU 名稱 (e.g., `date_parser`)

---

## 3. ID 命名規範

> **⚠️ 重要**：以下 ID 格式為全專案統一規範，必須嚴格遵守。

### 3.1 本文件定義 ID

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `TC-<SCOPE>-HAPPY-XXX` | Happy Path Test Case（三位數流水號） | §5 測試案例設計 |
| `TC-<SCOPE>-EDGE-XXX` | Edge Case Test Case（三位數流水號） | §5 測試案例設計 |
| `TC-<SCOPE>-ERR-XXX` | Error Handling Test Case（三位數流水號） | §5 測試案例設計 |
| `TC-INT-HAPPY-XXX` | Integration Test Case（三位數流水號） | §5 測試案例設計 |

> **TC ID 命名規則**：`TC-<FUNCTION_SCOPE>-<TYPE>-XXX`
>
> | 組成部分 | 說明 | 範例 |
> | :--- | :--- | :--- |
> | `FUNCTION_SCOPE` | 對應的函式或方法範圍 | `DUMP`, `LOAD`, `PARSE` |
> | `TYPE` | 測試類型 | `HAPPY`, `EDGE`, `ERR` |
> | `XXX` | 三位數流水號 | `001`, `002` |

### 3.2 引用 ID（來自 design.md）

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `Rule-XX` | Behavioral Rule | §5 測試案例設計 (Primary Verification Target) |
| `BV-XX` | Behavior Verification | §6 測試矩陣 (Scenario Mapping) |

> **💡 追溯性說明 (Traceability Note)**：
> 本測試規格採用 **間接追溯 (Indirect Traceability)** 策略：
> 1. **Tests 驗證 Design**：測試案例 (TC) 直接對應 Design 中的行為規則 (`Rule-XX`)。
> 2. **Design 滿足 Requirements**：Design 文件中的規則已在該文件的「需求追溯矩陣」中映射回需求 (`REQ-XX`)。
>
> 因此，**本文件不直接引用 `REQ-XX` ID**，以確保層級職責分明。

---

## 4. 內容結構模板

````markdown
# <FU Name> - Test Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `<fu_name>` |
| **Container Path** | `<fu_path>` |
| **Public Interface** | `<fu_path>` (`__init__.py`) |
| **Test Type** | Unit Test |
| **Layer** | Library (No Business Dependencies) |

### 1.2 測試範圍 (Test Scope)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 簡述本測試規格的驗證目標與覆蓋範圍。
>
> **💡 範例**：
>
> 「驗證 PickleIO 類別在正常讀寫、檔案不存在、權限錯誤等情境下的行為正確性，確保資源能被正確釋放，並驗證產生檔案的編碼符合 UTF-8 標準。」

<填入測試範圍>

## 2. 變更歷史 (Change History)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 記錄版本變更，Source 欄位必須**嚴格追溯**到對應的 **Requirements 與 Design 版本**。
>
> **Source 格式**：`Req: vX.Y.Z, Design: vX.Y.Z`
> **版本號格式**：`vX.Y.Z`（語意化版本）
>
> **💡 範例**：
>
> | Version | Date | Description | Source |
> | :--- | :--- | :--- | :--- |
> | v1.0.0 | 2024-01-15 | Initial Test Spec | Req: v1.0.0, Design: v1.0.0 |
> | v1.1.0 | 2024-02-01 | 新增 pathlib 測試案例 | Req: v1.1.0, Design: v1.1.0 |

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | <YYYY-MM-DD> | Initial Test Spec | Req: v<Ver>, Design: v<Ver> |

## 3. 測試概述 (Test Overview)

### 3.1 驗證重點 (Verification Focus)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 簡述本測試規格的主要驗證目標，以條列方式呈現。
>
> **💡 範例**：
>
> - 驗證正常讀寫流程的資料完整性
> - 驗證資源釋放機制（檔案正確關閉）
> - 驗證異常輸入時的錯誤處理行為

- <填入驗證重點>

### 3.2 測試策略 (Test Strategy)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義測試方法與工具。
>
> **💡 範例**：
>
> - **方法**：黑箱測試，針對 Public API 進行功能驗證
> - **工具**：`pytest` + `pytest-cov`
> - **Mock 策略**：
>   - 範例 A：「無需 Mock，使用 `tmp_path` 進行真實檔案 I/O 測試」
>   - 範例 B：「Mock 外部 API 呼叫，使用 `unittest.mock.patch` 隔離網路依賴」

- **方法**：<填入測試方法>
- **工具**：`pytest` + `pytest-cov`
- **Mock 策略**：<填入 Mock 策略>

## 4. 測試環境與配置 (Test Environment)

### 4.1 測試標記 (Markers)

> **📝 撰寫指引**（請勿保留本指引文字）：
> Library FU 必須標記為單元測試。

- `@pytest.mark.unit`: 必須標記為單元測試。

### 4.2 Fixtures 規劃 (Fixtures Planning)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義測試所需的共用資源或資料準備。
> - **Pytest 內建 Fixtures**：不需要 import，直接在 test function 參數中宣告即可使用
> - **自定義 Fixtures**：本測試檔案中定義的 fixtures，用於準備測試資料或共用資源

#### 4.2.1 Pytest 內建 Fixtures (Built-in Fixtures)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出本測試會使用的 pytest 內建 fixtures。這些 fixtures 不需要 import，直接宣告即可。
> 若不使用任何內建 fixture，可標註「無」或省略此表格。
>
> **常用內建 Fixtures 參考**：
> - **`tmp_path`**: 提供臨時目錄路徑 (pathlib.Path)，測試結束後自動清理
> - **`tmp_path_factory`**: 提供建立多個臨時目錄的工廠
> - **`monkeypatch`**: 動態修改物件、字典、環境變數
> - **`capsys`**: 擷取 stdout/stderr 輸出
> - **`caplog`**: 擷取 logging 輸出
>
> **💡 範例**：
>
> | Fixture Name | Scope | Usage |
> | :--- | :--- | :--- |
> | `tmp_path` | function | 提供獨立的臨時目錄，用於隔離檔案寫入測試，避免汙染環境 |
> | `caplog` | function | 驗證函式在錯誤發生時是否正確記錄了 Error 層級的 Log |

| Fixture Name | Scope | Usage |
| :--- | :--- | :--- |
| <fixture_name> | <scope> | <填入 Fixture 用途> |

#### 4.2.2 自定義 Fixtures (Custom Fixtures)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出本測試中需要定義的自定義 fixtures。
> 若無自定義 fixtures，可標註「無」或省略此表格。
>
> **💡 範例**：
>
> | Fixture Name | Scope | Description |
> | :--- | :--- | :--- |
> | `sample_dict` | function | 提供標準測試用字典物件 |
> | `large_object` | module | 提供大型物件以測試效能邊界 |

| Fixture Name | Scope | Description |
| :--- | :--- | :--- |
| <fixture_name> | <scope> | <填入 Fixture 描述> |

### 4.3 測試依賴項 (Test Dependencies)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節明確列出測試實作中**需要 import** 的所有元件，確保 Generator 生成正確的導入語句。
>
> **⚠️ 重要區分**：
> - **不需要 import 的項目**（如 `tmp_path`, `monkeypatch` 等 pytest 內建 fixtures）請放在 **Section 4.2**
> - **需要 import 的項目**才放在本節
>
> **分類原則**：
> - **測試主體 (SUT)**：本測試所驗證的核心公開介面，**必須**從 FU Container 導入
> - **專案內部輔助**：來自專案級 Library (`core`, `wutils`) 或同系統內其他 FU Container 的元件
> - **測試工具套件**：專案提供的共用測試輔助工具（如共用 fixtures、mock builders）
>
> **⚠️ 導入紅線**：
> - 禁止從私有實作模組導入（如 `_module.py` 或 `_impl/`）
> - 所有導入路徑必須指向 FU Container 的公開介面（`__init__.py`）
>
> **💡 範例 (各類依賴項寫法參考)**：
>
> **4.3.1 測試主體 (SUT)**
> | Component | Import Path | Description |
> | :--- | :--- | :--- |
> | `pickle_dump`, `pickle_load` | `from wutils.io import pickle_dump, pickle_load` | 測試主體 (SUT) |
>
> **4.3.2 專案內部輔助**
> | Component | Import Path | Usage |
> | :--- | :--- | :--- |
> | `UserStatus` | `from core.enums import UserStatus` | 用於設定測試資料的狀態欄位 |
> | `DateHelper` | `from wutils.time import DateHelper` | 用於產生測試用的時間戳記 |
>
> **4.3.3 測試工具套件**
> | Component | Import Path | Usage |
> | :--- | :--- | :--- |
> | `mock_db_session` | `from tests.fixtures.db import mock_db_session` | 共用的資料庫 mock fixture |
> | `mock_s3` | `from tests.fixtures.aws import mock_s3` | 模擬 S3 連線 |

#### 4.3.1 測試主體 (System Under Test)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出本測試所驗證的核心公開介面。這些是測試的「主角」，必須從 FU Container 的 `__init__.py` 導入。

| Component | Import Path | Description |
| :--- | :--- | :--- |
| <Component_1>, <Component_2>, ... | `from <fu_path> import ...` | <填入描述> |

#### 4.3.2 專案內部輔助依賴 (Internal Dependencies) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出來自專案級 Library (`core`, `wutils`) 或同系統內其他 FU Container 的輔助元件。
> 這些元件用於：建構測試資料、輔助斷言、或提供測試所需的領域物件。
> 若無內部輔助依賴，可標註「無」或省略此表格。

| Component | Import Path | Usage |
| :--- | :--- | :--- |
| <HelperComponent_1>, ... | `from <source_path> import ...` | <填入用途> |

#### 4.3.3 測試工具套件 (Test Utilities) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出專案提供的共用測試輔助工具，如共用 fixtures、mock builders、或測試用的 factory functions。
> 若無專案級共用測試工具，可標註「無」或省略此表格。

| Component | Import Path | Usage |
| :--- | :--- | :--- |
| <TestUtility_1>, ... | `from tests.<path> import ...` | <填入用途> |

## 5. 測試案例設計 (Test Cases)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本章節為 TDD 實作的核心依據。
> - 請依據 `design.md` 中的 **行為契約 (Behavioral Contracts)** 進行設計。
> - 每個案例必須追溯到 `design.md` 中對應的 `Rule-XX`。
> - **分層撰寫**：若 FU 具有多個公開介面 (例如 `dump` 和 `load`)，請分章節撰寫 (例如 5.1.1 針對 Dump, 5.1.2 針對 Load)。

### 5.1 主流程 (Happy Path)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 驗證功能在正常輸入下的預期行為。
>
> **💡 範例**：
>
> #### TC-DUMP-HAPPY-001: 基本字典序列化
>
> | Attribute | Description |
> | :--- | :--- |
> | **對應規則** | `design.md` **Rule-01**, **Rule-02** |
> | **測試目標** | 驗證基本 Python 字典可被正確序列化並寫入檔案 |
> | **前置條件** | 1. 準備測試用字典 `{"key": "value"}` <br> 2. 取得 `tmp_path` 臨時目錄 |
> | **測試步驟** | 1. 呼叫 `pickle_dump(data, tmp_path / "test.pkl")` <br> 2. 檢查檔案是否建立 |
> | **預期結果** | 檔案成功建立於指定路徑 |
> | **驗證方式 (Assertion)** | `assert (tmp_path / "test.pkl").exists()` |

#### TC-<SCOPE>-HAPPY-001: <測試案例名稱>

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-XX** |
| **測試目標** | <填入驗證目標> |
| **前置條件** | <填入前置條件 / 資料準備> |
| **測試步驟** | <填入測試步驟> |
| **預期結果** | <填入預期結果(輸出、狀態或行為)> |
| **驗證方式 (Assertion)** | <填入斷言方式> |

### 5.2 邊界案例 (Edge Cases)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 驗證極限值、空值、None、特殊格式或複雜的組合輸入。
>
> **💡 範例**：
>
> #### TC-DUMP-EDGE-001: 空字典序列化
>
> | Attribute | Description |
> | :--- | :--- |
> | **對應規則** | `design.md` **Rule-01** |
> | **測試目標** | 驗證空字典 `{}` 能被正常序列化且不拋出錯誤 |
> | **前置條件** | 1. 準備空字典 `data = {}` <br> 2. 取得 `tmp_path` |
> | **測試步驟** | 1. 呼叫 `pickle_dump(data, tmp_path / "empty.pkl")` <br> 2. 讀取該檔案確認內容 |
> | **預期結果** | 檔案存在且讀回後為空字典 `{}` |
> | **驗證方式 (Assertion)** | `assert loaded_data == {}` |

#### TC-<SCOPE>-EDGE-001: <測試案例名稱>

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` Rule-XX |
| **測試目標** | <填入驗證目標> |
| **前置條件** | <填入前置條件 / 資料準備> |
| **測試步驟** | <填入測試步驟>|
| **預期結果** | <填入預期結果(輸出、狀態或行為)> |
| **驗證方式 (Assertion)** | <填入斷言方式> |

### 5.3 錯誤處理 (Error Handling)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 驗證異常輸入是否正確拋出指定錯誤，並檢查錯誤訊息是否包含關鍵字。
>
> **💡 範例**：
>
> #### TC-LOAD-ERR-001: 讀取不存在的檔案
>
> | Attribute | Description |
> | :--- | :--- |
> | **對應規則** | `design.md` **Rule-05** |
> | **測試目標** | 驗證讀取不存在檔案時會拋出正確的標準例外 |
> | **前置條件** | 確保路徑 `tmp_path / "non_existent.pkl"` 不存在 |
> | **測試步驟** | 呼叫 `pickle_load(tmp_path / "non_existent.pkl")` |
> | **預期結果** | 拋出 `FileNotFoundError` |
> | **驗證方式 (Assertion)** | `pytest.raises(FileNotFoundError, match="No such file")` |

#### TC-<SCOPE>-ERR-001: <測試案例名稱>

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` Rule-XX |
| **測試目標** | <填入驗證目標> |
| **前置條件** | <填入前置條件 / 資料準備> |
| **測試步驟** | <填入測試步驟> |
| **預期結果** | 拋出 **`<例外類型>`** |
| **驗證方式 (Assertion)** | `pytest.raises(<例外類型>, match="<關鍵字>")` |

### 5.4 整合測試 (Integration Tests) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 驗證多個公開介面協作的案例（例如，`dump` 後 `load` 的完整 Round-Trip）。
>
> **💡 範例**：
>
> #### TC-INT-HAPPY-001: 完整讀寫循環 (Round-Trip)
>
> | Attribute | Description |
> | :--- | :--- |
> | **對應規則** | `design.md` **Rule-01**, **Rule-02** |
> | **測試目標** | 驗證寫入的物件可以被原本無誤地讀回 (End-to-End) |
> | **前置條件** | 準備複雜物件 (含 List, Dict) |
> | **測試步驟** | 1. 呼叫 `dump` 寫入檔案 <br> 2. 呼叫 `load` 讀取同一檔案 |
> | **預期結果** | 讀回的物件與原始物件完全相等 (`==`) |
> | **驗證方式 (Assertion)** | `assert original_obj == loaded_obj` |

#### TC-INT-HAPPY-001: <測試案例名稱>

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-XX** |
| **測試目標** | <填入驗證目標> |
| **前置條件** | <填入前置條件 / 資料準備> |
| **測試步驟** | 1. <填入測試步驟 1> <br> 2. <填入測試步驟 2> |
| **預期結果** | <填入預期結果(輸出、狀態或行為)> |
| **驗證方式 (Assertion)** | <填入斷言方式> |

## 6. 測試矩陣 (Test Matrix)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 總結所有 TC 與對應設計規則的追溯關係，確保完全覆蓋。

### 6.1 規則覆蓋矩陣 (Rule Coverage Matrix)

> **💡 範例**：
>
> | ID | Related Test Cases |
> | :--- | :--- |
> | **Rule-01** | **TC-DUMP-HAPPY-001**, **TC-INT-HAPPY-001** |
> | **Rule-02** | **TC-LOAD-HAPPY-001**, **TC-INT-HAPPY-001** |
> | **Rule-03** | **TC-DUMP-EDGE-001** |

| ID | Related Test Cases |
| :--- | :--- |
| **Rule-XX** | **TC-XX**, **TC-XX** |

### 6.2 行為驗證覆蓋矩陣 (BV Coverage Matrix)

> **💡 範例**：
>
> | ID | Related Test Cases |
> | :--- | :--- |
> | **BV-01** | **TC-DUMP-EDGE-001** |

| ID | Related Test Cases |
| :--- | :--- |
| **BV-XX** | **TC-XX** |

## 7. 實作指引 (Implementation Guide)

本節提供測試程式碼的骨架，確保「結構對應性」與「正確的 Import 路徑」。

### 7.1 檔案位置 (File Location)

> **💡 範例**：
>
> * **Target File**: `tests/wutils/io/pickle-io/test_pickle_io.py`

- **Target File**: `tests/<fu_path>/<fu_name>/test_<name>.py`

### 7.2 測試程式骨架 (Skeleton)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節僅需提供 **結構性** 的程式碼骨架，**嚴禁** 撰寫具體的實作邏輯與斷言 (Assertion)。
>
> **📌 職責邊界**：
> - **Section 5 (測試案例設計)**：定義 *What* — 測試什麼、預期什麼結果、如何驗證
> - **Section 7.2 (測試程式骨架)**：定義 *Where* — 程式碼結構、檔案位置、Import 來源
> - **實作階段 (test_*.py)**：實現 *How* — 根據 Section 5 的規格填入具體邏輯
>
> **規範要求**：
> 1. **Function Signature**：定義正確的函式名稱與參數（包含 Fixtures）
> 2. **Docstring**：必須包含 TC ID 與測試描述（複製自 Section 5）
> 3. **Body**：函式本體僅能包含 `# Arrange` / `# Act` / `# Assert` 註解標記，並以 `...` (Ellipsis) 結束
> 4. **Import**：依據 Section 4.3 填入必要的 Import 語句
>
> **⚠️ 導入紅線**：
> - 測試主體 (SUT) **必須**從 FU Container 導入，禁止導入私有實作 (`_module.py`)
> - 所有導入路徑必須指向公開介面（`__init__.py`）
>
> **❌ 錯誤示範（過度實作）**：
>
> ```python
> def test_tc_dump_happy_001_basic_dict(self, tmp_path):
>     """TC-DUMP-HAPPY-001: 基本字典序列化。"""
>     data = {"name": "test", "value": 123}  # ❌ 具體測試資料
>     result = PickleIO.dump(data, tmp_path / "test.pkl")  # ❌ 具體呼叫
>     assert result is True  # ❌ 具體斷言
>     assert (tmp_path / "test.pkl").exists()  # ❌ 具體斷言
> ```

```python
import pytest

# === 測試主體 (SUT) ===
# ⚠️ 必須從 FU Container 導入，禁止導入私有實作
from <fu_path> import <Component_1>, <Component_2>, ...

# === 專案內部輔助依賴 (如適用) ===
# from <source_path> import <HelperComponent_1>, ...

# === 測試工具套件 (如適用) ===
# from tests.<path> import <TestUtility_1>, ...

@pytest.mark.unit
class Test<class_name>:
    """Test suite for <FU Name>."""

    # --- 自定義 Fixtures (對應 Section 4.2.2) ---

    @pytest.fixture
    def sample_data(self):
        """提供測試資料 fixture。"""
        ...

    # === Happy Path (主流程) ===

    def test_tc_scope_happy_001_description(self, tmp_path, sample_data):
        """TC-SCOPE-HAPPY-001: <填入案例描述>.

        測試目標: <填入驗證目標>
        預期結果: <填入預期結果>
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    # === Edge Cases (邊界案例) ===

    def test_tc_scope_edge_001_description(self):
        """TC-SCOPE-EDGE-001: <填入案例描述>."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    # === Error Handling (錯誤處理) ===

    def test_tc_scope_err_001_description(self):
        """TC-SCOPE-ERR-001: <填入案例描述>."""
        # Act & Assert
        ...

    # === Integration Tests (整合測試) ===

    def test_tc_int_happy_001_description(self, tmp_path):
        """TC-INT-HAPPY-001: <填入案例描述>."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...
```

### 7.3 執行指令 (Execution Commands)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 提供常用測試指令，包含執行單元測試和產生覆蓋率報告的範例。

```bash
# 執行本 FU 的單元測試
pytest tests/<fu_path>/<fu_name>/test_<name>.py -v -m unit

# 執行並產生覆蓋率報告
pytest tests/<fu_path>/<fu_name>/test_<name>.py -v --cov=<fu_path> --cov-report=term-missing
```

### 7.4 注意事項 (Implementation Notes)

- **跨平台相容性**：所有檔案 I/O 測試必須使用 `tmp_path` fixture，嚴禁硬編碼路徑（如 `/tmp/` 或 `C:\`）。
- **異常測試**：若需模擬特定異常，請明確描述其實現方法（例如：使用 `lambda` 模擬不可序列化物件）。

## 8. 驗收標準 (Acceptance Criteria)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義本測試規格書與對應測試程式碼完成時的「完工定義 (DoD)」。旨在驗證測試的有效性、隔離性與架構合規性。

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
- [ ] **結構一致性**：測試檔案存放路徑嚴格遵循「結構對應性原則」(`tests/<fu_path>/<fu_name>/`)。

````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 文件追溯性與定位

- [ ] **設計來源追溯**：是否已填寫設計來源，並正確連結到 `vX.Y.Z` 版本 (對應 §1.3)？
- [ ] ⚠️ **間接追溯原則**：確認本文件僅引用 `Rule-XX` 與 `BV-XX`，嚴禁直接引用 `REQ-XX` (對應 §5, §6)？
- [ ] **完整覆蓋**：所有在 `design.md` 中定義的行為規則 (Rule) 是否都有對應的測試案例 (TC) (對應 §6.1)？
- [ ] **矩陣完整性**：是否同時包含了「規則覆蓋矩陣」與「行為驗證覆蓋矩陣」 (對應 §6)？

### B. 測試案例設計

- [ ] **ID 規範**：所有 TC ID 是否符合 `TC-<SCOPE>-<TYPE>-XXX` 格式（三位數流水號） (對應 §5)？
- [ ] **斷言明確性**：Assert 欄位是否定義了具體的驗證方式（如 `pytest.raises` 或 `assert ...exists()`） (對應 §5)？

### C. 測試配置與導入紅線

- [ ] ⚠️ **導入紅線**：測試主體 (SUT) 是否嚴格從公開容器 (`__init__.py`) 導入，嚴禁導入任何 `_` 開頭的私有實作 (對應 §4.3)？
- [ ] **Fixture 分類**：`tmp_path` 等內建項目是否放在 §4.2.1，而自定義項目放在 §4.2.2 (對應 §4.2)？
- [ ] **單元測試標記**：是否已正確加上 `@pytest.mark.unit` 裝飾器 (對應 §7.2)？

### D. 程式骨架規範

- [ ] ⚠️ **零實作原則**：骨架代碼中是否完全沒有具體測試資料、呼叫邏輯或斷言語句 (對應 §7.2)？
- [ ] **Ellipsis 使用**：所有函式實作部分是否皆使用 `...` (Ellipsis) 作為佔位符 (對應 §7.2)？
- [ ] **Docstring 對齊**：骨架中的 Docstring 是否完整複製了 §5 的 ID 與測試目標 (對應 §7.2)？

### E. 最終清理

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
