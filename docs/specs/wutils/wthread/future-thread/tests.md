# future-thread - Test Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `future-thread` |
| **Container Path** | `wutils/wthread` |
| **Public Interface** | `wutils/wthread/__init__.py` |
| **Test Type** | Unit Test |
| **Layer** | Library (No Business Dependencies) |

### 1.2 測試範圍 (Test Scope)

驗證 `FutureThread` 類別在執行緒生命週期管理、結果回傳、例外捕獲與傳遞、以及狀態屬性安全性檢查的正確性。涵蓋正常執行回傳值、執行中拋出例外、等待超時以及在未完成狀態下存取結果的邊界行為。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-07 | Initial Test Spec | Req: v1.0.0, Design: v1.0.0 |

## 3. 測試概述 (Test Overview)

### 3.1 驗證重點 (Verification Focus)

- 驗證 `get_result()` 能正確同步等待並回傳 Target 函數的執行結果。
- 驗證 Target 函數拋出例外時，能正確被捕獲並在 `get_result()` 中重新拋出 (Re-raise)。
- 驗證 `get_result(timeout)` 的超時機制能正確拋出 `TimeoutError`。
- 驗證 `.done`, `.result`, `.exception` 屬性在不同執行階段 (未啟動、執行中、已結束) 的狀態正確性與存取安全性。
- 驗證標準 `threading.Thread` 的參數 (args, kwargs, daemon, name) 能正確傳遞與生效。

### 3.2 測試策略 (Test Strategy)

- **方法**：黑箱測試，針對 `FutureThread` 公開介面進行功能驗證。
- **工具**：`pytest` + `pytest-cov`。
- **Mock 策略**：
    - 不使用外部 Mock，直接定義簡單的 Helper Function (如加法運算、拋錯函數、睡眠函數) 作為 `target` 傳入 `FutureThread` 進行測試。

## 4. 測試環境與配置 (Test Environment)

### 4.1 測試標記 (Markers)

- `@pytest.mark.unit`: 必須標記為單元測試。

### 4.2 Fixtures 規劃 (Fixtures Planning)

#### 4.2.1 Pytest 內建 Fixtures (Built-in Fixtures)

| Fixture Name | Scope | Usage |
| :--- | :--- | :--- |
| 無 | - | 本測試主要依賴 threading 行為，不需特殊內建 fixtures |

#### 4.2.2 自定義 Fixtures (Custom Fixtures)

| Fixture Name | Scope | Description |
| :--- | :--- | :--- |
| 無 | - | 測試輔助函數將直接定義於測試方法內或作為類別 helper |

### 4.3 測試依賴項 (Test Dependencies)

#### 4.3.1 測試主體 (System Under Test)

| Component | Import Path | Description |
| :--- | :--- | :--- |
| `FutureThread` | `from wutils.wthread import FutureThread` | 測試主體 (SUT) |

#### 4.3.2 專案內部輔助依賴 (Internal Dependencies) [Optional]

| Component | Import Path | Usage |
| :--- | :--- | :--- |
| 無 | - | - |

#### 4.3.3 測試工具套件 (Test Utilities) [Optional]

| Component | Import Path | Usage |
| :--- | :--- | :--- |
| 無 | - | - |

## 5. 測試案例設計 (Test Cases)

### 5.1 執行控制與結果獲取 (Execution & Result)

#### TC-EXEC-HAPPY-001: 正常執行與結果回傳

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01**, **Rule-02**, **Rule-05**, **Rule-07**, **Rule-08** |
| **測試目標** | 驗證執行緒能正常執行 Target 函數，並透過 `get_result` 獲取回傳值 |
| **前置條件** | 定義一加法函數 `add(a, b) -> return a + b` |
| **測試步驟** | 1. 初始化 `FutureThread(target=add, args=(1, 2))` <br> 2. 呼叫 `start()` <br> 3. 呼叫 `get_result()` |
| **預期結果** | 1. `get_result()` 回傳 `3` <br> 2. `done` 屬性變為 `True` <br> 3. `result` 屬性為 `3` <br> 4. `exception` 屬性為 `None` |
| **驗證方式 (Assertion)** | `assert t.get_result() == 3` <br> `assert t.done is True` |

#### TC-EXEC-HAPPY-002: 參數傳遞與標準屬性

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-01** |
| **測試目標** | 驗證 `args`, `kwargs`, `name`, `daemon` 參數能正確傳遞給父類別 `threading.Thread` |
| **前置條件** | 定義一回傳參數的函數 `echo(*args, **kwargs)` |
| **測試步驟** | 1. 初始化 `FutureThread(target=echo, args=(1,), kwargs={"k": 2}, name="MyThread", daemon=True)` <br> 2. 檢查 `t.name` 與 `t.daemon` <br> 3. 啟動並獲取結果 |
| **預期結果** | 1. `t.name` 為 "MyThread" <br> 2. `t.daemon` 為 `True` <br> 3. `get_result()` 回傳與輸入一致的參數 |
| **驗證方式 (Assertion)** | `assert t.name == "MyThread"` <br> `assert t.daemon is True` |

#### TC-EXEC-EDGE-001: 異常捕獲與傳播

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-03**, **Rule-05**, **Rule-07**, **Rule-08**, **Rule-09** |
| **測試目標** | 驗證 Target 拋出例外時，`get_result` 能重新拋出該例外，且屬性狀態正確 |
| **前置條件** | 定義一函數 `risky()` 拋出 `ValueError("Boom")` |
| **測試步驟** | 1. 初始化 `FutureThread(target=risky)` 並 `start()` <br> 2. 呼叫 `get_result()` <br> 3. 檢查 `done`, `result`, `exception` 屬性 |
| **預期結果** | 1. `get_result()` 拋出 `ValueError` <br> 2. `done` 為 `True` <br> 3. `result` 為 `None` <br> 4. `exception` 為 `ValueError` 實例 |
| **驗證方式 (Assertion)** | `pytest.raises(ValueError)` <br> `assert isinstance(t.exception, ValueError)` |

#### TC-EXEC-ERR-001: 等待超時

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-04** |
| **測試目標** | 驗證當執行時間超過 `timeout` 時，拋出 `TimeoutError` |
| **前置條件** | 定義一函數 `slow()` 睡眠 0.2 秒 |
| **測試步驟** | 1. 初始化 `FutureThread(target=slow)` 並 `start()` <br> 2. 呼叫 `get_result(timeout=0.05)` |
| **預期結果** | 拋出 `TimeoutError` |
| **驗證方式 (Assertion)** | `pytest.raises(TimeoutError)` |

### 5.2 狀態存取安全性 (State Safety)

#### TC-STATE-ERR-001: 執行中存取屬性 (Race Condition Prevention)

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-06** |
| **測試目標** | 驗證執行緒尚未結束前存取 `result` 或 `exception` 會被阻止 |
| **前置條件** | 定義一函數 `slow()` 睡眠 0.5 秒 |
| **測試步驟** | 1. 初始化 `FutureThread(target=slow)` 並 `start()` <br> 2. 確認 `done` 為 `False` <br> 3. 嘗試存取 `t.result` |
| **預期結果** | 拋出 `RuntimeError` |
| **驗證方式 (Assertion)** | `pytest.raises(RuntimeError)` |

#### TC-STATE-ERR-002: 未啟動存取屬性

| Attribute | Description |
| :--- | :--- |
| **對應規則** | `design.md` **Rule-06** |
| **測試目標** | 驗證執行緒初始化後但未呼叫 `start()` 前存取 `result` 會被阻止 |
| **前置條件** | 無 |
| **測試步驟** | 1. 初始化 `FutureThread(target=lambda: None)` <br> 2. 不呼叫 `start()` <br> 3. 嘗試存取 `t.result` |
| **預期結果** | 拋出 `RuntimeError` |
| **驗證方式 (Assertion)** | `pytest.raises(RuntimeError)` |

## 6. 測試矩陣 (Test Matrix)

### 6.1 規則覆蓋矩陣 (Rule Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **Rule-01** | **TC-EXEC-HAPPY-001**, **TC-EXEC-HAPPY-002** |
| **Rule-02** | **TC-EXEC-HAPPY-001** |
| **Rule-03** | **TC-EXEC-EDGE-001** |
| **Rule-04** | **TC-EXEC-ERR-001** |
| **Rule-05** | **TC-EXEC-HAPPY-001**, **TC-EXEC-EDGE-001** |
| **Rule-06** | **TC-STATE-ERR-001**, **TC-STATE-ERR-002** |
| **Rule-07** | **TC-EXEC-HAPPY-001**, **TC-EXEC-EDGE-001** |
| **Rule-08** | **TC-EXEC-HAPPY-001**, **TC-EXEC-EDGE-001** |
| **Rule-09** | **TC-EXEC-EDGE-001** |

### 6.2 行為驗證覆蓋矩陣 (BV Coverage Matrix)

| ID | Related Test Cases |
| :--- | :--- |
| **BV-01** | **TC-EXEC-HAPPY-001** |
| **BV-02** | **TC-EXEC-EDGE-001** |
| **BV-03** | **TC-EXEC-ERR-001** |
| **BV-04** | **TC-STATE-ERR-001** |
| **BV-05** | **TC-STATE-ERR-002** |

## 7. 實作指引 (Implementation Guide)

### 7.1 檔案位置 (File Location)

- **Target File**: `tests/wutils/wthread/future-thread/test_future_thread.py`

### 7.2 測試程式骨架 (Skeleton)

```python
import pytest
import time
import threading

# === 測試主體 (SUT) ===
# ⚠️ 必須從 FU Container 導入，禁止導入私有實作
from wutils.wthread import FutureThread

@pytest.mark.unit
class TestFutureThread:
    """Test suite for FutureThread."""

    # === Execution & Result (執行控制與結果獲取) ===

    def test_tc_exec_happy_001_basic_execution(self):
        """TC-EXEC-HAPPY-001: 正常執行與結果回傳。

        測試目標: 驗證執行緒能正常執行 Target 函數，並透過 get_result 獲取回傳值
        預期結果:
        1. get_result() 回傳正確值
        2. done 為 True
        3. result 屬性正確，exception 屬性為 None
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_exec_happy_002_args_passing(self):
        """TC-EXEC-HAPPY-002: 參數傳遞與標準屬性。

        測試目標: 驗證 args, kwargs, name, daemon 參數能正確傳遞給父類別 threading.Thread
        預期結果: name 與 daemon 屬性正確設定，且參數正確傳入 target
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_exec_edge_001_exception_propagation(self):
        """TC-EXEC-EDGE-001: 異常捕獲與傳播。

        測試目標: 驗證 Target 拋出例外時，get_result 能重新拋出該例外，且屬性狀態正確
        預期結果: get_result 拋出例外，done 為 True，exception 屬性持有該例外
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_exec_err_001_timeout(self):
        """TC-EXEC-ERR-001: 等待超時。

        測試目標: 驗證當執行時間超過 timeout 時，拋出 TimeoutError
        預期結果: 拋出 TimeoutError
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    # === State Safety (狀態存取安全性) ===

    def test_tc_state_err_001_access_while_running(self):
        """TC-STATE-ERR-001: 執行中存取屬性 (Race Condition Prevention)。

        測試目標: 驗證執行緒尚未結束前存取 result 或 exception 會被阻止
        預期結果: 拋出 RuntimeError
        """
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_tc_state_err_002_access_before_start(self):
        """TC-STATE-ERR-002: 未啟動存取屬性。

        測試目標: 驗證執行緒初始化後但未呼叫 start() 前存取 result 會被阻止
        預期結果: 拋出 RuntimeError
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
pytest tests/wutils/wthread/future-thread/test_future_thread.py -v -m unit

# 執行並產生覆蓋率報告
pytest tests/wutils/wthread/future-thread/test_future_thread.py -v --cov=wutils/wthread --cov-report=term-missing
```

### 7.4 注意事項 (Implementation Notes)

- **時間敏感性**：涉及 `timeout` 或 `sleep` 的測試，建議設定適當的寬容度或明顯的時間差 (例如 sleep 0.2s vs timeout 0.05s)，避免因 CI 環境執行緩慢導致 Flaky Tests。
- **資源清理**：雖然 `FutureThread` 為 Daemon 或 Local Scope，但確保測試結束後執行緒能自然結束，避免留存背景執行緒。

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
- [ ] **結構一致性**：測試檔案存放路徑嚴格遵循「結構對應性原則」(`tests/<fu_path>/<fu_name>/`)。
