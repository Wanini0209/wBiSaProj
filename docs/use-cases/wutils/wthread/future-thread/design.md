# future-thread - Design

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `future-thread` |
| **Target Library** | `wutils` |
| **Toolkit Category** | `wthread` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 價值主張 (Value Proposition)

- **痛點 (Pain Point)**：標準 `threading.Thread` 無法直接回傳執行結果或傳遞子執行緒的例外，導致開發者需手動撰寫 `Queue` 管理程式碼或重複的 `try-except` 樣板，且容易因忽略錯誤而發生「靜默失敗」。
- **效益 (Benefit)**：`FutureThread` 封裝了結果回傳與例外捕獲機制，提供類似 `concurrent.futures` 的操作體驗，同時保留 Thread 的輕量與直接控制特性，提升並發程式的安全性並減少 Boilerplate code。

### 1.3 設計範圍 (Scope)

- **In-Scope**：
    - 實作繼承自 `threading.Thread` 的 `FutureThread` 類別。
    - 支援同步等待並獲取回傳值 (`get_result`)。
    - 支援自動捕獲子執行緒例外並在主執行緒重新拋出 (Re-raise)。
    - 提供執行狀態查詢 (`done`) 與靜默屬性存取 (`result`, `exception`)。
    - 實作嚴格的狀態檢查 (Guard Clauses) 以防止誤用。
- **Out-of-Scope**：
    - 執行緒池 (Thread Pool) 管理。
    - 跨進程 (Process) 的 Future 實作。
    - 複雜的 Callback 機制 (如 `add_done_callback`)。

### 1.4 設計來源 (Design Source)

- **Based on**: `requirements.md` v1.0.0
- **Source Doc**: `docs/use-cases/wutils/wthread/future-thread/requirements.md`

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-07 | Initial Design | Based on requirements.md v1.0.0 |

## 3. 高階技術設計 (High-Level Design)

本章節定義 Feature 完成後的「最終樣貌」與「整體架構」。

### 3.1 模組架構 (Module Architecture)

#### 3.1.1 目錄結構 (Directory Structure)

```text
wutils/
└── wthread/
    ├── __init__.py         # Public Interface (Exports FutureThread)
    └── _future_thread.py   # Private Implementation
```

#### 3.1.2 外部依賴矩陣 (Dependency Matrix)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `threading` | Std | 核心執行緒功能繼承來源 |
| `sys` | Std | 用於 `sys.exc_info()` 捕獲例外資訊 |
| `typing` | Std | 提供泛型 (`Generic`, `TypeVar`) 與型別標註支援 |

### 3.2 公開 API 介面設計 (Public API Interface)

```python
from typing import TypeVar, Generic, Optional, Callable, Any
import threading

T = TypeVar("T")

class FutureThread(threading.Thread, Generic[T]):
    """
    擴充版 Thread，支援獲取執行結果與例外傳遞。
    """

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
        初始化 FutureThread。參數與 threading.Thread 兼容。
        """
        ...

    def get_result(self, timeout: Optional[float] = None) -> T:
        """
        等待執行緒結束並回傳結果。

        若執行緒發生例外，此方法將會 Re-raise 該例外。

        Args:
            timeout: 等待超時時間 (秒)。若為 None 則無限期等待。

        Returns:
            T: Target 函數的回傳值。

        Raises:
            TimeoutError: 若在 timeout 時間內未完成。 (註: 這裡復用 threading 的行為，或依據 FR-04 實作等待邏輯)
            RuntimeError: 若執行緒尚未啟動。
            Exception: Target 函數拋出的任何例外。
        """
        ...

    @property
    def result(self) -> Optional[T]:
        """
        獲取執行結果 (靜默模式)。

        Returns:
            T: 若執行成功且已結束。
            None: 若尚未結束、尚未啟動或執行失敗。

        Raises:
            RuntimeError: 若在不安全的狀態下存取 (如執行中)。
        """
        ...

    @property
    def exception(self) -> Optional[BaseException]:
        """
        獲取執行例外 (靜默模式)。

        Returns:
            BaseException: 若執行過程發生例外。
            None: 若執行成功或尚未結束。

        Raises:
            RuntimeError: 若在不安全的狀態下存取 (如執行中)。
        """
        ...

    @property
    def done(self) -> bool:
        """
        檢查執行緒是否已結束 (無論成功或失敗)。
        """
        ...
```

#### 3.2.1 需求覆蓋檢查 (Requirement Coverage)

| User Story / Req ID | API Mapping |
| :--- | :--- |
| **US-001** | `get_result()` (回傳值) |
| **US-002** | `get_result()` (Re-raise Exception) |
| **US-003** | Properties: `.done`, `.result`, `.exception` |

## 4. 功能單元劃分 (FU Decomposition)

### 4.1 FU: `future-thread`

#### 1. FU 屬性與整體職責 (Attributes & Responsibility)

| Attribute | Value |
| :--- | :--- |
| **Container Path** | `wutils/wthread` |
| **Responsibility** | 封裝 threading.Thread，管理執行結果與例外的生命週期，並提供安全的存取介面 |

#### 2. 核心公開元件指派與契約 (Assigned Components & Contracts)

| Component | Type | Expected Contract / Responsibility |
| :--- | :--- | :--- |
| `FutureThread` | Class | 繼承 `threading.Thread` 並實作 `Generic[T]` 的增強型執行緒類別。必須：(1) 在 `run()` 中自動捕獲 target 的回傳值與例外；(2) 提供 `get_result(timeout)` 方法，支援同步等待、結果回傳與例外重新拋出；(3) 提供 `.done`, `.result`, `.exception` 屬性，含未完成狀態的安全檢查（拋出 `RuntimeError`）；(4) 確保 Traceback 無循環引用。 |

#### 3. TDD 策略指示 (TDD Strategy Directive)

| Attribute | Value |
| :--- | :--- |
| **Strategy** | Standard TDD |
| **Reasoning** | 本功能邏輯封閉且明確，僅依賴標準庫，適合透過嚴格的測試案例定義狀態機行為 (State Machine) 與邊界條件。 |

#### 4. 實作設計約定 (Implementation Design)

##### A. 功能需求對應 (FR Mapping)

| ID | Description | Implementation Note |
| :--- | :--- | :--- |
| **FR-01** | 繼承 Thread | Class 定義為 `class FutureThread(threading.Thread, Generic[T])`，並在 `__init__` 呼叫 `super().__init__`。 |
| **FR-02** | 捕獲回傳值 | 覆寫 `run()` 或封裝 `target`。在 wrapper 函式中執行 `self._target` 並將回傳值存入私有變數 `self._return`。 |
| **FR-03** | 捕獲例外 | 在 wrapper 函式中使用 `try...except` 包裹執行邏輯，將捕獲的例外存入 `self._exc`。 |
| **FR-04** | get_result 方法 | 呼叫 `self.join(timeout)`。若 `is_alive()` 仍為 True 則處理超時；若有 `self._exc` 則 raise；否則回傳 `self._return`。 |
| **FR-05** | 屬性存取 | 實作 `@property`，直接回傳 `self._return` 或 `self._exc`，不主動拋出 target 的例外。 |
| **FR-06** | done 屬性 | 檢查內部狀態標記或 `not self.is_alive()` 且已啟動過。 |
| **FR-07** | 狀態安全檢查 | 在 `.result`, `.exception` 中檢查 `is_alive()` 與是否已啟動 (`_started` flag)，不符合則拋出 `RuntimeError`。 |

##### B. 驗收標準對應 (AC Mapping)

| ID | Scenario | Assertion |
| :--- | :--- | :--- |
| **AC-01** | Happy Path (Result) | 執行簡單加法函數，斷言 `get_result()` 回傳正確總和，`.done` 為 True，`.exception` 為 None。 |
| **AC-02** | Happy Path (Exception) | 執行拋錯函數，斷言 `get_result()` 拋出預期例外 (e.g. `ValueError`)，且 `.exception` 屬性不為空。 |
| **AC-03** | Guard (Not Started) | 實例化後直接存取 `.result`，斷言拋出 `RuntimeError`。 |
| **AC-04** | Guard (Running) | 在執行緒 sleep 期間存取 `.result`，斷言拋出 `RuntimeError`。 |
| **AC-05** | Timeout Handling | 設定短 timeout 呼叫 `get_result`，斷言執行緒仍 `is_alive()`。 |

##### C. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy |
| :--- | :--- | :--- |
| `Target Function Exception` | 執行緒內函數拋錯 | **Mixed**: 內部捕獲儲存 (Swallow at thread level)，但在 `get_result()` 被呼叫時重新拋出 (Propagate/Re-raise)。 |
| `RuntimeError` | 錯誤的生命週期存取 (未啟動/執行中) | **Propagate**: 直接拋出以警示開發者誤用。 |
| `TimeoutError` (或類似行為) | `get_result` 等待超時 | **Propagate**: 或是由呼叫者檢查 `is_alive()` 判定 (視實作細節，標準 Thread join 不拋錯，但 `get_result` 若設計為必須回傳值則需處理)。 |

##### D. 架構約束對應 (Architectural Constraints Mapping)

| ID | Constraint | Compliance Note |
| :--- | :--- | :--- |
| **CONS-01** | 僅依賴標準庫 | 僅使用 `threading`, `sys`, `typing`。 |
| **CONS-02** | 明確定義公開介面 | `wutils/wthread/__init__.py` 中設定 `__all__ = ["FutureThread"]`。 |
| **CONS-03** | 無額外業務狀態 | 類別僅持有執行結果與例外，不包含任何業務邏輯屬性。 |

##### E. 非功能需求對應 (NFR Mapping)

| ID | Description | Design Strategy |
| :--- | :--- | :--- |
| **NFR-01** | 清除 Traceback 循環引用 | 在例外捕獲邏輯中，將例外存入 `self._exc` 後，確保不持有 stack frame 的強引用 (Python 3 通常會處理，但可考慮顯式 `del` 區域變數或使用 `traceback` 模組輔助清理)。 |
| **NFR-02** | Python 3.12+ | 使用現代語法與 Type Hints。 |
| **NFR-03** | Type Safety | 全面使用 Generic[T] 與 Type Hints，通過 MyPy 檢查。 |
