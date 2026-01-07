# future-thread - Requirements Specification

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

提供一個繼承自標準 `threading.Thread` 的增強型執行緒類別 (`FutureThread`)，旨在解決原生執行緒無法直接獲取回傳值與傳遞例外 (Exception) 的痛點。此單元封裝了結果回傳與錯誤捕獲機制，提供類似 `concurrent.futures` 的安全性與便利性，同時保留執行緒的輕量特性，減少開發者重複撰寫 Queue 管理或 try-except 樣板程式碼的需求。

### 1.3 依賴盤點 (Dependencies)

| Package | Type | Purpose |
| :--- | :--- | :--- |
| `threading` | Std | 核心執行緒功能繼承來源 |
| `sys` | Std | 用於 `sys.exc_info()` 捕獲例外資訊 |
| `typing` | Std | 提供泛型 (`Generic`, `TypeVar`) 與型別標註支援 |

## 2. 變更歷史 (Change History)

| Version | Date | Description | Source |
| :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-01-07 | Initial Specification | Feature: future-thread (v1.0.0) |

## 3. 匯出能力 (Exported Capabilities)

### 3.1 匯出清單 (Export List)

```python
__all__ = ["FutureThread"]
```

### 3.2 能力定義 (Capability Definitions)

#### 3.2.1 FutureThread 類別

- **功能目標**: 提供具備結果回傳與例外傳遞能力的執行緒物件。
- **關鍵輸入**: 標準 `threading.Thread` 建構參數 (target, args, kwargs 等)。
- **關鍵輸出**: 執行緒實例，可透過方法獲取執行結果。
- **關鍵行為**:
    - 自動捕獲 Target Function 的回傳值。
    - 自動捕獲 Target Function 拋出的例外，並支援在主執行緒重新拋出。
    - 提供執行狀態檢查與安全的屬性存取。

### 3.3 使用範例 (Usage Examples)

```python
from wutils.wthread import FutureThread
import time

# Happy Path: 獲取結果
def add(a: int, b: int) -> int:
    return a + b

t1 = FutureThread(target=add, args=(1, 2))
t1.start()
result = t1.get_result()  # result == 3

# Error Handling: 捕獲例外
def risky_task():
    raise ValueError("Something went wrong")

t2 = FutureThread(target=risky_task)
t2.start()

try:
    t2.get_result()
except ValueError as e:
    print(f"Caught exception: {e}")

# State Inspection: 檢查狀態
t3 = FutureThread(target=time.sleep, args=(0.1,))
t3.start()
if not t3.done:
    print("Thread is still running")
```

## 4. 功能需求 (Functional Requirements)

### 4.1 核心邏輯 (Core Logic)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-LOGIC-01** | **繼承標準 Thread 行為**<br>必須繼承自 `threading.Thread` 並支援泛型 `Generic[T]`，確保與標準執行緒 API 兼容。 | 1. `isinstance(instance, threading.Thread)` 為 True。<br>2. 建構函式接受與 `Thread` 相同的參數 (`target`, `args`, `kwargs` 等)。 |
| **REQ-LOGIC-02** | **執行結果捕獲**<br>在執行緒內部執行 `target` 函數時，必須將其回傳值儲存於內部狀態中。 | 1. 執行成功後，內部變數持有正確的回傳值。<br>2. 透過 `get_result()` 可取得該值。 |
| **REQ-LOGIC-03** | **例外捕獲與儲存**<br>若 `target` 函數執行過程中拋出例外，必須捕獲該例外物件及其 Traceback 資訊，而非讓程式崩潰。 | 1. 執行緒不因未處理的例外而導致 Interpreter 錯誤輸出。<br>2. 內部變數持有捕獲的例外物件。 |
| **REQ-LOGIC-04** | **同步等待與結果獲取 (get_result)**<br>提供 `get_result(timeout)` 方法，等待執行緒結束。若執行成功回傳結果；若發生例外則重新拋出 (Re-raise) 該例外。 | 1. 若 Target 回傳值，此方法回傳該值。<br>2. 若 Target 拋錯，此方法拋出相同類型的例外。<br>3. 支援 `timeout` 參數設定等待時間。 |
| **REQ-LOGIC-05** | **靜默屬性存取**<br>提供 `.result` 與 `.exception` 屬性，允許在不重新拋出例外的情況下檢視執行結果或錯誤。 | 1. `.result` 回傳結果值或 None (若失敗)。<br>2. `.exception` 回傳例外物件或 None (若成功)。<br>3. 存取這些屬性**不會**觸發 Re-raise。 |
| **REQ-LOGIC-06** | **完成狀態查詢**<br>提供 `.done` 屬性以布林值表示執行緒是否已結束執行 (無論成功或失敗)。 | 1. 執行緒執行完畢 (正常或異常) 後，`.done` 為 True。<br>2. 執行中或尚未啟動時，`.done` 為 False。 |

### 4.2 驗證與約束 (Validation)

| ID | Description | Acceptance Criteria |
| :--- | :--- | :--- |
| **REQ-VAL-01** | **狀態安全檢查 (尚未啟動/執行中)**<br>在執行緒尚未結束 (`done` 為 False) 的狀態下存取 `.result` 或 `.exception` 時，必須阻止存取。 | 1. 若執行緒 `is_alive()` 為 True，存取屬性拋出 `RuntimeError`。<br>2. 若執行緒尚未 `start()`，存取屬性拋出 `RuntimeError`。 |
| **REQ-VAL-02** | **超時驗證**<br>`get_result(timeout)` 若在指定時間內未完成，必須中止等待並拋出錯誤。 | 1. 設定短於執行時間的 timeout 呼叫 `get_result` 時，拋出 `TimeoutError`。 |

## 5. 異常處理 (Exception Handling)

| Exception | Trigger | Strategy | Ref |
| :--- | :--- | :--- | :--- |
| `Target Function Exception` | 使用者傳入的 Target 函數拋出任何例外 | **Mixed**:<br>1. 在執行緒內部吞噬 (Swallow) 並儲存。<br>2. 在呼叫 `get_result()` 時透傳 (Propagate/Re-raise)。 | **REQ-LOGIC-03**<br>**REQ-LOGIC-04** |
| `RuntimeError` | 在不安全的狀態 (如執行中) 存取結果屬性 | **Propagate**: 直接拋出以警示開發者誤用。 | **REQ-VAL-01** |
| `TimeoutError` | `get_result()` 等待超過指定時間 | **Propagate**: 拋出標準 TimeoutError。 | **REQ-VAL-02** |

## 6. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Traceability |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Resource Management | **Traceback Cleanup**: 捕獲例外後，必須確保不造成 Stack Frame 的循環引用 (Circular Reference)，避免記憶體洩漏。 | Feature Design NFR-01 |
| **NFR-02** | Environment | **Python 3.12+**: 使用現代語法。 | Ref: PNFR-ENV-01 |
| **NFR-03** | Type Safety | **Generic Support**: 類別必須支援 `Generic[T]` 以提供準確的 IDE 提示與靜態檢查。 | Ref: PNFR-CDE-01 |

## 7. 架構約束 (Architectural Constraints)

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-01** | **Standard Library Only** | 本模組僅允許依賴 `threading`, `sys`, `typing`，嚴禁引入其他第三方套件。 |
| **CONS-02** | **Explicit Public Interface** | 必須透過 `wutils/wthread/__init__.py` 明確匯出 `FutureThread`，實作細節隱藏於私有模組。 |
| **CONS-03** | **No Business State** | `FutureThread` 僅負責執行控制與結果傳遞，類別定義中不得包含任何與具體業務邏輯相關的屬性或方法。 |
