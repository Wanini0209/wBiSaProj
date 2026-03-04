# FU Overview (Specs) - Documentation Guide

本規範定義 **FU Overview (功能單元總覽)** 文件的撰寫規範。適用於所有 `docs/specs/.../overview.md` 路徑下的總覽文件。目標是提供**技術資產庫存 (FU Inventory)** 與 **可復用性指引**，作為開發者執行「資產盤點」與「技術決策」時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範為**通用規範**，適用於以下所有類型與層級：
> - **業務系統 (Business System)**：`core`, `db`, `service`, `api`, `etl` 各層
> - **資料源系統 (Data Source System)**：`core`, `collector`, `service` 各層
> - **專案級函式庫 (Library)**：Toolkit 層級
> - **系統核心庫 (System Core)**：Toolkit 層級

*供 Generator: Prompt4FUOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是特定模組層級 (Module Layer) 或工具集 (Toolkit) 的「技術資產庫」。它不描述具體的實作邏輯，而是回答：「這裡有哪些現成的功能單元 (FU) 可以讓我使用？」

### 1.2 關鍵特性

- **資產導向 (Asset Oriented)**：以「可復用的功能單元」為核心組織 FU 清單。
- **路徑明確 (Path Explicit)**：每個 FU 必須標註其所屬的 FU-Container。
- **職責清晰 (Responsibility Clear)**：每個 FU 必須有一句話的職責描述。

### 1.3 核心概念釐清：FU vs Component

> **⚠️ 關鍵理解**：本文件的盤點粒度是 **FU (功能單元)**，但每個 FU 必須**完整列出**其所有公開 Components。
>
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 4 & 5.3*

| 概念 | 定義 | 命名格式 | 範例 |
|:-----|:-----|:---------|:-----|
| **FU Container** | 承載 FU 的目錄，定義功能的可見性邊界 | `snake_case` path | `wutils/io`, `gms/db/market/stock` |
| **FU (Functional Unit)** | 最小的邏輯完整性單位，由規格、實作、測試三部分構成 | `kebab-case` | `pickle-io`, `stock-price`, `user-profile` |
| **Component** | FU 內部的具體程式元素 (class/function/constant) | PascalCase (類別)<br>snake_case (函式) | `StockPriceRepository`, `pickle_dump()` |

**概念關係圖**：

```text
FU Container: wutils/io
├── FU: pickle-io
│   ├── Component: pickle_dump()
│   └── Component: pickle_load()
└── FU: json-io
    ├── Component: json_dump()
    └── Component: json_load()

FU Container: gms/db/market/stock
└── FU: stock-price
    ├── Component: StockPriceRepository (class)
    ├── Component: StockPriceSchema (class)
    └── Component: PRICE_TABLE_NAME (constant)
```

> **使用方式**：開發者透過 `from <fu_container_path> import <Component>` 使用 FU 的公開元件。
> 詳見 `PROJECT_DESIGN-ARCHITECTURE.md` Section 5.5。

#### Components 完整性契約

本文件中每個 FU 所列出的 **Components 清單**，必須與該 FU Container 的 `__init__.py` 中 `__all__` 所匯出的公開元件**完全一致**。這是一份**完整清單 (Exhaustive List)**，而非摘要。

| 規範 | 說明 |
|:-----|:-----|
| **完整性** | 必須列出 `__all__` 中的每一個公開元件，不得省略 |
| **同步性** | 新增或移除 Component 時，必須同步更新本 Overview 文件 |
| **用途** | 此清單作為自動化工具判定「Component → FU 歸屬」的 **Ground Truth** |

### 1.4 與其他層級的關係

| 層級 | 文件類型 | 核心問題 | 本層級的角色 |
|:-----|:---------|:---------|:-------------|
| **L1** | Architecture Overview | 「新需求屬於哪個 Domain/Toolkit？」 | - |
| **L2** | Feature Overview | 「這個需求以前做過嗎？」 | 被 L2 引導而來 |
| **L3** | **FU Overview (本文件)** | **「有哪些現成的 FU 可以使用？」** | **技術資產庫存** |

### 1.5 收錄範圍原則 (Scope Boundary)

當一個 Domain/Toolkit 已發展出 Sub-domain/Sub-toolkit 結構時，父層級與子層級的 overview.md 各自負責不同範圍的 FU：

| 層級 | 收錄範圍 | 典型特徵 |
|:-----|:---------|:---------|
| **父層級** (Domain/Toolkit) | 僅收錄**歸屬於本層級自身**的 FU：橫跨多個子層級的聚合型或共用型 FU | e.g., `market-dashboard-service` 聚合了 `stock` 與 `fund` 的查詢邏輯 |
| **子層級** (Sub-domain/Sub-toolkit) | 收錄歸屬於該子層級的所有 FU | e.g., `stock-price` 僅涉及 `stock` 範疇 |

**關鍵規則**：

- **嚴禁上收**：子層級專屬的 FU 不得登錄在父層級的 overview 中。
- **子層級導覽不由本層負責**：父層級的 overview 不需要列出其下的 Sub-domain/Sub-toolkit 清單，該職責由 **L1 Architecture Overview** 承擔。
- **觸發條件**：此規則僅在 Domain/Toolkit 確實存在子層級時適用。若無子層級，所有 FU 自然歸屬於該層級本身。

---

## 2. 檔案路徑標準

路徑結構由系統類型與模組層級決定：

### 2.1 業務系統

```text
docs/specs/<system>/
├── core/                              # System Core
│   └── <toolkit>/
│       ├── overview.md
│       └── <subtoolkit>/
│           └── overview.md
├── db/                                # DB Layer
│   ├── overview.md                    # (單一領域系統) DB 層級 FU 總覽
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
├── service/                           # Service Layer
│   ├── overview.md                    # (單一領域系統) Service 層級 FU 總覽
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
├── api/                               # API Layer
│   ├── overview.md                    # (單一領域系統) API 層級 FU 總覽
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
└── etl/                               # ETL Layer
    ├── overview.md                    # (單一領域系統) ETL 層級 FU 總覽
    └── <domain>/
        ├── overview.md                # Domain 層級 FU 總覽
        └── <subdomain>/
            └── overview.md            # Sub-domain 層級 FU 總覽
```

### 2.2 資料源系統

```text
docs/specs/<system>/
├── core/                              # System Core
│   └── <toolkit>/
│       ├── overview.md
│       └── <subtoolkit>/
│           └── overview.md
├── collector/                         # Collector Layer
│   ├── overview.md                    # (單一領域系統) Collector 層級 FU 總覽
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
└── service/                           # Service Layer
    ├── overview.md                    # (單一領域系統) Service 層級 FU 總覽
    └── <domain>/
        ├── overview.md                # Domain 層級 FU 總覽
        └── <subdomain>/
            └── overview.md            # Sub-domain 層級 FU 總覽
```

### 2.3 專案級函式庫

```text
docs/specs/<library>/
└── <toolkit>/
    ├── overview.md
    └── <subtoolkit>/
        └── overview.md
```

---

## 3. 命名規範 (Naming Conventions)

### 3.1 FU 命名

| 屬性 | 格式規範 | 說明 | 範例 |
|:-----|:---------|:-----|:-----|
| **FU Name** | `kebab-case` | 功能單元的邏輯名稱（目錄友善格式）。<br>必須反映其功能職責。 | `pickle-io`, `stock-price`, `daily-sync` |
| **FU-Container** | `snake_case` path | FU 所在的 Python Package 路徑。 | `wutils/io`, `gms/db/market/stock` |

> **⚠️ 注意**：FU Name 使用 `kebab-case` 是因為它是「邏輯概念名稱」，會對應到 `docs/specs/<fu_path>/<fu_name>/` 的目錄結構，而非直接作為 Python identifier。

### 3.2 公開 Components 命名

FU 對外暴露的 Components（透過 `__init__.py` 匯出）應遵循 Python 命名慣例：

| Component 類型 | 格式規範 | 範例 |
|:---------------|:---------|:-----|
| Class | `PascalCase` | `StockPriceRepository`, `CsvReader` |
| Function | `snake_case` | `pickle_dump`, `get_stock_price` |
| Constant | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT`, `PRICE_TABLE_NAME` |

---

## 4. 內容結構模板

````markdown
# FU Overview: <root>/<layer>/<scope_path>

> **📝 撰寫指引**（請勿保留本指引文字）：
> - 標題格式為 `FU Overview: <root>/<layer>/<scope_path>`，對應該 overview.md 在 `docs/specs/` 下的相對路徑。
>   - 業務系統：`<system>/<layer>` (單一領域系統)、`<system>/<layer>/<domain>[/<subdomain>]` (e.g., `crm/db`, `gms/db/market/stock`, `gms/service/market`)
>   - 資料源系統：`<system>/<layer>` (單一領域系統)、`<system>/<layer>/<domain>[/<subdomain>]` (e.g., `twseprice/collector/price`)
>   - 專案級函式庫：`<library>/<toolkit_path>` (e.g., `wutils/io`, `wutils/concurrent/wthread`)
>   - 系統核心庫：`<system>/core/<toolkit_path>` (e.g., `gms/core/config`)
> - 函式庫與系統核心庫因路徑中不含獨立的 layer 層級，標題自然省略 `<layer>` 段。
> - 本文件將被用作 Prompt Input 餵給 LLM 進行分析。請確保內容精簡、無歧義。

## 1. Context (上下文)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節說明當前 Overview 的位置與適用範圍。
>
> **💡 範例 (業務系統 DB Layer)**：
>
> - **System**: `gms` (Business System)
> - **Layer**: `DB`
> - **Scope**: `market/stock` (Sub-domain)
> - **FU-Container Path**: `gms/db/market/stock`
>
> *→ 標題：`# FU Overview: gms/db/market/stock`*
>
> **💡 範例 (函式庫 Toolkit)**：
>
> - **Library**: `wutils`
> - **Layer**: `Toolkit`
> - **Scope**: `io`
> - **FU-Container Path**: `wutils/io`
>
> *→ 標題：`# FU Overview: wutils/io`*

- **System / Library**: `<name>` (<type>)
- **Layer**: `<layer_name>`
- **Scope**: `<domain_path or toolkit_path>`
- **FU-Container Path**: `<fu_path>`

## 2. Layer Constraints (層級限制)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節說明此層級的架構限制。不同層級有不同的依賴規則。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 6.3*
>
> **💡 業務系統各層限制範例**：
>
> | Layer | 可依賴 | 禁止依賴 |
> |:------|:-------|:---------|
> | `db` | `<system>/core`, `core`, `wutils` | `service`, `api`, `etl`, 外部 API |
> | `service` | `db`, `<system>/core`, `core`, `wutils` | `api`, `etl`, 外部 API |
> | `api` | `service`, `<system>/core`, `core`, `wutils` | `db` (直接), `etl` |
> | `etl` | `db`, `<system>/core`, `core`, `wutils`, `core/interfaces` | `service`, `api` |
>
> **💡 資料源系統各層限制範例**：
>
> | Layer | 可依賴 | 禁止依賴 |
> |:------|:-------|:---------|
> | `collector` | `<system>/core`, `core`, `wutils` | `service`, 其他系統 |
> | `service` | `collector`, `<system>/core`, `core`, `wutils` | 其他系統 (須透過 interface) |

- **Allowed Dependencies**: <列出可依賴的層級/套件>
- **Prohibited Dependencies**: <列出禁止依賴的層級/套件>
- **Special Rules** (若有): <列出特殊規則>

## 3. FU Inventory (功能單元清單)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節列出此 FU-Container 下所有的 Functional Units。
>
> **⚠️ 重要概念提醒**：
> - 此處的組織粒度是 **FU (功能單元)**，每個 FU 以 `###` 標題呈現
> - 每個 FU 必須**完整列出**其所有公開 Components（對應 `__init__.py` 的 `__all__`）
> - Components 以子列表形式逐一列出，作為自動化工具判定歸屬的 Ground Truth
>
> **⚠️ 收錄範圍提醒**：
> 若本 Overview 所屬的 Domain/Toolkit 已存在 Sub-domain/Sub-toolkit，本清單**僅收錄歸屬於本層級自身**的聚合型或共用型 FU。屬於特定 Sub-domain/Sub-toolkit 的 FU 應登錄在對應的子層級 overview.md 中，請勿列入本文件。
>
> **通用欄位**：
> - **Responsibility**: 一句話描述 FU 的核心職責。
> - **Components**: 完整列出該 FU 的所有公開 Components（對應 `__init__.py` 的 `__all__`）。
> - **Spec**: 連結至該 FU 的詳細規格文件目錄。
>
> **Layer 專屬欄位**：
> 不同 Layer 的 overview.md 需額外標註以下欄位（置於 Responsibility 之後、Components 之前）：
>
> | Layer | 專屬欄位 | 說明 |
> |:------|:---------|:-----|
> | **DB** | `Storage` | 儲存類型 (SQL / NoSQL / FS / Hybrid) |
> | **API** | `Endpoints` | 主要 Endpoint Pattern |
> | **ETL** | `Data Flow` | 資料流向 (Source → Target) |
> | **Collector** | `Source Type` | 資料來源類型 |
> | **Service** | （無額外欄位） | — |
> | **Library / System Core** | （無額外欄位） | — |
>
> **💡 範例 (DB Layer)**：
>
> ### `stock-price`
> - **Responsibility**: 管理股票每日價格的存取
> - **Storage**: Hybrid (SQL + FS)
> - **Components**:
>   - `StockPriceRepository`
>   - `StockPriceSchema`
>   - `StockPriceInput`
>   - `PRICE_TABLE_NAME`
> - **Spec**: [→](./stock-price/)
>
> ### `stock-info`
> - **Responsibility**: 管理股票基本資料的查詢
> - **Storage**: SQL
> - **Components**:
>   - `StockInfoRepository`
>   - `StockInfoSchema`
> - **Spec**: [→](./stock-info/)
>
> **💡 範例 (Service Layer)**：
>
> ### `stock-query`
> - **Responsibility**: 提供股票資料的查詢與聚合服務
> - **Components**:
>   - `StockQueryService`
>   - `StockQueryInput`
>   - `StockQueryResult`
> - **Spec**: [→](./stock-query/)
>
> **💡 範例 (API Layer)**：
>
> ### `stock-endpoint`
> - **Responsibility**: 提供股票相關 REST API
> - **Endpoints**: `/stocks/*`
> - **Components**:
>   - `get_stock`
>   - `list_stocks`
>   - `StockResponse`
>   - `StockListResponse`
> - **Spec**: [→](./stock-endpoint/)
>
> **💡 範例 (ETL Layer)**：
>
> ### `daily-price-sync`
> - **Responsibility**: 每日股價同步
> - **Data Flow**: twseprice → gms.db
> - **Components**:
>   - `DailyPriceExtractor`
>   - `DailyPriceLoader`
>   - `DailySyncJob`
> - **Spec**: [→](./daily-price-sync/)
>
> **💡 範例 (Collector Layer)**：
>
> ### `daily-price-crawler`
> - **Responsibility**: 收集每日股票收盤價
> - **Source Type**: Web Scraping (HTML)
> - **Components**:
>   - `DailyPriceCrawler`
>   - `DailyPriceRawSchema`
> - **Spec**: [→](./daily-price-crawler/)
>
> **💡 範例 (Library Toolkit)**：
>
> ### `pickle-io`
> - **Responsibility**: 提供 Pickle 格式的序列化能力
> - **Components**:
>   - `pickle_dump`
>   - `pickle_load`
>   - `PickleError`
>   - `DEFAULT_PICKLE_PROTOCOL`
> - **Spec**: [→](./pickle-io/)
>
> ### `json-io`
> - **Responsibility**: 提供 JSON 格式的序列化能力
> - **Components**:
>   - `json_dump`
>   - `json_load`
>   - `JsonParseError`
>   - `JsonConfig`
> - **Spec**: [→](./json-io/)

### `<fu-name>`
- **Responsibility**: <職責描述>
- **Components**:
  - `<Component1>`
  - `<Component2>`
- **Spec**: [→](<relative_path>)

## 4. Decision Guide (決策指引)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節提供具體的決策指引，協助開發者快速判斷新需求應「擴充既有 FU」還是「新增 FU」。
>
> **撰寫原則**：
> 1. **情境導向**：以「若您要...」開頭，描述常見的需求情境。
> 2. **明確指向**：給出具體的建議行動（擴充哪個 FU / 新增 FU）。
> 3. **覆蓋邊界案例**：特別說明容易混淆的情境。
>
> **💡 範例 (DB Layer)**：
>
> ### 4.1 擴充既有 FU 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 新增股票價格的查詢條件（如依日期範圍） | 擴充 `stock-price` FU |
> | 新增股票基本資料的欄位 | 擴充 `stock-info` FU |
>
> ### 4.2 需要新增 FU 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 提供股票技術指標的儲存與查詢 | 新增 `stock-indicator` FU |
> | 提供股票財報資料的存取 | 新增 `stock-financial` FU |
>
> ### 4.3 常見混淆情境
>
> | 情境 | 正確歸屬 | 原因 |
> |:-----|:---------|:-----|
> | 「在 stock-price 中加入技術指標計算」 | 新增獨立 FU | 技術指標是衍生計算，不應混入價格資料的 Repository |
> | 「新增另一種價格資料來源的支援」 | 擴充 `stock-price` | 這是同一 FU 的資料來源擴充，非新職責 |
>
> **💡 範例 (Library Toolkit)**：
>
> ### 4.1 擴充既有 FU 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 新增 CSV 讀取時的編碼支援 | 擴充 `csv-processing` FU |
> | 新增 JSON 的壓縮輸出選項 | 擴充 `json-io` FU |
>
> ### 4.2 需要新增 FU 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 提供 YAML 格式的讀寫能力 | 新增 `yaml-io` FU |
> | 提供 Excel 檔案的處理能力 | 新增 `excel-processing` FU |

### 4.1 擴充既有 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 擴充 `<fu_name>` FU |

### 4.2 需要新增 FU 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 新增 `<suggested_fu_name>` FU |

### 4.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| <混淆情境> | `<correct_fu>` | <判斷理由> |

````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 概念正確性

- [ ] **FU vs Component**：清單中列出的是否都是 FU（`kebab-case`），而非 Component（類別/函式）？
- [ ] **粒度正確**：每個 FU 是否代表一個「最小邏輯完整性單位」，而非單一函式或類別？

### B. 結構完整性

- [ ] **上下文**：Section 1 是否已明確定義 System/Library, Layer, Scope, FU-Container Path？
- [ ] **層級限制**：Section 2 是否已列出此層級的依賴規則 (Allowed/Prohibited)？
- [ ] **FU 清單**：Section 3 是否已列出所有已知的 FU？每個 FU 是否都有 Responsibility 與完整的 Components 清單？
- [ ] **收錄範圍**：(若存在子層級) Section 3 是否僅收錄歸屬於本層級的 FU，未混入子層級專屬的 FU？
- [ ] **Components 完整性**：每個 FU 的 Components 清單是否與其 `__init__.py` 的 `__all__` 完全一致？

### C. 決策指引品質

- [ ] **情境覆蓋**：Section 4 是否覆蓋了「擴充」與「新增」兩種情境？
- [ ] **混淆情境**：是否已識別並說明容易混淆的邊界案例？
- [ ] **指向明確**：每個決策建議是否都指向具體的 FU 名稱？

### D. 導航一致性

- [ ] **路徑正確**：所有相對路徑連結是否正確可達？
- [ ] **與 L1 一致**：本 Overview 的 Scope 是否與 Architecture Overview 中的定義一致？

### E. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的資訊？
- [ ] **FU 命名**：所有 FU Name 是否都使用 `kebab-case`？
- [ ] **Spec Link 正確**：所有 Spec Link 路徑是否正確可達？
