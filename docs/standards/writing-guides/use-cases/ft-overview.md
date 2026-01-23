# Feature Overview - Documentation Guide

本規範定義 **Feature Overview (功能總覽)** 文件的撰寫規範。適用於所有 `docs/use-cases/.../overview.md` 路徑下的總覽文件。目標是提供**價值清單 (Feature Catalog)** 與 **決策指引 (Decision Guide)**，作為 System Analyst (LLM) 執行「Feature 歸屬判定」與「新增 vs 修改決策」時的 **Ground Truth (單一真理來源)**。

> **⚠️ 適用範圍**：本規範為**通用規範**，適用於以下所有類型：
> - **業務系統 (Business System)**：Domain / Sub-domain 層級
> - **資料源系統 (Data Source System)**：Domain 層級
> - **專案級函式庫 (Library)**：Toolkit 層級
> - **系統核心庫 (System Core)**：Toolkit 層級

*供 Generator: Prompt4FeatureOverview 使用*

---

## 1. 核心原則 (Core Principles)

### 1.1 文件定位

本文件是特定領域 (Domain/Toolkit) 的「價值目錄」。它不描述具體的技術實作，而是回答：「這個領域已經交付了哪些價值？」、「新需求應該歸屬於哪個既有 Feature，還是需要新增？」

### 1.2 關鍵特性

- **價值導向 (Value Oriented)**：以「交付的價值」而非「技術實作」來組織 Feature 清單。
- **決策支援 (Decision Support)**：提供明確的決策指引，協助 SA 快速判斷「新增 vs 修改」。
- **導航樞紐 (Navigation Hub)**：作為 L1 (Architecture) 與 L3 (Specs) 之間的橋樑。

### 1.3 與其他層級的關係

| 層級 | 文件類型 | 核心問題 | 本層級的角色 |
|:-----|:---------|:---------|:-------------|
| **L1** | Architecture Overview | 「新需求屬於哪個 Domain/Toolkit？」 | 被 L1 引導而來 |
| **L2** | **Feature Overview (本文件)** | **「這個需求以前做過嗎？該新增還是修改？」** | **價值清單與決策支援** |
| **L3** | FU Overview (Specs) | 「有哪些現成的 FU 可以使用？」 | 引導至 L3 查看技術細節 |

---

## 2. 檔案路徑標準

路徑結構由 Feature 的歸屬類型決定：

### 2.1 業務系統 / 資料源系統

```text
docs/use-cases/<system>/
├── <domain>/
│   ├── overview.md                    # Domain 層級 Feature 總覽
│   └── <subdomain>/
│       └── overview.md                # Sub-domain 層級 Feature 總覽
└── etl/                               # (僅業務系統) ETL Feature
    └── <domain>/
        └── overview.md
```

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
| **Feature Name** | `kebab-case` | 全小寫，使用連字號分隔。<br>必須描述「對外交付的完整能力」。 | ✅ `user-registration`, `stock-price-sync`<br>❌ `user_registration` (應用 kebab-case)<br>❌ `add-user-table` (過於技術導向) |

### 3.2 命名導向原則

> *Ref: `docs/PROJECT_DESIGN-METHODOLOGY.md` Section 2*

- **聚合能力命名**：Feature 名稱必須描述其**「對外交付的完整能力」**，而非僅描述內部單一 FU 的實作。
- ❌ **Bad (Too Narrow)**: `excel-reader` (若該 Feature 同時包含 Writer)
- ❌ **Bad (Too Broad)**: `file-helper` (若該 Feature 僅處理 Excel)
- ✅ **Good (Precise)**: `excel-processing` (精確涵蓋完整能力)

---

## 4. 內容結構模板

````markdown
# Feature Overview: <Scope Name>

> **📝 撰寫指引**（請勿保留本指引文字）：
> - `<Scope Name>` 應填入當前層級的名稱：
>   - 業務/資料源系統：Domain 或 Sub-domain 名稱 (e.g., `Market`, `Stock`)
>   - 函式庫：Toolkit 名稱 (e.g., `IO`, `Validator`)
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
> **💡 範例 (業務系統 Sub-domain)**：
>
> - **System**: `gms` (Business System)
> - **Scope Type**: `Sub-domain`
> - **Scope Name**: `market/stock`
> - **Description**: 處理股票類資產的查詢與分析功能。
>
> **💡 範例 (函式庫 Toolkit)**：
>
> - **Library**: `wutils`
> - **Scope Type**: `Toolkit`
> - **Scope Name**: `io`
> - **Description**: 提供統一的 I/O 操作介面，封裝檔案與網路存取的複雜度。

- **System / Library**: `<name>` (<type>)
- **Scope Type**: `<Domain | Sub-domain | Toolkit>`
- **Scope Name**: `<name or path>`
- **Description**: <簡述此範圍的核心職責>

## 2. Feature Catalog (功能清單)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節列出此範圍下所有已交付或開發中的 Feature。
>
> **欄位說明**：
> - **Feature Name**: 功能名稱 (kebab-case)。
> - **Value / Goal**: 此 Feature 交付的核心價值。
>   - 業務系統：描述業務價值 (e.g., 「讓使用者能夠...」)
>   - 函式庫：描述技術能力 (e.g., 「提供...能力」)
> - **Status**: `Released` | `In Progress` | `Planned` | `Deprecated`
> - **Link**: 連結至該 Feature 的 Use Case 目錄。
>
> **Status 狀態說明**：
> | 狀態 | 說明 |
> |:-----|:-----|
> | `Released` | 已發布，可正常使用 |
> | `In Progress` | 開發中 |
> | `Planned` | 已規劃，尚未開始開發 |
> | `Deprecated` | 已棄用，不建議使用但尚未移除 |
>
> **💡 範例 (業務系統)**：
>
> | Feature Name | Value / Goal | Status | Link |
> |:-------------|:-------------|:-------|:-----|
> | `stock-profile` | 讓使用者能夠查詢股票的基本資料與即時報價 | Released | [→](./stock-profile/) |
> | `stock-watchlist` | 讓使用者能夠建立與管理個人股票自選清單 | In Progress | [→](./stock-watchlist/) |
> | `stock-comparison` | 讓使用者能夠比較多檔股票的關鍵指標 | Planned | - |
> | `stock-alert-v1` | (舊版) 股價警示功能，請改用 `stock-notification` | Deprecated | [→](./stock-alert-v1/) |
>
> **💡 範例 (函式庫)**：
>
> | Feature Name | Value / Goal | Status | Link |
> |:-------------|:-------------|:-------|:-----|
> | `csv-processing` | 提供 CSV 格式的讀寫與 Schema 驗證能力 | Released | [→](./csv-processing/) |
> | `parquet-processing` | 提供 Parquet 格式的讀寫與 Schema 管理能力 | Released | [→](./parquet-processing/) |

| Feature Name | Value / Goal | Status | Link |
|:-------------|:-------------|:-------|:-----|
| `<feature_name>` | <交付的核心價值> | `<status>` | [→](<relative_path>) |

## 3. Decision Guide (決策指引)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 本節提供具體的決策指引，協助 SA 快速判斷新需求應「修改既有 Feature」還是「新增 Feature」。
>
> **撰寫原則**：
> 1. **情境導向**：以「若您要...」開頭，描述常見的需求情境。
> 2. **明確指向**：給出具體的建議行動（修改哪個 Feature / 新增 Feature）。
> 3. **覆蓋邊界案例**：特別說明容易混淆的情境。
>
> **💡 範例**：
>
> ### 3.1 修改既有 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 新增股票基本資料的欄位 | 修改 `stock-profile` Feature |
> | 調整自選清單的排序邏輯 | 修改 `stock-watchlist` Feature |
> | 修復股價顯示的格式問題 | 修改 `stock-profile` Feature |
>
> ### 3.2 需要新增 Feature 的情境
>
> | 若您要... | 建議行動 |
> |:----------|:---------|
> | 提供股票的技術分析圖表 | 新增 `stock-chart` Feature |
> | 提供股票的財報分析功能 | 新增 `stock-financial` Feature |
>
> ### 3.3 常見混淆情境
>
> | 情境 | 正確歸屬 | 原因 |
> |:-----|:---------|:-----|
> | 「在自選清單中顯示即時股價」 | `stock-watchlist` | 這是自選清單的「顯示增強」，而非股價查詢的核心功能 |
> | 「批次匯入多檔股票到自選清單」 | `stock-watchlist` | 這是自選清單的「輸入方式擴充」 |

### 3.1 修改既有 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 修改 `<feature_name>` Feature |

### 3.2 需要新增 Feature 的情境

| 若您要... | 建議行動 |
|:----------|:---------|
| <情境描述> | 新增 `<suggested_feature_name>` Feature |

### 3.3 常見混淆情境

| 情境 | 正確歸屬 | 原因 |
|:-----|:---------|:-----|
| <混淆情境> | `<correct_feature>` | <判斷理由> |

## 4. Related Resources (相關資源)

> **📝 撰寫指引**（請勿保留本指引文字）：
> 列出與此範圍相關的 L1 (Architecture) 與 L3 (Specs) 文件連結。
>
> **💡 範例**：
>
> - **Architecture Overview**: [→ gms_overview.md](../../../architecture/gms_overview.md)
> - **Specs (DB Layer)**: [→ specs/gms/db/market/stock/overview.md](../../../specs/gms/db/market/stock/overview.md)
> - **Specs (Service Layer)**: [→ specs/gms/service/market/stock/overview.md](../../../specs/gms/service/market/stock/overview.md)

- **Architecture Overview**: [→ <filename>](<relative_path>)
- **Specs (<layer>)**: [→ <path>](<relative_path>)
````

---

## 5. 撰寫檢查清單 (Quality Checklist)

在提交文件前，請逐一核對以下項目：

### A. 結構完整性

- [ ] **上下文**：Section 1 是否已明確定義 System/Library, Scope Type, Scope Name, Description？
- [ ] **功能清單**：Section 2 是否已列出所有已知的 Feature？每個 Feature 是否都有 Value/Goal 說明？

### B. 決策指引品質

- [ ] **情境覆蓋**：Section 3 是否覆蓋了「修改」與「新增」兩種情境？
- [ ] **混淆情境**：是否已識別並說明容易混淆的邊界案例？
- [ ] **指向明確**：每個決策建議是否都指向具體的 Feature 名稱？

### C. 導航一致性

- [ ] **路徑正確**：所有相對路徑連結是否正確可達？
- [ ] **與 L1 一致**：本 Overview 的 Scope 是否與 Architecture Overview 中的定義一致？
- [ ] **與 L3 連結**：是否已在 Section 4 列出相關的 Specs Overview 連結？

### D. 格式規範

- [ ] **指引文字清理**：是否已移除所有「📝 撰寫指引」與「💡 範例」區塊？
- [ ] **變數替換**：是否已將所有 `<...>` 佔位符替換為具體的資訊？
- [ ] **Feature 命名**：所有 Feature 名稱是否都使用 `kebab-case`？
