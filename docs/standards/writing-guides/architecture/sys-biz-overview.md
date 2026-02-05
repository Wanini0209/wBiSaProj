# Business System Architecture Overview - Documentation Guide

本規範定義 **Business System (業務系統)** 的 `SYSTEM_OVERVIEW.md` 撰寫規範。目標是定義系統的 **邊界 (Boundaries)**、**領域職責 (Domain Responsibilities)**、**核心基礎設施 (System Core)** 與 **架構限制 (Constraints)**，作為 System Analyst (LLM) 執行需求分析與架構設計時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範僅適用於 **Business System** (如 `gms`, `sqs`)。資料源系統 (Data Source System) 請另參閱 `sys-ds-overview.md`。

*供 Generator: Prompt4BusinessSystemOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是業務系統的「憲法」。它不描述具體功能的實作細節，而是定義「什麼該做」、「什麼不該做」、「各領域的職責劃分」以及「共用的技術地基」。

### 1.2 關鍵特性

- **單一真理來源 (SSOT)**：所有 Feature 的領域歸屬 (Domain Ownership) 與技術選型 (Tech Stack) 均以此文件為最高指導原則。
- **邊界優先 (Boundary First)**：必須明確定義「非目標範圍 (Out of Scope)」與「排除規則 (Excludes)」，以防止架構腐化。
- **類型導向 (Type Driven)**：依據資料特性（如結構化、時序性）選擇合適的儲存類型 (RDBMS/NoSQL/FS)。
- **基礎設施顯性化 (Explicit Infrastructure)**：明確定義 `<system>/core` 中的共享工具集，避免重複造輪子。

---

## 2. 檔案路徑標準

`docs/architecture/<system>_overview.md`

- `<system>`: 系統縮寫名稱 (e.g., `gms`, `sqs`)。

---

## 3. 命名規範 (Naming Conventions)

> **⚠️ 重要**：請嚴格遵守以下命名規範，以確保 Python 套件結構的合法性與一致性。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 5.3 & 8.2*

### 3.1 系統與結構命名

| 屬性 | 格式規範 | 說明 | 範例 |
| :--- | :--- | :--- | :--- |
| **System Name** | `[a-z0-9]+` | **系統縮寫 ID**。全小寫，無任何分隔符號。保持頂層 Namespace 簡潔。 | `gms`, `sqs` |
| **Domain Name** | `snake_case` | **全小寫，使用底線分隔，嚴禁連字號 (-)**。<br>必須是合法的 Python Package Name。<br>應使用純業務名詞，避免 `_data`, `_info` 等技術後綴。 | ✅ `market`, `risk_control`<br>❌ `market-data` (非法套件名)<br>❌ `market_db` (技術命名) |
| **Sub-domain Name** | `snake_case` | 同 Domain Name 規範。 | `stock`, `valuation` |
| **Toolkit Name** | `snake_case` | **技術分類名稱**。用於 System Core 中的工具集分類。<br>必須反映技術解決方案領域。 | `security`, `logging`, `config`<br>❌ `common`, `utils` (禁止模糊命名) |

---

## 4. 內容結構模板

````markdown
# Business System Architecture Overview

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本文件將被用作 Prompt Input 餵給 LLM 進行分析。請確保內容精簡、無歧義，並專注於「定義規則」。

## 1. System Identity (系統識別)

### 1.1 基本資料 (Basic Info)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **System Name**: 系統縮寫 ID (對應目錄名稱)。
> - **System Full Name**: 系統全名 (對應專案立項名稱)。
> - **System Type**: 固定填寫 `Business System`。
>
> **💡 範例**：
>
> - **System Name**: `gms`
> - **System Full Name**: `Global Market System`
> - **System Type**: `Business System`

- **System Name**: `<system_name>`
- **System Full Name**: `<system_full_name>`
- **System Type**: `Business System`

### 1.2 願景與邊界 (Vision & Scope)

> **📝 撰寫指引**（請勿保留本指引文字）：
> - **Core Vision**: 一句話描述系統價值，作為功能是否屬於本系統的最終判斷依據。
> - **Out of Scope**: **(關鍵)** 明確列出「不做」什麼。這能有效防止 LLM 產生超出系統職責的幻覺 (Hallucination)。
>
> **💡 範例**：
>
> - **Core Vision**: 作為全公司的金融市場數據中心，提供全球金融市場的各種數據與分析服務。
> - **Out of Scope**:
>     - 不涉及使用者資產庫存管理 (Inventory)。
>     - 不涉及交易下單執行 (Execution)。

- **Core Vision (核心願景)**:
    <一句話描述系統的核心價值與定位>
- **Out of Scope (非目標範圍)**:
    - <明確列出不做的功能>

## 2. Domain Model & Boundaries (領域模型與邊界)

> **📝 總體撰寫指引**（請勿保留本指引文字）：
> 本節定義了系統的領域邊界與職責。這是 **System Analyst (LLM)** 執行 **「領域歸屬判定 (Domain Ownership Check)」** 時的 **唯一真理來源 (SSOT)**。
>
> **⚠️ 架構規則 (Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 3.2 & 3.3)**：
> 1. **獨立型 (Independent)**：本質上不可分割的單一業務領域。
> 2. **聚合型 (Aggregate)**：由多個子領域聚合而成的概念。
>    - **重要規則（先驗式聚合, §3.2 路徑 B）**：即使目前**只有一個** Sub-domain，若該 Domain 的上層抽象概念來自**已確立的外部知識體系**（如金融學科中 `market` 已確立包含 stock, fund, bond 等子概念），且未來擴展預期合理，仍**必須**定義為 `Aggregate` 類型，並建立 Sub-domain 層級，以避免未來的結構性重構。

### 2.1 Domain: `<domain_name>`

> **📝 撰寫指引**：
> - **Abbreviation**: 標準縮寫 (3-5 碼)，用於 DB/API 命名。
> - **Type**:
>   - `Independent`: 僅當此領域在可預見的未來都不會有子領域時選擇。
>   - `Aggregate`: 有多個子領域，**或**目前僅有一個但其上層抽象概念來自已確立的外部知識體系且未來擴展預期合理（先驗式聚合, §3.2 路徑 B）。
> - **Responsibility**: 定義核心實體或聚合概念。
> - **Boundary Rules**: 若為 Aggregate，重點在於定義「跨 Sub-domain 的共用屬性」。
>
> **⚠️ Responsibility 與 Boundary Rules 撰寫要點 [CRITICAL]**：
> - **Responsibility** 應描述「職責範圍」（負責管理哪類業務實體/資料），而非「具體功能」（目前能做什麼）。
> - **Includes/Excludes** 的目的是「劃定邊界」，協助判斷新需求是否歸屬於此。應使用「通用的資料類型或業務概念」，而非列舉具體功能。
> - **禁止**將當前已知的具體功能需求直接寫入，這會限縮職責範圍的理解。
>
> **💡 思考方式**：
> - Responsibility：「這個 Domain 存在的目的是管理哪一類業務實體？」
> - Includes：「哪些類型的資料/業務概念屬於這個職責範圍？」
> - Excludes：「哪些類型的資料/業務概念不屬於這個職責範圍，應歸屬於其他 Domain？」
>
> **💡 範例 (單一子領域的聚合型)**：
> - **Domain**: `market` (Type: `Aggregate`)
> - **Sub-domain**: `stock`
> - *理由：雖然目前只有 Stock，但 Market 本質是聚合概念，保留架構以待未來加入 Bond。*

- **Abbreviation (Prefix)**: `<abbr>`
- **Type**: `<Independent | Aggregate>`
- **Responsibility**: <定義核心實體或聚合概念>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: <列出特徵>
    - **Excludes (排除)**: <列出排除項目與理由>

#### 2.1.1 Sub-domain: `<subdomain_name>`

> **📝 撰寫指引**：
> *僅當 Domain Type 為 `Aggregate` 時填寫。*
> **即使只有一個 Sub-domain，也必須完整填寫此區塊。**

- **Abbreviation**: `<abbr>`
- **Responsibility**: <定義子領域具體職責>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: <明確定義子領域包含的範圍>
    - **Excludes (排除)**: <明確定義子領域排除的範圍>

#### 2.1.2 Sub-domain: `<subdomain_name>`

*(若有第二個子領域，請複製上述 2.1.1 的格式填寫。若無則刪除此區塊)*

### 2.2 Domain: `<domain_name>`

> **📝 撰寫指引**：
> 請完整複製 2.1 的結構進行定義。
> 若此 Domain 為 Aggregate Type，請務必包含下方的 Sub-domain 區塊。

- **Abbreviation (Prefix)**: `<abbr>`
- **Type**: `<Independent | Aggregate>`
- **Responsibility**: <定義核心實體或聚合概念>
- **Boundary Rules (邊界規則)**:
    - **Includes (包含)**: ...
    - **Excludes (排除)**: ...

#### 2.2.1 Sub-domain: `<subdomain_name>`

*(若 Domain 2.2 為 Aggregate Type，請在此處展開定義。格式同 2.1.1)*

- **Abbreviation**: `<abbr>`
- **Responsibility**: ...
- **Boundary Rules**:
    - **Includes**: ...
    - **Excludes**: ...

## 3. System Core Architecture (系統核心架構)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節定義本系統專屬的內部核心庫 (`<system>/core`)。這些元件不屬於特定業務 Domain，而是作為基礎設施供全系統各模組 (db/service/api/etl) 使用。
>
> **⚠️ 區分原則**：
> - **Project Core (`core`)**：專案級共用（所有系統都用）。
> - **System Core (`<system>/core`)**：本系統特有（僅本系統用）。

### 3.1 Toolkit Structure Map (工具集結構圖)

> **📝 撰寫指引**：
> 請以 ASCII Tree 格式展示 `<system>/core` 下的 Toolkit 目錄結構。Toolkit 可支援巢狀結構 (Nested Structure)。
>
> **💡 範例**：
> ```text
> <system>/core/
> ├── config/
> ├── logging/
> └── security/
>     ├── crypto/
>     └── session/
> ```

```text
<system>/core/
├── <toolkit_A>/
│   └── <toolkit_A_sub>/
├── <toolkit_B>/
└── ...
```

### 3.2 Toolkit Definitions (工具集職責定義)

> **📝 撰寫指引**：
> 請依照 3.1 的結構，對應說明每個 Toolkit (含子節點) 的職責。
> 若有巢狀結構，請使用 **縮排 (Indentation)** 清單來表示層級關係。
>
> **⚠️ Responsibility 與 Boundary Rules 撰寫要點 [CRITICAL]**：
> - **Responsibility** 應描述「職責範圍」（負責處理哪類問題），而非「具體功能」（目前能做什麼）。
> - **Boundary Rules** 為**可選欄位**，當 Toolkit 職責較廣或與其他 Toolkit/Domain 有潛在歧義時填寫，用於劃定邊界。
> - **禁止**將當前已知的具體功能需求直接寫入，這會限縮職責範圍的理解。
>
> **💡 思考方式**：
> - Responsibility：「這個 Toolkit 存在的目的是解決哪一類問題？」
> - Boundary Rules：「哪些能力屬於/不屬於這個 Toolkit？是否有與其他地方的職責重疊需要釐清？」
>
> **💡 範例（無 Boundary Rules）**：
>
> - **Toolkit**: `config`
>     - **Responsibility**: 提供系統組態的讀取與驗證能力，包含環境變數解析、設定檔載入與強型別組態物件。
>
> **💡 範例（有 Boundary Rules 與 Sub-toolkits）**：
>
> - **Toolkit**: `security`
>     - **Responsibility**: 處理系統內部的安全機制，包含身份驗證、授權檢查與加解密運算。
>     - **Boundary Rules**:
>         - **Includes**: Token 驗證與解析、加解密運算、權限檢查輔助工具
>         - **Excludes**: 使用者帳號的 CRUD 管理（屬於 `user` Domain）
>     - **Sub-toolkits**:
>         - `auth` - 提供身份驗證令牌的解析與驗證能力。
>         - `crypto` - 提供加解密運算與金鑰管理能力。

- **Toolkit**: `<toolkit_root_name>`
    - **Responsibility**: <定義核心職責與關鍵能力>
    - **Boundary Rules** (可選，當有歧義時填寫):
        - **Includes**: <屬於此 Toolkit 的能力類別>
        - **Excludes**: <不屬於此 Toolkit 的能力類別，並說明歸屬>
    - **Sub-toolkits** (若有):
        - `<sub_toolkit_name>` - <一句話職責描述>

- **Toolkit**: `<toolkit_root_name>`
    - **Responsibility**: ...

## 4. Technology Constraints (技術堆疊限制)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節定義了系統**允許使用**的儲存技術清單 (Allowlist)。這是 **System Analyst (LLM)** 執行技術選型時的硬性限制。
>
> **⚠️ 關鍵原則：區分「技術類型」與「基礎設施」**
> - **專注於協定與格式**：應限制「資料如何被存取 (SQL, NoSQL, FileSystem)」與「資料格式 (Parquet, JSON)」。
> - **保留環境彈性**：**嚴禁**將**正式環境 (Production)** 的特定基礎設施 (如 AWS S3, Google Cloud SQL) 列為唯一選項。必須保留**開發/測試環境 (Dev/Test)** 使用 Local 實作 (如 Local Disk, Docker Container) 的空間。
>
> **💡 撰寫範例（請依系統需求調整內容）**：
> - **SQL (RDBMS)**: `PostgreSQL`
>     - *適用場景: 結構化且具強關聯性的資料（如用戶設定、權限、主檔）。正式環境建議使用託管服務，開發/測試環境可使用 Docker 容器。*
> - **NoSQL**: `Redis` (Cache), `MongoDB` (Document)
>     - *適用場景: 高頻存取的暫存資料或高度動態的報告內容。正式環境與開發環境應允許直接存取本地磁碟，避免強烈依賴雲端物件儲存。*
> - **FileSystem**: `Parquet` (建議介面: S3-compatible / Local Disk)
>     - *適用場景: 大數據、時間序列、不可變歷史資料。開發/測試環境應允許直接存取本地磁碟，避免強烈依賴雲端物件儲存。*

- **SQL (RDBMS)**: `<建議技術, e.g., PostgreSQL>`
    - *適用場景: 結構化資料、高關聯性、需強一致性 (ACID) 的業務交易。*
- **NoSQL**: `<建議技術, e.g., MongoDB, Redis>`
    - *適用場景: 半結構化文件 (Document)、高頻快取 (KV)。*
- **FileSystem**: `<建議技術, e.g., Parquet>`
    - *適用場景: 大數據、時間序列 (Time-series)、不可變歷史資料 (Immutable)。*

## 5. Interface Strategy (介面策略)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 定義本系統的主要客戶端類型。若系統需服務多種類型的客戶端，應區分 Primary 與 Secondary。
> *Ref: `docs/PROJECT_DESIGN-ARCHITECTURE.md` Section 6.1 (System Communication)*
>
> **類型選擇**：
> 1. **Frontend Application**: 給人用的 (Web/App)。注重 UI 體驗、分頁、Session。
> 2. **External System**: 給外部廠商用的 (B2B)。注重嚴格契約、限流、API Key。
> 3. **Internal System**: 給專案內其他系統用的 (Service)。注重高吞吐、批量介面、輕量認證。
>
> **💡 多客戶端範例**：
> 若系統同時服務前端應用與內部系統，可採用以下格式：
>
> - **Primary Client Type**: `Frontend Application`
>     - *Design Focus: UI 友善性, 低延遲, Session/Token Auth。*
> - **Secondary Client Type**: `Internal System`
>     - *Design Focus: 高吞吐量, 批量介面, 輕量認證。*

- **Primary Client Type**: <選擇以下一項>
    - `Frontend Application` (Web/Mobile App)
        - *Design Focus: UI 友善性 (Pagination/Filtering), 低延遲 (Latency), Session/Token Auth。*
    - `External System` (3rd Party Integration)
        - *Design Focus: 嚴格契約 (Strict Versioning), 防禦性限流 (Rate Limiting), API Key/Signature。*
    - `Internal System` (Project Internal Service)
        - *Design Focus: 高吞吐量 (High Throughput), 批量介面 (Batch APIs), 輕量認證 (Trust Boundary 內)。*

- **Secondary Client Type** (若有): <同上格式>

## 6. Cross-Domain Relationships (跨領域關係)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節描述系統內各 Domain 之間的**資料流向**與**協作模式**。這是 **System Analyst (LLM)** 執行 **Feature 設計** 與 **資料建模** 時，理解跨領域依賴脈絡的重要參考。
>
> **撰寫原則**：
> 1. **聚焦關鍵關係**：僅記錄具有實質資料依賴或業務協作的關係，避免列舉所有可能的組合。
> 2. **標註方向性**：使用箭頭 (`→`, `←`, `↔`) 標示資料流向或依賴方向。
>    - `A → B`: A 提供資料給 B，或 B 依賴 A。
>    - `A ↔ B`: 雙向關係，A 與 B 互相依賴對方的資料。
>    - **註**：雙向關係 (`↔`) 在設計良好的系統中**相對少見**，因其意味著較高的耦合度。若無明確的雙向資料依賴，不必刻意列舉。
> 3. **說明協作語意**：簡述關係的業務意義，而非技術實作細節。
>
> **💡 範例**：
>
> | 關係 | 說明 |
> |:-----|:-----|
> | `market` → `classification` | `market` 領域的商品引用 `classification` 提供的 GICS 分類標準進行標記。 |
> | `analysis` → `market` | `analysis` 領域的指標計算，以 `market` 的原始價量數據為輸入來源。 |
> | `analysis` → `economy` | `analysis` 領域進行總經相關分析時，以 `economy` 的經濟指標為輸入來源。 |
> | `user` → `market` | 使用者自選股清單 (Watchlist) 在 `market` 實作，但需關聯 `user` 的身份識別。 |
>
> **⚠️ 注意**：
> - 若系統僅有單一 Domain，本節可省略。
> - 跨**系統**的依賴關係（如本系統依賴外部資料源）不在此節範圍，應記錄於系統間的整合文件。

| 關係 | 說明 |
|:-----|:-----|
| `<domain_a>` → `<domain_b>` | <描述 A 與 B 的協作模式與資料流向> |
| `<domain_c>` ↔ `<domain_d>` | <描述 C 與 D 的雙向關係> |
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 命名與結構合規性

- [ ] **命名檢查**：System Name 是否全小寫無分隔？System Full Name 是否已填寫？Domain/Sub-domain/Toolkit 是否為合法 `snake_case`？
- [ ] **縮寫檢查**：是否為每個 Domain 和 Sub-domain 定義了 3-5 碼的標準縮寫 (Abbreviation)？
- [ ] **類型檢查**：是否為每個 Domain 正確標註 Type (`Independent` 或 `Aggregate`)？Aggregate 類型的 Domain 是否都有展開 Sub-domain 定義？

### B. 核心與邊界

- [ ] **系統核心**：是否已定義 `<system>/core` 的樹狀結構圖 (Toolkit Structure Map)？
- [ ] **職責定義**：Core Toolkit 的 Responsibility 是否已包含具體的「關鍵能力」描述？
- [ ] **資料重力**：對於跨 Domain 的模糊地帶（如使用者清單、交易紀錄），是否已依據「Entity Identity vs. Context」原則明確界定歸屬？
- [ ] **負面表列**：`Out of Scope` 與 `Excludes` 是否已明確填寫？

### C. 技術與介面策略

- [ ] **技術類型**：是否確認了系統支援的三大儲存類型 (RDBMS, NoSQL, FileSystem)？是否避免將特定雲端基礎設施列為唯一選項？
- [ ] **介面策略**：是否依據真實的下游消費者 (Consumer) 選擇了正確的 Client Type？若有多種客戶端，是否區分 Primary/Secondary？

### D. 跨領域關係

- [ ] **關係完整性**：是否已識別並記錄所有具實質依賴的跨 Domain 關係？
- [ ] **方向性標註**：每個關係是否已標註正確的資料流向 (`→`, `↔`)？
- [ ] **語意清晰**：每個關係的說明是否聚焦於業務協作意義，而非技術實作？

### E. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的系統資訊？
