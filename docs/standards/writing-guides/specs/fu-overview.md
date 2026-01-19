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

> **⚠️ 關鍵理解**：本文件盤點的是 **FU (功能單元)**，而非 FU 內部的 Component。
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

### 1.4 與其他層級的關係

| 層級 | 文件類型 | 核心問題 | 本層級的角色 |
|:-----|:---------|:---------|:-------------|
| **L1** | Architecture Overview | 「新需求屬於哪個 Domain/Toolkit？」 | - |
| **L2** | Feature Overview | 「這個需求以前做過嗎？」 | 被 L2 引導而來 |
| **L3** | **FU Overview (本文件)** | **「有哪些現成的 FU 可以使用？」** | **技術資產庫存** |

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
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
├── service/                           # Service Layer
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
├── api/                               # API Layer
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
└── etl/                               # ETL Layer
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
│   └── <domain>/
│       ├── overview.md                # Domain 層級 FU 總覽
│       └── <subdomain>/
│           └── overview.md            # Sub-domain 層級 FU 總覽
└── service/                           # Service Layer
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
# FU Overview: <Layer> / <Scope>

> **📝 撰寫指引**（請勿保留本指引文字）：
> - `<Layer>`: 模組層級名稱 (e.g., `DB`, `Service`, `API`, `ETL`, `Collector`, `Toolkit`)
> - `<Scope>`: Domain / Sub-domain / Toolkit 名稱
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
> **💡 範例 (函式庫 Toolkit)**：
>
> - **Library**: `wutils`
> - **Layer**: `Toolkit`
> - **Scope**: `io`
> - **FU-Container Path**: `wutils/io`

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
> - 此處列出的是 **FU (功能單元)**，不是 Component (類別/函式)
> - 一個 FU 可能包含多個 Components，但在 Overview 層級我們只關心 FU
> - FU 的詳細 Components 請參閱各 FU 的 `design.md`
>
> **欄位說明**：
> - **FU Name**: 功能單元名稱 (`kebab-case`)。
> - **Responsibility**: 一句話描述 FU 的核心職責。
> - **Key Components**: 列出主要的公開 Components (供快速參考)。
> - **Spec Link**: 連結至該 FU 的詳細規格文件目錄。
>
> **⚠️ Layer 特定補充資訊**：
> 根據不同 Layer，可在 Responsibility 中補充關鍵屬性：
> - **DB Layer**: 儲存類型 (SQL/NoSQL/FS/Hybrid)
> - **API Layer**: 主要 Endpoint Pattern
> - **ETL Layer**: 資料流向 (Source → Target)
> - **Collector Layer**: 資料來源類型
>
> **💡 範例 (DB Layer)**：
>
> | FU Name | Responsibility | Key Components | Spec |
> |:--------|:---------------|:---------------|:-----|
> | `stock-price` | 管理股票每日價格的存取 (Hybrid: SQL + FS) | `StockPriceRepository`, `StockPriceSchema` | [→](./stock-price/) |
> | `stock-info` | 管理股票基本資料的查詢 (SQL) | `StockInfoRepository`, `StockInfoSchema` | [→](./stock-info/) |
>
> **💡 範例 (Service Layer)**：
>
> | FU Name | Responsibility | Key Components | Spec |
> |:--------|:---------------|:---------------|:-----|
> | `stock-query` | 提供股票資料的查詢與聚合服務 | `StockQueryService`, `StockQueryInput` | [→](./stock-query/) |
> | `stock-analysis` | 提供股票技術分析計算服務 | `StockAnalysisService`, `AnalysisResult` | [→](./stock-analysis/) |
>
> **💡 範例 (API Layer)**：
>
> | FU Name | Responsibility | Key Components | Spec |
> |:--------|:---------------|:---------------|:-----|
> | `stock-endpoint` | 提供股票相關 REST API (`/stocks/*`) | `get_stock`, `list_stocks`, `StockResponse` | [→](./stock-endpoint/) |
>
> **💡 範例 (ETL Layer)**：
>
> | FU Name | Responsibility | Key Components | Spec |
> |:--------|:---------------|:---------------|:-----|
> | `daily-price-sync` | 每日股價同步 (twseprice → gms.db) | `DailyPriceExtractor`, `DailyPriceLoader`, `DailySyncJob` | [→](./daily-price-sync/) |
>
> **💡 範例 (Library Toolkit)**：
>
> | FU Name | Responsibility | Key Components | Spec |
> |:--------|:---------------|:---------------|:-----|
> | `pickle-io` | 提供 Pickle 格式的序列化能力 | `pickle_dump`, `pickle_load` | [→](./pickle-io/) |
> | `json-io` | 提供 JSON 格式的序列化能力 | `json_dump`, `json_load` | [→](./json-io/) |
> | `csv-processing` | 提供 CSV 格式的讀寫與驗證能力 | `CsvReader`, `CsvWriter`, `CsvSchema` | [→](./csv-processing/) |

| FU Name | Responsibility | Key Components | Spec |
|:--------|:---------------|:---------------|:-----|
| `<fu-name>` | <職責描述> | `<Component1>`, `<Component2>` | [→](<relative_path>) |
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
- [ ] **FU 清單**：Section 3 是否已列出所有已知的 FU？每個 FU 是否都有 Responsibility 與 Key Components？

### C. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的資訊？
- [ ] **FU 命名**：所有 FU Name 是否都使用 `kebab-case`？
- [ ] **Spec Link 正確**：所有 Spec Link 路徑是否正確可達？
