# future-thread - Requirements

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `future-thread` |
| **Target Library** | `wutils` |
| **Toolkit Category** | `wthread` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 功能描述 (Description)

本功能旨在擴充 Python 原生 `threading.Thread` 的能力，實作一個具備「結果回傳」與「例外捕獲」機制的 `FutureThread` 類別。

**價值主張 (Value Proposition)**：
標準的 Python Thread 無法直接回傳執行結果或將子執行緒的錯誤傳遞至主執行緒，導致開發者必須撰寫大量重複的 `Queue` 管理或 `try-except` 樣板程式碼。`FutureThread` 透過封裝這些複雜性，提供類似 `concurrent.futures` 的操作體驗，但保留了 Thread 的輕量與直接控制特性，有效減少 Boilerplate 並提升並發程式的安全性與可維護性。

## 2. 變更歷史 (Change History)

| Version | Date | Description |
| :--- | :--- | :--- |
| v1.0.0 | 2026-01-07 | Initial Release |

## 3. 使用者故事 (User Stories)

- **US-001**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 能夠直接獲取執行緒中函數的回傳值
  > 以便於 省去手動建立與管理 `queue.Queue` 來傳遞資料的繁瑣工作

- **US-002**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 子執行緒發生的例外能夠被自動捕獲並在主執行緒中重新拋出
  > 以便於 避免執行緒發生「靜默失敗 (Silent Failure)」，確保錯誤能被正確處理

- **US-003**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 有明確的機制查詢執行緒是否已完成，並安全地存取結果
  > 以便於 防止在執行緒尚未結束時存取資料導致的 Race Condition 或未定義行為

## 4. 功能需求 (Functional Requirements)

| ID | Description | Notes |
| :--- | :--- | :--- |
| **FR-01** | 繼承自 `threading.Thread` 並支援標準生命週期方法 (`start`, `join`) | 保持與原生 API 的兼容性 |
| **FR-02** | 自動捕獲並儲存 `target` 函數的執行回傳值 | 成功執行時儲存結果 |
| **FR-03** | 自動捕獲並儲存 `target` 函數執行過程中拋出的例外 (Exception) | 需包含完整 Traceback 資訊 |
| **FR-04** | 提供 `get_result(timeout=None)` 方法，主動等待執行緒結束並回傳結果 | 若執行失敗則 Re-raise 捕獲的例外；支援超時設定 |
| **FR-05** | 提供 `.result` 與 `.exception` 屬性供直接存取 | **靜默模式**：僅回傳物件或 `None`，絕不主動拋出例外 |
| **FR-06** | 提供 `.done` 屬性以布林值回傳執行緒工作狀態 | `True` 表示已結束 (無論成功或失敗) |
| **FR-07** | 實作狀態安全檢查 (Guard Clauses)，防止在錯誤生命週期階段存取資料 | 詳見 AC 定義之 RuntimeErrors |

## 5. 驗收標準 (Acceptance Criteria)

- **AC-01: Happy Path (執行成功)**
  - **Given**: 一個定義了回傳值的簡單函數，與一個以此函數為目標的 `FutureThread`
  - **When**: 啟動執行緒 (`start`) 並呼叫 `get_result()` 等待結束
  - **Then**: `get_result` 應回傳該函數的正確計算結果
  - **And**: `.result` 屬性應包含該結果，`.exception` 屬性應為 `None`，`.done` 為 True

- **AC-02: Happy Path (例外捕獲與傳遞)**
  - **Given**: 一個會拋出特定例外 (如 `ValueError`) 的函數
  - **When**: 啟動執行緒並呼叫 `get_result()`
  - **Then**: 主執行緒應收到被重新拋出的該特定例外 (`ValueError`)
  - **And**: 該例外應保留原始子執行緒的 Traceback 資訊
  - **And**: `.exception` 屬性應包含該例外物件，`.result` 屬性應為 `None`

- **AC-03: Edge Case (狀態安全檢查 - 尚未啟動)**
  - **Given**: 一個已實例化但尚未呼叫 `start()` 的 `FutureThread`
  - **When**: 嘗試存取 `.result` 或 `.exception` 屬性
  - **Then**: 應拋出 `RuntimeError`，並提示執行緒尚未啟動

- **AC-04: Edge Case (狀態安全檢查 - 執行中)**
  - **Given**: 一個正在執行中 (`is_alive()` 為 True) 的 `FutureThread`
  - **When**: 嘗試存取 `.result` 或 `.exception` 屬性
  - **Then**: 應拋出 `RuntimeError`，並提示應先呼叫 `join()` 或 `get_result()`

- **AC-05: Error Handling (超時處理)**
  - **Given**: 一個執行時間長於預期的 `FutureThread`
  - **When**: 呼叫 `get_result(timeout=short_time)` 且發生超時
  - **Then**: 執行緒應保持活躍狀態 (`is_alive()` 為 True)
  - **And**: 若接著嘗試存取 `.result`，應觸發執行中狀態的 `RuntimeError` (依據 FR-07)

## 6. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Justification |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Resource | 必須清除 Exception 物件中的 Traceback 循環引用 | 防止長時間運行下發生記憶體洩漏 |
| **NFR-02** | Environment | Ref: **PNFR-ENV-01** (Python 3.12+) | 專案通用標準 |
| **NFR-03** | Type Safety | Ref: **PNFR-CDE-01** (100% Type Hint Coverage) | 專案通用標準 |

## 7. 架構約束 (Architectural Constraints)

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-01** | 僅允許依賴 Python 標準庫 (`threading`, `sys` 等) | 禁止引入任何第三方套件以保持輕量 |
| **CONS-02** | 必須透過 `__init__.py` 的 `__all__` 明確定義公開介面 | 落實 Public Container Pattern |
| **CONS-03** | 類別設計除執行緒本身狀態外，不應持有額外業務狀態 | 保持通用性與低耦合 |
