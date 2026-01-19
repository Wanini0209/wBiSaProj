# Data Source System Architecture Overview - Documentation Guide

本規範定義 **Data Source System (資料源系統)** 的 `SYSTEM_OVERVIEW.md` 撰寫規範。目標是定義系統的 **邊界 (Boundaries)**、**領域職責 (Domain Responsibilities)**、**核心基礎設施 (System Core)** 與 **架構限制 (Constraints)**，作為 System Analyst (LLM) 執行需求分析與架構設計時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範僅適用於 **Data Source System** (如 `twseprice`, `yfinance`)。業務系統請參閱 `sys-biz-overview.md`，專案級函式庫請參閱 `lib-overview.md`。

*供 Generator: Prompt4DataSourceSystemOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是資料源系統的「憲法」。它不描述具體功能的實作細節，而是定義「提供什麼資料」、「不提供什麼」、「各領域的職責劃分」以及「如何封裝外部資料源」。

### 1.2 關鍵特性

- **單一真理來源 (SSOT)**：所有 Feature 的領域歸屬 (Domain Ownership) 與資料範圍 (Data Scope) 均以此文件為最高指導原則。
- **邊界優先 (Boundary First)**：必須明確定義「非目標範圍 (Out of Scope)」與「排除規則 (Excludes)」，以防止架構腐化。
- **適配器導向 (Adapter Oriented)**：資料源系統的核心職責是封裝外部資料源，對內提供標準化、唯讀的數據服務。
- **基礎設施顯性化 (Explicit Infrastructure)**：明確定義 `<system>/core` 中的共享工具集，避免重複造輪子。

### 1.3 與業務系統的差異

| 面向 | Data Source System | Business System |
|:-----|:-------------------|:----------------|
| **核心職責** | 封裝外部資料源，提供唯讀數據 | 實現業務邏輯，提供讀寫服務 |
| **標準架構** | 兩層 (`collector`, `service`) | 五層 (`core`, `etl`, `db`, `service`, `api`) |
| **資料流向** | 外部 → 內部 (單向) | 雙向 (讀寫) |
| **介面實作** | 實作 `core/interfaces` 定義的抽象 | 消費 `core/interfaces` 定義的抽象 |

---

## 2. 檔案路徑標準

`docs/architecture/<system>_overview.md`

- `<system>`: 系統縮寫名稱 (e.g., `twseprice`, `yfinance`)。

---

## 3. 命名規範 (Naming Conventions)

> **⚠️ 重要**：請嚴格遵守以下命名規範，以確保 Python 套件結構的合法性與一致性。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 5.3 & 8.2*

### 3.1 系統與結構命名

| 屬性 | 格式規範 | 說明 | 範例 |
|:-----|:---------|:-----|:-----|
| **System Name** | `[a-z0-9]+` | **系統縮寫 ID**。全小寫，無任何分隔符號。保持頂層 Namespace 簡潔。 | `twseprice`, `yfinance` |
| **Domain Name** | `snake_case` | **全小寫，使用底線分隔，嚴禁連字號 (-)**。<br>必須是合法的 Python Package Name。<br>應使用資料類型名詞，反映資料源提供的資料類別。 | ✅ `daily_price`, `stock_info`<br>❌ `daily-price` (非法套件名)<br>❌ `price_collector` (技術命名) |
| **Sub-domain Name** | `snake_case` | 同 Domain Name 規範。 | `twse`, `otc` |
| **Toolkit Name** | `snake_case` | **技術分類名稱**。用於 System Core 中的工具集分類。<br>必須反映技術解決方案領域。 | `http_client`, `parser`, `cache`<br>❌ `common`, `utils` (禁止模糊命名) |

---

## 4. 內容結構模板

````markdown
# Data Source System Architecture Overview

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本文件將被用作 Prompt Input 餵給 LLM 進行分析。請確保內容精簡、無歧義，並專注於「定義規則」。

## 1. System Identity (系統識別)

### 1.1 基本資料 (Basic Info)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **System Name**: 系統縮寫 ID (對應目錄名稱)。
> - **System Full Name**: 系統全名 (對應專案立項名稱)。
> - **System Type**: 固定填寫 `Data Source System`。
> - **Source Type**: 選擇 `Internal` (內部資料庫) 或 `External` (外部 API/爬蟲)。
>
> **💡 範例**：
>
> - **System Name**: `twseprice`
> - **System Full Name**: `TWSE Price Data Source`
> - **System Type**: `Data Source System`
> - **Source Type**: `External` (Web Scraping)

- **System Name**: `<system_name>`
- **System Full Name**: `<system_full_name>`
- **System Type**: `Data Source System`
- **Source Type**: `<Internal | External>`

### 1.2 願景與邊界 (Vision & Scope)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **Core Vision**: 一句話描述系統價值，作為功能是否屬於本系統的最終判斷依據。
> - **Data Source**: 說明資料的來源（網站 URL、API Endpoint、資料庫連線）。
> - **Out of Scope**: **(關鍵)** 明確列出「不做」什麼。這能有效防止 LLM 產生超出系統職責的幻覺 (Hallucination)。
>
> **💡 範例**：
>
> - **Core Vision**: 封裝台灣證券交易所的公開資料，提供標準化的股價與交易資訊查詢介面。
> - **Data Source**: `https://www.twse.com.tw` (Web Scraping)
> - **Out of Scope**:
>     - 不涉及資料的二次加工或衍生計算（應由業務系統處理）。
>     - 不涉及資料的持久化儲存（僅提供即時查詢或快取）。
>     - 不涉及非證交所來源的資料。

- **Core Vision (核心願景)**:
    <一句話描述系統的核心價值與定位>
- **Data Source (資料來源)**:
    <說明資料的來源位置與存取方式>
- **Out of Scope (非目標範圍)**:
    - <明確列出不做的功能>

## 2. Domain Model & Boundaries (領域模型與邊界)

> **📝 總體撰寫指引**（請勿保留本指引文字）：
> 本節定義了系統的領域邊界與職責。這是 **System Analyst (LLM)** 執行 **「領域歸屬判定 (Domain Ownership Check)」** 時的 **唯一真理來源 (SSOT)**。
>
> **⚠️ 資料源系統的領域劃分原則**：
> - 領域應依據「資料類型」而非「技術實作」劃分。
> - 每個 Domain 對應一種「可獨立查詢的資料集」。

### 2.1 Domain: `<domain_name>`

> **📝 撰寫指引**：
> - **Abbreviation**: 標準縮寫 (3-5 碼)，用於命名。
> - **Type**:
>   - `Independent`: 僅當此領域在可預見的未來都不會有子領域時選擇。
>   - `Aggregate`: 有多個子領域，**或**目前僅有一個但未來有擴充規劃。
> - **Data Description**: 描述此領域提供的資料內容與格式。
> - **Boundary Rules**: 定義資料的包含與排除範圍。
>
> **💡 範例**：
>
> - **Domain**: `daily_price` (Type: `Independent`)
> - **Data Description**: 提供每日收盤價、開高低收、成交量等交易資訊。
> - **Boundary Rules**:
>     - **Includes**: 每日收盤後的歷史價量資料。
>     - **Excludes**: 盤中即時報價、分時資料。

- **Abbreviation (Prefix)**: `<abbr>`
- **Type**: `<Independent | Aggregate>`
- **Data Description**: <描述此領域提供的資料內容>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: <列出包含的資料範圍>
    - **Excludes (排除)**: <列出排除的資料範圍與理由>

#### 2.1.1 Sub-domain: `<subdomain_name>`

> **📝 撰寫指引**：
> *僅當 Domain Type 為 `Aggregate` 時填寫。*
> **即使只有一個 Sub-domain，也必須完整填寫此區塊。**

- **Abbreviation**: `<abbr>`
- **Data Description**: <描述子領域具體的資料內容>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: <明確定義子領域包含的範圍>
    - **Excludes (排除)**: <明確定義子領域排除的範圍>

### 2.2 Domain: `<domain_name>`

> **📝 撰寫指引**：
> 請完整複製 2.1 的結構進行定義。

- **Abbreviation (Prefix)**: `<abbr>`
- **Type**: `<Independent | Aggregate>`
- **Data Description**: <描述此領域提供的資料內容>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: ...
    - **Excludes (排除)**: ...

## 3. Two-Layer Architecture (標準兩層架構)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節說明資料源系統的標準兩層架構。所有資料源系統都必須遵循此架構。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 1.2*

### 3.1 Architecture Overview (架構總覽)

```text
<system>/
├── collector/     → 資料收集層：處理原始資料的獲取
│   └── <domain>/
└── service/       → 服務層：實作標準化介面，提供對外服務
    └── <domain>/
```

### 3.2 Layer Responsibilities (層級職責)

| 層級 | 職責 | 輸入 | 輸出 |
|:-----|:-----|:-----|:-----|
| **Collector** | <描述資料收集的具體方式> | <外部資料源格式> | <原始資料格式> |
| **Service** | <描述服務層的處理邏輯> | <原始資料格式> | <標準化資料格式> |

> **💡 範例**：
>
> | 層級 | 職責 | 輸入 | 輸出 |
> |:-----|:-----|:-----|:-----|
> | **Collector** | 執行 HTTP 請求，解析 HTML 表格 | HTML Page | Raw DataFrame |
> | **Service** | 資料驗證、格式標準化、快取處理 | Raw DataFrame | Pydantic Schema |
>
> **⚠️ Service 層的消費者**：
> Service 層透過實作 `core/interfaces` 定義的抽象介面，其主要消費者通常是**業務系統的 ETL Extractor**。這是資料流進入業務系統的標準入口。

## 4. System Core Architecture (系統核心架構)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節定義本系統專屬的內部核心庫 (`<system>/core`)。這些元件不屬於特定業務 Domain，而是作為基礎設施供 `collector` 與 `service` 層使用。
>
> **⚠️ 區分原則**：
> - **Project Core (`core`)**：專案級共用（所有系統都用）。
> - **System Core (`<system>/core`)**：本系統特有（僅本系統用）。

### 4.1 Toolkit Structure Map (工具集結構圖)

> **📝 撰寫指引**：
> 請以 ASCII Tree 格式展示 `<system>/core` 下的 Toolkit 目錄結構。
>
> **💡 範例**：
> ```text
> <system>/core/
> ├── http_client/
> ├── parser/
> │   ├── html/
> │   └── json/
> └── cache/
> ```

```text
<system>/core/
├── <toolkit_A>/
│   └── <toolkit_A_sub>/
├── <toolkit_B>/
└── ...
```

### 4.2 Toolkit Definitions (工具集職責定義)

> **📝 撰寫指引**：
> 請依照 4.1 的結構，對應說明每個 Toolkit 的職責。
> **Responsibility** 應具體描述其提供的**關鍵能力 (Key Capabilities)**。
>
> **💡 範例**：
> - **Toolkit**: `http_client`
>     - **Responsibility**: 封裝 HTTP 請求，提供重試機制、Rate Limiting 與 Session 管理。
> - **Toolkit**: `parser`
>     - **Responsibility**: 解析外部資料格式。
>     - **Sub-toolkits**:
>         - **Toolkit**: `html`
>             - **Responsibility**: 解析 HTML 表格，轉換為 DataFrame。

- **Toolkit**: `<toolkit_root_name>`
    - **Responsibility**: <定義核心職責與關鍵能力>
    - **Sub-toolkits** (若有):
        - **Toolkit**: `<sub_toolkit_name>`
            - **Responsibility**: <定義子工具集職責與關鍵能力>

## 5. Technology Constraints (技術限制)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節定義了系統的技術限制與依賴規則。
>
> **💡 範例**：
>
> - **Python Version**: `>=3.12`
> - **HTTP Client**: `httpx` (async support required)
> - **HTML Parser**: `beautifulsoup4` + `lxml`
> - **Caching Strategy**: In-memory (TTL-based) or Redis
> - **Rate Limiting** *(External Source Only)*: 每秒最多 3 次請求，避免被來源封鎖
> - **Interface Contract**: Must implement `core/interfaces/<domain>` abstract class

- **Python Version**: `<version_requirement>`
- **HTTP Client**: `<library_name>` <說明選擇原因>
- **Parser**: `<library_name>` <說明用途>
- **Caching Strategy**: `<策略說明>`
- **Rate Limiting** *(僅適用於 External Source Type)*: `<限流策略，例如：每秒 N 次請求>`
- **Interface Contract**: <說明需實作的介面位置>

> **⚠️ Rate Limiting 說明**：
> 此項僅適用於 **Source Type: External** 的資料源系統。當系統需要存取第三方 API 或網站時，必須定義限流策略以避免被來源封鎖。對於 **Source Type: Internal** 的系統（直接存取內部資料庫），此項可省略。

## 6. Interface Implementation (介面實作)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節說明此資料源系統實作的介面契約。資料源系統的 `service` 層必須實作 `core/interfaces` 中定義的抽象介面，以實現依賴反轉。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 2 & 6*
>
> **💡 範例**：
>
> | Interface | Location | Implementation |
> |:----------|:---------|:---------------|
> | `IDailyPriceRepository` | `core/interfaces/market/price.py` | `twseprice/service/daily_price/repository.py` |
> | `IStockInfoRepository` | `core/interfaces/market/stock.py` | `twseprice/service/stock_info/repository.py` |

| Interface | Location | Implementation |
|:----------|:---------|:---------------|
| `<interface_name>` | `<core/interfaces path>` | `<implementation path>` |

## 7. Data Flow Diagram (資料流程圖)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節以視覺化方式展示資料從外部來源到對外服務的完整流程。
>
> **💡 範例**：
>
> ```text
> [External Source]          [Collector Layer]         [Service Layer]           [Consumer]
>       │                          │                         │                       │
>       │   HTTP Request           │                         │                       │
>       │ ─────────────────────>   │                         │                       │
>       │                          │                         │                       │
>       │   HTML Response          │   Raw DataFrame         │                       │
>       │ <─────────────────────   │ ───────────────────>    │                       │
>       │                          │                         │                       │
>       │                          │                         │   Validated Schema    │
>       │                          │                         │ ───────────────────>  │
>       │                          │                         │                       │
> ```

```text
<請繪製資料流程圖>
```
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 命名與結構合規性

- [ ] **命名檢查**：System Name 是否全小寫無分隔？Domain/Sub-domain/Toolkit 是否為合法 `snake_case`？
- [ ] **縮寫檢查**：是否為每個 Domain 和 Sub-domain 定義了 3-5 碼的標準縮寫 (Abbreviation)？
- [ ] **類型檢查**：是否為每個 Domain 正確標註 Type (`Independent` 或 `Aggregate`)？

### B. 核心與邊界

- [ ] **系統核心**：是否已定義 `<system>/core` 的樹狀結構圖 (Toolkit Structure Map)？
- [ ] **職責定義**：Core Toolkit 的 Responsibility 是否已包含具體的「關鍵能力」描述？
- [ ] **資料來源**：是否已明確說明外部資料來源的位置與存取方式？
- [ ] **負面表列**：`Out of Scope` 與 `Excludes` 是否已明確填寫？

### C. 架構與介面

- [ ] **兩層架構**：是否已說明 `collector` 與 `service` 層的具體職責？
- [ ] **介面實作**：是否已列出需實作的 `core/interfaces` 介面清單？
- [ ] **資料流程**：是否已繪製從外部來源到對外服務的完整資料流程圖？

### D. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的系統資訊？
