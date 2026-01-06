# json-io - Requirements

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `json-io` |
| **Target Library** | `wutils` |
| **Toolkit Category** | `io` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 功能描述 (Description)

本功能旨在為 `wutils` 擴充 I/O 能力，提供封裝完善的 JSON 讀寫工具函式。其核心價值在於消除 Python 標準庫 `json` 模組操作檔案時所需的 `with open()` 重複性樣板程式碼 (Boilerplate)，並強制執行統一的資源管理與編碼規範 (UTF-8)，從而提升開發效率並減少因忘記關閉檔案或編碼錯誤導致的潛在風險。

## 2. 變更歷史 (Change History)

| Version | Date | Description |
| :--- | :--- | :--- |
| v1.0.0 | 2026-01-02 | Initial Release |

## 3. 使用者故事 (User Stories)

- **US-001**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 透過單一函式呼叫直接將 Python 物件寫入 JSON 檔案
  > 以便於 減少處理檔案開啟、編碼設定與關閉的重複程式碼

- **US-002**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 透過單一函式呼叫直接從檔案路徑讀取 JSON 內容
  > 以便於 快速獲取資料並自動確保資源被正確釋放

- **US-003**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 在讀寫函式中直接傳入 `pathlib.Path` 物件或字串路徑
  > 以便於 與現有的路徑處理邏輯無縫整合，無需手動轉換型別

- **US-004**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 能夠傳遞標準庫 `json` 的額外參數 (如 `indent`, `sort_keys`)
  > 以便於 在簡化 I/O 的同時，仍能彈性控制 JSON 的格式化輸出

## 4. 功能需求 (Functional Requirements)

| ID | Description | Notes |
| :--- | :--- | :--- |
| **FR-01** | 提供 `json_dump` 函式，接受可序列化物件與目標路徑，將內容寫入檔案 | 需支援 `**kwargs` 透傳至標準庫 |
| **FR-02** | 提供 `json_load` 函式，接受來源檔案路徑，讀取並回傳反序列化後的物件 | 需支援 `**kwargs` 透傳至標準庫 |
| **FR-03** | 讀寫函式必須支援 `str` 與 `pathlib.Path` 兩種類型的路徑輸入 | 內部需自動正規化處理 |
| **FR-04** | 函式內部必須自動管理檔案資源 (Context Manager)，確保操作完成或發生例外時檔案均能正確關閉 | 消除外部 `with open` 依賴 |
| **FR-05** | 寫入與讀取操作必須具備對稱性 (Symmetry)，即透過 `json_dump` 寫入的資料必須能透過 `json_load` 完整讀回 | 確保資料一致性 |

## 5. 驗收標準 (Acceptance Criteria)

- **AC-01: Happy Path (寫入與讀取主流程)**
  - **Given**: 一個包含巢狀結構 (Dict/List) 的 Python 物件與一個有效的目標檔案路徑
  - **When**: 呼叫寫入函式將物件儲存至該路徑，接著呼叫讀取函式讀取該路徑
  - **Then**: 檔案被成功建立，且讀回的物件內容與結構與原始物件完全一致

- **AC-02: Happy Path (參數透傳)**
  - **Given**: 一個 Python 物件與目標路徑
  - **When**: 呼叫寫入函式並傳入格式化參數 (如縮排設定)
  - **Then**: 產生的檔案內容應符合指定的格式化排版 (如包含換行與縮排)

- **AC-03: Edge Case (Path 物件支援)**
  - **Given**: 一個由 `pathlib` 建立的路徑物件 (Path Object)
  - **When**: 將此物件直接作為參數傳入讀寫函式
  - **Then**: 函式能正常執行，無型別錯誤，且檔案操作成功

- **AC-04: Error Handling (檔案不存在)**
  - **Given**: 一個不存在的檔案路徑
  - **When**: 呼叫讀取函式
  - **Then**: 應拋出標準的檔案找不到例外 (FileNotFoundError)，且不應造成資源洩漏

- **AC-05: Error Handling (JSON 格式錯誤)**
  - **Given**: 一個內容不符合 JSON 語法的損毀檔案
  - **When**: 呼叫讀取函式
  - **Then**: 應拋出 JSON 解碼例外 (JSONDecodeError)

## 6. 非功能需求 (Non-Functional Requirements)

| ID | Category | Description | Justification |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Encoding | 強制使用 UTF-8 編碼進行檔案讀寫 | Ref: PNFR-ENC-01 |
| **NFR-02** | Type Safety | 公開介面須具備 100% Type Hints 覆蓋率 | Ref: PNFR-CDE-01 |
| **NFR-03** | Compatibility | 必須完整相容 Python 標準庫 `json` 的 `dump/load` 參數介面 | 降低學習曲線與遷移成本 |

## 7. 架構約束 (Architectural Constraints)

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-01** | 僅允許依賴 Python 標準庫 (`json`, `pathlib`, `typing`)，禁止引入第三方套件 | 保持 Library 輕量化 |
| **CONS-02** | 函式需保持無狀態 (Stateless)，不得使用全域變數或類別屬性儲存狀態 | 確保執行緒安全 |
| **CONS-03** | `json_dump` 與 `json_load` 必須位於同一個 Functional Unit 中 | 保持模組內聚性 |
| **CONS-04** | 嚴禁依賴任何業務系統 (Business System) 或資料源 (Datasource) 層級的模組 | 遵守 Dependency Rule |
