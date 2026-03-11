# wBiSaProj 專案設計文件 - 導航體系篇

## 文件定位與導覽

本文件是 wBiSaProj 專案的**文件導航體系設計規範**，為 [總體設計文件](PROJECT_DESIGN.md) 的延伸。它定義了專案 Overview 文件的三層導航架構、目錄結構映射規則，以及各層級 Overview 的內容標準，協助 SA 與開發者快速定位所需資訊。

**文件體系**：

```text
總體設計文件 (PROJECT_DESIGN.md)
    ├── 📘 架構篇 (PROJECT_DESIGN-ARCHITECTURE.md)
    ├── 📗 方法論篇 (PROJECT_DESIGN-METHODOLOGY.md)
    ├── 📙 協作篇 (PROJECT_DESIGN-COLLABORATION.md)
    └── 📕 導航體系篇 (本文件)
```

**本文件結構**：

1. **核心設計哲學**：闡述「由粗到細的決策漏斗」與「結構對應性」原則
2. **三層導航體系**：定義 Architecture、Feature、FU 三層 Overview 的分層職責
3. **目錄結構映射表**：嚴格定義各層級 Overview 文件在檔案系統中的實體位置
4. **導航與決策路徑**：說明 SA 與開發者如何使用此體系進行資訊定位
5. **總覽文件內容規範**：定義各層級 Overview 文件的標準內容要素

---

## 1. 核心設計哲學

本專案的文件體系設計旨在解決大型系統中「資訊過載」與「資產迷航」的痛點。我們採用以下兩大核心原則：

### 1.1 決策漏斗 (Decision Funnel)

文件層級應反映**決策的顆粒度**。使用者（SA/Developer）在尋找資訊時，應順著「戰略定位 (Map) → 價值交付 (Feature) → 技術資產 (Asset)」的路徑，像漏斗一樣逐步縮小範圍，精準定位。

### 1.2 結構對應性 (Structural Correspondence)

文件的物理目錄結構必須與**模組層級**及**業務/技術領域結構**保持嚴格的映射關係。

- **Use Cases**：映射業務領域 (Domain) 與工具集 (Toolkit)。
- **Specs**：映射程式碼的模組層級 (Module Layers) 與領域結構。

---

## 2. 三層導航體系 (The 3-Tier Navigation System)

我們建立一個三層級的總覽 (Overview) 體系，為不同階段的決策提供資訊支援。

| 層級 (Level) | 文件類型 | 核心職責 | 對應受眾 | 關鍵決策問題 | 典型查詢範例 |
|:---|:---|:---|:---|:---|:---|
| **L1** | **Architecture Overview**<br>(架構地圖) | **定義邊界**<br>展示系統/函式庫的整體疆域、Domain 劃分，以及**系統核心 (System Core) 的工具集架構**。 | Architect,<br>Lead SA | 「新需求屬於哪個系統？哪個 Domain？還是基礎設施？」 | 「用戶授權功能該放在哪個系統的哪個 Domain？」 |
| **L2** | **Feature Overview**<br>(價值清單) | **盤點交付物**<br>列出該領域下已交付或開發中的**功能特性 (Features)**。<br>*(Feature = 完整的業務/技術價值單元)* | SA, PM | 「這個**業務需求**以前做過嗎？該新增還是修改 Feature？」 | 「系統有沒有做過『股票自選清單』功能？」 |
| **L3** | **FU Overview**<br>(資產庫存) | **盤點技術元件**<br>列出該模組層級下可供調用的**功能單元 (Functional Units)**。<br>*(FU = 最小邏輯完整性單位/技術資產)* | Dev, SA | 「我有哪些現成的 **FU** 可以使用？」 | 「db 層有沒有現成的 `StockPriceRepository`？」 |

> **L2 與 L3 的核心差異**
>
> | 面向 | L2 (Feature Overview) | L3 (FU Overview) |
> |:---|:---|:---|
> | **視角** | 業務/價值視角 | 技術/實作視角 |
> | **粒度** | 一個 Feature 可能橫跨多個模組層 (db + service + api) | 一個 FU 僅存在於單一模組層內 |
> | **命名風格** | 以業務能力命名 (e.g., `user-registration`) | 以技術元件命名 (e.g., `UserProfileRepository`) |
> | **使用時機** | 確認「要不要做」、「做過沒有」 | 確認「怎麼做」、「有什麼可以用」 |

---

## 3. 目錄結構映射表 (Directory Structure Mapping)

本章節定義各層級 `overview.md` 檔案的實體位置。所有新增的文件必須嚴格遵守此路徑規範。

### 3.1 Level 1: 架構總覽 (Architecture)

位於 `docs/architecture/`，以單一檔案完整描述一個系統或函式庫的宏觀結構。

```text
docs/architecture/
├── <system>_overview.md       # 業務/資料源系統總覽 (e.g., gms_overview.md)
│                              # 內容包含：Domain 結構樹 + System Core Toolkit 結構樹
└── <library>_overview.md      # 專案級函式庫總覽 (e.g., wutils_overview.md)
                               # 內容包含：Toolkit 結構樹
```

### 3.2 Level 2: Feature 總覽 (Use Cases)

位於 `docs/use-cases/`，路徑結構由「業務領域 (Domain)」或「工具集 (Toolkit)」驅動，專注於**價值交付**。

**A. 業務與資料源系統**

```text
docs/use-cases/<system>/
├── <domain>/
│   ├── overview.md            # Domain 層級 Feature 總覽
│   └── <subdomain>/
│       └── overview.md        # Sub-domain 層級 Feature 總覽
└── core/
    └── <toolkit>/
        └── overview.md        # 系統核心庫 (System Core) Toolkit 層級 Feature 總覽
```

**B. 專案級通用函式庫**

```text
docs/use-cases/<library>/
└── <toolkit>/
    └── overview.md            # Toolkit 層級 Feature 總覽
```

### 3.3 Level 3: FU 總覽 (Specs)

位於 `docs/specs/`，其路徑結構對應程式碼的**模組層級 (db, service, api...)** 以及 **領域/工具集 (Domain/Toolkit)** 層次。

> **總覽文件職責**：
> 本層級所有的 `overview.md` 必須：**列出該 Domain / Sub-domain 或 Toolkit 下所屬的 FU 列表，並說明每個 FU 的功能以及所屬的 FU-container。**

**A. 業務系統 (Business System)**

*重點：必須區分 `db`, `service`, `api`, `etl` 以及 `core` 等模組層。*

```text
docs/specs/<system>/
├── core/                      # 系統級核心 (System Core)
│   └── <toolkit>/
│       └── overview.md
├── db/                        # DB 層 (Repositories)
│   ├── <domain>/
│   │   ├── overview.md
│   │   └── <subdomain>/
│   │       └── overview.md
│   └── ...
├── service/                   # Service 層 (Logic)
│   ├── <domain>/
│   │   ├── overview.md
│   │   └── <subdomain>/
│   │       └── overview.md
│   └── ...
├── api/                       # API 層 (Endpoints)
│   ├── <domain>/
│   │   ├── overview.md
│   │   └── <subdomain>/
│   │       └── overview.md
│   └── ...
└── etl/                       # ETL 層 (Jobs/Pipelines)
    ├── <domain>/
    │   ├── overview.md
    │   └── <subdomain>/
    │       └── overview.md
    └── ...
```

**B. 資料源系統 (Data Source System)**

```text
docs/specs/<system>/
├── core/                      # 系統級核心 (System Core)
│   └── <toolkit>/
│       └── overview.md
├── collector/                 # 收集層
│   ├── <domain>/
│   │   ├── overview.md
│   │   └── <subdomain>/
│   │       └── overview.md
│   └── ...
└── service/                   # 服務層 (Adapter)
    ├── <domain>/
    │   ├── overview.md
    │   └── <subdomain>/
    │       └── overview.md
    └── ...
```

> **模組層級的 Domain 結構說明**
>
> 業務系統與資料源系統的所有模組層（如 `db`, `service`, `api`, `etl`, `collector`）皆採用一致的 `<domain>/[<subdomain>]` 結構組織。此設計確保：
>
> 1. **垂直一致性**：同一業務領域的程式碼與文件，在各模組層的路徑結構保持對應（例如：`db/market/stock` 與 `service/market/stock`）。
> 2. **資料流可追溯性**：ETL 模組的 domain 對應的是**業務系統自身的領域結構**，而非資料來源，確保 `etl/<domain>` → `db/<domain>` 的資料流向清晰可見。
> 3. **導航可預測性**：開發者可依據 domain 歸屬，直觀推斷任一模組層的 `overview.md` 位置。

**C. 專案級通用函式庫 (Project-Level Libraries)**

```text
docs/specs/<library>/          # e.g., wutils, core (project level)
└── <toolkit>/
    └── overview.md
```

---

## 4. 導航與決策路徑 (Navigation Flow)

為確保不同類型的需求能被正確歸類，本體系提供兩條標準的導航軌道。

### 4.1 軌道 A：業務與資料需求 (Business & Data Requirements)

*適用對象：新增業務功能、報表、資料爬蟲或 ETL 流程。*

**步驟一：戰略定位 (Check Architecture)**

- **動作**：查閱 `docs/architecture/<system>_overview.md`。
- **決策**：確認需求歸屬的 **Domain** 或 **Sub-domain**。
- **目標路徑**：
    - 歸屬 Domain：`docs/use-cases/<system>/<domain>`
    - 歸屬 Sub-domain：`docs/use-cases/<system>/<domain>/<subdomain>`

**步驟二：價值確認 (Check Features)**

- **動作**：查閱目標路徑（Domain 或 Sub-domain）下的 `overview.md`。
- **決策**：
    1. **查重**：是否已有類似的業務功能 (Feature)？
    2. **定性**：是「修改既有 Feature」還是「新增 Feature」？
- **產出**：Feature 名稱與規格撰寫計畫。

**步驟三：資產盤點 (Check FUs)**

- **動作**：查閱各模組層級 (Module Layer) 的 overview (如 `docs/specs/<system>/db/<domain>/overview.md`)。
- **決策**：盤點現有資產，確認是否有可復用的 FU (如 Repository 或 Service)。
- **產出**：明確的 Dependency 清單 (列出可復用的 FU)。

### 4.2 軌道 B：技術與基礎設施需求 (Technical & Infrastructure Requirements)

*適用對象：新增共用工具、重構核心元件、升級系統基礎設施。*

**步驟一：範疇界定 (Scope Definition)**

- **動作**：判斷影響範圍。
    - **全專案共用**：定位至 `docs/architecture/<library>_overview.md`。
    - **單系統專用**：定位至 `docs/architecture/<system>_overview.md`。
- **目標路徑**：確定的 Library 或 System Core Toolkit 路徑。

> **System Core (`<system>/core`) 的定位指引**
>
> System Core 同時具備「系統子模組」與「內部函式庫」的雙重角色，其範疇判定應遵循以下原則：
>
> | 情境 | 判定結果 | 定位路徑 |
> |:---|:---|:---|
> | 工具**僅供單一系統**內部使用 | 歸屬 System Core | `docs/architecture/<system>_overview.md` 的 Core Toolkit 區段 |
> | 工具**已被或預期被多個系統**使用 | 應提升至專案級 Library | `docs/architecture/<library>_overview.md` (如 `core` 或 `wutils`) |
>
> **決策原則**：當不確定時，優先放置於 System Core。待實際出現跨系統需求時，再透過重構提升至專案級 Library。

**步驟二：工具集定位 (Locate Toolkit)**

- **動作**：查閱對應 Architecture 文件中的 Toolkit 結構樹。
- **決策**：確認是否已有合適的 Toolkit，或需提案新增。

**步驟三：技術資產確認 (Check Technical FUs)**

- **動作**：查閱 `docs/specs/.../<toolkit>/overview.md`。
- **決策**：確認是否已有可用的 FU (如 Helper Function 或 Base Class)。
- **產出**：決定實作策略（新增 Feature 或擴充現有 FU）。

---

## 5. 總覽文件內容規範 (Overview Content Standards)

所有層級的 `overview.md` 必須具備「導航指引」與「決策支援」的功能，嚴格遵守以下內容規範：

1. **唯一性**：每個目錄層級僅能有一個 `overview.md`。
2. **內容要求**：
    - **L1 (Architecture)**：必須作為「系統地圖」，包含：
        - **系統定位**：一句話描述核心價值。
        - **結構圖**：完整的 Domain / Sub-domain / Toolkit 樹狀結構。
        - **邊界與職責 (Critical)**：針對每個下級節點 (Domain/Toolkit)，明確定義**職責 (Responsibility)** 與 **排除事項 (Excludes)**。這是不看細節就能判斷「新需求該放哪」的關鍵。
    - **L2 (Features)**：必須作為「價值目錄」，包含：
        - **範圍描述**：簡述此領域 (Domain/Toolkit) 的業務或技術範疇。
        - **Feature 清單與價值說明**：列出 Feature 並說明其 **目的與價值 (Goal/Value)**，而不僅僅是名稱。
        - **技術資產追溯 (Owned FUs)**：基於 FU 單一驅動原則，明確列出該 Feature 所唯一擁有與驅動的所有底層功能單元 (FU)，實現**由上而下 (Top-Down) 的架構追溯**。
        - **SA 決策指引 (Decision Guide)**：提供「若您要...請參考...」的具體導航建議，協助 SA 快速判斷是新增還是修改。
    - **L3 (Specs)**：必須作為「技術資產庫」，包含：
        - **FU 列表**：列出該 Domain/Toolkit 下所有的 Functional Units。
        - **業務源頭追溯 (Parent Feature)**：明確標註該 FU 唯一隸屬的 Parent Feature，貫徹 FU 單一驅動原則，實現**由下而上 (Bottom-Up) 的價值追溯**。
        - **功能簡述**：說明每個 FU 的核心職責。
        - **FU-Container**：明確標註該 FU 所屬的 FU-container (即 Import Path)。
3. **同步性**：符合以下任一情境時，必須同步更新對應父目錄的 `overview.md`：
    - 新增或調整 **Feature** 與 **FU** 時。
    - 新增或調整 **Toolkit**、**Domain** 或 **Sub-domain** 結構時。
4. **自動化檢查**：
    專案提供 `invoke` 指令協助維護 Overview 文件的正確性與完整性：

    | 命令 | 用途 |
    |:-----|:-----|
    | `inv docs.overview-check` | 檢查 `overview.md` 中列出的 Feature / FU 是否與實際檔案結構一致，並驗證 L2 與 L3 之間的雙向追溯 (Parent Feature ↔ Owned FUs) 是否契合 |

    > **使用時機**：建議在以下情境執行此檢查：
    > - 新增或移除 Feature / FU 後
    > - 調整 Domain / Sub-domain / Toolkit 結構後
    > - 提交 PR 前的自我檢核
