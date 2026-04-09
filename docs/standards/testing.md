# wBiSaProj 測試規範 (Testing Standards)

## 1. 測試框架與環境

### 1.1 核心框架

本專案統一採用 **Pytest** 配合 **pytest-asyncio** 作為測試框架。

- **Pytest**: 提供簡潔的語法與強大的擴充性。
- **pytest-asyncio**: 提供對 `async/await` 非同步測試的完整支援。

### 1.2 非同步測試規範 (Async Testing)

由於本專案核心 (FastAPI, SQLAlchemy Async) 均為非同步架構，測試程式碼必須遵循以下規範：

- **全面非同步**：涉及 I/O (DB, API) 的測試函數必須定義為 `async def`。
- **自動模式**：專案已配置 `asyncio_mode = auto`，無需手動添加裝飾器。
- **等待執行**：所有非同步呼叫必須使用 `await`。

```python
# ✅ 正確：非同步測試定義
import pytest

@pytest.mark.asyncio  # 在 auto 模式下可省略，但標註可增加可讀性
async def test_async_operation():
    result = await some_async_function()
    assert result is True
```

### 1.3 測試標記 (Markers) 規範

所有測試必須根據性質標註正確的 Marker，以利 CI/CD 流程精準執行。標記定義必須與 `pytest.ini` 保持嚴格一致：

| Marker | 用途 | 適用場景 |
| :--- | :--- | :--- |
| `@pytest.mark.unit` | 單元測試 | 執行速度快、無外部 I/O、邏輯驗證 |
| `@pytest.mark.integration` | 整合測試 | 元件互動、使用 In-Memory DB |
| `@pytest.mark.e2e` | 端到端測試 | 完整流程、真實外部連線 |
| `@pytest.mark.slow` | 慢速測試 | 執行時間 > 1秒 |
| `@pytest.mark.fast` | 快速測試 | 執行時間極短的測試 |
| `@pytest.mark.database` | 資料庫測試 | 需要 DB Session 的測試 |
| `@pytest.mark.network` | 網路測試 | 需要外部網路連線 (如爬蟲) |
| `@pytest.mark.external` | 外部依賴測試 | 依賴外部服務 (如 TEJ, 第三方 API, 資料源系統) |
| `@pytest.mark.io` | I/O 測試 | 檔案讀寫、序列化操作 (如 pickle-io) |
| `@pytest.mark.auth` | 認證測試 | 登入、權限驗證相關 |
| `@pytest.mark.api` | API 測試 | 針對 Router Endpoint 的測試 |

---

## 2. 檔案組織規範

### 2.1 結構對應性原則 [CRITICAL]

測試目錄結構必須嚴格遵循《架構篇》所定義的 **「結構對應性原則 (Structural Correspondence Principle)」**。對於每一個 FU，規格、測試與實作的對應關係如下：

- **規格**：`docs/specs/<fu_path>/<fu_name>/...`
- **測試**：`tests/<fu_path>/<fu_name>/...`
- **實作**：`<fu_path>/_<feature_snake_name>/...`

其中，測試的導航主體為 **FU（功能單元）** 與 **FU Container**，而非 private python file。測試路徑以 `<fu_name>` 作為目錄級定位依據，確保從邏輯單元到其驗證程式碼的直接可追溯性。

### 2.2 測試路徑不得深入到 private python file [CRITICAL]

測試結構的主要導航層級應停留在 FU Container 與 FU。測試目錄**不應**鏡射到 private implementation file。

> `tests/<fu_path>/_<feature_name>/test_impl_file.py` **不是**本專案推薦模式。

此原則與 import 規範一致：公開入口由 `__init__.py` 定義，外部與一般模組不得穿透 private path；真正穩定的存取點是 package / FU Container，不是 private python file。因此，測試文件也應反映相同哲學。

### 2.3 範例結構

#### 範例 A：Library 型 FU

- **FU Container**：`testlib/text/normalize`
- **Feature 私有目錄**：`testlib/text/normalize/_string_cleanup/`
- **實作檔案**：`_normalizer.py`, `_rules.py`

```text
testlib/
└── text/
    └── normalize/                      # FU Container
        ├── __init__.py                 # 公開介面
        └── _string_cleanup/            # Feature 私有目錄
            ├── _normalizer.py
            └── _rules.py

tests/
└── testlib/
    └── text/
        └── normalize/                  # 對應 FU Container
            └── string_cleanup/         # <fu_name>
                ├── __init__.py
                ├── test_string_cleanup.py
                ├── test_text_normalizer__basic_cases.py
                └── test_text_normalizer__edge_cases.py
```

**說明**：測試目錄對應的是 `FU Container + FU 名稱`（`normalize/string_cleanup/`），而非鏡射到 `_string_cleanup/_normalizer.py`。同一個 FU 可依需要拆成多個小測試檔，利於 LLM 協作與維護。

#### 範例 B：業務系統 FU

- **FU Container**：`sampleapp/db/catalog/product`
- **Feature 私有目錄**：`sampleapp/db/catalog/product/_product_inventory/`

```text
sampleapp/
└── db/
    └── catalog/
        └── product/                    # FU Container
            ├── __init__.py
            ├── _imports.py
            └── _product_inventory/     # Feature 私有目錄
                ├── _schemas.py
                ├── _models.py
                └── _repository.py

tests/
└── sampleapp/
    └── db/
        └── catalog/
            └── product/               # 對應 FU Container
                └── inventory/          # <fu_name>
                    ├── __init__.py
                    ├── test_inventory.py
                    └── test_inventory__error_handling.py
```

**說明**：測試導航主體為 FU 名稱 `inventory`，而非 private file `_repository.py` 或 `_schemas.py`。

---

## 2.4 測試檔命名規範

### 2.4.1 命名主體的優先順序

測試檔命名的主體，依下列優先順序選擇：

1. **單一公開元件名稱**（如 `__init__.py` 匯出的 class 或 function）
2. **FU 名稱**
3. **公開能力 / 公開行為名稱**

**格式規則**：若主體來源為公開 class 名稱，測試檔名中的 `<public_component>` 應使用其 `snake_case` 形式。例如 `StockProfileRepository` → `test_stock_profile_repository.py`。

**禁止事項**：不得預設以下列名稱作為主要導航主體：private python file 名稱、internal-only component 名稱、單純描述 implementation 細節但不具公開意義的名稱。此方向與「公開入口由 `__init__.py` 定義、一般模組不得穿透 private path」相一致。

### 2.4.2 單檔命名規則

若某 FU 目前僅有一個主要測試檔，使用 `test_<fu_name>.py` 或 `test_<public_component>.py`。

```text
test_string_cleanup.py
test_text_normalizer.py
```

### 2.4.3 多檔拆分命名規則

當同一 FU 的測試需要拆分時，使用 `test_<subject>__<aspect>.py`：

- `subject`：此測試檔主要驗證的公開主體（公開元件名稱或 FU 名稱）
- `aspect`：此測試檔負責的驗證切片

```text
test_text_normalizer__basic_cases.py
test_text_normalizer__unicode_cases.py
test_string_cleanup__error_handling.py
test_string_cleanup__edge_cases.py
```

### 2.4.4 internal-only component 的預設處理

FU 內部共用但未被提升為正式公開能力的 component，預設不作為獨立測試主體；其正確性應主要透過所屬公開元件或整個 FU 的對外行為進行驗證。

若某個內部 helper、builder、mapper 仍未被提升為正式共用結構，通常表示它在架構上仍屬於某個較大功能的一部分；此時測試應優先驗證整體行為，而不是把該 internal 名稱提升為測試導航主角。

### 2.4.5 允許的例外

若某 internal-only component 的演算法、規則或邊界條件極複雜，且透過公開入口驗證會造成測試失焦，則可為其安排更細的測試切片；但測試檔名仍應優先反映公開主體或 FU 能力，而非直接反映 private file 名稱。

**不建議**：

```text
test_query_builder.py
```

**建議**：

```text
test_order_query_service__query_composition.py
test_string_cleanup__rule_composition.py
```

---

## 2.5 LLM 協作導向的測試拆分原則

為配合本專案的人機協作模式，測試檔應維持適中的責任範圍。當單一 FU 的測試內容過大時，應優先採用 `test_<subject>__<aspect>.py` 的方式拆分，而非將所有案例集中於單一巨型檔案中。

拆分的目的包含：提升人類可讀性、降低 LLM 單次理解負擔、讓責任邊界更清楚。測試檔不應無限制膨脹成單一巨型檔案。

---

## 2.6 Test Module Plan 要求

每個 FU 的 `docs/specs/<fu_path>/<fu_name>/tests.md` 不僅需列出測試案例，也**必須**包含一個 **Test Module Plan**，明確列出預計存在的測試模組與命名理由。

**建議格式**：

```markdown
## Test Module Plan

| File | Subject | Aspect | Purpose |
|------|---------|--------|---------|
| test_string_cleanup.py | string_cleanup | overall | 驗證整體清理能力的主要行為 |
| test_text_normalizer__basic_cases.py | text_normalizer | basic_cases | 驗證一般輸入情境 |
| test_text_normalizer__unicode_cases.py | text_normalizer | unicode_cases | 驗證 Unicode 與特殊字元情境 |
```

此 Plan 說明了測試模組的切分方式與命名依據，確保測試與規格、實作之間的直接可追溯性。

---

## 3. 雙軌測試策略

根據 **[方法論篇](PROJECT_DESIGN-METHODOLOGY.md)**，開發過程依據任務性質採用不同的測試策略。

### 3.1 標準 TDD (Standard TDD)

- **適用對象**：Library, DB Layer, Service Layer, Internal Logic。
- **特徵**：邏輯可控、輸入輸出明確。
- **流程**：先寫測試 (Red) → 實作 (Green) → 重構 (Refactor)。
- **要求**：必須覆蓋所有核心邏輯與邊界條件。

### 3.2 探索式驗證 (Exploratory Validation)

- **適用對象**：Collector (爬蟲), Extractor (外部 API), Job (端到端)。
- **特徵**：外部資料結構未知或不穩定。
- **流程**：撰寫探索腳本 → 分析回傳資料 → 定義驗證規則 → 轉化為測試案例。
- **要求**：重點在於驗證資料格式的相容性與錯誤處理機制。

---

## 4. 各類型 FU 測試規範與範例

不同架構層級的 FU 具有不同的職責與依賴，因此需要不同的測試手段。

### 4.1 Type I: Library FU (純邏輯)

- **特徵**：無外部依賴，純粹的輸入輸出函數或類別。
- **測試策略**：標準單元測試。
- **依賴處理**：無須 Mock。

**範例 (FU Container: core/utils/time)**：

```python
import pytest
from datetime import datetime
from core.utils.time import to_taipei_time

@pytest.mark.unit
def test_to_taipei_time_conversion():
    # Arrange
    utc_time = datetime(2024, 1, 1, 0, 0, 0)

    # Act
    tw_time = to_taipei_time(utc_time)

    # Assert
    assert tw_time.hour == 8
    assert tw_time.tzinfo is not None
```

### 4.2 Type II: DB Layer FU (Repository)

- **特徵**：負責資料庫 CRUD，依賴 SQLAlchemy Session。
- **測試策略**：**整合測試**。
- **依賴處理**：
    - **禁止 Mock 資料庫**：Mock SQL 行為沒有意義且容易出錯。
    - **使用 SQLite In-Memory**：使用 `sqlite_session` fixture 進行快速、隔離的真實 DB 操作。
- **標記**：`@pytest.mark.database`, `@pytest.mark.integration`

**範例 (FU Container: gms/db/market/stock/price)**：

```python
import pytest
from datetime import date
from decimal import Decimal
from gms.db.market.stock.price import StockPriceRepository, StockPriceModel

@pytest.mark.database
@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_get_price(sqlite_session):
    # Arrange: 使用共用的 sqlite_session fixture
    repo = StockPriceRepository(sqlite_session)
    price_data = StockPriceModel(
        symbol="2330",
        trade_date=date(2024, 1, 1),
        close_price=Decimal("500")
    )

    # Act
    sqlite_session.add(price_data)
    await sqlite_session.commit()

    result = await repo.get_by_symbol_date("2330", date(2024, 1, 1))

    # Assert
    assert result is not None
    assert result.close_price == Decimal("500")
```

### 4.3 Type III: Service Layer FU (Business Logic)

- **特徵**：實作純業務邏輯，依賴 Repository 介面。
- **測試策略**：**標準單元測試**。
- **依賴處理**：
    - **必須 Mock Repository**：Service 測試不應受限於 DB 狀態。
    - **依賴注入**：透過構造函數注入 Mock 物件。
- **標記**：`@pytest.mark.unit`

**範例 (FU Container: gms/service/market/analysis)**：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from gms.service.market.analysis import StockAnalysisService
from gms.db.market.stock.price import IStockPriceRepository

@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_abnormal_volume():
    # Arrange: Mock Repository 介面
    mock_repo = MagicMock(spec=IStockPriceRepository)
    # 設定非同步回傳值
    mock_repo.get_by_symbol_date = AsyncMock(return_value=MagicMock(volume=1000))
    mock_repo.get_avg_volume = AsyncMock(return_value=100) # 平均量 100

    service = StockAnalysisService(repo=mock_repo)

    # Act
    result = await service.check_abnormal("2330", "2024-01-01")

    # Assert: 驗證邏輯 (1000 > 100 * 2 -> Abnormal)
    assert result.is_abnormal is True
    # 驗證 Service 是否正確呼叫了 Repository
    mock_repo.get_by_symbol_date.assert_called_once()
```

### 4.4 Type IV: API Layer FU (Router)

- **特徵**：處理 HTTP 請求、參數驗證、狀態碼。
- **測試策略**：**單元測試** (針對 Router 邏輯)。
- **依賴處理**：
    - **Mock Service**：隔離業務邏輯，專注測試 API 行為。
    - **使用 Dependency Overrides**：FastAPI 特有的測試機制。
- **標記**：`@pytest.mark.api`, `@pytest.mark.unit`

**範例 (FU Container: gms/api/market/stock)**：

```python
import pytest
from httpx import AsyncClient, ASGITransport
from gms.main import app
from gms.api.dependencies import get_analysis_service

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_volume_analysis_endpoint():
    # Arrange: Mock Service
    mock_service = AsyncMock()
    mock_service.check_abnormal.return_value = {"status": "ok"}

    # 使用 dependency_overrides 替換真實 Service
    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act
        response = await client.get("/api/v1/market/analysis/2330")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    # 清理
    app.dependency_overrides = {}
```

### 4.5 Type V: Data Source / ETL (Integration)

- **特徵**：與外部互動或執行長時間任務。
- **測試策略**：**整合測試** 或 **探索式驗證**。
- **依賴處理**：視情況使用真實連線 (需標記 `@external`) 或 VCR (錄製回應)。
- **標記**：`@pytest.mark.external`, `@pytest.mark.slow`

---

## 5. 通用最佳實踐

### 5.1 斷言與異常

- 統一使用 Python 標準 `assert`。
- 測試異常時務必使用 `pytest.raises` 並驗證錯誤訊息，確保捕捉到正確的錯誤。

```python
with pytest.raises(ValueError, match="Invalid symbol"):
    validate_symbol("INVALID")
```

### 5.2 Fixtures 使用原則

- **共用 Fixtures**：通用的 DB Session, API Client 應定義在根目錄或模組層級的 `conftest.py` 中，避免重複程式碼。
- **Scope 管理**：
    - `function` (預設)：每個測試獨立 (推薦用於 DB 測試以確保隔離)。
    - `session`：整個測試過程只執行一次 (用於建立 expensive resources)。

### 5.3 導入規範

- **禁止區域導入**：嚴禁在測試函數內部進行 `import`。所有依賴必須在檔案頂部導入。
- **TDD 導入**：在 TDD 的 Red 階段，頂部導入不存在的模組導致測試報錯是預期行為，不應為了避開 ImportError 而改變導入位置。

### 5.4 跨平台測試規範 (Cross-Platform Testing)

本專案的測試必須能在 Windows、macOS、Linux 上一致執行。

#### 5.4.1 路徑處理

- **禁止硬編碼絕對路徑**：嚴禁使用 `/root/`、`/tmp/`、`C:\` 等平台特定路徑。
- **統一使用 `tmp_path`**：所有需要檔案路徑的測試必須使用 Pytest 內建的 `tmp_path` fixture。

```python
# ❌ 錯誤：硬編碼 Unix 路徑，Windows 上會失敗
def test_permission_error():
    with patch("builtins.open", side_effect=PermissionError):
        pickle_dump(data, "/root/protected.pkl")  # FileNotFoundError on Windows!

# ✅ 正確：使用 tmp_path 確保跨平台相容
def test_permission_error(tmp_path: Path):
    protected_path = tmp_path / "protected.pkl"
    with patch("builtins.open", side_effect=PermissionError):
        pickle_dump(data, protected_path)
```

#### 5.4.2 路徑型別

- 測試時應同時驗證 `pathlib.Path` 與 `str` 兩種路徑型別的相容性。
- 使用 `pathlib.Path` 進行路徑操作，避免手動字串拼接。

### 5.5 Mock 策略規範 (Mocking Strategy)

#### 5.5.1 Mock 攔截點選擇 [CRITICAL]

Mock 必須攔截 **被測模組實際使用的進入點**，而非假設的進入點。

**常見陷阱：檔案 I/O Mock**

Python 開啟檔案有兩種常見方式，Mock 時必須考慮實作可能使用的方式：

| 實作方式 | 需要 Mock 的目標 |
| :--- | :--- |
| `open(path, mode)` | `builtins.open` |
| `Path(path).open(mode)` | `pathlib.Path.open` |

**建議做法**：同時 Mock 兩個進入點以確保攔截成功。

```python
# ✅ 正確：同時攔截兩種可能的實作方式
from pathlib import Path
from unittest.mock import patch

def test_permission_error(tmp_path: Path):
    protected_path = tmp_path / "protected.pkl"

    with (
        patch("builtins.open", side_effect=PermissionError("Access denied")),
        patch.object(Path, "open", side_effect=PermissionError("Access denied")),
    ):
        with pytest.raises(PermissionError):
            pickle_dump(data, protected_path)
```

#### 5.5.2 Mock 位置原則

Mock 應該 patch **被測模組中的名稱**，而非原始定義處：

```python
# 假設 mymodule.py 中有: from os.path import exists

# ❌ 錯誤：Mock 原始定義處
with patch("os.path.exists", return_value=False):
    ...

# ✅ 正確：Mock 被測模組中的引用
with patch("mymodule.exists", return_value=False):
    ...
```

#### 5.5.3 何時使用 Mock

| 場景 | Mock 策略 |
| :--- | :--- |
| 模擬異常 (權限、網路錯誤) | ✅ 使用 Mock |
| 驗證呼叫參數 (如 open mode) | ✅ 使用 Mock |
| 驗證實際 I/O 結果 | ❌ 使用 `tmp_path` 真實操作 |
| DB 操作 | ❌ 使用 `sqlite_session` |

### 5.6 測試類別

- 測試類別**不需要**繼承任何基礎類別。
- 類別名稱應以 `Test` 開頭。

```python
class TestStockPricing:
    async def test_price_calculation(self):
        ...
```

---

## 6. 品質保證與自我檢查 (Quality Assurance & Self-Check)

在提交 Pull Request (PR) 之前，請務必對照以下清單進行自我審查。本專案強調「品質內建」，測試程式碼的品質直接影響系統的穩定性與可維護性。

### 6.1 自動化檢查 (Automated Checks)

- [ ] **測試通過**: 已執行 `pytest` 並確認所有測試皆通過 (Green Light)。
- [ ] **風格合規**: 測試程式碼本身已通過 `inv style` (Black/Ruff) 檢查。
- [ ] **Async 檢查**: 確認執行過程中無 `RuntimeWarning: coroutine ... was never awaited` 警告。

### 6.2 架構合規性檢查 (Architectural Compliance) [CRITICAL]

- [ ] **路徑對應性**: 測試檔案路徑是否遵循 `tests/<fu_path>/<fu_name>/...` 的 FU 級目錄結構？
- [ ] **私有路徑隔離**: 測試目錄是否避免鏡射 private implementation file（如 `_<feature_name>/`）？
- [ ] **命名合規性**: 測試檔名是否以公開主體或 FU 名稱為導航主體，而非 private file 名稱？
- [ ] **跨平台相容性**:
    - [ ] 是否使用 `tmp_path` 而非硬編碼路徑 (`/root/`, `/tmp/`, `C:\`)？
    - [ ] Mock 檔案 I/O 時是否同時考慮 `builtins.open` 與 `Path.open`？
- [ ] **隔離性 (Isolation)**:
    - [ ] **DB Layer**: 是否使用 `sqlite_session` fixture 而非連線真實/開發資料庫？
    - [ ] **Service Layer**: 是否 Mock 了 Repository 層？確認沒有真實的 DB 操作。
    - [ ] **API Layer**: 是否 Mock 了 Service 層？確認 API 測試不依賴業務邏輯的實作細節。
- [ ] **雙軌策略**:
    - [ ] 對於 Collector/Extractor (外部資料源)，是否採用「探索式驗證」思路而非僅 Mock 快樂路徑？

### 6.3 實作細節檢查 (Implementation Details)

- [ ] **Markers 標記**: 是否已根據測試性質加上正確的 `@pytest.mark.xxx` (如 `unit`, `integration`, `asyncio`)？
- [ ] **頂層導入**: 確認沒有在測試函數內部進行 `import` (除了解決循環依賴的極少數特例外)。
- [ ] **斷言使用**: 是否使用標準 `assert` 語句？
- [ ] **非同步語法**: 涉及 I/O 的測試是否定義為 `async def` 並正確使用 `await`？
