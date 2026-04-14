# Library Feature Use-Cases - Requirements Guide

本規範定義 Library Feature 的 `requirements.md` 撰寫規範。目標是定義 **What**（做什麼）與 **Why**（價值），但不涉及技術實作細節。

*供 Generator: Prompt4NewLibFtReqSpec 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

Library Feature 的需求文件聚焦於「介面契約」與「行為規範」，作為後續技術設計 (`design.md`) 的唯一輸入來源。

### 1.2 關鍵特性

- **定義 What 而非 How**：僅描述功能目標與行為，不涉及實作細節。
- **正式依據**：此文件是該 Feature 業務需求範圍內的正式依據。
- **可追溯性**：所有需求必須可追溯至後續的設計與測試。

---

## 2. 檔案路徑標準

`docs/use-cases/<library>/<toolkit>/<feature_name>/requirements.md`

- `<library>`: 函式庫名稱 (e.g., `wutils`, `core`, `<system>/core`)
- `<toolkit>`: 功能分類 (e.g., `io`, `validator`, `ds/tree`)
- `<feature_name>`: 功能名稱 (e.g., `pickle-io`)

---

## 3. ID 命名規範

> **⚠️ 重要**：以下 ID 格式為全專案統一規範，必須嚴格遵守。

### 3.1 本文件定義 ID

| ID 格式 | 說明 | 用途 |
| :--- | :--- | :--- |
| `US-XXX` | User Story（三位數流水號） | §3 使用者故事 |
| `FR-XX` | Functional Requirement（兩位數流水號） | §4 功能需求 |
| `AC-XX` | Acceptance Criteria（兩位數流水號） | §5 驗收標準 |
| `NFR-XX` | Non-Functional Requirement（兩位數流水號） | §6 非功能需求 |
| `CONS-XX` | Architectural Constraint（兩位數流水號） | §7 架構約束 |

---

## 4. 內容結構模板

````markdown
# <Feature Name> - Requirements

## 1. Feature 概述 (Feature Overview)

### 1.1 元數據 (Metadata)

| Attribute | Value |
| :--- | :--- |
| **Feature Name** | `<feature_name>` |
| **Target Library** | `<library>` |
| **Toolkit Category** | `<toolkit>` |
| **Layer** | Library (No Business Dependencies) |

### 1.2 功能描述 (Description)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請描述以下兩點：
> - **目的**：一句話說明這個工具是做什麼的。
> - **價值主張 (Value Proposition)**：說明解決了什麼痛點？（如：Boilerplate、資源洩漏）。
>
> **💡 範例**：
>
> 「本功能旨在為 `wutils` 擴充 I/O 能力，提供更安全的 Pickle 讀寫介面，減少開發者處理 `with open()` 的重複性程式碼。」

<填入功能描述>

## 2. 變更歷史 (Change History)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 記錄版本變更與變更原因。由於 use-cases 文件是需求的起點，無上游來源文件可追溯，故本表格不包含 Source 欄位。
>
> **版本號格式**：`vX.Y.Z`（語意化版本）
>
> **💡 範例**：
>
> | Version | Date | Description |
> | :--- | :--- | :--- |
> | v1.0.0 | 2024-01-15 | Initial Release |
> | v1.1.0 | 2024-02-01 | 新增 pathlib 支援需求（因應跨平台部署回饋）|

| Version | Date | Description |
| :--- | :--- | :--- |
| v1.0.0 | <YYYY-MM-DD> | Initial Release |

## 3. 使用者故事 (User Stories)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請依循以下原則撰寫：
> - **角色**：本文件固定為 Python 開發者 (Developer)。
> - **重點**：聚焦於「開發體驗 (DX)」，描述開發者想達成的目標與獲得的效益。
> - **格式**：採用標準 User Story 格式。
> - **ID 規範**：`US-XXX`（三位數流水號，如 `US-001`）。
>
> **💡 範例**：
>
> - **US-001**
>   > 作為一名 Python 開發者 (Developer)
>   > 我想要 透過單一函式呼叫完成 Pickle 序列化與檔案寫入
>   > 以便於 減少重複的 `with open()` 樣板程式碼

- **US-001**
  > 作為一名 Python 開發者 (Developer)
  > 我想要 <填入執行的技術操作>
  > 以便於 <填入獲得的開發效益/解決的問題>

## 4. 功能需求 (Functional Requirements)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 請定義具體的行為邊界：
> - **不包含**：函式簽名或實作程式碼。
> - **輸入 (Input)**：描述函式接受的資訊類型（e.g., 路徑字串、設定物件）。
> - **輸出 (Output)**：描述預期回傳的結果。
> - **行為 (Behavior)**：包含資源管理、模式強制、錯誤傳遞等。
> - **ID 規範**：`FR-XX`（兩位數流水號，如 `FR-01`）。
>
> **💡 範例**：
>
> | ID | Description | Notes |
> | :--- | :--- | :--- |
> | **FR-01** | 接受任意可序列化物件與目標路徑，將物件序列化後寫入檔案 | 路徑支援 `str` 或 `PathLike` |
> | **FR-02** | 接受檔案路徑，讀取並反序列化後回傳原始物件 | 自動處理檔案開關 |
> | **FR-03** | 寫入操作需確保檔案正確關閉，即使發生例外 | Context Manager 模式 |

| ID | Description | Notes |
| :--- | :--- | :--- |
| **FR-01** | <填入具體需求> | <填入備註> |

## 5. 驗收標準 (Acceptance Criteria)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義「做完的定義 (Definition of Done)」：
> - **格式**：採用 BDD (Given/When/Then) 格式。
> - **禁止**：撰寫任何 Python 程式碼片段。
> - **必須包含**：Happy Path (主流程), Edge Case (邊界案例), Error Handling (錯誤處理) 三種情境。
> - **ID 規範**：`AC-XX`（兩位數流水號，如 `AC-01`）。
>
> **💡 範例**：
>
> - **AC-01: Happy Path (主流程)**
>   - **Given**: 一個可序列化的 Python 物件與有效的目標路徑
>   - **When**: 呼叫寫入功能
>   - **Then**: 檔案被建立且內容可被正確讀回還原為原始物件

- **AC-XX: Happy Path (主流程)**
  - **Given**: <填入前置條件 / 輸入狀態>
  - **When**: <填入執行的動作>
  - **Then**: <填入預期的結果 / 狀態改變>

- **AC-XX: Edge Case (邊界案例)**
  - **Given**: <填入前置條件 / 輸入狀態>
  - **When**: <填入執行的動作>
  - **Then**: <填入預期的結果 / 狀態改變>

- **AC-XX: Error Handling (錯誤處理)**
  - **Given**: <填入前置條件 / 輸入狀態>
  - **When**: <填入執行的動作>
  - **Then**: <填入預期的結果 / 狀態改變>

## 6. 非功能需求 (Non-Functional Requirements) [Optional]

> **📝 撰寫指引**（請勿保留本指引文字）：
> 僅當具有明確、可量化的效能指標或資源限制時填寫。
> 若無特殊需求，可標註「無特殊非功能需求」或省略本章節。
> - **ID 規範**：`NFR-XX`（兩位數流水號，如 `NFR-01`）。
>
> **常見類別**：
> - **Complexity**：演算法複雜度要求（e.g., O(1), O(n)）
> - **Resource**：記憶體或 CPU 限制（e.g., 峰值 < 100MB）
> - **Compatibility**：相容性要求（e.g., 支援 Windows 路徑）
> - **Performance**：效能指標（e.g., 處理 1GB 檔案 < 10s）
>
> **💡 範例**：
>
> | ID | Category | Description | Justification |
> | :--- | :--- | :--- | :--- |
> | **NFR-01** | Resource | 記憶體峰值 < 100MB | 需在記憶體受限環境運行 |
> | **NFR-02** | Compatibility | 支援 Windows/Linux/macOS 路徑格式 | 跨平台部署需求 |

| ID | Category | Description | Justification |
| :--- | :--- | :--- | :--- |
| **NFR-01** | <填入類別> | <填入具體指標> | <填入理由> |

## 7. 架構約束 (Architectural Constraints)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義實作時必須遵守的系統級限制：
> - **依賴規則**：允許/禁止使用的套件（e.g., 僅限標準庫、禁止依賴 `business` 層）。
> - **實作原則**：原子性、無狀態 (Statelessness)、封裝性等限制。
> - **相容性**：Python 版本要求、平台限制等。
> - **ID 規範**：`CONS-XX`（兩位數流水號，如 `CONS-01`）。
>
> **💡 範例**：
>
> | ID | Constraint | Notes |
> | :--- | :--- | :--- |
> | **CONS-01** | 僅允許依賴 Python 標準庫，禁止引入第三方套件。 | <備註> |
> | **CONS-02** | 函式需保持無狀態 (Stateless)，不得使用全域變數或類別屬性儲存狀態。 | <備註> |

| ID | Constraint | Notes |
| :--- | :--- | :--- |
| **CONS-XX** | <填入約束描述> | <填入備註> |

````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 檔案規範與定位

- [ ] **路徑正確性**：檔案路徑是否嚴格遵循 `docs/use-cases/<library>/<toolkit>/<feature_name>/requirements.md`？
- [ ] **Metadata 完整性**：元數據表格是否填寫完整？且 `Layer` 明確標註為 `Library (No Business Dependencies)` (對應 §1.1)？
- [ ] **變更歷史**：是否已填寫變更歷史，且版本號遵循 `vX.Y.Z` 語意化格式 (對應 §2)？

### B. 核心價值定義

- [ ] **描述深度**：功能描述是否包含「目的」與「價值主張 (Value Proposition)」，並清晰說明了解決什麼痛點 (對應 §1.2)？
- [ ] **User Story 聚焦**：主詞是否固定為「開發者 (Developer)」，並聚焦於提升開發體驗 (DX) 與獲得的效益 (對應 §3)？

### C. 需求與行為邊界

- [ ] **行為定義**：`Functional Requirements` 是否僅描述行為（輸入/輸出特性），且完全不含函式簽名或實作程式碼 (對應 §4)？
- [ ] ⚠️ **架構約束確認**：`Architectural Constraints` 是否明確列出允許或禁止使用的套件，如僅限標準庫 (對應 §7)？

### D. 驗收標準

- [ ] **格式規範**：是否嚴格採用 BDD (Given/When/Then) 格式 (對應 §5)？
- [ ] **情境覆蓋**：確保完整包含 Happy Path、Edge Case、Error Handling 三種情境 (對應 §5)？
- [ ] **程式碼禁令**：驗收標準描述中是否完全不包含任何 Python 語法或程式碼片段 (對應 §5)？

### E. 格式與命名規範

- [ ] **ID 命名精確度**：確保 `US` 採三位數 (`US-XXX`)，其餘 (`FR`, `AC`, `NFR`, `CONS`) 均採二位數 (`-XX`) (對應 §3, §4, §5, §6, §7)？

### F. 最終清理

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
