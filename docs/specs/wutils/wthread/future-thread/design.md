# future-thread - Design Specification

## 1. FU 概述 (FU Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **FU Name** | `future-thread` |
| **Container Path** | `wutils/wthread` |
| **Public Interface** | `wutils/wthread/__init__.py` |
| **Exports** | `FutureThread` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 目的 (Purpose)

本單元提供一個增強型的執行緒類別 `FutureThread`，封裝標準 `threading.Thread` 的執行邏輯。它解決了原生執行緒無法直觀獲取回傳值與傳遞例外的問題，通過內部狀態管理與同步機制，讓開發者能以類似 `Future` 的方式安全地處理執行緒結果與錯誤，消除重複撰寫 Queue 或全域變數傳遞結果的 Boilerplate code。

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-07 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 檔案組織 (File Organization)

```text
wutils/wthread/
├── __init__.py          # Public Container
└── _future_thread.py    # Private Implementation
```

### 3.1 公開介面 (Public Interface)

**檔案**: `wutils/wthread/__init__.py`

```python
from ._future_thread import FutureThread

__all__ = ["FutureThread"]
```

### 3.2 私有實作 (Private Implementation)

| File Path | Responsibility |
| :--- | :--- |
| `_future_thread.py` | 實作 `FutureThread` 類別，包含執行緒生命週期管理、結果/例外捕獲與同步等待邏輯。 |

## 4. 依賴項 (Dependencies)

| Package | Type | Import Statement | Purpose |
| :--- | :--- | :--- | :--- |
| `threading` | Std | `import threading` | 繼承 `Thread` 類別與使用 `Event` 進行同步 |
| `sys` | Std | `import sys` | 使用 `sys.exc_info()` 捕獲完整例外資訊 |
| `typing` | Std | `from typing import TypeVar, Generic, Callable, Any, Optional` | 支援泛型與型別標註 |

## 5. 介面設計與行為 (Interface Design & Rules)

### 5.1 `FutureThread` 類別

繼承自 `threading.Thread`，並實作 `Generic[T]` 以支援強型別的回傳值。

#### 5.1.1 `__init__` (Constructor)

```python
T = TypeVar("T")

class FutureThread(threading.Thread, Generic[T]):
    def __init__(
        self,
        group: None = None,
        target: Optional[Callable[..., T]] = None,
        name: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        *,
        daemon: Optional[bool] = None
    ) -> None:
        """
        初始化 FutureThread 實例。

        Parameters
        ----------
        group : None
            保留參數，必須為 None (兼容 threading.Thread)。
        target : Optional[Callable[..., T]]
            執行緒欲執行的目標函數。
        name : Optional[str]
            執行緒名稱。
        args : tuple
            傳遞給 target 的位置參數。
        kwargs : Optional[dict]
            傳遞給 target 的關鍵字參數。
        daemon : Optional[bool]
            是否設為守護執行緒。

        Returns
        -------
        None
        """
        ...
```

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-01** | 標準 Thread 兼容性與初始化 | 1. 必須呼叫 `super().__init__` 確保 `threading.Thread` 正確初始化。<br>2. 初始化內部狀態變數：結果容器、例外容器、完成信號 (`Event`)。 |

#### 5.1.2 `get_result`

```python
    def get_result(self, timeout: Optional[float] = None) -> T:
        """
        等待執行緒結束並獲取結果。若執行過程發生例外，則在此處重新拋出。

        Parameters
        ----------
        timeout : Optional[float]
            等待的最長秒數。若為 None 則無限期等待。

        Returns
        -------
        T
            Target 函數的回傳值。

        Raises
        ------
        TimeoutError
            若等待超過 timeout 時間且執行緒尚未結束。
        BaseException
            若 Target 函數執行過程中拋出例外，將在此處重新拋出相同例外。
        """
        ...
```

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-02** | 同步等待與結果回傳 | 1. 呼叫時阻塞直到執行緒結束或超時。<br>2. 若執行成功，回傳 Target 的回傳值。 |
| **Rule-03** | 例外透傳 (Re-raise) | 若 Target 執行時發生例外，必須在此方法被呼叫時重新拋出 (Re-raise) 該例外，並保留原始 Traceback 資訊。 |
| **Rule-04** | 超時處理 | 若超過 `timeout` 指定時間仍未完成，拋出 `TimeoutError`。 |

#### 5.1.3 Properties (`done`, `result`, `exception`)

```python
    @property
    def done(self) -> bool:
        """
        檢查執行緒是否已完成執行 (無論成功或失敗)。

        Returns
        -------
        bool
            True 表示已結束，False 表示尚未啟動或執行中。
        """
        ...

    @property
    def result(self) -> Optional[T]:
        """
        獲取執行結果，不進行等待或重新拋出例外。

        Returns
        -------
        Optional[T]
            執行成功時回傳結果，失敗或未執行完畢時的行為詳見 Rule-06。

        Raises
        ------
        RuntimeError
            若執行緒尚未結束 (`done` 為 False)。
        """
        ...

    @property
    def exception(self) -> Optional[BaseException]:
        """
        獲取捕獲的例外物件。

        Returns
        -------
        Optional[BaseException]
            執行失敗時回傳例外物件，成功時回傳 None。

        Raises
        ------
        RuntimeError
            若執行緒尚未結束 (`done` 為 False)。
        """
        ...
```

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-05** | 執行狀態查詢 (`done`) | 1. 透過內部 Event 或狀態旗標判斷。<br>2. 執行緒結束 (正常或異常) 後回傳 True，否則 False。 |
| **Rule-06** | 安全屬性存取檢查 | 存取 `result` 或 `exception` 時，若 `done` 為 False，必須拋出 `RuntimeError`，防止Race Condition 或未定義行為。 |
| **Rule-07** | 靜默結果存取 | 1. `result`: 成功回傳值，失敗回傳 None (不拋錯)。<br>2. `exception`: 失敗回傳例外物件，成功回傳 None。 |

#### 5.1.4 內部執行邏輯 (Internal Execution Logic)

> 此部分描述 `run()` 方法的覆寫行為，雖然 `run` 是公開方法，但通常由 `start()` 觸發。

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **Rule-08** | 執行封裝與捕捉 | 1. 覆寫 `run()` 方法。<br>2. 使用 `try-except` 包裹 `target` 的執行。<br>3. 成功時儲存回傳值；失敗時使用 `sys.exc_info()` 儲存例外與 Traceback。<br>4. 無論成功失敗，最後必須設定完成信號 (Event set)。 |
| **Rule-09** | 避免循環引用 | 在儲存例外後，應適當處理 Traceback 物件 (如使用局部變數刪除引用)，以符合 NFR-01 防止記憶體洩漏。 |

## 6. 異常處理 (Exception Handling)

### 6.1 異常傳播策略 (Propagation Strategy)

- **策略**: **Mixed (Swallow & Propagate)**
- **理由**: 執行緒內部的例外不能直接傳播到主執行緒 (會導致 Crash)，因此必須先在內部 "Swallow" (捕獲並儲存)。當使用者主動呼叫 `get_result()` 時，明確表示準備好處理結果，此時再 "Propagate" (Re-raise) 該例外，符合 Python 的顯式處理原則。

### 6.2 異常對照表 (Exception Mapping Table)

| Exception | Trigger | Function | Ref |
| :--- | :--- | :--- | :--- |
| `Target Exception` | Target 函數拋出任何例外 | `run` (Internal), `get_result` | **Rule-03**, **Rule-08** |
| `TimeoutError` | `get_result` 等待超時 | `get_result` | **Rule-04** |
| `RuntimeError` | 在未完成狀態存取 `result`/`exception` | `result`, `exception` (Properties) | **Rule-06** |

## 7. 行為驗證 (Behavior Verification)

| BV ID | Scenario | Expected Behavior | Ref |
| :--- | :--- | :--- | :--- |
| **BV-01** | Happy Path: 執行成功並獲取結果 | 1. `get_result()` 回傳預期值。<br>2. `done` 為 True。<br>3. `exception` 為 None。<br>4. `result` 為預期值。 | **Rule-02**, **Rule-05**, **Rule-07** |
| **BV-02** | Edge Case: Target 拋出例外 | 1. `get_result()` 拋出相同例外。<br>2. `done` 為 True。<br>3. `exception` 屬性持有該例外物件。<br>4. `result` 為 None。 | **Rule-03**, **Rule-07**, **Rule-08** |
| **BV-03** | Error: `get_result` 超時 | 設定 `timeout` 小於執行時間，呼叫 `get_result()` 拋出 `TimeoutError`。 | **Rule-04** |
| **BV-04** | Error: 執行中存取屬性 | 在 `start()` 後但未結束前存取 `result`，拋出 `RuntimeError`。 | **Rule-06** |
| **BV-05** | Edge Case: 未啟動存取屬性 | 在 `start()` 前存取 `result`，拋出 `RuntimeError`。 | **Rule-06** |

## 8. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Resource Management | **Traceback Cleanup**: 確保 `run` 方法在捕獲例外後，妥善處理 `sys.exc_info()` 的 traceback 引用，避免 Circular Reference 導致記憶體洩漏。 | **NFR-01** |
| **NFR-02** | Type Safety | **Generic Support**: 類別定義使用 `Generic[T]`，並在 `__init__` 與 `get_result` 中正確標註型別。 | **NFR-03** |

## 9. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | Standard Library Only | 依賴項表格 (§4) 確認僅使用 `threading`, `sys`, `typing`。 |
| **CONS-02** | Explicit Public Interface | 檔案組織 (§3.1) 定義僅透過 `__init__.py` 匯出 `FutureThread`。 |
| **CONS-03** | No Business State | 設計中僅包含執行緒控制與結果傳遞邏輯，無任何業務相關屬性。 |

## 10. 需求追溯矩陣 (Traceability Matrix)

| Requirement (REQ) | Design Element (Rules) | Verification (BV) |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | **Rule-01** | **BV-01** |
| **REQ-LOGIC-02** | **Rule-02**, **Rule-08** | **BV-01** |
| **REQ-LOGIC-03** | **Rule-08** | **BV-02** |
| **REQ-LOGIC-04** | **Rule-02**, **Rule-03**, **Rule-04** | **BV-01**, **BV-02**, **BV-03** |
| **REQ-LOGIC-05** | **Rule-07** | **BV-01**, **BV-02** |
| **REQ-LOGIC-06** | **Rule-05** | **BV-01** |
| **REQ-VAL-01** | **Rule-06** | **BV-04**, **BV-05** |
| **REQ-VAL-02** | **Rule-04** | **BV-03** |

## 11. 驗收標準 (Acceptance Criteria)

- [ ] **介面一致性**：實作的 Function/Class Signature 與本設計文件 (§5.1) 100% 一致。
- [ ] **行為完整性**：實作程式碼已完整涵蓋並符合所有定義的行為規則 (`Rule-01` 至 `Rule-09`)。
- [ ] **型別安全**：符合 **PNFR-CDE-01**，實作具備 100% Type Hint 覆蓋率（Strict Mode）。
- [ ] **文件規範**：符合 **PNFR-DOC-01**，所有公開介面均具備完整的 NumPy Style Docstrings。
- [ ] **架構紅線 (DIP)**：
    - [ ] **封裝性**：`FutureThread` 具體實作存放於 `_future_thread.py` 私有模組中。
    - [ ] **導入規範**：本模組僅依賴標準庫，無其他 Library 依賴。
