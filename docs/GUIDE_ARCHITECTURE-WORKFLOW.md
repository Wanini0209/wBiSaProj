# wBiSaProj 開發流程實作指引：GMS 股價分析系統範例

## 1. 範例情境與目標

本指引使用 **「GMS 系統整合 TEJ 資料源」** 作為核心範例。

### 應用情境

我們即將開發本專案的第一個核心業務系統 —— **GMS (Global Market Information & Analysis System，全球市場資訊與分析系統)**。

GMS 的核心職責是匯聚全球市場數據並提供深度分析服務。在第一階段，我們將聚焦於台灣股市，目標是提供使用者查詢歷史股價並執行技術分析（如成交量異常檢測）。GMS 本身不生產原始交易數據，而是需要從公司內部的 **TEJ 資料庫** 攝取數據。

### 開發目標

構建一個完整的端到端系統，包含：

1. **資料源適配**：連接既有的 TEJ 資料庫，轉換為標準契約。
2. **資料落地**：在 GMS 內部建立專屬資料庫，並每日同步數據。
3. **業務分析**：實作成交量異常分析與技術指標計算。
4. **對外服務**：透過 RESTful API 開放功能，並確保系統具備穩固的啟動架構。

---

## 2. 架構拆分策略與思考

在進入開發前，我們根據「價值驅動」與「Walking Skeleton (會走路的骨架)」策略進行規劃。

### 思考點 A：為何將「標準契約 (Contracts)」獨立為第一個 Feature？

- **解耦需求**：為了避免 GMS 直接依賴 TEJ 的實作細節，必須先定義通用的溝通語言。
- **技術價值**：先行定義介面與 DTO，讓後續的適配器與業務邏輯可平行開發。

### 思考點 B：為何將「基礎建設 (DB & App Infra)」獨立交付？

- **骨架優先**：在開發具體業務 API 前，先建立「能運作的系統骨架」(Database + FastAPI App)，確保 Config、Log、DB 連線等基礎設施已就緒。
- **技術價值**：這讓後續的業務 Feature 開發只需專注於「掛載」新功能，而非重複處理基礎配置。

### 思考點 C：為何將 ETL 觸發點包含在 Pipeline Feature 中？

- **高內聚**：資料管線的「執行能力」是其核心價值的一部分。若需求包含「透過 API 手動觸發同步」，則應在交付 Pipeline 的同時交付觸發介面。

### 思考點 D：為何 Service 與 API 合併為一個 Feature？

- **垂直切片 (Vertical Slice)**：`Business Feature` 應交付完整的業務價值（從邏輯到介面）。將兩者整合開發，符合端到端交付的精神。

---

## 3. 實作開發流程詳解

### FEATURE_1: 定義市場數據標準契約 (Library Feature)

- **類型**：Library Feature (Technical Value)
- **目的**：確立系統間溝通的標準語言，定義「什麼是股價資料」。
- **Branch**: `feature/core/market/define-market-contracts`

*(註：此處假設 `market` 為 core 中的一個領域分類 toolkit)*

#### Task 1.1: 定義數據模型與介面

- **FU (Functional Unit)**: `MarketContract`
- **對應檔案**:
    - `core/schemas/market.py`: 使用 Pydantic 定義 `StockPriceDTO`，規範標準欄位與精確度。
    - `core/interfaces/market.py`: 定義抽象基類 `IStockPriceProvider`。
    - `core/exceptions.py`: 定義標準異常類別。
- **實作重點**: 純定義，無邏輯實作。

---

### FEATURE_2: TEJ 股價資料源服務 (Data Source Feature)

- **類型**：Data Source Feature (Business Value - Data)
- **目的**：建立適配器，將 TEJ 原始數據轉換為標準格式。
- **Branch**: `feature/tej/market/stock-price-adapter`

#### Task 2.1: 實作資料收集器 (Collector)

- **FU**: `TejCollector`
- **對應檔案**: `tej/collector/db_client.py`, `tej/collector/schema.py`。
- **實作重點**: 執行 Raw SQL 獲取髒資料，採用探索式驗證 (Exploratory Validation)。

#### Task 2.2: 實作服務適配器 (Service)

- **FU**: `TejProviderService`
- **對應檔案**: `tej/service/provider.py`
- **實作重點**: 實作 `IStockPriceProvider`，負責將髒資料轉換為 `StockPriceDTO`。

---

### 補充範例：資料源系統的 System Core Feature (Library Feature)

在實際開發中，資料源系統若有多個 Feature 共用的基礎能力（如欄位對應工具、HTTP 客戶端封裝、解析器等），應優先規劃為 `<system>/core` 中的 Library Feature，而非散落在各 Feature 的私有目錄中。

以下是幾個 TEJ 資料源系統中可能出現的 System Core Feature 範例：

| Feature 名稱 | Branch | 說明 |
|:-------------|:-------|:-----|
| `legacy-column-map` | `feature/tej/core/mapping/legacy-column-map` | 封裝 TEJ 舊欄位名稱的對應邏輯，供 collector / service 共用 |
| `normalize-price-fields` | `feature/tej/core/parser/normalize-price-fields` | 標準化價格欄位的解析與轉換工具 |
| `db-access-policy` | `feature/tej/core/db/access-policy` | 封裝 TEJ 資料庫連線與存取策略 |

> **關鍵理解**：資料源系統的 `<system>/core` 不是抽象口號，而是可以實際被當成 Feature / Use Case / Specs 的承載位置。其路徑規則遵循方法論中的 Library Feature 路徑格式：`docs/use-cases/<system>/core/<toolkit>/<feature_name>/`。

---

### FEATURE_3: GMS 股價資料存取層 (Technical Feature)

- **類型**：Business Feature (Technical Value - DB Only)
- **目的**：建立 GMS 系統內部的資料落地能力。
- **Branch**: `feature/gms/market/stock/create-price-repository`

#### Task 3.1: 建立 Repository 與 Model

- **FU**: `StockPriceRepo`
- **Container**: `gms/db/market/stock/price/`
- **對應檔案**: `_stock_price_storage/_models.py`, `_stock_price_storage/_interfaces.py`, `_stock_price_storage/_repository.py`。
- **實作重點**:
    - 嚴格遵循 DIP，透過 `__init__.py` 僅暴露介面與 Repository。
    - 跨公開邊界的依賴使用正式絕對 import，邊界內部使用相對 import。

---

### FEATURE_4: GMS 應用程式基礎建設 (Technical Feature)

**(必選 - 專案初始化階段需執行一次)**

- **類型**：Business Feature (Technical Value - Infrastructure)
- **目的**：建立系統的 Composition Root (組裝根)，確保應用程式可以啟動、讀取設定並連接資料庫。這是「會走路的骨架」。
- **Branch**: `feature/gms/core/init-app-skeleton`

#### Task 4.1: 建立系統組裝根 (Composition Root)

- **FU**: `GmsApp`
- **Container**: `gms/` (Root level)
- **對應檔案**:
    - `gms/config.py`: 定義 `Settings` 類別，讀取環境變數 (如 `DATABASE_URL`)。
    - `gms/api/dependencies.py`: 建立基礎依賴注入工廠 (初始階段至少需包含 `get_db_session`)。
    - `gms/main.py`:
        1. 初始化 `FastAPI` 實例。
        2. 設定 `lifespan` 以管理 DB 連線池的啟動與關閉。
        3. 提供基礎 Endpoint (如 `/health`) 以驗證服務狀態。
- **實作重點**:
    - 此階段尚未註冊任何業務 Router。
    - 目標是 `uvicorn gms.main:app` 能成功啟動且無錯誤。

---

### FEATURE_5: GMS 每日股價同步作業 (Data Pipeline Feature)

- **類型**：Data Pipeline Feature (Business Value - Data Freshness)
- **目的**：打通資料流，將 FEATURE_2 (Source) 搬運至 FEATURE_3 (Target)。
- **Branch**: `feature/gms/etl/market/stock/daily-sync-job`

#### Task 5.1: 實作同步 Pipeline

- **FU**: `DailyStockSyncJob`
- **Container**: `gms/etl/market/stock/sync_job/`
- **對應檔案**: `_daily_sync_job/_pipeline.py`, `_daily_sync_job/_loader.py`。
- **實作重點**:
    - 透過正式絕對 import 取得 Source 介面（`core.interfaces`）與 Target 介面（`gms.db` 公開容器）。
    - 實作 Extract -> Transform -> Load 流程。

#### Task 5.2: 更新系統組裝 (Register ETL Trigger)

**(可選 - 視觸發需求而定)**

- **FU**: `GmsApp` (Modification)
- **對應檔案**: `gms/main.py`
- **實作重點**:
    - 僅在「需要透過 API 手動觸發 ETL」時執行。若專案僅依賴排程器 (Scheduler) 或 CLI 工具觸發，則可跳過此步驟。
    - 在 `main.py` 中新增一個 Admin Endpoint (例如 `POST /admin/etl/sync-prices`)。
    - 在此 Endpoint 內手動實例化 `TejProvider` 與 `GmsRepository`，並組裝 `DailyStockSyncJob`。

---

### FEATURE_6: GMS 股價查詢服務 (Business Feature)

- **類型**：Business Feature (Business Value - End User Functionality)
- **目的**：提供使用者查詢與分析股價的能力。此階段將業務邏輯掛載到 FEATURE_4 建立的骨架上。
- **Branch**: `feature/gms/market/stock/stock-analysis-api`

#### Task 6.1: 實作分析業務邏輯 (Service Layer)

- **FU**: `StockAnalysisService`
- **Container**: `gms/service/market/stock/analysis/`
- **對應檔案**: `_stock_analysis_api/_service.py`, `_stock_analysis_api/_dto.py`。
- **實作重點**: 透過介面實作純粹的業務邏輯，不觸碰 HTTP。

#### Task 6.2: 實作 API 介面 (API Layer)

- **FU**: `StockAnalysisApi`
- **Container**: `gms/api/market/stock/`
- **對應檔案**: `_stock_analysis_api/_router.py`, `_stock_analysis_api/_schemas.py`。
- **實作重點**: 定義 Endpoint 並使用 FastAPI `Depends` 注入 Service。

#### Task 6.3: 更新系統組裝 (Register API Router)

**(必要 - 每次新增 API 或依賴時需執行)**

- **FU**: `GmsApp` (Modification)
- **對應檔案**: `gms/main.py`, `gms/api/dependencies.py`。
- **實作重點**:
    1. **修改 `dependencies.py`**：新增此 Feature 所需的工廠方法 (如 `get_analysis_service`)，將 `Repository` 實例組裝進 `Service`。
    2. **修改 `main.py`**：匯入 Task 6.2 建立的 Router，並使用 `app.include_router()` 將其註冊到系統中。
