# wBiSaProj 專案設計文件 - 方法論篇

## 文件定位與導覽

本文件是 wBiSaProj 專案**方法論篇設計文件**，為 [總體設計文件](PROJECT_DESIGN.md) 第三部分的詳細展開。

**文件體系**：

```text
總體設計文件 (PROJECT_DESIGN.md)
    ├── 📘 架構篇 (PROJECT_DESIGN-ARCHITECTURE.md)
    ├── 📗 方法論篇 (本文件)
    └── 📙 協作篇 (PROJECT_DESIGN-COLLABORATION.md)
```

**本文件結構**：

1. **核心開發哲學**：闘述價值驅動、文件先行、文件即程式、品質內建、原子化提交的設計理念
2. **Feature-Task 二層結構**：定義開發的基本單位與層級關係
3. **Feature 分類體系**：詳述四大類型 Feature 及其標準任務模板
4. **Feature 開發生命週期**：說明 1+N 提交結構的執行流程
5. **Task 開發模式**：深入探討兩階段 TDD 決策模型
6. **Git 工作流程規範**：定義分支策略與提交格式
7. **品質保證機制**：建立開發流程的品質閘道
8. **文件組織結構**：規範 use-cases 的組織與內容標準

---

## 1. 核心開發哲學

採用一個**以價值為導向 (Value-Driven)**、**文件先行 (Document-First)** 的**結構化開發框架**。本框架深度結合了**雙軌制的測試策略**（包含標準 TDD 與探索式驗證），並為 LLM 人機協作預留標準化介入點。

### 1.1 價值驅動 (Value-Driven)

- 以交付完整的 **Feature（功能）** 作為開發的基本單位
- 每個 Feature 必須是可獨立交付的價值單元
- **價值 = 業務價值 + 技術價值**（例如：可維護性、可重用性、降低未來重構成本等）
- 根據價值對象與交付模式分為四大類型

### 1.2 文件先行 (Document-First)

- 嚴格遵循「先定義，後實現」的開發順序
- **業務層面**：先撰寫 `use-cases` 文件，定義 What & Why
- **技術層面**：再撰寫 `specs` 文件，定義 How
- 文件與程式碼同步提交，確保一致性

### 1.3 文件即程式 (Docs-as-Code)

- 將所有受版本控制的專案文件視為人機溝通與系統執行的「單一事實來源 (Single Source of Truth)」
- 程式碼的實現必須與技術規格文件保持絕對一致，確保文件的權威性與可執行性

### 1.4 品質內建 (Quality Built-in)

- 以內建於流程的雙軌測試策略（包含標準 TDD 與探索式驗證）作為品質保證的基礎
- 測試內建於開發流程，而非獨立步驟
- 透過「紅燈-綠燈-重構」循環從源頭保證品質

### 1.5 原子化與可追溯性 (Atomicity and Traceability)

- **Feature ↔ Branch**：一個功能對應一個分支
- **Task ↔ Commit**：一個任務對應一個原子提交
- 建立清晰、可追溯的 Git 歷史脈絡

---

## 2. Feature-Task 二層開發結構

開發工作圍繞「功能 (Feature)」和「任務 (Task)」兩層結構展開：

```text
Feature（業務價值單元）
├── Use Cases Commit（定義 What & Why）
└── Task Commits（實現 How）
    ├── Task 1: 對 Functional Unit A 的操作
    ├── Task 2: 對 Functional Unit B 的操作
    └── Task N: 對 Functional Unit N 的操作
```

**核心定義**：
- **Feature**：完整的、可獨立交付的業務/技術價值單元
    - 在**業務系統**或**資料源系統**中，它必須歸屬於一個業務 `Domain`
    - 在**函式庫 (Library)** 中，它必須歸屬於一個**具體的**技術功能分類 `Toolkit`
    - **原子化原則 (Atomicity Principle)**：
        - **單一職責**：一個 Feature 只能解決一個特定的技術問題或業務需求。
        - **領域隔離**：嚴禁將不同技術領域 (如 Crypto 與 Date) 的工具合併在同一個 Feature 中。
    - **命名導向 (Naming Orientation) [CRITICAL]**：
        - **聚合能力命名**：Feature 名稱必須描述其 **「對外交付的完整能力 (Aggregate Capability)」**，而非僅描述內部單一 FU 的實作。
        - ❌ **Bad (Too Narrow)**: `excel-reader` (若該 Feature 同時包含 Writer，此命名則定義過窄)。
        - ❌ **Bad (Too Broad)**: `file-helper` (若該 Feature 僅處理 Excel，此命名則定義過寬)。
        - ✅ **Good (Precise)**: `excel-processing` (精確涵蓋了 Reader 與 Writer 的完整能力)。

- **Task**：對某個特定 Functional Unit 的新增或修改操作

> **關鍵理解：Feature 與 FU 的關係**
>
> - `FU (Functional Unit)` 是從**技術實作**角度出發的最小結構單元
> - `Feature` 是從**業務價值**角度出發的交付單位
> - 一個 Feature 的實現，通常涉及對一個或多個 FU 的新增或修改

### 2.1 Feature 拆分與原子化原則 (Feature Decomposition)

為了避免產生「巨型 Feature (Monolithic Feature)」，在定義 Feature 範圍時，必須執行以下拆解檢核：

#### A. 複合式需求拆解 (Composite Requirement Breakdown)

若一條原始需求描述包含了「多個步驟」或「多種資料維度」，**嚴禁**合併為一個 Feature。

- **異質技術熱點 (Heterogeneous Tech Spots)**：
    - *範例*：需求為「搜尋股票並顯示 K 線圖」。
    - *拆解*：
        1. `stock-search` (專注於全文檢索與模糊比對)
        2. `stock-chart` (專注於時間序列資料的查詢與計算)
    - *理由*：兩者依賴的底層技術 (Search Engine vs. Time-series DB) 與變動頻率完全不同。

- **UI/流程 區塊分離**：
    - *範例*：需求為「股票總覽看板 (含列表、篩選、當日走勢)」。
    - *拆解*：
        1. `stock-overview-list` (列表與篩選邏輯)
        2. `stock-intraday-trend` (當日走勢計算)
    - *理由*：確保每個 Feature 可獨立測試與交付，避免單一 Feature 牽涉過多 Repository。

#### B. 共用能力提取 (Shared Capability Extraction)

若某項能力可以被多個 Feature 或 ETL Job 使用，應該將其拆分為獨立的 Feature，作為其他 Feature 的依賴，而非重複實作。拆分時需依據**可攜性**判斷其歸屬層級：

| 能力性質 | 判斷基準 | 歸屬 | 範例 |
|:---------|:---------|:-----|:-----|
| 真實世界已確立的通用公式、定義或演算法 | 離開本專案仍適用 | **wutils** Library Feature | MA 計算、Black-Scholes 定價、Country 定義 |
| 本專案跨系統共用的介面或 Schema | 離開此系統仍適用，但限於本專案 | **core** Library Feature | 跨系統資料契約 |
| 特定系統內部多處共用的邏輯 | 僅此系統內部適用 | **`<system>/core`** Library Feature 或 **Internal Service Feature** | 系統特有的商業規則組合 |

---

## 3. Feature 分類體系

根據專案架構設計，Feature 分為四大類型，每種類型都有其標準的任務模板。

### 3.1 Feature 類型總覽

| Feature 類型 | 核心職責 | 對應架構 | 標準 Task 模板 |
|:-------------|:---------|:---------|:---------------|
| **Business Feature** | 即時業務功能 | 業務系統的 api, service, db 層 | DB → Service → API |
| **Library Feature** | 開發者工具與共用元件 | Library 層 | 彈性（根據 FU 特性） |
| **Data Source Feature** | 提供唯讀原始數據 | 資料源系統 | Collector → Service |
| **Data Pipeline Feature** | 批次資料處理 | 業務系統的 etl 層 | Extractor → Transformer → Loader → Job |

### 3.2 Task 模板詳細說明

#### Business Feature Tasks（標準三層架構）

| Task 類型 | 職責 | 產出 |
|:----------|:-----|:-----|
| **DB Task** | 建立資料模型與存取邏輯 | Storage Structure、Repository 實作 |
| **Service Task** | 實作業務邏輯與規則 | 業務服務、領域邏輯 |
| **API Task** | 定義對外介面端點 | RESTful API、回應格式 |

#### 技術型特例 (Technical Value Features)

技術型特例是指**非 Library 卻不直接提供業務價值**的 Feature，其價值在於為其他 Feature 提供穩定的技術基礎。本專案定義兩種技術型特例：

##### A. DB-only Feature（資料存取能力）

DB-only Feature 專注於定義資料模型與存取能力，為下游的 Business Feature 或 Data Pipeline Feature 提供穩定的資料契約。

**交付策略**：本專案採用**資料需求獨立原則**，所有涉及資料的需求，**固定採用雙軌交付 (Dual Track Delivery)**：

1. **第一軌**：先行交付 DB-only Feature（定義資料模型與存取能力）
2. **第二軌**：再交付 Business Feature（僅含 Service + API，依賴 DB-only Feature）

**設計理念**：

| 理由 | 說明 |
|:---|:---|
| **Schema 穩定性** | 避免資料模型因多個業務需求零散變更而頻繁異動 |
| **前瞻性設計** | 在資料層優先規劃，預先發想未來可能的資料需求 |
| **儲存複雜性** | 本專案的 DB 層可能涉及 SQL、NoSQL、FileSystem 或混合儲存，設計複雜度較高 |
| **契約穩定性** | DB-only Feature 成為下游 Business Feature 的穩定依賴契約 |

**規範**：
- **Public Interface**: 必須明確定義 Repository Interface 與 Domain Schemas (Pydantic)。
- **Encapsulation**: 必須完整封裝底層儲存實作 (SQL/FS/NoSQL)，下游不得感知。

##### B. Internal Service Feature（內部運算能力）

Internal Service Feature 專注於封裝複雜的業務運算邏輯，供多個 Feature 或 ETL Job 共用，但不對外暴露 API。

**適用情境**：當符合以下條件時，應獨立為 Internal Service Feature：
- 複雜的業務運算（如：選擇權定價公式、風險計算模型）
- 需被多個 Business Feature 或 ETL Job 共用
- 不需對外暴露 API

**規範**：
- **Scope**: 僅包含 Service 層，不包含 API 層。
- **Testing**: 必須包含完整的 Unit Tests。
- **Interface**: 應定義清晰的函數簽章與輸入輸出規格。

#### Data Source Feature Tasks

| Task 類型 | 職責 | 實作核心 |
|:----------|:-----|:-----|
| **Collector Task** | 實作資料收集 | 爬蟲邏輯或資料庫連線 |
| **Service Task** | 提供統一存取介面 | 實作 core/interfaces 定義的抽象 |

#### Data Pipeline Feature Tasks（ETL 流程）

此類 Feature 專注於批次資料處理。

> **核心原則**：ETL 層是業務領域模型的消費者，原則上以既有的 DB schema 作為一份穩定契約，使 ETL 可與 Schema 演進解耦。

一個 `Data Pipeline Feature` 可由以下任一任務組合而成：

| Task 類型 | 職責 | 資料流向 |
|:----------|:-----|:---------|
| **Extractor Task** | 從資料源擷取資料 | 資料源 → ETL |
| **Transformer Task** | 資料清理、轉換、計算 | ETL 內部處理 |
| **Loader Task** | 將處理後資料載入目標 | ETL → 目標系統 |
| **Job Task** | 整合上述元件為可排程作業 | 端到端協調 |

#### Library Feature Tasks

- **原則**：形式彈性，但必須遵守 **One Feature = One Technical Topic** 原則。
    - **高內聚性 (High Cohesion)**：一個 Feature 應包含該主題下**邏輯緊密相關**的所有元件（例如：**成對的序列化/反序列化函數**、或一組針對同一資料結構的 Helper），**不可為了追求原子化而將原本應屬一體的邏輯拆散**。
- **反模式 (Anti-Pattern)**：
    - 禁止建立名為 `common`, `utils`, `helpers`, `misc` 的 Feature。
    - 若發現需求包含多個**不同技術領域**的工具 (e.g., String + Crypto)，**必須**拆解為多個獨立的 Features。

---

## 4. Feature 開發生命週期 (1+N 提交結構)

每個 Feature 都遵循一個標準生命週期，確保「文件先行」與「原子化提交」。

### 4.1 階段一：業務需求定義 (The First Commit)

**目標**：定義功能的 **What, Why, 以及執行層面的 How**

**執行者**：專案關係人、SA (系統分析師)、Developer

**產出**：完整的 `use-cases` 文件，必須包含 `requirements.md` 與 `design.md`

**Git 操作流程**：

1. 基於 `develop` 分支，建立新的 `feature` 分支
2. 撰寫完整的 `use-cases` 文件：
   - **`requirements.md`**：定義 What (業務需求、使用者故事)
   - **`design.md`**：定義 Why (背景目標) 與 How (高階技術設計、任務分解)
3. 將包含上述完整內容的 `use-cases` 目錄，作為此分支的**第一個 Commit** 提交
   - Commit 類型：`docs`
   - Scope：對應的 `use-cases` 路徑

> 此提交確立了整個 Feature 的開發目標、邊界、以及詳細的執行計畫。

### 4.2 階段二：技術任務執行 (The N Commits)

**目標**：根據**已規劃好的任務清單**，逐步實現功能的技術細節

**執行者**：Developer、Operator (在人機協作模式下)

**產出**：規格文件 (`specs`)、測試程式與功能程式碼

**Git 操作流程**：

1. 根據 `use-cases/design.md` 中已定義的「任務分解」清單，Developer 開始逐一執行技術任務 (Tasks)
2. 針對**每一個 Task**，嚴格遵循 TDD 執行模式進行開發
3. 每個 Task 完成後，將其**所有產出**（`specs` 文件、測試碼、實作碼）作為一個**原子化的 Commit** 提交

**最終結果**：

```text
Feature Branch
├── 1 個 docs 類型的 use-cases 提交 (已包含任務規劃)
└── N 個 feat/fix/refactor 類型的 Task 提交
```

---

## 5. Task 開發模式：雙軌測試策略決策

所有 Task 都遵循 TDD 精神。開發流程需依循一個兩階段的決策模型：首先根據任務處理對象的**「確定性與可控性」**選擇合適的 **TDD 模式**（標準 TDD 或探索式 TDD）；然後再根據目標 Functional Unit 的狀態，選擇對應的 **Task 執行模式**（新增或修改）。

### 5.1 第一階段：選擇測試策略模式 (標準 vs. 探索式)

雖然所有 Task 都遵循 TDD 精神，但根據其處理對象的特性，應選擇不同的 TDD 模式。

#### 測試策略決策表

| Task 處理的資料來源/性質 | 核心挑戰 | 建議 TDD 模式 |
|:------------------------|:---------|:---------|
| **專案內部的資料儲存**<br>(SQL / NoSQL / File) | 結構由我方定義且完全可控，挑戰在於邏輯正確性 | **標準 TDD** |
| **外部網站 (Web Scraping)** | HTML/JSON 結構未知，且隨時可能變更 | **探索式 TDD** |
| **第三方 RESTful API** | API 合約雖有文件，但需驗證實際回傳的格式與邊界值 | **探索式 TDD** |
| **外部提供的檔案 (CSV, Excel)** | 格式可能不一致，資料品質（如編碼、空值表示）未知 | **探索式 TDD** |
| **Job Task (端到端整合)** | 需驗證包含多個元件（可能含外部依賴）的完整資料流程 | **探索式 TDD (優先)** |

#### 測試策略決策樹

```text
Task 類型判斷：
├─ Collector Task → 探索式 TDD（無條件）
├─ Extractor Task
│   ├─ 資料來自外部 → 探索式 TDD
│   └─ 資料來自內部 → 標準 TDD
├─ Job Task → 探索式 TDD（建議優先）
└─ 其他 Task → 標準 TDD（預設）
```

> **技術選型說明**
>
> 所有 Task 的技術選型，皆須遵循架構篇 #6.5 關於「資料存取技術選型」的架構決策：
> - **SQL (RDBMS)**: 使用 ORM 進行封裝 (e.g., SQLAlchemy)
> - **NoSQL**: 使用 ODM 進行封裝 (e.g., Motor/Pymongo)
> - **FileSystem**: 使用 DTO 進行結構化存取

> **Extractor Task 的測試策略選擇**
>
> `Extractor Task` 在選擇 TDD 模式時，需要特別注意其最終資料來源：
> - **從內部 DB 直接擷取**：適用**標準 TDD**
> - **透過資料源系統的 service 層擷取**：
>   - 若原始來源是內部 DB → 適用**標準 TDD**
>   - 若原始來源是外部爬蟲/API → 適用**探索式 TDD**
>
> **核心判斷原則**：追溯資料的「原始來源」，判斷其是否由我方完全控制。

> **Job Task 的測試策略選擇**
>
> - 若 Job **僅**整合內部、可控的元件，理論上可採用標準 TDD
> - 若 Job 流程中包含任何與外部資料源的互動，則必須採用**探索式 TDD**
> - **實務建議**：Job Task 優先採用探索式 TDD，驗證完整流程在真實環境下的運作

### 5.2 第二階段：選擇 Task 執行模式 (新增 vs. 修改)

在確定了採用標準或探索式 TDD 之後，再根據目標 Functional Unit 的狀態，選擇具體的執行模式。

#### 執行模式判斷準則

**首要判斷**：目標 Functional Unit 是否已存在？

| 狀態 | Task 執行模式 | Generator 類型 | 關鍵差異 |
|:-----|:---------|:---------------|:---------|
| **不存在** | 模式一（新增） | 生成類 | 從零開始創建 |
| **已存在** | 模式二（修改） | 更新類 | 基於現有程式碼修改 |

#### 執行模式間的關鍵差異

| 差異點 | 模式一：新增 | 模式二：修改 |
|:-------|:-------------|:-------------|
| **輸入準備** | 僅需前置文件 | 需現有文件 + 變更需求 |
| **中間產物** | 無 | `*_changes.md`（記錄差異） |
| **審核重點** | 符合需求 | 符合需求 + 向下相容 |

### 5.3 標準 TDD 執行步驟

適用於：Business Tasks、Library Tasks、Service Task、Transformer Task、Loader Task

#### 執行模式一：新增 Functional Unit

| 步驟 | 目的 | 產出 | TDD 狀態 |
|:-----|:-----|:-----|:---------|
| 1. 需求規格 | 將業務需求轉為技術規格 | specs/.../requirements.md | - |
| 2. 設計規格 | 定義架構與介面 | specs/.../design.md | - |
| 3. 測試規格 | 定義測試情境與預期結果 | specs/.../tests.md | - |
| 4. 測試實作 | 撰寫測試程式 | tests/.../test_*.py | 🔴 紅燈 |
| 5. 功能實作 | 實現最小可行功能 | 功能程式碼 | 🟢 綠燈 |
| 6. 重構優化 | 改善程式品質 | 優化後程式碼 | 🟢 維持綠燈 |

#### 執行模式二：修改現有 Functional Unit

| 步驟 | 目的 | 產出 | TDD 狀態 |
|:-----|:-----|:-----|:---------|
| 1. 更新需求規格 | 反映新業務需求 | 更新的 requirements.md + requirements_changes.md* | - |
| 2. 更新設計規格 | 調整實作架構 | 更新的 design.md + design_changes.md* | - |
| 3. 更新測試規格 | 調整測試情境 | 更新的 tests.md + tests_changes.md* | - |
| 4. 測試實作 | 修改測試程式 | 更新的 test_*.py | 🔴 紅燈 |
| 5. 功能實作 | 修改功能程式 | 更新的程式碼 | 🟢 綠燈 |
| 6. 重構優化 | 改善整體品質 | 優化後程式碼 | 🟢 維持綠燈 |

*註：`*_changes.md` 文件記錄變更差異，僅供開發過程使用，不隨程式碼提交

> **TDD 測試狀態流轉**
> - 步驟 4（測試實作）→ 必須是【🔴 紅燈】（測試失敗）
> - 步驟 5（功能實作）→ 必須達到【🟢 綠燈】（測試通過）
> - 步驟 6（重構優化）→ 必須維持【🟢 綠燈】（測試仍通過）
>
> 這個紅→綠→維持綠的流轉是 TDD 的核心精神

#### 變更追蹤機制（*_changes.md）

| 屬性 | 說明 |
|:-----|:-----|
| **用途** | 在修改現有 FU 時，記錄變更理由與影響分析 |
| **生命週期** | 僅存在於開發過程，不納入版本控制 |
| **內容結構** | 變更原因、影響範圍、相容性考量、關鍵差異對照 |

> **重要**：這些文件是更新類 Generator 的重要輸入，幫助 LLM 理解修改脈絡

### 5.4 探索式驗證 (Exploratory Validation) 執行步驟

適用於需要探索外部資料源的 Tasks：

- `Collector Task` (所有場景)
- 處理**外部資料源**的 `Extractor Task`
- `Job Task` (端到端測試)

> **重要說明**：針對**內部資料源**的 `Extractor Task`，因其資料庫 Schema 完全可控且已知，應直接採用**標準 TDD**。

#### 執行模式一：新增 Functional Unit

| 步驟 | 目的 | 產出 | TDD 狀態 |
|:-----|:-----|:-----|:---------|
| 1. 需求規格 | 定義資料需求 | specs/.../requirements.md | - |
| 2. 初步設計 | 設計資料處理流程 | specs/.../design.md | - |
| 3. 探索實作 | 連接資料源，取得樣本 | 初版程式碼 | - |
| 4. 資料剖析 | 分析資料特性與邊界案例 | 資料特性文件 | - |
| 5. 驗證規格* | 基於實際資料定義驗證標準 | specs/.../validation.md | - |
| 6. 驗證實作 | 撰寫資料品質測試 | test_*.py | 🔴 紅燈 |
| 7. 修正實作 | 調整程式通過驗證 | 功能程式碼 | 🟢 綠燈 |
| 8. 優化 | 改善效能與錯誤處理 | 優化後程式碼 | 🟢 維持綠燈 |

*註：此處的「驗證規格」基於探索後的真實資料樣本來定義，其本質是「將發現轉化為規格」

#### 執行模式二：修改現有 Functional Unit

| 步驟 | 目的 | 產出 | TDD 狀態 |
|:-----|:-----|:-----|:---------|
| 1. 更新需求規格 | 反映新業務需求 | 更新的 requirements.md + requirements_changes.md* | - |
| 2. 更新初步設計 | 調整資料處理流程 | 更新的 design.md + design_changes.md* | - |
| 3. 重新探索 | 驗證資料源是否改變 | 更新的探索程式碼 | - |
| 4. 更新資料剖析 | 識別新的邊界案例 | 更新的資料特性文件 | - |
| 5. 更新驗證規格 | 調整驗證標準 | 更新的 validation.md + validation_changes.md* | - |
| 6. 更新驗證實作 | 修改測試程式 | 更新的 test_*.py | 🔴 紅燈 |
| 7. 修正實作 | 修改功能程式 | 更新的程式碼 | 🟢 綠燈 |
| 8. 優化 | 改善整體品質 | 優化後程式碼 | 🟢 維持綠燈 |

> **關鍵差異**
> - **標準 TDD**：預先定義測試 → 實作
> - **探索式驗證**：探索資料 → 定義驗證 → 測試 → 修正

### 5.5 Task 產出的標準路徑

| 步驟類型 | 新增模式產出 | 修改模式產出 |
|:---------|:-------------|:-------------|
| 需求規格 | `docs/specs/<fu_path>/<fu_name>/requirements.md` | 更新原檔 + `requirements_changes.md*` |
| 設計規格 | `docs/specs/<fu_path>/<fu_name>/design.md` | 更新原檔 + `design_changes.md*` |
| 測試規格 | `docs/specs/<fu_path>/<fu_name>/tests.md` | 更新原檔 + `tests_changes.md*` |
| 測試實作 | `tests/<fu_path>/<fu_name>/test_*.py` | 更新原檔 |
| 功能實作 | `<fu_path>/<impl_file>` | 更新原檔 |

*開發過程檔案，不提交

> **路徑對應關係說明 (Path Correspondence)**
>
> 為強化文件與程式碼之間的連結，專案的結構遵循`架構篇`所定義的「結構對應性原則」。表格路徑中的佔位符定義如下：
>
> - **`<fu_path>`**：本次 Task 所操作的 **功能單元容器 (FU Container) 相對於專案根目錄的完整路徑**
> - **`<fu_name>`**：本次 Task 所操作的 **具體功能單元 (FU) 的名稱**，以目錄或檔案命名友善的格式表示 (例如：`create-user-profile` 或 `user_profile`)
>
> 透過此設計，開發者可以藉由 `<fu_name>` 快速定位其對應的規格與測試文件。規格文件中則會進一步指引至功能實作的具體路徑，從而確保專案的可維護性與導航效率。關於此原則的完整設計理念與細節，請參閱《架構篇》中的「結構對應性原則」章節。

---

## 6. Git 工作流程規範

### 6.1 核心規則（規範定義）

#### 分支策略

| 分支類型 | 用途 | 生命週期 |
|:---------|:-----|:---------|
| **master** | 生產分支 | 永久 |
| **develop** | 開發主線 | 永久 |
| **feature/<path>/<description>** | 功能開發分支 | 短期 |

#### 分支 Path 決策規則

**規則核心**：分支名稱必須採用**階層式命名**，其路徑結構應與該 Feature 在 `docs/use-cases/` 中的相對路徑完全一致（不含 `docs/use-cases/` 前綴）。這能確保 Git 分支結構、文件目錄結構與程式碼架構三者的高度對應，並有效避免命名衝突。

**格式標準**：`feature/<root>/<hierarchy>/<feature_name>`

| Feature 類型 | 命名邏輯 | Branch Path 範例 |
|:---|:---|:---|
| **System-Type Feature**<br>(Business, Data Pipeline, Data Source) | `<system>/<domain>/[<subdomain>]/<feature_name>`<br>*(若無 subdomain 則省略)* | **多層級 (有 sub-domain)**:<br>`feature/gms/market/stock/stock-profile`<br><br>**單層級 (僅 domain)**:<br>`feature/gms/user/registration`<br><br>**ETL Feature**:<br>`feature/gms/etl/market/stock/daily-sync` |
| **Library-Type Feature**<br>(General) | `<library>/<toolkit>/<feature_name>` | **通用函式庫**:<br>`feature/wutils/io/pickle-io`<br>`feature/core/validator/format-rules` |
| **Library-Type Feature**<br>(System Internal) | `<system>/core/<toolkit>/<feature_name>` | **系統內核心庫**:<br>`feature/gms/core/config/env-management` |

#### 提交格式規範

**基本格式**：`<type>(<scope>): <subject>`

**Type 類型定義**：

| Type | 用途 | 範例 |
|:-----|:-----|:-----|
| `feat` | 新增功能 | `feat(gms/api/user): add endpoint` |
| `fix` | 修復錯誤 | `fix(gms/db/user): correct query` |
| `refactor` | 重構（不改變功能） | `refactor(core/validator): simplify logic` |
| `test` | 測試相關 | `test(gms/service/user): add unit tests` |
| `docs` | 文件更新 | `docs(use-cases/gms/user): define requirements` |
| `chore` | 建構/工具相關 | `chore(build): update dependencies` |

#### Scope 格式規範（雙軌制）

基於架構篇的核心開發術語定義，我們採用以下 Scope 規則：

| 提交類型 | Scope 格式說明 | 範例 |
|:---|:---|:---|
| **`docs` 提交**<br/>(Use Cases 文件) | Scope 需對應文件的父目錄路徑，根據模組類型分為兩種格式：<br/>1. **系統**: `use-cases/<system>/[<domain>]`<br/>2. **函式庫**: `use-cases/<library>/<toolkit>` | 1. `docs(use-cases/gms/user): ...`<br/>2. `docs(use-cases/core/config): ...` |
| **實作提交**<br/>(feat, fix, etc.) | Scope 為受影響的功能單元容器路徑 (`<fu_path>`) | `feat(gms/api/user/profile): ...` |

### 6.2 標準範例（團隊共識）

以下範例展示了不同類型的 Feature 如何實踐「1+N」開發生命週期。Commit 歷史由新到舊排列。

#### Business Feature 範例

```bash
# Feature: 使用者註冊功能 (屬於 User Domain)
# Path: gms/user
# Branch: feature/gms/user/user-registration

# Commit 歷史（由新到舊）：
feat(gms/api/user): create POST /users endpoint for registration
feat(gms/service/user): implement user creation and validation logic
feat(gms/db/user): implement user profile model and repository
docs(use-cases/gms/user): define user registration requirements and tasks
```

#### Data Pipeline Feature 範例

```bash
# Feature: 每日股價同步 (屬於 Market Domain, Price Sub-domain)
# Path: gms/etl/market/stock
# Branch: feature/gms/etl/market/stock/daily-stock-sync

# Commit 歷史（由新到舊）：
feat(gms/etl/jobs/market): create and schedule daily stock sync job
feat(gms/etl/loaders/market/price): implement loader for stock price db
feat(gms/etl/transformers/market/price): implement stock data cleansing
feat(gms/etl/extractors/market/price): implement stock data source extractor
docs(use-cases/gms/etl/market): define daily stock sync requirements
```

#### Data Source Feature 範例

```bash
# Feature: 證交所爬蟲 (屬於 Price Domain)
# Path: twseprice/price
# Branch: feature/twseprice/price/init-daily-price

# Commit 歷史（由新到舊）：
feat(twseprice/service/daily_price): implement repository interface
feat(twseprice/collector/daily_price): implement html parser and request
docs(use-cases/twseprice/daily_price): define twse scraper requirements
```

#### Library Feature 範例

```bash
# Feature: 資料驗證器 - 格式規則
# Path: core/validator
# Branch: feature/core/validator/add-validator-format-rules

# Commit 歷史（由新到舊）：
feat(core/validator/rules): add email format validation rule
feat(core/validator/rules): implement basic data type validation rule
docs(use-cases/core/validator/rules): define data format validator api and requirements
```

---

## 7. 通用品質閘道

> **品質閘道原則**：每個提交都必須通過完整的品質檢查，這是強制性的架構要求。

在每次執行 `git commit` 前，開發者應確認以下品質閘道均已通過：

| 檢查項目 | 說明 | 自動化支援 |
|:---|:---|:---|
| **依賴管理正確性** | 若本次 Task 新增或調整 FU Container，已執行對應的 `inv dev.imports-*` 命令。若未正確執行，通常會導致測試階段因導入失敗而中斷。 | - |
| **測試通過** | 所有與本次變更相關的測試均已執行並成功通過 | commit-touch 自動執行相關測試 |
| **文件與程式碼一致性** | 最終實現完整對應 `specs` 技術規格與 `use-cases` 業務目標 | 人工確認 or 人工引導 LLM 協作確認 |

---

## 8. Use Cases 文件組織結構

`use-cases` 的組織結構直接映射了專案的核心組織原則，其路徑由 Feature 的歸屬（系統或函式庫）及其業務/技術範疇（Domain/Toolkit）精確決定，確保文件與架構的絕對一致性。

### 8.1 路徑結構總覽

| Feature 類型 | 核心職責 | 路徑結構範本 |
|:---------------|:---------|:-------------|
| **Business Feature**<br/>**Data Source Feature** | 實現業務功能或提供資料 | `docs/use-cases/<system>/[<domain>]/[<subdomain>]/<feature_name>/` |
| **Data Pipeline Feature** | 批次資料處理 (ETL) | `docs/use-cases/<system>/etl/[<domain>]/[<subdomain>]/<feature_name>/` |
| **Library Feature** | 提供共用元件或工具 | `docs/use-cases/<library>/<toolkit>/<feature_name>/` |

### 8.2 系統 Feature 路徑歸屬規則 (Business, Data Source, Data Pipeline)

系統中的 Feature 路徑，由其歸屬的業務範疇以及系統本身的領域單一性直接決定。

#### 規則一：若 Feature 歸屬於 Sub-domain

此規則適用於**多領域系統**。文件應被放置在對應的 `sub-domain` 目錄下。

- **路徑格式**：`docs/use-cases/<system>/<domain>/<subdomain>/<feature_name>/`
- **範例**：`gms` 系統中，一個歸屬於 `mkt` Domain 下 `stk` 子領域的 `stock-info-sync` Feature：
  - `docs/use-cases/gms/mkt/stk/stock-info-sync/`

#### 規則二：若 Feature 歸屬於 Domain

此規則適用於**多領域系統**。文件應被放置在父層 `domain` 的根目錄下。

- **路徑格式**：`docs/use-cases/<system>/<domain>/<feature_name>/`
- **範例**：`gms` 系統中，整合了多個子領域資訊的 `market-dashboard` Feature：
  - `docs/use-cases/gms/mkt/market-dashboard/`

#### 規則三：若系統為單一業務領域

此規則適用於**單領域系統**，根據「系統即領域原則」，應省略 `<domain>` 層級。

- **路徑格式**：`docs/use-cases/<system>/<feature_name>/`
- **範例**：假設有一個只處理客戶關係的 `crm` 系統，`add-new-contact` Feature 的路徑為：
  - `docs/use-cases/crm/add-new-contact/`

#### 規則四：Data Pipeline Feature 的特殊規則

對於 `Data Pipeline Feature`，需在其系統路徑後插入 `etl` 層，以明確其架構歸屬。

- **路徑格式**：`docs/use-cases/<system>/etl/[<domain>]/[<subdomain>]/<feature_name>/`
- **範例**：`gms` 系統中，一個處理市場股票資料的 ETL Feature：
  - `docs/use-cases/gms/etl/mkt/stk/daily-stock-sync/`

### 8.3 函式庫 Feature 路徑歸屬規則 (Library Feature)

函式庫 Feature 的組織由其功能分類 (`toolkit`) 驅動，而非業務領域。

#### 規則一：專案級函式庫

適用於專案根目錄下的 `core`, `wutils` 等函式庫。

- **路徑格式**：`docs/use-cases/<library>/<toolkit...>/<feature_name>/`
- **範例**：為 `core` 函式庫的 `validator` toolkit 新增格式驗證規則：
  - `docs/use-cases/core/validator/rules/add-format-rules/`

#### 規則二：系統級核心函式庫

適用於特定系統內部的 `<system>/core` 模組。其路徑結構反映了它既屬於某個系統，又是一個函式庫的雙重特性。

- **路徑格式**：`docs/use-cases/<system>/core/<toolkit...>/<feature_name>/`
- **範例**：為 `gms` 系統的內部核心模組 `gms/core` 的日誌工具集新增功能：
  - `docs/use-cases/gms/core/logging/add-trace-id/`

> **註**：`<toolkit...>` 路徑代表了技術功能的分類，它本身也可以是嵌套的，以反映技術概念的層次結構。

### 8.4 文件內容規範

為達到最大程度的精簡與聚焦，每個 `use-cases` 目錄僅包含以下兩份核心文件：

| 文件 | 職責 | 內容結構 |
|:-----|:-----|:---------|
| **requirements.md** | 定義 **What** | 業務需求、使用者故事、驗收條件 |
| **design.md** | 定義 **Why** 和 **How** | 1. 背景與目標<br/>2. 高階技術設計<br/>3. 任務分解 |

#### design.md 三大區塊詳細說明

| 區塊 | 內容 | 目的 |
|:-----|:-----|:-----|
| **背景與目標** | 簡述 Feature 的商業價值與要解決的問題 | 說明 Why |
| **高階技術設計** | 整體架構、模組互動、資料流、API 規格等 | 說明 How (架構層面) |
| **任務分解** | 可執行的、有序的技術任務清單 | 說明 How (執行層面) |

---

## 9. 人機協作準備

本開發方法論為 LLM 協作預留了標準化的介入點：

### 9.1 標準化步驟

每個開發步驟都可被 Prompt Generator 驅動執行，確保流程的一致性與可重複性。

### 9.2 審核循環

內建涵蓋「生成、審核、修正」三大環節的品質保證循環，確保所有產出符合專案標準。

### 9.3 結構化文件

高度結構化的文件體系，便於 LLM 理解與生成，降低歧義性。

### 9.4 明確的介入點

| 介入點 | LLM 角色 | 人類角色 |
|:-------|:---------|:---------|
| Use Cases 撰寫 | 根據需求生成初稿 | 審核與修正 |
| Specs 文件生成 | 根據 use-cases 生成技術規格 | 技術決策與審核 |
| 測試案例設計 | 生成測試情境與案例 | 確認業務邏輯正確性 |
| 程式碼實作 | 根據規格生成程式碼 | 程式碼審查 |
| 程式碼重構 | 提出優化建議 | 決定重構範圍 |

---

## 總結與後續閱讀

透過這套方法論，我們將「價值交付」的核心目標與「品質內建」的工程實踐緊密結合，並根據不同 Task 的特性採用適合的執行模式，為高效的人機協作奠定基礎。

**後續閱讀建議**：

| 文件 | 內容重點 | 適合場景 |
|:-----|:---------|:---------|
| [專案架構篇](PROJECT_DESIGN-ARCHITECTURE.md) | 系統架構與技術選型 | 了解系統組織結構 |
| [人機協作篇](PROJECT_DESIGN-COLLABORATION.md) | LLM 協作的標準化流程 | 掌握協作工具使用 |
| [架構實作指引](GUIDE_ARCHITECTURE.md) | 具體實作範例與最佳實踐 | 實際開發時參考 |
