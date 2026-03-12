# Feature Overview - Documentation Guide

本規範定義 **Feature Overview (功能總覽)** 文件的撰寫規範。適用於所有 `docs/use-cases/.../overview.md` 路徑下的總覽文件。目標是提供**價值清單 (Feature Catalog)** 與 **決策指引 (Decision Guide)**，作為 System Analyst (LLM) 執行「Feature 歸屬判定」與「新增 vs 修改決策」時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範為**通用規範**，適用於以下所有類型：
> - **業務系統 (Business System)**：System (單一領域) / Domain / Sub-domain 層級
> - **資料源系統 (Data Source System)**：System (單一領域) / Domain 層級
> - **專案級函式庫 (Library)**：Toolkit 層級
> - **系統核心庫 (System Core)**：Toolkit 層級
>
> 各類型共用相同的文件結構，但在 **Feature Catalog** 與 **Decision Guide** 的內容要求上存在差異，詳見 [Section 4.2](#42-feature-catalog-功能清單) 與 [Section 4.3](#43-decision-guide-決策指引) 中的類型專屬規範。

*供 Generator: Prompt4FeatureOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是特定領域 (Domain/Toolkit) 的「價值目錄」。它不描述具體的技術實作，而是回答：「這個領域已經交付了哪些價值？」、「新需求應該歸屬於哪個既有 Feature，還是需要新增？」

### 1.2 關鍵特性

- **價值導向 (Value Oriented)**：以「交付的價值」而非「技術實作」來組織 Feature 清單。
- **決策支援 (Decision Support)**：提供明確的決策指引，協助 SA 快速判斷「新增 vs 修改」，並（於業務系統中）引導正確的架構交付模式。

### 1.3 與其他層級的關係

| 層級 | 文件類型 | 核心問題 | 本層級的角色 |
|:-----|:---------|:---------|:-------------|
| **L1** | Architecture Overview | 「新需求屬於哪個 Domain/Toolkit？」 | 被 L1 引導而來 |
| **L2** | **Feature Overview (本文件)** | **「這個需求以前做過嗎？該新增還是修改？屬於什麼類型的交付？」** | **價值清單與決策支援** |
| **L3** | FU Overview (Specs) | 「有哪些現成的 FU 可以使用？」 | (由 L1 導航至 L3) |

### 1.4 收錄範圍原則 (Scope Boundary)

當一個 Domain/Toolkit 已發展出 Sub-domain/Sub-toolkit 結構時，父層級與子層級的 overview.md 各自負責不同範圍的 Feature：

| 層級 | 收錄範圍 | 典型特徵 |
|:-----|:---------|:---------|
| **父層級** (Domain/Toolkit) | 僅收錄**歸屬於自身**的 Feature：橫跨多個子層級的聚合型或共用型 Feature | e.g., `market-dashboard` 聚合了 `stock` 與 `fund` 的資料 |
| **子層級** (Sub-domain/Sub-toolkit) | 收錄歸屬於該子層級的所有 Feature | e.g., `stock-price-query` 僅涉及 `stock` 範疇 |

**關鍵規則**：

- **嚴禁上收**：子層級專屬的 Feature 不得登錄在父層級的 overview 中。
- **子層級導覽不由本層負責**：父層級的 overview 不需要列出其下的 Sub-domain/Sub-toolkit 清單，該職責由 **L1 Architecture Overview** 承擔。
- **觸發條件**：此規則僅在 Domain/Toolkit 確實存在子層級時適用。若無子層級，所有 Feature 自然歸屬於該層級本身。

---

## 2. 檔案路徑標準

路徑結構由 Feature 的歸屬類型決定：

### 2.1 業務系統 / 資料源系統

```text
docs/use-cases/<system>/
├── overview.md                        # (單一領域系統) 系統級 Feature 總覽
├── <domain>/
│   ├── overview.md                    # Domain 層級 Feature 總覽
│   └── <subdomain>/
│       └── overview.md                # Sub-domain 層級 Feature 總覽
└── etl/                               # (僅業務系統) ETL Feature — 獨立導航體系
    ├── overview.md                    # (單一領域系統) 系統級 ETL Feature 總覽
    └── <domain>/
        ├── overview.md                # ETL Domain 層級 Feature 總覽
        └── [<subdomain>]/
            └── overview.md            # ETL Sub-domain 層級 Feature 總覽
```

> **ETL Feature 的導航分離**
>
> Data Pipeline Feature (ETL) 擁有獨立的 `docs/use-cases/<system>/etl/` 導航體系，由其專屬的 overview.md 負責。業務系統的 Domain/Sub-domain 層級 overview.md **不包含** ETL Feature。
>
> 若需查閱 ETL 相關 Feature，請前往 `docs/use-cases/<system>/etl/<domain>/overview.md`。

### 2.2 專案級函式庫

```text
docs/use-cases/<library>/
└── <toolkit>/
    └── overview.md                    # Toolkit 層級 Feature 總覽
```

### 2.3 系統核心庫

```text
docs/use-cases/<system>/core/
└── <toolkit>/
    └── overview.md                    # System Core Toolkit 層級 Feature 總覽
```

---

## 3. 命名規範 (Naming Conventions)

### 3.1 Feature 命名

| 屬性 | 格式規範 | 說明 | 範例 |
|:-----|:---------|:-----|:-----|
| **Feature Name** | `kebab-case` | 全小寫，使用連字號分隔。<br>必須描述「對外交付的完整能力」。 | ✅ `user-registration`, `stock-price-sync`<br>❌ `user_registration` (應為 kebab-case)<br>❌ `add-user-table` (過於技術導向) |

### 3.2 命名導向原則

> *Ref: `docs/PROJECT_DESIGN-METHODOLOGY.md` Section 2*

- **聚合能力命名**：Feature 名稱必須描述其**「對外交付的完整能力」**，而非僅描述內部單一 FU 的實作。
- ❌ **Bad (Too Narrow)**: `excel-reader` (若該 Feature 同時包含 Writer)
- ❌ **Bad (Too Broad)**: `file-helper` (若該 Feature 僅處理 Excel)
- ✅ **Good (Precise)**: `excel-processing` (精確涵蓋完整能力)

---

## 4. 內容結構模板

> **閱讀指引**：本章節定義 overview.md 的三大區塊。其中 Section 4.2 (Feature Catalog) 與 Section 4.3 (Decision Guide) 依系統類型有不同的內容要求，請務必參照對應的類型專屬規範。

````markdown
# Feature Overview: <root>/<scope_path>

> **📝 撰寫指引**（請勿保留本指引文字）：
> - 標題格式為 `Feature Overview: <root>/<scope_path>`，對應該 overview.md 在 `docs/use-cases/` 下的相對路徑。
>   - 業務/資料源系統：`<system>` (單一領域系統)、`<system>/<domain>` 或 `<system>/<domain>/<subdomain>` (e.g., `crm`, `gms/market`, `gms/market/stock`)
>   - 專案級函式庫：`<library>/<toolkit_path>` (e.g., `wutils/io`, `wutils/concurrent/wthread`)
>   - 系統核心庫：`<system>/core/<toolkit_path>` (e.g., `gms/core/config`)
> - 本文件將被用作 Prompt Input 餵給 LLM 進行分析。請確保內容精簡、無歧義。

## 1. Context (上下文)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節說明當前 Overview 的位置與適用範圍，協助使用者確認是否來對地方。
>
> **💡 範例 (業務系統 Domain)**：
>
> - **System**: `gms` (Business System)
> - **Scope Type**: `Domain`
> - **Scope Name**: `market`
> - **Description**: 涵蓋所有金融市場相關的數據查詢與分析功能。
>
> *→ 標題：`# Feature Overview: gms/market`*
>
> **💡 範例 (業務系統 Sub-domain)**：
>
> - **System**: `gms` (Business System)
> - **Scope Type**: `Sub-domain`
> - **Scope Name**: `market/stock`
> - **Description**: 處理股票類資產的查詢與分析功能。
>
> *→ 標題：`# Feature Overview: gms/market/stock`*
>
> **💡 範例 (函式庫 Toolkit)**：
>
> - **Library**: `wutils`
> - **Scope Type**: `Toolkit`
> - **Scope Name**: `io`
> - **Description**: 提供統一的 I/O 操作介面，封裝檔案與網路存取的複雜度。
>
> *→ 標題：`# Feature Overview: wutils/io`*

>
> **💡 範例 (系統核心庫 Toolkit)**：
>
> - **Library**: `gms/core` (System-Level Library)
> - **Scope Type**: `Toolkit`
> - **Scope Name**: `config`
> - **Description**: 提供 GMS 系統內部共用的配置管理能力。
>
> *→ 標題：`# Feature Overview: gms/core/config`*
>
> **⚠️ 欄位選擇規則**：第一個欄位依所屬類型而定：
> - 業務/資料源系統的 Domain/Sub-domain → 使用 `**System**`
> - 專案級函式庫 (Project-Level Library) → 使用 `**Library**`
> - 系統核心庫 (System-Level Library) → 使用 `**Library**`（值為 `<system>/core`）

- **System** / **Library**: `<name>` (<type>)
- **Scope Type**: `<System | Domain | Sub-domain | Toolkit>`
- **Scope Name**: `<name or path>`
- **Description**: <簡述此範圍的核心職責>

## 2. Feature Catalog (功能清單)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節列出此範圍下所有已交付或開發中的 Feature。每個 Feature 以 `###` 標題呈現。
> 請依據當前 Overview 所屬的系統類型，選擇對應的格式：
>
> - **業務系統 (Business System)**：使用**含 Feature Type 欄位**的格式 → 參見下方「業務系統專用格式」
> - **其他類型 (Library / Data Source / System Core)**：使用**標準格式** → 參見下方「通用格式」
>
> **⚠️ 收錄範圍提醒**：
> 若本 Overview 所屬的 Domain/Toolkit 已存在 Sub-domain/Sub-toolkit，本清單**僅收錄歸屬於本層級自身**的聚合型或共用型 Feature。屬於特定 Sub-domain/Sub-toolkit 的 Feature 應登錄在對應的子層級 overview.md 中，請勿列入本文件。
>
> **通用欄位**：
> - **Value / Goal**: 一句話描述此 Feature 交付的核心價值。
> - **Owned FUs**: 基於「FU 單一驅動原則」，列出由該 Feature 唯一驅動與擁有的所有功能單元 (FU)。
>   - **業務系統/資料源系統 [CRITICAL]**：因 FU 分散於不同模組層 (Layer)，**必須加上層級前綴**，格式為 `<layer>:<fu_name>`（例如：`db:stock-price, service:stock-query`）。
>   - **函式庫 (Library/System Core)**：因無分層結構，直接填寫 `<fu_name>` 即可（例如：`pickle-io`）。
> - **Status**: Feature 的當前狀態（`Released` / `In Progress` / `Planned` / `Deprecated`）。
>
> **Layer 專屬欄位**：
> - **業務系統**需額外標註 **Feature Type**（`DB-only` / `Internal Service` / `Standard`）。

### 業務系統專用格式

> **📝 撰寫指引**（請勿保留本指引文字）：
> 業務系統的 Domain/Sub-domain 下會同時存在三種 Feature 類型，必須透過 `Feature Type` 欄位明確區分。
>
> **Feature Type 定義**：
>
> | 類型 | 說明 | Ref |
> |:-----|:-----|:----|
> | `Standard` | 標準的端到端業務功能（通常包含 API + Service，依賴 DB-only Feature） | Methodology §3.2 Business Feature |
> | `DB-only` | 技術型特例：僅定義底層資料模型與儲存介面，作為穩定的資料契約 | Methodology §3.2 DB-only Feature |
> | `Internal Service` | 技術型特例：純後端運算邏輯封裝，不對外暴露 API，供其他 Feature 共用 | Methodology §3.2 Internal Service Feature |
>
> **排列順序建議**：依 Feature Type 分組排列（DB-only → Internal Service → Standard），同類型內依字母或業務相關性排列，以提升掃描效率。
>
> **💡 範例**：
>
> ### `stock-price-storage`
> - **Feature Type**: `DB-only`
> - **Value / Goal**: 提供股票價格的底層儲存模型與存取介面 (資料契約)
> - **Owned FUs**: `db:stock-price`
> - **Status**: Released
>
> ### `stock-info-storage`
> - **Feature Type**: `DB-only`
> - **Value / Goal**: 提供股票基本資料的儲存模型與存取介面 (資料契約)
> - **Owned FUs**: `db:stock-info`
> - **Status**: Released
>
> ### `stock-valuation-calc`
> - **Feature Type**: `Internal Service`
> - **Value / Goal**: 封裝股票估值演算法，供多個查詢 API 共用
> - **Owned FUs**: `service:valuation-core`
> - **Status**: In Progress
>
> ### `stock-price-query`
> - **Feature Type**: `Standard`
> - **Value / Goal**: 提供前端查詢股票價格的 REST API
> - **Owned FUs**: `service:stock-query, api:stock-price`
> - **Status**: Released
>
> ### `stock-profile`
> - **Feature Type**: `Standard`
> - **Value / Goal**: 提供股票基本資料與即時報價查詢 API
> - **Owned FUs**: `service:stock-profile, api:stock-profile`
> - **Status**: Released

### `<feature_name>`
- **Feature Type**: `<DB-only / Internal Service / Standard>`
- **Value / Goal**: <交付的核心價值>
- **Owned FUs**: `<layer>:<fu_name>`
- **Status**: `<status>`

### 通用格式 (Library / Data Source / System Core)

> **📝 撰寫指引**（請勿保留本指引文字）：
> Library、Data Source 與 System Core 的 Feature 不存在 DB-only / Internal Service 的分類需求，
> 因此使用不含 Feature Type 的精簡格式。
>
> **💡 範例 (函式庫)**：
>
> ### `csv-processing`
> - **Value / Goal**: 提供 CSV 格式的讀寫與 Schema 驗證能力
> - **Owned FUs**: `csv-io, csv-validator`
> - **Status**: Released
>
> ### `parquet-processing`
> - **Value / Goal**: 提供 Parquet 格式的讀寫與 Schema 管理能力
> - **Owned FUs**: `parquet-io`
> - **Status**: Released
>
> **💡 範例 (資料源系統)**：
>
> ### `daily-price`
> - **Value / Goal**: 提供每日收盤價的爬取與標準化存取介面
> - **Owned FUs**: `collector:daily-price, service:daily-price`
> - **Status**: Released
>
> ### `company-profile`
> - **Value / Goal**: 提供上市公司基本資料的爬取與查詢介面
> - **Owned FUs**: `collector:company-profile, service:company-profile`
> - **Status**: In Progress

### `<feature_name>`
- **Value / Goal**: <交付的核心價值>
- **Owned FUs**: `<layer>:<fu_name>` 或 `<fu_name>`
- **Status**: `<status>`

## 3. Decision Guide (決策指引)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節提供具體的決策指引，協助 SA 快速判斷新需求應「修改既有 Feature」還是「新增 Feature」。
> 請依據當前 Overview 所屬的系統類型，遵循對應的撰寫要求：
>
> - **業務系統 (Business System)**：**必須**包含雙軌交付引導與 Feature Type 指定 → 參見下方「業務系統專屬要求」
> - **其他類型 (Library / Data Source / System Core)**：使用通用決策指引格式即可

### 通用撰寫原則

> **📝 撰寫指引**（請勿保留本指引文字）：
> 無論系統類型，所有 Decision Guide 都必須遵循以下原則：
> 1. **情境導向**：以「若您要...」開頭，描述常見的需求情境。
> 2. **明確指向**：給出具體的建議行動（修改哪個 Feature / 新增 Feature）。
> 3. **覆蓋邊界案例**：特別說明容易混淆的情境。

### 業務系統專屬要求

> **📝 撰寫指引**（請勿保留本指引文字）：
> 業務系統的 Decision Guide **必須**額外滿足以下要求：
>
> 1. **雙軌交付引導**：在「需要新增 Feature」的情境中，必須明確區分應新增 **DB-only**、**Internal Service** 還是 **Standard** Feature，引導 SA 遵循「先資料契約，後業務功能」的雙軌交付策略。
> 2. **Feature Type 指定**：每條新增建議必須標註建議的 Feature Type。
> 3. **跨類型混淆澄清**：在「常見混淆情境」中，必須涵蓋 DB-only 與 Standard 之間的職責邊界。
>
> *Ref: `docs/PROJECT_DESIGN-METHODOLOGY.md` Section 3.2 — 雙軌交付 (Dual Track Delivery)*
>
> **💡 範例 (業務系統)**：
>
> #### 3.1 修改既有 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 擴充股票價格的查詢欄位或修改 API 回應格式 | 修改 `stock-price-query` (Standard) |
> | 調整股票估值的核心公式 | 修改 `stock-valuation-calc` (Internal Service) |
> | 為股票價格新增 FileSystem 儲存支援 | 修改 `stock-price-storage` (DB-only) |
>
> #### 3.2 需要新增 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 建立 ETF 的資料模型與存取邏輯 | 新增 **DB-only** Feature (`etf-storage`)，定義底層資料契約 |
> | 開發對外的 ETF 查詢 API | 新增 **Standard** Feature (`etf-query`)，依賴 `etf-storage` |
> | 封裝金融風險計算公式，供多個 API 共用 | 新增 **Internal Service** Feature (`risk-calculator`) |
>
> #### 3.3 常見混淆情境
>
> | 情境 | 正確歸屬 | 原因 |
> |:-----|:---------|:-----|
> | 「要在查詢 API 中新增一種儲存格式」 | `stock-price-storage` (DB-only) | 儲存模型屬於底層契約，應在 DB-only Feature 中修改，Standard Feature 嚴禁直接變更資料層實作 |
> | 「在自選清單 API 中加入即時股價計算」 | 視情況判斷 | 若為簡單欄位查詢：修改 Standard Feature；若為複雜運算且需被多處共用：應提取為 Internal Service Feature |

> **💡 範例 (函式庫 — 通用格式)**：
>
> #### 3.1 修改既有 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 新增 CSV 的欄位型別驗證規則 | 修改 `csv-processing` Feature |
> | 調整 Parquet Schema 的版本管理邏輯 | 修改 `parquet-processing` Feature |
>
> #### 3.2 需要新增 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 提供 Excel 格式的讀寫能力 | 新增 `excel-processing` Feature |
>
> #### 3.3 常見混淆情境
>
> | 情境 | 正確歸屬 | 原因 |
> |:-----|:---------|:-----|
> | 「在 CSV Reader 中支援 TSV 格式」 | `csv-processing` | TSV 是 CSV 的分隔符變體，屬於同一 Feature 的能力擴充 |

### 3.1 修改既有 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 修改 `<feature_name>` Feature |

### 3.2 需要新增 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 新增 `<suggested_feature_name>` Feature <(業務系統) 請標註 Feature Type> |

### 3.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| <混淆情境> | `<correct_feature>` | <判斷理由> |


````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 結構完整性

- [ ] **上下文**：Section 1 是否已明確定義 System/Library, Scope Type, Scope Name, Description？
- [ ] **功能清單**：Section 2 是否已列出所有已知的 Feature？每個 Feature 是否都有 Value/Goal 與 Owned FUs 說明？
- [ ] **Owned FUs 雙向一致性**：每個 Feature 的 `Owned FUs` 欄位所列出的 FU，其對應的 `specs/.../requirements.md` Metadata 中的 `Parent Feature` 是否反向指回同一個 Feature？
- [ ] **收錄範圍**：(若存在子層級) Section 2 是否僅收錄歸屬於本層級的 Feature，未混入子層級專屬的 Feature？

### B. Feature Type 正確性 (僅業務系統)

- [ ] **欄位存在**：每個 Feature 條目是否都標註了 `Feature Type` 欄位？
- [ ] **類型正確**：所有 Feature 是否都正確標示為 `Standard`、`DB-only` 或 `Internal Service`？
- [ ] **分組排列**：Feature 是否盡量依 Feature Type 分組排列 (DB-only → Internal Service → Standard)？

### C. 決策指引品質

- [ ] **情境覆蓋**：Section 3 是否覆蓋了「修改」與「新增」兩種情境？
- [ ] **混淆情境**：是否已識別並說明容易混淆的邊界案例？
- [ ] **指向明確**：每個決策建議是否都指向具體的 Feature 名稱？
- [ ] **雙軌交付引導**：(針對業務系統) 新增情境是否明確區分 DB-only / Internal Service / Standard 的建立時機？
- [ ] **跨類型混淆**：(針對業務系統) 混淆情境是否涵蓋 DB-only 與 Standard 之間的職責邊界？

### D. 導航一致性

- [ ] **與 L1 一致**：本 Overview 的 Scope 是否與 Architecture Overview 中的定義一致？

### E. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的資訊？
- [ ] **Feature 命名**：所有 Feature 名稱是否都使用 `kebab-case`？
