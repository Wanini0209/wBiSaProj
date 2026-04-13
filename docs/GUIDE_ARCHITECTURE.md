# wBiSaProj 架構實作指引

本文件提供 wBiSaProj 專案**架構設計**的實作建議與範例，作為開發團隊的技術參考指南。

## 1. 核心依賴管理：統一 Import 原則

本章節說明專案中用以管理依賴、確保模組封裝的核心組織模式。所有模組類型（Library、Data Source、Business System）遵循同一套統一 import 原則。

### 1.1 統一 Import 原則概述

本專案的依賴管理建立在三條統一原則之上，不因模組類型不同而另設機制：

| 情境 | 做法 | 說明 |
|:-----|:-----|:-----|
| **跨公開邊界** | 絕對 import | 從正式公開容器的 `__init__.py` 導入 |
| **邊界內部** | 相對 import | 同一公開容器內的私有模組間互相引用 |
| **依賴需要整理** | Facade-like private modules | 以具語義的私有模組集中整理依賴路徑 |

#### 核心檔案職責

`__init__.py` 是 FU Container 的唯一公開入口，定義了容器的對外存取邊界：

| 檔案 | 職責 | 規範 |
|:-----|:-----|:-----|
| `__init__.py` | 定義該容器的**公開介面 (Public API)**；亦可承擔 metadata 與輕量初始化 | 當承擔公開匯出角色時，**必須**定義 `__all__`；僅含 docstring / metadata / 輕量初始化時可省略。 |

#### `__all__` 規範

`__init__.py` 承擔公開匯出角色時，必須定義 `__all__`。

```python
# __init__.py - 定義公開介面
__all__ = ['UserProfile', 'UserProfileRepository']
```

-----

### 1.2 層級私有共用模組的角色

#### 設計理念

在業務系統的多層級結構中，各層級（Layer / Domain / Sub-domain）可能存在層級內共用的私有元件。這些元件具有以下特性：

- **非系統級共用**：不適用於整個系統（否則應放在 `<system>/core`）
- **層級內共用**：在特定層級（Layer）或領域（Domain）內部被廣泛共用
- **私有實作**：這些模組以底線前綴命名（如 `_orm/`、`_rules.py`），對外部層級完全不可見

#### 層級應用

層級私有共用模組可存在於各個需要內部共用元件的層級，並以具語義的名稱命名：

```text
[system]/
├── [layer]/
│   ├── _orm/               # Layer 層級共用（如 db/_orm/）
│   └── [domain]/
│       ├── _rules.py       # Domain 層級共用（如 market/_rules.py）
│       └── [subdomain]/
│           ├── _validators.py  # Sub-domain 層級共用
│           └── [fu-container]/
│               └── ...     # FU 內部元件
```

#### 封裝邊界與使用頻率

層級私有共用模組在不同層級的使用頻率與必要性各有不同：

| 層級 | 使用頻率 | 說明 |
|:-----|:---------|:-----|
| **Layer** | 幾乎必然存在 | 如 `db/_orm/` 提供整個 DB 層的 ORM 基礎元件 |
| **Domain / Sub-domain** | 經常存在 | 如 `market/_rules.py` 提供領域特有的共用規則 |
| **FU Container** | 較為少見 | FU Container 本身已可建立各種私有實作檔案 |

**關鍵理解**：

- 層級私有共用模組應以具語義的名稱命名（如 `_orm/`、`_rules.py`、`_validators.py`），而非使用泛用名稱
- FU Container 層級較少需要額外的私有共用模組，因為 FU Container 本身就可以建立各種私有實作檔案（如 `_models.py`、`_utils.py`）
- **可見範圍**：這些私有共用模組僅對其所屬層級及子層級可見，對外部層級完全封閉

-----

### 1.3 使用原則

#### 原則一：封裝邊界與 Import 方向

所有模組類型遵循同一套封裝規則：

- **實作檔案**（如 `_models.py`、`_repository.py`）：
    - 位於 Feature 級私有目錄內，**嚴禁**被外部直接導入
    - 跨公開邊界的依賴，使用正式絕對 import 從目標公開容器的 `__init__.py` 取得
    - 同一 Feature 私有目錄內的檔案間互相引用，使用相對 import

- **`__init__.py`**：
    - 是公開容器的唯一公開入口
    - 可向內導入多層 private path 以組裝公開介面（參見 §4.4 邊界檔定位）

```python
# === 在 _stock_profile/_repository.py (Feature 級私有目錄內的實作檔案) 中 ===

# ✅ 正確：跨公開邊界，使用正式絕對 import
from gms.core.exceptions import DomainException
from gms.db.market.stock.profile import StockProfileSchema

# ✅ 正確：從同一 Feature 私有目錄內的其他檔案導入
from ._models import StockProfileModel

# ✅ 正確：專案級函式庫與第三方套件，直接絕對導入
from core.constants import Language
from sqlalchemy import select

# ❌ 錯誤：實作檔案嚴禁被外部以絕對路徑穿透導入
# from gms.service.market._stock_profile._service import StockService  # 禁止！
```

#### 原則二：Facade-like Private Modules

當某個模組或 FU Container 的依賴較為複雜，直接在每個實作檔案中重複書寫多條絕對 import 會造成維護負擔時，可使用具語義的 facade-like private modules 集中整理依賴。

**關鍵原則**：

- Facade 是**可選的整理手段**，不是強制的制度性要求
- 應以職責命名（`_repositories.py`、`_contracts.py`），不使用泛用名稱
- 一個容器可以有多個 facade-like modules，按職責拆分
- 當依賴關係足夠簡單時，直接使用絕對 import 即可，無需額外建立 facade

```python
# _contracts.py — facade-like private module，整理跨邊界的介面依賴
from gms.core.exceptions import DomainException, ValidationError
from gms.core.interfaces import IStockPriceProvider
from gms.db.market.stock.profile import (
    StockProfileRepository,
    IStockProfileRepository,
)
```

```python
# _stock_analysis/_service.py — 實作檔案從 facade 取得已整理的依賴
from .._contracts import (
    IStockProfileRepository,
    DomainException,
)
```

#### 原則三：防止循環依賴

- **`__init__.py`**：嚴禁從 Feature 級私有目錄的實作檔案中導入再 re-export（會導致循環）
- **Facade-like modules**：應只向外（跨公開邊界）或向上（父層私有共用模組）查找依賴，嚴禁向內導入同層的 Feature 私有實作
- **層級私有共用模組**（如 `_orm/`、`_rules.py`）：僅對子層級可見，不被同層的其他模組直接導入

```python
# === 在 facade-like module 中 ===

# ✅ 正確：向外查找依賴
from gms.core.exceptions import DomainException
from gms.db.market.stock.profile import StockProfileRepository

# ✅ 正確：從父層私有共用模組導入
from .._orm.base import Base, BaseRepository

# ❌ 錯誤：嚴禁導入同層 Feature 私有目錄內的實作檔案
from ._stock_profile._models import StockProfileModel
```

-----

### 1.4 Business Backbone 實務範例

以下範例展示 Business System 的各層級如何在統一 import 原則下管理依賴。

#### 1.4.1 DB 層 FU Container 的實作檔案

實作檔案直接使用絕對 import 取得所需的外部依賴，使用相對 import 取得同 Feature 目錄內的協作檔案。

```python
# gms/db/market/stock/profile/_stock_profile/_models.py
"""Stock Profile FU 的 ORM 模型定義"""

# 第三方套件：直接絕對導入
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date

# 父層私有共用模組：相對 import
from ..._orm.base import Base
from ..._orm.mixins import TimestampMixin

class StockProfile(Base, TimestampMixin):
    """股票基本資料模型."""
    __tablename__ = "stock_profiles"
    symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
```

#### 1.4.2 Service 層依賴 DB 層

Service 層跨公開邊界取用 DB 層的公開介面，使用正式絕對 import。

```python
# gms/service/market/stock/analysis/_stock_analysis/_service.py
"""Stock Analysis Service 實作"""

# 跨公開邊界：正式絕對 import
from gms.db.market.stock.profile import (
    IStockProfileRepository,
    StockProfileSchema,
)
from gms.core.exceptions import DomainException

class StockAnalysisService:
    """股票分析服務."""

    def __init__(self, repo: IStockProfileRepository) -> None:
        self._repo = repo

    def get_analysis(self, symbol: str) -> StockProfileSchema:
        """Retrieve and analyze stock profile."""
        profile = self._repo.find_by_symbol(symbol)
        if not profile:
            raise DomainException(f"Stock {symbol} not found")
        return profile
```

#### 1.4.3 使用 Facade 整理複雜依賴

當 FU Container 需要從多個外部來源取得依賴，且多個實作檔案都需要同一組依賴時，可建立 facade-like private module 集中整理。

```text
gms/service/market/stock/analysis/
├── __init__.py
├── _contracts.py              # Facade：整理跨邊界的介面依賴
└── _stock_analysis/
    ├── _service.py
    └── _dto.py
```

```python
# _contracts.py — 集中整理本 FU Container 的外部依賴
from gms.db.market.stock.profile import (
    IStockProfileRepository,
    StockProfileSchema,
)
from gms.db.market.stock.trading_data import (
    IStockTradingDataRepository,
    StockTradingDataSchema,
)
from gms.core.exceptions import DomainException, ValidationError
```

```python
# _stock_analysis/_service.py — 從 facade 取得已整理的依賴
from .._contracts import (
    IStockProfileRepository,
    IStockTradingDataRepository,
    DomainException,
)
```

**關鍵理解**：

- 實作檔案（`_service.py`）不需要知道各個 Repository 的實際來源路徑
- 當 DB 層的公開容器路徑變更時，只需修改 `_contracts.py` 一處
- 但如果 FU Container 只有少量依賴，直接在實作檔案中絕對 import 即可，不必強制建立 facade


-----

## 2. 核心契約定義：Core Layer 實作

本章節定義專案的契約中心，展示如何建立標準化的資料模型與抽象介面，實現系統間的清晰溝通。

### 2.1 設計理念：契約優先開發

Core Layer 是整個 Workspace 的「法律中心」，定義了系統間溝通的標準語言。它回答兩個關鍵問題：

- **什麼**：標準化的資料結構（Schemas/DTO）
- **如何**：抽象的行為契約（Interfaces）

#### 架構定位

`core` 套件作為純粹的契約層，具有以下特性：

- **零實作**：只定義契約，不包含任何具體實作
- **零依賴**：不依賴任何業務系統（tej, gms）
- **單向依賴**：所有系統依賴 core，core 不依賴任何系統

#### 範例場景

本章以「每日股價同步」為核心範例，展示如何定義貫穿系統的標準契約。

-----

### 2.2 標準化資料模型（Schemas/DTO）

資料模型定義了系統間的「共同語言」，確保 `tej` 與 `gms` 在談論「股價」時，指的是完全相同的資料結構。

#### 設計原則

- **使用 Pydantic**：提供運行時驗證與序列化能力
- **金融精度**：使用 `Decimal` 處理金額，避免浮點數誤差
- **明確型別**：使用 Enum 定義有限選項，避免魔術字串
- **驗證邏輯**：在 DTO 層級進行基礎格式驗證

#### 實作範例：股價資料模型

**檔案位置**：`core/schemas/market.py`

```python
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date
from typing import Optional, List
from enum import Enum

class MarketType(str, Enum):
    """
    市場類型枚舉
    繼承 str 使其可直接序列化為 JSON
    """
    TWSE = "TWSE"  # 上市
    TPEX = "TPEX"  # 上櫃
    ESB = "ESB"    # 興櫃

class StockPriceDTO(BaseModel):
    """
    跨系統通用的股價資料模型

    用途：
    1. Data Source System (tej) 的標準輸出格式
    2. ETL Pipeline 的標準輸入格式
    3. API Response 的標準格式
    4. Repository 與 Service 之間的資料傳遞格式

    設計考量：
    - 使用 Decimal 確保金融計算精確度
    - 所有必要欄位都設為 required（...）
    - 選填欄位使用 Optional 明確標示
    """
    # === 識別欄位 ===
    symbol: str = Field(
        ...,
        description="股票代碼",
        min_length=4,
        max_length=10,
        examples=["2330", "2330.TW"]
    )
    trade_date: date = Field(
        ...,
        description="交易日期"
    )

    # === 價格欄位（使用 Decimal）===
    open_price: Decimal = Field(
        ...,
        ge=0,
        description="開盤價"
    )
    high_price: Decimal = Field(
        ...,
        ge=0,
        description="最高價"
    )
    low_price: Decimal = Field(
        ...,
        ge=0,
        description="最低價"
    )
    close_price: Decimal = Field(
        ...,
        ge=0,
        description="收盤價"
    )

    # === 成交量欄位 ===
    volume: int = Field(
        ...,
        ge=0,
        description="成交量（股）"
    )
    turnover: Optional[Decimal] = Field(
        None,
        ge=0,
        description="成交金額"
    )

    # === 市場資訊 ===
    market_type: Optional[MarketType] = Field(
        None,
        description="市場類型"
    )

    # === 驗證器 ===
    @field_validator('symbol')
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """標準化股票代碼格式"""
        return v.upper().strip()

    @field_validator('high_price')
    @classmethod
    def validate_high_price(cls, v: Decimal, info) -> Decimal:
        """驗證最高價邏輯"""
        if 'low_price' in info.data and v < info.data['low_price']:
            raise ValueError('最高價不得低於最低價')
        return v

    # === Pydantic 設定 ===
    model_config = {
        "json_schema_extra": {
            "example": {
                "symbol": "2330",
                "trade_date": "2024-01-01",
                "open_price": "590.00",
                "high_price": "595.00",
                "low_price": "588.00",
                "close_price": "593.00",
                "volume": 25000000,
                "market_type": "TWSE"
            }
        }
    }
```

-----

### 2.3 資料提供者介面（Provider Interfaces）

這是實現**跨系統依賴反轉（Cross-System DIP）**的關鍵。透過定義抽象介面，業務系統不需要知道資料來源的實作細節。

#### 設計原則

- **由需求驅動**：介面由使用方（業務系統）的需求定義
- **最小化介面**：只定義必要的方法，避免過度設計
- **異步優先**：使用 `async/await` 支援非阻塞 I/O
- **明確錯誤**：定義清楚的異常類型

#### 實作範例：股價資料提供者介面

**檔案位置**：`core/interfaces/market.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from ..schemas.market import StockPriceDTO

class IStockPriceProvider(ABC):
    """
    股價資料提供者介面（跨系統契約）

    設計理念：
    - 定義「能力」而非「實作」
    - 任何資料源（TEJ DB、Yahoo Finance、證交所）都可實作此介面
    - 使用方只需依賴此介面，不需知道具體實作

    實作者包括：
    - TEJ 內部資料庫（公司內部資料源）
    - Bloomberg API（外部付費資料源）
    - Yahoo Finance（外部免費資料源）
    """

    @abstractmethod
    async def get_daily_prices(
        self,
        target_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[StockPriceDTO]:
        """
        取得指定日期的股價資料

        Args:
            target_date: 交易日期
            symbols: 股票代碼列表，None 表示全市場

        Returns:
            標準化的股價資料列表

        Raises:
            DataSourceError: 資料源連線錯誤
            DataValidationError: 資料格式驗證錯誤
        """
        pass

    @abstractmethod
    async def get_history_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> List[StockPriceDTO]:
        """
        取得個股歷史股價

        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            時間序列股價資料
        """
        pass

    async def health_check(self) -> bool:
        """
        健康檢查（可選覆寫）

        Returns:
            資料源是否正常
        """
        return True
```

-----

### 2.4 異常體系定義（Exceptions）

統一的異常體系讓錯誤處理更加優雅，並提供清晰的錯誤上下文。

**檔案位置**：`core/exceptions.py`

```python
from typing import Optional, Dict, Any
from datetime import datetime

class CoreError(Exception):
    """
    專案基礎異常類
    所有自定義異常都應繼承此類
    """
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """序列化為字典（用於日誌或 API 回應）"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class DataSourceError(CoreError):
    """資料源錯誤基類"""
    pass

class DataValidationError(CoreError):
    """資料驗證錯誤基類"""
    pass

class BusinessLogicError(CoreError):
    """業務邏輯錯誤基類"""
    pass
```

-----

## 3. 資料源系統實作：Internal Data Source Adapter

> **示例定位說明**：本章以 TEJ 系統為例展示資料源系統的適配器設計模式。本章範例中的目錄結構（如 `collector/db_client.py`、`service/provider.py`）反映的是該系統的既有實作樣貌，尚未收斂至本專案正式的 FU Container 結構模型。讀者不應將此處的扁平結構視為現行正式推薦模板；TEJ 系統的結構是否需遷移至 FU Container 模型，仍待後續正式整理。

本章節展示如何建立資料源系統（如 `tej`），作為內部資料庫的適配器，將老舊資料庫 Schema 轉換為標準契約。

### 3.1 架構定位：Internal Database Adapter

> **重要修正**：TEJ 在本架構中被視為**公司內部資料庫**（Internal Data Source），而非外部 API。

資料源系統扮演 **適配器（Adapter）** 角色，職責如下：

- **內部資料存取**：與公司內部資料庫（如 TEJ）直接連線
- **Schema 隔離**：隔離老舊或特定的資料庫 Schema，避免污染業務系統
- **資料轉換**：將原始資料表結構轉換為 Core 定義的標準 DTO
- **錯誤處理**：將底層 SQL 錯誤包裝為 Core 定義的異常
- **實作契約**：完整實現 Core 定義的介面

這展示了資料源系統作為「適配器」的重要場景：**隔離內部老舊資料庫**，讓業務系統不需要知道 TEJ 的特殊欄位命名（如 `coid`、`open_d`）。

#### 層級架構

```text
tej/                        # Data Source System (Internal DB Adapter)
├── __init__.py
├── core/                  # 系統級共用函式庫
│   ├── __init__.py
│   └── mapping/           # 欄位對應工具集
│       ├── __init__.py
│       └── _field_mapping/
│           └── _mapping.py  # 欄位對應工具
│
├── collector/             # 資料庫存取層
│   ├── __init__.py
│   ├── db_client.py      # 資料庫連線與 SQL 執行
│   └── schema.py         # TEJ 資料表 Schema 定義
│
└── service/               # 服務實作層
    ├── __init__.py
    └── provider.py       # IStockPriceProvider 實作
```

> **結構說明**：原先放置在 `utils/` 的系統級共用能力（如欄位對應工具），應規劃至 `tej/core/` 中。`<system>/core` 是資料源系統承載系統內部共用基礎設施的正式結構，而非使用鬆散的 `utils/` 目錄。此原則適用於所有系統類型。

-----

### 3.2 Collector 層：內部資料庫存取

此層級負責處理與 TEJ 資料庫的連線細節，包括處理特殊的 Schema、欄位命名、資料型別等。

#### 設計原則

- **單一職責**：只負責資料庫連線與 SQL 執行
- **Schema 封裝**：隱藏 TEJ 特有的表格結構
- **原始資料**：回傳未處理的資料庫記錄
- **連線管理**：處理資料庫連線池與事務

#### 實作範例：TEJ 資料庫客戶端

**檔案位置**：`tej/collector/db_client.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text, MetaData
from typing import List, Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

class TejDbCollector:
    """
    TEJ 資料庫收集器

    職責：
    1. 管理 TEJ 資料庫連線
    2. 執行 Raw SQL 查詢
    3. 處理 TEJ 特有的表格結構與欄位命名

    TEJ 資料庫特性：
    - 使用特殊欄位命名（coid = 股票代碼, mdate = 交易日期）
    - 價格欄位以 _d 結尾（open_d, high_d, low_d, close_d）
    - 成交量單位是「張」而非「股」
    """

    def __init__(self, db_url: str):
        """
        初始化 TEJ 資料庫連線

        Args:
            db_url: 資料庫連線字串
                   例如: "postgresql+asyncpg://user:pass@tej-db:5432/tej_market"
        """
        # 建立針對 TEJ 資料庫的連線引擎
        self.engine: AsyncEngine = create_async_engine(
            db_url,
            echo=False,  # 生產環境設為 False
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,  # 連線健康檢查
        )
        self.metadata = MetaData()

    async def fetch_raw_prices(
        self,
        target_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        從 TEJ 資料庫撈取原始股價資料

        注意：這裡處理的是 TEJ 原始欄位
        - coid: 股票代碼
        - mdate: 交易日期
        - open_d, high_d, low_d, close_d: 價格
        - vol: 成交量（張）

        Args:
            target_date: 查詢日期
            symbols: 股票代碼列表（可選）

        Returns:
            原始資料庫記錄列表
        """
        # TEJ 的表格可能有特殊命名規則
        base_sql = """
            SELECT
                coid,           -- TEJ 的股票代碼欄位
                mdate,          -- TEJ 的日期欄位
                open_d,         -- 開盤價
                high_d,         -- 最高價
                low_d,          -- 最低價
                close_d,        -- 收盤價
                vol,            -- 成交量（張）
                amt             -- 成交金額（千元）
            FROM tej_stock_daily_price
            WHERE mdate = :target_date
        """

        # 動態建構 SQL
        if symbols:
            sql = base_sql + " AND coid IN :symbols"
            params = {"target_date": target_date, "symbols": tuple(symbols)}
        else:
            sql = base_sql
            params = {"target_date": target_date}

        sql += " ORDER BY coid"

        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params)
            # 將結果轉換為字典列表
            rows = [dict(row._mapping) for row in result]

            logger.info(
                f"Fetched {len(rows)} records from TEJ for date {target_date}"
            )

            return rows

    async def close(self):
        """關閉資料庫連線"""
        await self.engine.dispose()
```

#### TEJ Schema 定義

**檔案位置**：`tej/collector/schema.py`

```python
"""
TEJ 資料庫 Schema 文件
記錄 TEJ 特有的表格結構與欄位定義
"""

# TEJ 股價表格欄位對應
TEJ_PRICE_COLUMNS = {
    'coid': 'symbol',           # 股票代碼
    'mdate': 'trade_date',      # 交易日期
    'open_d': 'open_price',     # 開盤價
    'high_d': 'high_price',     # 最高價
    'low_d': 'low_price',       # 最低價
    'close_d': 'close_price',   # 收盤價
    'vol': 'volume_lots',       # 成交量（張）
    'amt': 'turnover_thousand', # 成交金額（千元）
}

# 單位轉換常數
LOTS_TO_SHARES = 1000  # 1張 = 1000股
THOUSAND_TO_UNIT = 1000  # 千元轉元
```

-----

### 3.3 Service 層：實作核心契約

Service 層將 Collector 撈到的「TEJ 原始資料」適配成 Core 定義的「標準契約」。

#### 實作範例：TEJ 股價提供者

**檔案位置**：`tej/service/provider.py`

```python
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
import logging
from sqlalchemy import text

# Core 契約
from core.interfaces.market import IStockPriceProvider
from core.schemas.market import StockPriceDTO, MarketType
from core.exceptions import DataSourceError

# 內部元件
from ..collector.db_client import TejDbCollector
from ..collector.schema import LOTS_TO_SHARES, THOUSAND_TO_UNIT

logger = logging.getLogger(__name__)

class TejStockPriceProvider(IStockPriceProvider):
    """
    TEJ 股價資料提供者（內部資料庫適配器）

    實作 IStockPriceProvider 介面，
    將 TEJ 內部資料庫適配為標準契約

    職責：
    1. 隔離 TEJ 特有的 Schema 與命名
    2. 處理單位轉換（張→股、千元→元）
    3. 轉換為標準 DTO 格式
    """

    def __init__(self, db_url: str):
        """
        初始化

        Args:
            db_url: TEJ 資料庫連線字串
        """
        self.collector = TejDbCollector(db_url)

    async def get_daily_prices(
        self,
        target_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[StockPriceDTO]:
        """
        實作：取得每日股價

        TEJ 特定處理：
        1. 欄位對應：coid → symbol, open_d → open_price
        2. 單位轉換：vol（張）→ volume（股）
        3. 金額轉換：amt（千元）→ turnover（元）
        """
        try:
            # 1. 透過 Collector 撈取 TEJ 原始資料
            raw_rows = await self.collector.fetch_raw_prices(
                target_date, symbols
            )

            if not raw_rows:
                logger.warning(f"No data found in TEJ for date {target_date}")
                return []

            # 2. 轉換為標準 DTO
            results = []
            for row in raw_rows:
                try:
                    dto = self._convert_tej_record_to_dto(row, target_date)
                    results.append(dto)

                except Exception as e:
                    # 記錄但繼續處理其他記錄
                    logger.warning(
                        f"Failed to convert TEJ record for {row.get('coid')}: {e}"
                    )
                    continue

            logger.info(
                f"Converted {len(results)} records from TEJ to standard DTOs"
            )
            return results

        except Exception as e:
            # 包裝為標準異常
            raise DataSourceError(
                message=f"TEJ database access failed: {str(e)}",
                context={
                    "date": str(target_date),
                    "symbols": symbols
                }
            ) from e

    def _convert_tej_record_to_dto(
        self,
        tej_record: Dict[str, Any],
        target_date: date
    ) -> StockPriceDTO:
        """
        內部方法：轉換 TEJ 記錄為標準 DTO

        處理所有 TEJ 特有的轉換邏輯
        """
        # 取得 TEJ 原始欄位
        symbol = str(tej_record['coid']).strip()

        # 價格轉換
        open_price = Decimal(str(tej_record['open_d']))
        high_price = Decimal(str(tej_record['high_d']))
        low_price = Decimal(str(tej_record['low_d']))
        close_price = Decimal(str(tej_record['close_d']))

        # 成交量轉換：張 → 股
        volume_lots = int(tej_record['vol'])
        volume_shares = volume_lots * LOTS_TO_SHARES

        # 成交金額轉換：千元 → 元
        turnover = None
        if tej_record.get('amt'):
            turnover_thousand = Decimal(str(tej_record['amt']))
            turnover = turnover_thousand * THOUSAND_TO_UNIT

        # 判斷市場類型
        market_type = self._detect_market_type(symbol)

        # 建立標準 DTO
        return StockPriceDTO(
            symbol=symbol,
            trade_date=target_date,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume_shares,
            turnover=turnover,
            market_type=market_type
        )

    def _detect_market_type(self, symbol: str) -> Optional[MarketType]:
        """
        從股票代碼判斷市場類型

        TEJ 特定規則：
        - 4碼數字：上市（TWSE）
        - 6碼含英文：上櫃（TPEX）
        """
        clean_symbol = symbol.strip()

        if clean_symbol.isdigit() and len(clean_symbol) == 4:
            return MarketType.TWSE
        elif len(clean_symbol) == 6 and clean_symbol[:4].isdigit():
            return MarketType.TPEX

        return None

    async def get_history_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> List[StockPriceDTO]:
        """實作：取得歷史股價"""
        # 實作邏輯類似 get_daily_prices
        pass

    async def health_check(self) -> bool:
        """
        健康檢查

        測試 TEJ 資料庫連線
        """
        try:
            async with self.collector.engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"TEJ database health check failed: {e}")
            return False
```

-----

## 4. 業務系統實作 I：資料存取層 (DB Layer with DIP)

本章節展示如何在業務系統（`gms`）的 DB 層實現**嚴格的介面導向設計（DIP）**。

### 4.1 架構定位：Repository Pattern with Interfaces

> **重要修正**：嚴格遵守**依賴反轉原則（DIP）**，在 FU Container 內定義抽象介面，Repository 實作該介面。

DB 層使用 Repository Pattern 配合抽象介面，提供以下優勢：

- **依賴反轉**：Service 層依賴介面而非具體實作
- **易於測試**：可輕易 Mock Repository 介面
- **隔離 SQL**：業務邏輯不直接接觸 SQL
- **支援切換**：可更換底層資料庫實作

#### 目錄結構（修正版）

```text
gms/db/
├── _orm/                       # DB 層私有共用模組（ORM 基礎元件）
│   ├── base.py                 # Base, BaseRepository
│   └── mixins.py               # TimestampMixin
└── market/                     # Domain
    └── stock/                  # Sub-domain
        └── price/              # FU Container (股價功能單元)
            ├── __init__.py     # 公開介面
            └── _stock_price_storage/  # Feature 級私有實作空間
                ├── _interfaces.py  # 抽象介面定義
                ├── _models.py      # ORM 定義 (私有)
                └── _repository.py  # Repository 實作 (私有)
```

-----

### 4.2 抽象介面定義（Interfaces）

這是在**系統內（Intra-system）**實現 DIP 的關鍵。Service 層將依賴此介面，而非具體的 Repository 類別。

**檔案位置**：`gms/db/market/stock/price/_stock_price_storage/_interfaces.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

# 注意：介面可以依賴同目錄的 Model（同屬一個 Feature 的私有實作空間）
from ._models import StockPriceModel

class IStockPriceRepository(ABC):
    """
    股價資料存取介面

    設計理念：
    - Service 層依賴此介面，而非具體 Repository
    - 定義所有資料存取操作的契約
    - 支援 Mock 測試

    使用場景：
    1. Service 層注入此介面
    2. 測試時提供 Mock 實作
    3. 未來可切換不同資料庫實作
    """

    # === 查詢操作 ===

    @abstractmethod
    async def get_by_symbol_date(
        self,
        symbol: str,
        trade_date: date
    ) -> Optional[StockPriceModel]:
        """查詢單日股價"""
        pass

    @abstractmethod
    async def get_latest_price(
        self,
        symbol: str
    ) -> Optional[StockPriceModel]:
        """取得最新股價"""
        pass

    @abstractmethod
    async def get_daily_prices(
        self,
        trade_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[StockPriceModel]:
        """查詢指定日期的股價"""
        pass

    # === 寫入操作 ===

    @abstractmethod
    async def upsert_batch(
        self,
        prices: List[Dict[str, Any]]
    ) -> int:
        """批次寫入或更新（Upsert）"""
        pass
```

-----

### 4.3 Repository 實作（Implementation）

**明確繼承 IStockPriceRepository 介面**，實現所有抽象方法。

**檔案位置**：`gms/db/market/stock/price/_stock_price_storage/_repository.py`

```python
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from gms.db.market.stock.profile import BaseRepository  # 跨公開邊界，絕對 import
from ._models import StockPriceModel
from ._interfaces import IStockPriceRepository

class StockPriceRepository(BaseRepository[StockPriceModel], IStockPriceRepository):
    """
    股價資料存取層實作

    繼承：
    1. BaseRepository：提供基礎 CRUD 操作
    2. IStockPriceRepository：實現介面契約

    設計考量：
    - 所有方法都實現介面定義
    - 使用批次操作優化效能
    - 支援 PostgreSQL 特有功能（如 ON CONFLICT）
    """

    def __init__(self, session: AsyncSession):
        """初始化 Repository"""
        super().__init__(session, StockPriceModel)

    async def get_by_symbol_date(
        self,
        symbol: str,
        trade_date: date
    ) -> Optional[StockPriceModel]:
        """實作：查詢單日股價"""
        stmt = select(StockPriceModel).where(
            and_(
                StockPriceModel.symbol == symbol,
                StockPriceModel.trade_date == trade_date
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_price(
        self,
        symbol: str
    ) -> Optional[StockPriceModel]:
        """實作：取得最新股價"""
        stmt = (
            select(StockPriceModel)
            .where(StockPriceModel.symbol == symbol)
            .order_by(desc(StockPriceModel.trade_date))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_daily_prices(
        self,
        trade_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[StockPriceModel]:
        """實作：查詢指定日期的股價"""
        stmt = select(StockPriceModel).where(
            StockPriceModel.trade_date == trade_date
        )

        if symbols:
            stmt = stmt.where(
                StockPriceModel.symbol.in_(symbols)
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_batch(
        self,
        prices: List[Dict[str, Any]]
    ) -> int:
        """實作：批次 Upsert"""
        if not prices:
            return 0

        stmt = insert(StockPriceModel).values(prices)

        # ON CONFLICT DO UPDATE
        stmt = stmt.on_conflict_do_update(
            constraint='pk_stock_prices',
            set_={
                'open_price': stmt.excluded.open_price,
                'high_price': stmt.excluded.high_price,
                'low_price': stmt.excluded.low_price,
                'close_price': stmt.excluded.close_price,
                'volume': stmt.excluded.volume,
                'updated_at': func.now()
            }
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount
```

-----

### 4.4 公開介面封裝

**重要**：對外暴露介面，供 Service 層使用。

**檔案位置**：`gms/db/market/stock/price/__init__.py`

```python
"""
股價資料存取模組
提供股價的 ORM 模型、Repository 介面與實作
"""

# 暴露模型（透過 Feature 級私有目錄）
from ._stock_price_storage._models import StockPriceModel

# 暴露介面（重要！）
from ._stock_price_storage._interfaces import IStockPriceRepository

# 暴露實作
from ._stock_price_storage._repository import StockPriceRepository

__all__ = [
    'StockPriceModel',
    'IStockPriceRepository',  # Service 層將依賴此介面
    'StockPriceRepository',   # DI Container 將注入此實作
]
```

-----

## 5. 業務系統實作 II：業務邏輯層 (Service Layer)

本章節展示 Service 層如何實作純粹的業務規則與用例（Use Cases），成為系統的「大腦」。

### 5.1 架構定位：Business Logic Container

Service 層的核心特性：

- **依賴介面**：只依賴 DB 層的抽象介面（`IStockPriceRepository`）
- **業務規則**：實作領域特定的業務邏輯
- **用例協調**：協調多個 Repository 完成業務流程
- **零 SQL**：完全不接觸 SQL 或資料庫細節

#### 目錄結構與依賴管理

```text
gms/service/
├── _validators.py              # 業務驗證器
├── _calculators.py              # 業務計算器
│
└── market/
    └── stock/
        └── analysis/           # FU Container: 股價分析服務
            ├── __init__.py
            └── _stock_analysis_api/  # Feature 級私有實作空間
                ├── _service.py     # 業務邏輯實作
                └── _dto.py         # Service 層 DTO
```

-----

### 5.2 Service 層依賴管理

Service 層跨公開邊界取用 DB 層與 System Core 的公開介面，使用正式絕對 import。依賴較複雜時，可使用 facade-like private modules 整理。

```python
"""
Service 層根依賴管理
職責：統一導入外部模組 (DB 介面、Core 元件)

關鍵原則：
- 只導入介面，不導入實作
- 統一管理跨層依賴
"""

# 1. 導入 DB 層的抽象介面（注意：只導入介面！）
from gms.db.market.stock.price import IStockPriceRepository

# 2. 導入 Core 的標準元件
from core.exceptions import (
    BusinessLogicError,
    DataValidationError
)
from core.schemas.market import StockPriceDTO

__all__ = [
    # DB 介面
    'IStockPriceRepository',

    # Core 元件
    'BusinessLogicError',
    'DataValidationError',
    'StockPriceDTO',
]
```

-----

### 5.3 業務邏輯實作

展示 Service 如何使用介面進行業務運算，完全不關心資料的儲存細節。

#### 業務服務實作

**檔案位置**：`gms/service/market/stock/analysis/_stock_analysis_api/_service.py`

```python
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional
import logging

# 跨公開邊界：正式絕對 import（DIP）
from gms.db.market.stock.price import (
    IStockPriceRepository,
    StockPriceDTO,
)
from gms.core.exceptions import BusinessLogicError, DataValidationError

logger = logging.getLogger(__name__)

class StockAnalysisService:
    """
    股價分析服務

    設計理念：
    - 只依賴 Repository 介面
    - 專注於業務邏輯實作
    - 不處理資料存取細節
    """

    def __init__(self, price_repo: IStockPriceRepository):
        """
        初始化服務

        Args:
            price_repo: 股價資料存取介面（依賴注入）
        """
        self.price_repo = price_repo

    async def check_abnormal_volume(
        self,
        symbol: str,
        check_date: date
    ) -> Dict[str, any]:
        """
        業務邏輯：檢查成交量是否異常

        規則定義：
        - 成交量超過 20 日平均量的 2 倍視為暴量
        - 成交量低於 20 日平均量的 0.3 倍視為縮量

        Args:
            symbol: 股票代碼
            check_date: 檢查日期

        Returns:
            分析結果字典

        Raises:
            BusinessLogicError: 資料不足或其他業務錯誤
        """
        # 1. 取得當日資料
        current_data = await self.price_repo.get_by_symbol_date(
            symbol, check_date
        )

        if not current_data:
            raise BusinessLogicError(
                message=f"No price data for {symbol} on {check_date}",
                context={"symbol": symbol, "date": str(check_date)}
            )

        # 2. 計算 20 日平均成交量
        avg_volume = await self._calculate_average_volume(
            symbol, check_date, days=20
        )

        if avg_volume is None:
            raise BusinessLogicError(
                message=f"Insufficient historical data for {symbol}",
                context={"symbol": symbol}
            )

        # 3. 判斷異常類型
        volume_ratio = current_data.volume / avg_volume

        abnormal_type = "normal"
        if volume_ratio > 2.0:
            abnormal_type = "surge"  # 暴量
        elif volume_ratio < 0.3:
            abnormal_type = "shrink"  # 縮量

        # 4. 組裝回傳結果
        return {
            "symbol": symbol,
            "date": check_date,
            "volume": current_data.volume,
            "avg_volume_20d": int(avg_volume),
            "volume_ratio": round(volume_ratio, 2),
            "abnormal_type": abnormal_type,
            "is_abnormal": abnormal_type != "normal",
            "close_price": float(current_data.close_price)
        }

    async def calculate_moving_averages(
        self,
        symbol: str,
        end_date: date,
        periods: List[int] = [5, 10, 20, 60]
    ) -> Dict[str, Optional[Decimal]]:
        """
        業務邏輯：計算移動平均線

        Args:
            symbol: 股票代碼
            end_date: 計算截止日期
            periods: MA 期間列表

        Returns:
            各期間 MA 值
        """
        result = {}

        for period in periods:
            ma_value = await self._calculate_ma(
                symbol, end_date, period
            )
            result[f"MA{period}"] = ma_value

        return result

    async def detect_golden_cross(
        self,
        symbol: str,
        check_date: date
    ) -> bool:
        """
        業務邏輯：檢測黃金交叉

        定義：短期均線（MA5）向上突破長期均線（MA20）

        Args:
            symbol: 股票代碼
            check_date: 檢查日期

        Returns:
            是否出現黃金交叉
        """
        # 取得今日與昨日的 MA 值
        today_ma = await self.calculate_moving_averages(
            symbol, check_date, [5, 20]
        )

        yesterday = check_date - timedelta(days=1)
        yesterday_ma = await self.calculate_moving_averages(
            symbol, yesterday, [5, 20]
        )

        # 檢查是否形成黃金交叉
        if (today_ma["MA5"] and today_ma["MA20"] and
            yesterday_ma["MA5"] and yesterday_ma["MA20"]):

            # 昨日 MA5 < MA20，今日 MA5 > MA20
            return (yesterday_ma["MA5"] < yesterday_ma["MA20"] and
                    today_ma["MA5"] > today_ma["MA20"])

        return False

    # === 內部輔助方法 ===

    async def _calculate_average_volume(
        self,
        symbol: str,
        end_date: date,
        days: int
    ) -> Optional[float]:
        """
        內部方法：計算平均成交量

        使用 Repository 介面取得歷史資料並計算
        """
        start_date = end_date - timedelta(days=days * 2)  # 考慮假日

        # 使用介面方法取得歷史資料
        historical_data = await self.price_repo.get_price_range(
            symbol, start_date, end_date
        )

        # 取最近 N 筆交易日資料
        if len(historical_data) < days:
            return None

        recent_data = historical_data[-days:]
        total_volume = sum(d.volume for d in recent_data)

        return total_volume / days

    async def _calculate_ma(
        self,
        symbol: str,
        end_date: date,
        period: int
    ) -> Optional[Decimal]:
        """
        內部方法：計算移動平均價
        """
        start_date = end_date - timedelta(days=period * 2)

        historical_data = await self.price_repo.get_price_range(
            symbol, start_date, end_date
        )

        if len(historical_data) < period:
            return None

        recent_data = historical_data[-period:]
        total_price = sum(d.close_price for d in recent_data)

        return total_price / period
```

#### Service 層 DTO

Service 層可以定義自己的 DTO，用於複雜的業務結果。

**檔案位置**：`gms/service/market/stock/analysis/_stock_analysis_api/_dto.py`

```python
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional, Dict

class VolumeAnalysisResult(BaseModel):
    """成交量分析結果"""
    symbol: str
    date: date
    volume: int
    avg_volume_20d: int
    volume_ratio: float = Field(..., description="相對於平均量的倍數")
    abnormal_type: str = Field(..., description="normal/surge/shrink")
    is_abnormal: bool
    close_price: float

class TechnicalIndicators(BaseModel):
    """技術指標結果"""
    symbol: str
    date: date
    ma5: Optional[Decimal]
    ma10: Optional[Decimal]
    ma20: Optional[Decimal]
    ma60: Optional[Decimal]
    has_golden_cross: bool = False
    has_death_cross: bool = False
```

-----

## 6. 業務系統實作 III：資料管線層 (ETL Layer)

本章節展示 ETL 層如何成為資料流的核心樞紐，協調資料源與資料庫之間的資料搬運。

### 6.1 架構定位：Data Pipeline Orchestrator

> **架構亮點**：這是展示**跨系統依賴反轉**最極致的地方。

ETL Pipeline 的設計精髓：

- **Source 端**：依賴 `core.interfaces.IStockPriceProvider`（抽象契約）
- **Target 端**：依賴 `gms.db....IStockPriceRepository`（抽象契約）
- **結果**：ETL 程式碼中**完全看不到 `tej` 或 `SQLAlchemy` 的蹤影**

#### 目錄結構

```text
gms/etl/
├── _validators.py              # 資料驗證器
├── _transformers.py             # 資料轉換器
│
└── market/
    └── stock/
        └── sync_job/           # FU Container: 每日同步作業
            ├── __init__.py
            └── _daily_sync_job/    # Feature 級私有實作空間
                ├── _pipeline.py    # ETL 流程控制
                ├── _extractor.py   # 抽取邏輯
                └── _loader.py      # 載入邏輯
```

-----

### 6.2 ETL 層依賴管理

ETL 層需要同時依賴資料源介面與資料庫介面。

ETL 層跨公開邊界取用 DB 層介面與 Core 介面，使用正式絕對 import。

```python
"""
ETL 層根依賴管理

關鍵設計：
- 同時依賴 Source 與 Target 的介面
- 不依賴任何具體實作
"""

# 1. 導入 Core 的跨系統契約（Source 介面）
from core.interfaces.market import IStockPriceProvider
from core.schemas.market import StockPriceDTO

# 2. 導入 DB 層介面（Target 介面）
from gms.db.market.stock.price import IStockPriceRepository

# 3. 導入 Core 異常
from core.exceptions import (
    DataSourceError,
    BusinessLogicError
)

__all__ = [
    # Source
    'IStockPriceProvider',
    'StockPriceDTO',

    # Target
    'IStockPriceRepository',

    # Exceptions
    'DataSourceError',
    'BusinessLogicError',
]
```

-----

### 6.3 ETL Pipeline 實作

展示如何協調兩個抽象介面完成資料搬運。

#### Pipeline 主體

**檔案位置**：`gms/etl/market/stock/sync_job/_daily_sync_job/_pipeline.py`

```python
from datetime import date, datetime
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

# 跨公開邊界：正式絕對 import
from core.interfaces import IStockPriceProvider     # 來自 Core（代表 TEJ）
from gms.db.market.stock.price import (
    IStockPriceRepository,   # 來自 DB（代表 GMS DB）
    StockPriceDTO,
)
from gms.core.exceptions import DataSourceError, BusinessLogicError

logger = logging.getLogger(__name__)

@dataclass
class SyncResult:
    """同步結果"""
    success: bool
    total_extracted: int
    total_loaded: int
    failed_records: List[str]
    execution_time: float
    error_message: Optional[str] = None

class DailyStockSyncPipeline:
    """
    每日股價同步 Pipeline

    設計亮點：
    - 完全基於介面編程
    - 不知道資料源是 TEJ 還是其他
    - 不知道目標是 PostgreSQL 還是其他

    流程：
    External Provider -> DTO -> Internal Repository
    """

    def __init__(
        self,
        source_provider: IStockPriceProvider,  # 注入資料源介面
        target_repo: IStockPriceRepository     # 注入資料庫介面
    ):
        """
        初始化 Pipeline

        Args:
            source_provider: 資料源提供者（可能是 TEJ、Yahoo 等）
            target_repo: 目標資料庫（可能是 PostgreSQL、MongoDB 等）
        """
        self.source = source_provider
        self.target = target_repo
        self.validators = []  # 可擴充的驗證器

    async def run(
        self,
        target_date: date,
        symbols: Optional[List[str]] = None
    ) -> SyncResult:
        """
        執行同步作業

        Args:
            target_date: 同步日期
            symbols: 指定股票列表（None 表示全市場）

        Returns:
            同步結果
        """
        start_time = datetime.now()
        result = SyncResult(
            success=False,
            total_extracted=0,
            total_loaded=0,
            failed_records=[],
            execution_time=0
        )

        try:
            logger.info(f"Starting sync for {target_date}...")

            # 1. Extract：從資料源取得標準 DTO
            dtos = await self._extract(target_date, symbols)
            result.total_extracted = len(dtos)
            logger.info(f"Extracted {len(dtos)} records")

            if not dtos:
                logger.warning("No data to sync")
                result.success = True
                return result

            # 2. Transform：轉換與驗證
            valid_records, invalid_symbols = await self._transform(dtos)
            result.failed_records = invalid_symbols

            # 3. Load：批次寫入資料庫
            loaded_count = await self._load(valid_records)
            result.total_loaded = loaded_count

            # 4. 完成
            result.success = True
            logger.info(
                f"Sync completed: {loaded_count}/{len(dtos)} records"
            )

        except DataSourceError as e:
            logger.error(f"Data source error: {e}")
            result.error_message = str(e)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            result.error_message = str(e)

        finally:
            # 計算執行時間
            result.execution_time = (
                datetime.now() - start_time
            ).total_seconds()

        return result

    async def _extract(
        self,
        target_date: date,
        symbols: Optional[List[str]] = None
    ) -> List[StockPriceDTO]:
        """
        Extract 階段：從資料源取得資料

        注意：我們不知道資料源是什麼，
        只知道它實作了 IStockPriceProvider
        """
        try:
            return await self.source.get_daily_prices(
                target_date,
                symbols
            )
        except Exception as e:
            raise DataSourceError(
                message="Failed to extract data from source",
                context={"date": str(target_date), "error": str(e)}
            ) from e

    async def _transform(
        self,
        dtos: List[StockPriceDTO]
    ) -> tuple[List[Dict], List[str]]:
        """
        Transform 階段：資料轉換與驗證

        Returns:
            (有效記錄, 無效股票代碼列表)
        """
        valid_records = []
        invalid_symbols = []

        for dto in dtos:
            # 執行業務規則驗證
            if not self._validate_price_data(dto):
                invalid_symbols.append(dto.symbol)
                logger.warning(f"Invalid data for {dto.symbol}")
                continue

            # 轉換為資料庫格式
            record = {
                "symbol": dto.symbol,
                "trade_date": dto.trade_date,
                "open_price": dto.open_price,
                "high_price": dto.high_price,
                "low_price": dto.low_price,
                "close_price": dto.close_price,
                "volume": dto.volume,
                "turnover": dto.turnover,
                "market_type": (
                    dto.market_type.value
                    if dto.market_type else None
                )
            }

            valid_records.append(record)

        return valid_records, invalid_symbols

    async def _load(
        self,
        records: List[Dict]
    ) -> int:
        """
        Load 階段：寫入目標資料庫

        注意：我們不知道資料庫是什麼，
        只知道它實作了 IStockPriceRepository
        """
        if not records:
            return 0

        try:
            # 使用介面方法寫入
            return await self.target.upsert_batch(records)

        except Exception as e:
            raise BusinessLogicError(
                message="Failed to load data to target",
                context={"record_count": len(records), "error": str(e)}
            ) from e

    def _validate_price_data(self, dto: StockPriceDTO) -> bool:
        """
        內部方法：驗證價格資料

        業務規則範例：
        - 價格必須大於 0
        - 最高價不能低於最低價
        - 成交量不能為負
        """
        if dto.close_price <= 0:
            return False

        if dto.high_price < dto.low_price:
            return False

        if dto.volume < 0:
            return False

        return True
```

#### 批次處理優化

**檔案位置**：`gms/etl/market/stock/sync_job/_daily_sync_job/_loader.py`

```python
from typing import List, Dict, Any
import asyncio
from gms.db.market.stock.price import IStockPriceRepository

class BatchLoader:
    """
    批次載入器
    處理大量資料的分批載入
    """

    def __init__(
        self,
        repository: IStockPriceRepository,
        batch_size: int = 1000
    ):
        self.repository = repository
        self.batch_size = batch_size

    async def load_in_batches(
        self,
        records: List[Dict[str, Any]]
    ) -> int:
        """
        分批載入資料

        Args:
            records: 待載入的記錄

        Returns:
            總載入筆數
        """
        total_loaded = 0

        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            loaded = await self.repository.upsert_batch(batch)
            total_loaded += loaded

            # 避免過度佔用資源
            await asyncio.sleep(0.1)

        return total_loaded
```

-----

## 7. 業務系統實作 IV：介面層 (API Layer)

本章節展示如何建立 RESTful API 層，並運用統一 import 原則與 facade 管理依賴。

### 7.1 架構定位：HTTP Interface Adapter

API 層的核心職責：

- **HTTP 處理**：處理請求與回應的轉換
- **參數驗證**：驗證並轉換輸入參數
- **錯誤轉換**：將業務異常轉為適當的 HTTP 狀態碼
- **依賴注入**：透過 FastAPI 的 Depends 機制注入服務

> **實作重點**：利用 `dependencies.py` 定義依賴注入工廠，Router 透過絕對 import 或 facade-like private module 取得依賴。

#### 目錄結構

展示 API 層如何組織，特別注意 `dependencies.py` 的配置與依賴管理方式。

```text
gms/api/
├── dependencies.py             # 依賴注入工廠（Composition Root）
├── middleware.py               # 中間件配置
│
└── market/                     # Domain 層
    └── stock/                  # Sub-domain 層 (FU Container)
        └── _stock_analysis_api/  # Feature 級私有實作空間
            ├── _router.py          # Router 實作
            └── _schemas.py         # API 請求/回應模型
```

-----

### 7.2 依賴注入工廠（Dependencies）

`dependencies.py` 是 API 層的共用元件，負責組裝服務與資料存取層。這是實現依賴注入的關鍵。

#### 設計原則

- **工廠模式**：每個依賴都透過工廠函數建立
- **層級組裝**：從底層（Repository）到高層（Service）逐層組裝
- **介面導向**：返回介面型別，隱藏具體實作

#### 實作範例：依賴注入工廠

**檔案位置**：`gms/api/dependencies.py`

```python
"""
API 層依賴注入工廠
職責：組裝各層元件，實現依賴注入

這是 API 層的 Composition Root，
負責將具體實作組裝成可注入的依賴
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# Database Session
from gms.db.session import get_async_session

# Repository 層（具體實作）
from gms.db.market.stock.price import (
    IStockPriceRepository,
    StockPriceRepository
)

# Service 層（具體實作）
from gms.service.market.stock.analysis import StockAnalysisService

# Data Source（如果需要）
from tej.service.provider import TejStockPriceProvider
from core.interfaces.market import IStockPriceProvider

# === Database Session Factory ===

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    取得資料庫 Session

    使用 async generator 確保 Session 正確關閉
    """
    async with get_async_session() as session:
        yield session

# === Repository Factories ===

async def get_stock_price_repository(
    session: AsyncSession = Depends(get_db_session)
) -> IStockPriceRepository:
    """
    依賴注入工廠：建立股價 Repository

    注意：返回介面型別，隱藏具體實作
    """
    return StockPriceRepository(session)

# === Service Factories ===

async def get_analysis_service(
    repository: IStockPriceRepository = Depends(get_stock_price_repository)
) -> StockAnalysisService:
    """
    依賴注入工廠：建立股價分析服務

    透過 Depends 鏈式注入：
    1. 先注入 Repository
    2. 再將 Repository 注入 Service
    """
    return StockAnalysisService(price_repo=repository)

# === Data Source Factories（如果需要）===

def get_tej_provider() -> IStockPriceProvider:
    """
    依賴注入工廠：建立 TEJ 資料提供者

    從環境變數或配置檔讀取連線資訊
    """
    import os
    tej_db_url = os.getenv(
        "TEJ_DB_URL",
        "postgresql+asyncpg://user:pass@tej-db/tej"
    )
    return TejStockPriceProvider(db_url=tej_db_url)
```

-----

### 7.3 API 層依賴管理

API 層的依賴管理遵循統一 import 原則，不另設分層傳播機制。

#### 依賴來源

Router 實作檔案直接從各來源取得所需依賴：

| 依賴類型 | 來源 | Import 方式 |
|:---------|:-----|:------------|
| FastAPI 元件 | `fastapi`, `starlette` | 直接絕對 import（第三方套件） |
| Service 層型別 | `gms.service.*` | 正式絕對 import（跨公開邊界） |
| Core 異常 | `gms.core.exceptions` | 正式絕對 import（跨公開邊界） |
| DI 工廠函式 | `dependencies.py` | 相對 import（同層 API 模組內） |
| 同 Feature Schemas | `_schemas.py` | 相對 import（同 Feature 私有目錄內） |

#### `dependencies.py` 的定位

`dependencies.py` 是 API 層的**依賴注入工廠 (DI Factory)**，負責組裝具體的 Service / Repository 實例並透過 FastAPI 的 `Depends` 機制提供給 Router。

它**不是**依賴傳播骨幹或分層中介，而是一個普通的模組，Router 直接從中 import 所需的工廠函式即可。

```python
# gms/api/dependencies.py
"""API 層的依賴注入工廠."""

from sqlalchemy.ext.asyncio import AsyncSession
from gms.db.market.stock.price import StockPriceRepository
from gms.service.market.stock.analysis import StockAnalysisService

async def get_db_session() -> AsyncSession:
    """Provide database session."""
    ...

def get_stock_price_repository(
    session: AsyncSession = Depends(get_db_session),
) -> StockPriceRepository:
    """Provide stock price repository."""
    return StockPriceRepository(session)

def get_analysis_service(
    repo: StockPriceRepository = Depends(get_stock_price_repository),
) -> StockAnalysisService:
    """Provide stock analysis service."""
    return StockAnalysisService(repo)
```

-----

### 7.4 Router 實作

Router 直接使用絕對 import 取得外部依賴，使用相對 import 取得同模組的 DI 工廠與同 Feature 的 Schemas。

#### 設計原則

- **外部依賴**：FastAPI 元件、Service 型別、Core 異常，直接絕對 import
- **DI 工廠**：從同層 `dependencies.py` 以相對 import 取得
- **同 Feature Schemas**：從同 Feature 目錄內以相對 import 取得
- **依賴注入**：使用 FastAPI 的 `Depends` 機制

#### 實作範例：股票分析 Router

**檔案位置**：`gms/api/market/stock/_stock_analysis_api/_router.py`

```python
"""股票市場 API Router."""

from datetime import date
from typing import List, Optional
import logging

# 第三方套件：直接絕對 import
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

# 跨公開邊界：正式絕對 import
from gms.service.market.stock.analysis import (
    StockAnalysisService,
    VolumeAnalysisResult,
)
from gms.core.exceptions import BusinessLogicError, DataValidationError

# 同層 API 模組：DI 工廠
from ...dependencies import get_analysis_service

# 同 Feature 目錄內的 Schemas（內部協作）
from ._schemas import StockAnalysisResponse, ErrorResponse

logger = logging.getLogger(__name__)

# 建立 Router
router = APIRouter(
    prefix="/market/stocks",
    tags=["Market Analysis"],
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)

@router.get(
    "/{symbol}/volume-analysis",
    response_model=VolumeAnalysisResult,
    summary="成交量異常分析",
)
async def analyze_stock_volume(
    symbol: str,
    check_date: date = Query(..., description="分析日期"),
    service: StockAnalysisService = Depends(get_analysis_service),
):
    """Analyze stock volume anomalies."""
    try:
        return await service.check_abnormal_volume(symbol, check_date)
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.message))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))
    except Exception as e:
        logger.error(f"Unexpected error analyzing {symbol}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
```

**關鍵理解**：

- Router 不經過任何中介層，直接從各來源取得依賴
- `dependencies.py` 只是提供 DI 工廠函式的普通模組，不是傳播骨幹
- 依賴方向清晰：`dependencies.py` → Service/Repository，Router → `dependencies.py`

#### API Schemas

**檔案位置**：`gms/api/market/stock/_stock_analysis_api/_schemas.py`

```python
"""
API 請求與回應模型
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional, Dict
from decimal import Decimal

class StockAnalysisRequest(BaseModel):
    """股票分析請求"""
    symbol: str = Field(..., description="股票代碼")
    date: date = Field(..., description="分析日期")

class StockAnalysisResponse(BaseModel):
    """股票分析回應"""
    symbol: str
    date: date
    volume_analysis: Optional[Dict]
    technical_indicators: Optional[Dict]

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
        }
    )

class ErrorResponse(BaseModel):
    """錯誤回應"""
    error_code: str
    message: str
    detail: Optional[Dict] = None
```

-----

## 8. 應用程式組裝：Composition Root

本章節展示整個系統的「組裝工廠」，這是唯一同時知道所有具體實作的地方。

### 8.1 架構定位：Dependency Injection Container

> **關鍵時刻**：這是唯一同時導入 `tej`（實作）、`gms.db`（實作）與 `gms.etl`（邏輯）的地方。

Composition Root 的職責：

- **組裝元件**：將具體實作注入到抽象依賴
- **配置管理**：管理環境變數與設定
- **生命週期**：管理應用程式啟動與關閉
- **路由註冊**：組合所有 API 路由

-----

### 8.2 主應用程式

**檔案位置**：`gms/main.py`

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from datetime import date
from sqlalchemy import text
import logging

# === 具體實作導入（只在這裡！）===

# Database
from gms.db.session import AsyncSessionLocal, init_database
from gms.db.market.stock.price import StockPriceRepository

# Data Source
from tej.service.provider import TejStockPriceProvider

# ETL
from gms.etl.market.stock.sync_job import DailyStockSyncPipeline

# Service
from gms.service.market.stock.analysis import StockAnalysisService

# API
from gms.api.market.stock import router as stock_router

# Config
from gms.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# === 應用程式生命週期管理 ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用程式生命週期管理

    啟動時：
    - 初始化資料庫
    - 建立連線池
    - 載入快取

    關閉時：
    - 關閉資料庫連線
    - 清理資源
    """
    # === 啟動階段 ===
    logger.info("Starting application...")

    # 初始化資料庫
    await init_database()

    # 初始化資料源
    app.state.tej_provider = TejStockPriceProvider(
        db_url=settings.TEJ_DB_URL
    )

    logger.info("Application started successfully")

    yield  # 應用程式運行中

    # === 關閉階段 ===
    logger.info("Shutting down application...")

    # 清理資源
    if hasattr(app.state, "tej_provider"):
        await app.state.tej_provider.close()

    logger.info("Application shut down")

# === 建立應用程式 ===

app = FastAPI(
    title="wBiSaProj Stock Analysis System",
    version="1.0.0",
    lifespan=lifespan
)

# === 註冊路由 ===

app.include_router(stock_router)

# === 組裝 ETL Pipeline（範例端點）===

@app.post("/admin/etl/sync-prices")
async def trigger_price_sync(
    target_date: date,
    symbols: list[str] = None
):
    """
    Composition Root 範例：組裝 ETL Pipeline

    這是整個架構的精髓展示：
    1. 具體實作在這裡組裝
    2. Pipeline 只知道介面
    3. 完全符合 DIP 原則
    """
    async with AsyncSessionLocal() as session:
        # === 實例化具體元件 ===

        # 1. Source: TEJ Provider（實作 IStockPriceProvider）
        tej_provider = app.state.tej_provider

        # 2. Target: GMS Repository（實作 IStockPriceRepository）
        gms_repo = StockPriceRepository(session)

        # === 依賴注入（關鍵！）===
        # Pipeline 接收的是介面，不是具體實作
        pipeline = DailyStockSyncPipeline(
            source_provider=tej_provider,  # 注入 IStockPriceProvider
            target_repo=gms_repo           # 注入 IStockPriceRepository
        )

        # === 執行 ===
        result = await pipeline.run(target_date, symbols)

        return {
            "status": "success" if result.success else "failed",
            "extracted": result.total_extracted,
            "loaded": result.total_loaded,
            "failed_records": result.failed_records,
            "execution_time": result.execution_time
        }

# === 健康檢查 ===

@app.get("/health")
async def health_check():
    """系統健康檢查"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "data_source": "unknown"
    }

    # 檢查資料庫
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # 檢查資料源
    try:
        if await app.state.tej_provider.health_check():
            health_status["data_source"] = "healthy"
        else:
            health_status["data_source"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["data_source"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
```

-----

### 8.3 配置管理

**檔案位置**：`gms/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    應用程式設定
    使用環境變數覆寫預設值（pydantic-settings 自動依欄位名稱讀取同名環境變數）
    """

    # === Database ===
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/gms"

    # === TEJ Database ===
    TEJ_DB_URL: str = "postgresql+asyncpg://tej_user:pass@tej-db/tej"

    # === Application ===
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # === API ===
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # === ETL ===
    ETL_BATCH_SIZE: int = 1000
    ETL_RETRY_COUNT: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )
```

-----

## 9. 測試策略實作

本章節詳述 wBiSaProj 專案的測試實作細節，採用 **`pytest` + `pytest-asyncio`** 框架，並依據「測試金字塔」原則，針對不同系統與層級採用相應的隔離策略。

### 9.1 測試環境配置

建立所有系統共用的基礎測試環境，此處僅配置最核心的框架行為與共用工具，避免特定業務邏輯耦合。

#### 框架配置

**檔案位置**：`pytest.ini`  *(本範例以 `pytest.ini` 為示例；實際配置位置可能依專案治理決策採用 `pyproject.toml` 等替代方案，此處不構成唯一正式政策)*

```ini
[tool:pytest]
# 指定測試目錄，避免掃描虛擬環境或無關目錄
testpaths = tests

# 啟動 pytest-asyncio 的自動模式（支援 async def 測試）
asyncio_mode = auto

# 測試執行選項
addopts = -v --tb=short --strict-markers

# 定義測試標記（須與 docs/standards/testing.md §1.3 保持一致）
markers =
    unit: 單元測試（快速執行，無外部 I/O）
    integration: 整合測試（元件互動、使用 In-Memory DB）
    e2e: 端到端測試（完整流程、真實外部連線）
    llm: LLM 測試（需要人工觸發 LLM 互動，預設排除於一般自動化執行）
    slow: 慢速測試（執行時間 > 1秒）
    fast: 快速測試（執行時間極短）
    database: 資料庫測試（需要 DB Session）
    network: 網路測試（需要外部網路連線）
    external: 外部依賴測試（依賴外部服務）
    io: I/O 測試（檔案讀寫、序列化操作）
    auth: 認證測試（登入、權限驗證相關）
    api: API 測試（針對 Router Endpoint）
```

#### 通用 Fixtures

**檔案位置**：`tests/conftest.py`

```python
"""
全域測試配置
僅提供最基礎的共用工具，避免特定業務邏輯耦合
"""

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

@pytest.fixture(scope="function")
async def sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    """
    通用 SQLite In-Memory Session
    用於 DB 層與整合測試，提供快速、隔離的資料庫環境

    注意：具體的 Table Schema 建立 (Base.metadata.create_all)
    應在各別測試檔案或特定的 conftest 中執行
    """
    # 使用 aiosqlite 驅動
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    # 建立 Session 工廠
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()
```

-----

### 9.2 業務系統測試（GMS System Tests）

針對 GMS 業務系統的各層級進行測試。

> **架構定位**：GMS 是核心業務系統，需要完整的測試覆蓋
> **測試範圍**：DB Repository、Business Service、API Router、ETL Pipeline

#### 9.2.1 DB 層單元測試（Repository）

測試資料存取層的 SQL 語法正確性、ORM 映射與資料庫約束。

**測試重點**：
- SQL 語法正確性
- ORM 映射驗證
- 資料庫約束檢查

**隔離策略**：使用 In-Memory SQLite

**檔案位置**：`tests/gms/db/market/stock/price/stock_price_storage/test_stock_price_repository.py`

```python
"""
股價 Repository 單元測試
測試重點：CRUD 操作、查詢邏輯、批次處理
"""

import pytest
from datetime import date
from decimal import Decimal

from gms.db.market.stock.price import (
    StockPriceRepository,
    StockPriceModel,
    Base  # 導入 Base 以建立表格
)

@pytest.mark.unit
@pytest.mark.asyncio
async def test_repository_crud_operations(sqlite_session):
    """測試：基本 CRUD 操作"""
    # Arrange: 在 SQLite 中建立表格
    engine = sqlite_session.bind
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = StockPriceRepository(sqlite_session)
    target_date = date(2024, 1, 1)
    symbol = "2330"

    # Act: 寫入資料
    new_price = StockPriceModel(
        symbol=symbol,
        trade_date=target_date,
        open_price=Decimal("590.00"),
        high_price=Decimal("595.00"),
        low_price=Decimal("588.00"),
        close_price=Decimal("593.00"),
        volume=25000000
    )
    sqlite_session.add(new_price)
    await sqlite_session.commit()

    # Act: 讀取資料
    result = await repo.get_by_symbol_date(symbol, target_date)

    # Assert
    assert result is not None
    assert result.symbol == symbol
    assert result.close_price == Decimal("593.00")
    assert result.volume == 25000000
```

#### 9.2.2 Service 層單元測試（Business Logic）

測試純業務邏輯，完全不依賴資料庫。

**測試重點**：
- 業務邏輯正確性
- 異常處理
- 分支判斷

**隔離策略**：Mock Repository 介面

**檔案位置**：`tests/gms/service/market/stock/analysis/stock_analysis_api/test_stock_analysis_service.py`

```python
"""
股價分析服務單元測試
測試重點：業務邏輯、異常處理、計算正確性
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import date
from decimal import Decimal

from gms.service.market.stock.analysis import StockAnalysisService
from gms.db.market.stock.price import IStockPriceRepository

@pytest.mark.unit
@pytest.mark.asyncio
async def test_abnormal_volume_detection():
    """測試：成交量異常檢測"""
    # Arrange: Mock Repository
    mock_repo = MagicMock(spec=IStockPriceRepository)

    # 模擬回傳暴量資料（5000萬股）
    current_price = MagicMock()
    current_price.symbol = "2330"
    current_price.trade_date = date(2024, 1, 1)
    current_price.close_price = Decimal("600.00")
    current_price.volume = 50000000  # 暴量

    mock_repo.get_by_symbol_date = AsyncMock(
        return_value=current_price
    )

    # 模擬歷史平均（2000萬股）
    historical_prices = [
        MagicMock(volume=20000000) for _ in range(20)
    ]
    mock_repo.get_price_range = AsyncMock(
        return_value=historical_prices
    )

    service = StockAnalysisService(price_repo=mock_repo)

    # Act
    result = await service.check_abnormal_volume("2330", date(2024, 1, 1))

    # Assert
    assert result["is_abnormal"] is True
    assert result["abnormal_type"] == "surge"
    assert result["volume_ratio"] == 2.5

    # 驗證 Mock 被正確呼叫
    mock_repo.get_by_symbol_date.assert_called_once_with(
        "2330", date(2024, 1, 1)
    )
```

#### 9.2.3 API 層單元測試（Router）

測試 HTTP 端點的路由、參數驗證與狀態碼。

**測試重點**：
- HTTP 路由正確性
- 參數驗證
- 狀態碼回應

**隔離策略**：Mock Service（透過 FastAPI dependency_overrides）

**檔案位置**：`tests/gms/api/market/stock/stock_analysis_api/test_stock_analysis_router.py`

```python
"""
API Router 單元測試
測試重點：HTTP 端點、參數驗證、錯誤回應
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from gms.main import app
from gms.api.dependencies import get_analysis_service

@pytest.mark.unit
@pytest.mark.asyncio
async def test_volume_analysis_endpoint():
    """測試：成交量分析 API 端點"""
    # Arrange: Mock Service
    mock_service = AsyncMock()
    mock_service.check_abnormal_volume.return_value = {
        "symbol": "2330",
        "is_abnormal": True,
        "abnormal_type": "surge",
        "volume_ratio": 2.5
    }

    # 覆蓋依賴注入
    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    # Act: 發送 HTTP 請求
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/market/stocks/2330/volume-analysis",
            params={"check_date": "2024-01-01"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["is_abnormal"] is True
    assert data["abnormal_type"] == "surge"

    # 清理
    app.dependency_overrides.clear()
```

#### 9.2.4 ETL 層單元測試（Pipeline）

測試資料流協調邏輯。

**測試重點**：
- 資料流控制（Extract → Transform → Load）
- 轉換邏輯
- 錯誤處理

**隔離策略**：Mock Source 與 Target 介面

**檔案位置**：`tests/gms/etl/market/stock/sync_job/daily_sync_job/test_daily_stock_sync_pipeline.py`

```python
"""
ETL Pipeline 單元測試
測試重點：資料流控制、轉換邏輯、錯誤處理
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from decimal import Decimal

from gms.etl.market.stock.sync_job import DailyStockSyncPipeline
from core.interfaces.market import IStockPriceProvider
from gms.db.market.stock.price import IStockPriceRepository
from core.schemas.market import StockPriceDTO, MarketType

@pytest.mark.unit
@pytest.mark.asyncio
async def test_sync_pipeline_flow():
    """測試：ETL 資料同步流程"""
    # Arrange
    # Mock Source（模擬 TEJ 回傳標準 DTO）
    mock_source = MagicMock(spec=IStockPriceProvider)
    mock_source.get_daily_prices = AsyncMock(return_value=[
        StockPriceDTO(
            symbol="2330",
            trade_date=date(2024, 1, 1),
            open_price=Decimal("590.00"),
            high_price=Decimal("595.00"),
            low_price=Decimal("588.00"),
            close_price=Decimal("593.00"),
            volume=25000000,
            turnover=Decimal("14825000000"),
            market_type=MarketType.TWSE
        )
    ])

    # Mock Target（模擬 DB 寫入）
    mock_target = MagicMock(spec=IStockPriceRepository)
    mock_target.upsert_batch = AsyncMock(return_value=1)

    # Act
    pipeline = DailyStockSyncPipeline(mock_source, mock_target)
    result = await pipeline.run(date(2024, 1, 1))

    # Assert
    assert result.success is True
    assert result.total_extracted == 1
    assert result.total_loaded == 1

    # 驗證 Source 被呼叫
    mock_source.get_daily_prices.assert_called_once_with(
        date(2024, 1, 1)
    )

    # 驗證 Target 被呼叫
    mock_target.upsert_batch.assert_called_once()

    # 驗證資料轉換
    call_args = mock_target.upsert_batch.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]['symbol'] == "2330"
```

#### 9.2.5 GMS 整合測試（Integration）

> **路徑待定說明**：整合測試的目錄結構規則尚未在現行測試規範中正式定義。以下路徑僅為示意，不構成正式標準模板。

驗證 DB → Service → API 的完整路徑。

**測試重點**：
- 多層協作
- 完整資料流
- 真實業務場景

**策略**：使用 SQLite 覆蓋 DB，但不 Mock Service 與 Repository

**檔案位置**：`tests/gms/integration/test_market_flow.py`  *(整合測試路徑結構待後續正式定義)*

```python
"""
GMS 整合測試
測試重點：多層協作、完整流程、真實資料流
"""

import pytest
from httpx import AsyncClient, ASGITransport
from decimal import Decimal
from datetime import date

from gms.main import app
from gms.db.session import get_db_session
from gms.db.market.stock.price import StockPriceModel, Base

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_market_analysis_flow(sqlite_session):
    """
    整合測試：完整的市場分析流程
    DB 寫入 → Service 處理 → API 回應
    """
    # Arrange: 建立表格
    engine = sqlite_session.bind
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 覆蓋 DB Session
    app.dependency_overrides[get_db_session] = lambda: sqlite_session

    # 準備測試資料（暴量）
    test_data = StockPriceModel(
        symbol="2330",
        trade_date=date(2024, 1, 1),
        open_price=Decimal("590.00"),
        high_price=Decimal("595.00"),
        low_price=Decimal("588.00"),
        close_price=Decimal("593.00"),
        volume=99999999  # 暴量
    )
    sqlite_session.add(test_data)
    await sqlite_session.commit()

    # Act: 呼叫真實 API
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/market/stocks/2330/volume-analysis",
            params={"check_date": "2024-01-01"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "2330"
    assert data["is_abnormal"] is True  # 確認 Service 邏輯有執行

    # 清理
    app.dependency_overrides.clear()
```

-----

### 9.3 資料源系統測試（Data Source System Tests）

> **示例定位說明**：本節測試範例對應 §3 中 TEJ 系統的既有結構。由於 TEJ 系統尚未收斂至 FU Container 模型，以下測試路徑亦反映既有結構，不應被視為現行正式測試路徑模板。

驗證資料源系統（TEJ）作為獨立適配器的正確性。

> **架構定位**：TEJ 系統獨立於業務系統開發，擁有獨立的測試策略
> **測試重點**：適配邏輯與 Schema 相容性

#### 9.3.1 測試策略定位

資料源系統的測試著重於：

1. **適配邏輯（Adapter Logic）**：確保髒資料正確轉換為標準 DTO
2. **Schema 相容性**：確保 SQL 語法與真實資料庫 Schema 一致

#### 9.3.2 Service 層單元測試（Adapter Logic）

測試欄位映射與型別轉換邏輯。

**測試重點**：
- 欄位映射（Field Mapping）
- 型別轉換（Type Casting）
- 資料清理（Data Cleaning）

**隔離策略**：Mock Collector（模擬 DB 回傳的原始字典）

**檔案位置**：`tests/tej/service/test_provider.py`  *(TEJ 系統目前未採用 FU Container 結構，路徑待後續整理)*

```python
"""
TEJ Provider 適配器測試
測試重點：欄位映射、型別轉換、資料清理
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from decimal import Decimal

from tej.service.provider import TejStockPriceProvider
from core.schemas.market import StockPriceDTO, MarketType

@pytest.mark.unit
@pytest.mark.asyncio
async def test_tej_adapter_transformation():
    """測試：TEJ 資料轉換邏輯"""
    # Arrange: Mock Collector
    mock_collector = MagicMock()

    # 模擬 DB 回傳的原始資料（使用 TEJ 舊欄位名稱）
    mock_collector.fetch_raw_prices = AsyncMock(return_value=[
        {
            "coid": "2330  ",      # 有尾隨空白
            "mdate": date(2024, 1, 1),
            "open_d": 590.0,       # float 型別
            "high_d": 595.0,
            "low_d": 588.0,
            "close_d": 593.0,
            "vol": 25000.0,        # 張數（需要 × 1000）
            "amt": 14825000.0      # 千元（需要 × 1000）
        }
    ])

    provider = TejStockPriceProvider(db_url="mock://url")
    provider.collector = mock_collector  # 注入 Mock

    # Act
    results = await provider.get_daily_prices(date(2024, 1, 1))

    # Assert: 驗證轉換邏輯
    assert len(results) == 1
    dto = results[0]
    assert isinstance(dto, StockPriceDTO)
    assert dto.symbol == "2330"  # 空白已清除
    assert dto.open_price == Decimal("590.00")  # 轉為 Decimal
    assert dto.volume == 25000000  # 張轉股
    assert dto.turnover == Decimal("14825000000")  # 千元轉元
    assert dto.market_type == MarketType.TWSE  # 市場判斷
```

#### 9.3.3 Collector 層整合測試（SQL Verification）

驗證 SQL 執行與 Schema 相容性。

**測試重點**：
- SQL 語法正確性
- DB 連線管理
- Schema 欄位驗證

**策略**：連線真實測試資料庫（透過環境變數控制）

**檔案位置**：`tests/tej/collector/test_db_client.py`  *(TEJ 系統目前未採用 FU Container 結構，路徑待後續整理)*

```python
"""
TEJ Collector 整合測試
測試重點：SQL 執行、Schema 相容性、連線管理
"""

import pytest
import os
from datetime import date
from tej.collector.db_client import TejDbCollector

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("TEJ_TEST_DB_URL"),
    reason="需要設定 TEJ_TEST_DB_URL 環境變數"
)
@pytest.mark.asyncio
async def test_tej_sql_execution():
    """測試：SQL 執行與 Schema 驗證"""
    # Arrange
    db_url = os.getenv("TEJ_TEST_DB_URL")
    collector = TejDbCollector(db_url=db_url)

    # Act: 選擇已知有資料的歷史日期
    raw_data = await collector.fetch_raw_prices(date(2024, 1, 5))

    # Assert: 驗證 SQL 能執行且欄位正確
    assert isinstance(raw_data, list)

    if len(raw_data) > 0:
        row = raw_data[0]
        # 驗證必要欄位存在
        required_fields = [
            "coid",    # 股票代碼
            "mdate",   # 交易日期
            "open_d",  # 開盤價
            "high_d",  # 最高價
            "low_d",   # 最低價
            "close_d", # 收盤價
            "vol",     # 成交量
            "amt"      # 成交金額
        ]
        for field in required_fields:
            assert field in row, f"Missing field: {field}"

    # Cleanup
    await collector.close()
```

#### 9.3.4 TEJ 專屬 Fixtures

TEJ 系統專屬的測試資料與配置。

**檔案位置**：`tests/tej/conftest.py`

```python
"""
TEJ 資料源系統專屬測試配置
提供 TEJ 測試所需的 Fixtures
"""

import pytest
from datetime import date

@pytest.fixture
def tej_sample_raw_data():
    """提供 TEJ 原始資料範例"""
    return [
        {
            "coid": "2330  ",
            "mdate": date(2024, 1, 1),
            "open_d": 590.0,
            "high_d": 595.0,
            "low_d": 588.0,
            "close_d": 593.0,
            "vol": 25000.0,
            "amt": 14825000.0
        }
    ]

@pytest.fixture
def tej_test_config():
    """TEJ 測試環境配置"""
    return {
        "test_date": date(2024, 1, 5),
        "test_symbols": ["2330", "2317", "2454"]
    }
```

-----

### 9.4 測試執行

本專案使用 [Invoke](https://www.pyinvoke.org/) 作為測試執行的標準工具鏈。以下為日常開發中最常用的指令；完整的指令規格、參數說明與執行規範，請參閱 [測試規範 §1.4](standards/testing.md)。

#### 常用指令

```bash
# 執行一般測試（自動排除 LLM 測試）
inv test

# 以 project 為單位執行測試
inv test --project gms
inv test --project wutils

# 指定路徑或關鍵字過濾
inv test --path tests/gms/db/market/stock/price/
inv test --k test_stock_price

# 執行 LLM 測試（需人工觸發）
inv test.llm

# 測試覆蓋率報告
inv test.cov
```

> 本專案不建議在日常開發中直接呼叫 `pytest`。`inv test` 系列指令已整合必要的 marker 過濾與執行環境設定，確保測試行為與 CI/CD 流程一致。

-----

## 總結

本文件完整展示了 wBiSaProj 架構的實作指引，涵蓋從核心契約到應用組裝的所有層級。

### 架構精髓

1. **契約優先**：所有系統基於 Core 定義的標準契約
2. **介面隔離**：每一層只依賴介面，不依賴實作
3. **依賴注入**：具體實作延遲到 Composition Root 組裝
4. **測試友善**：透過介面輕鬆實現 Mock 測試

### 測試策略總結

透過完整的測試策略，我們確保了：

- **單元測試**：驗證各層邏輯的正確性
- **整合測試**：確認層級間協作無誤
- **隔離策略**：使用 SQLite 與 Mock 達成快速測試
- **覆蓋率追蹤**：監控測試的完整性

### 實現效益

透過這套架構，我們實現了：

- **高內聚**：每個模組職責單一明確
- **低耦合**：模組間只透過介面互動
- **易擴展**：可輕易新增資料源或更換實作
- **可測試**：所有元件都可獨立測試
- **可維護**：清晰的層級結構與依賴管理

這形成了一個真正符合 **SOLID 原則**與 **Clean Architecture** 精神的企業級系統架構。
