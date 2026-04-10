# Import 情境範例與解讀指南
## Python Import Scenarios & Interpretation Guide

> **文件定位**：本文件為 import 規範的**配套情境範例與解讀指南**，不是獨立的規範本體。
> 正式權威規範以 `docs/PROJECT_DESIGN-ARCHITECTURE.md`（§6.3 統一 Import 原則）與 `docs/standards/python_coding.md`（§2 導入規範）為準。

本文件以本專案既有架構為背景，針對常見 import 決策提供具體情境範例。  
其目的有二：

1. 幫助閱讀者建立更清晰的操作直覺
2. 確保規範撰寫者、審查者與實作者對規則的理解一致

---

### 8.1 同一 private 目錄中的兄弟檔案互相引用

```text
gms/
└── service/
    └── market/
        └── stock/
            └── profile/                        ← FU Container
                ├── __init__.py
                └── _stock_profile/             ← Feature 私有目錄
                    ├── _service.py             ← [source]
                    └── _validators.py          ← [target]
```

**正確：**

```python
from ._validators import validate_symbol
```

**錯誤：**

```python
from gms.service.market.stock.profile._stock_profile._validators import validate_symbol
```

**說明：**  
這是同一公開邊界內部的私有實作協作，應使用相對 Import。  
絕對路徑中出現 `_private`，違反 3.1。

---

### 8.2 一般實作檔跨公開邊界取得依賴

```text
gms/
└── service/
    └── market/
        └── stock/
            └── profile/                        ← FU Container（所屬容器）
                ├── __init__.py
                └── _stock_profile/             ← 私有目錄
                    └── _service.py             ← [source]
```

**正確（直接絕對 import）：**

```python
from gms.db.market.stock.profile import StockProfileRepository
```

**正確（透過 facade 整理）：**

```python
from .._contracts import StockProfileRepository
```

**說明：**  
實作檔案跨公開邊界取得依賴時，使用正式絕對 import 從目標公開容器導入。  
若同容器內多個實作檔案共用同一組依賴，可建立 facade-like private module 整理。

---

### 8.3 Business `service` 需要同系統內的 `db`

```text
gms/                                            ← 同一系統
├── db/
│   └── market/
│       └── stock/
│           └── profile/                        ← 目標 FU Container
│               ├── __init__.py                 ← 公開介面：匯出 StockProfileRepository
│               └── ...
│
└── service/
    └── market/
        └── stock/
            └── profile/                        ← 所屬 FU Container
                └── _stock_profile/
                    └── _service.py             ← [source]
```

**正確（直接絕對 import）：**

```python
# _service.py 中：跨公開邊界，使用正式絕對 import
from gms.db.market.stock.profile import StockProfileRepository
```

**正確（透過 facade 整理）：**

```python
from .._repositories import StockProfileRepository
```

**說明：**  
跨公開邊界取用其他公開容器的元件，使用正式絕對 import。  
若依賴較多，可建立 facade-like private module（如 `_repositories.py`）集中整理。

---

### 8.4 Business `service` 需要同系統內的 `gms/core`

```text
gms/                                            ← 同一系統
├── core/                                       ← System Core
│   └── exceptions.py                           ← 目標：DomainException
│
└── service/
    └── market/
        └── stock/
            └── profile/                        ← 所屬 FU Container
                └── _stock_profile/
                    └── _service.py             ← [source]
```

**正確：**

```python
from gms.core.exceptions import DomainException
```

**說明：**  
`gms.core` 是跨公開邊界的依賴，使用正式絕對 import 直接取用。

---

### 8.5 Data Source `service` 需要 `tej/core`

```text
tej/
├── core/                                       ← 分水嶺之外（System Core）
│   └── parser/
│       └── price_fields.py                     ← [target]：PriceFieldNormalizer
│
└── service/                                    ← 分水嶺（標準 Layer）
    └── market/
        └── stock/
            └── _provider.py                    ← [source]
```

`_provider.py` 位於 `service` Layer 內部，`tej/core` 位於 `service` Layer 之外。  
這是**跨越分水嶺**的依賴，應使用絕對 Import（§4）。

**正確（直接絕對 Import）：**

```python
from tej.core.parser import PriceFieldNormalizer
```

**建議：使用 Facade 集中管理跨分水嶺依賴：**

```text
tej/
└── service/
    └── market/
        └── stock/
            ├── _parsing.py                     ← Facade：集中跨分水嶺的絕對 Import
            └── _provider.py                    ← [source]
```

```python
# _parsing.py（Facade）— 跨越分水嶺，使用絕對 Import
from tej.core.parser import PriceFieldNormalizer
from tej.core.constants import PRICE_SCALE

# _provider.py（實作檔）— 同一分水嶺內部，使用相對 Import
from ._parsing import PriceFieldNormalizer
```

**說明：**  
跨越分水嶺到 `<system>/core` 的依賴，使用正式絕對 import。  
Facade 的價值在於將跨分水嶺的絕對 Import 集中在一處，同 Layer 的實作檔只需從本地 Facade 取用（分水嶺內部，相對 Import）。

---

### 8.6 `<system>/core` 內部的依賴管理

```text
gms/
└── core/                                       ← System Core
    ├── config.py                               ← [target]：RuntimeConfig
    └── cache/                                  ← 第一層 Toolkit（分水嶺）
        └── ttl/
            ├── _constants.py                   ← [target]：DEFAULT_TTL
            └── _policy.py                      ← [source]
```

**正確：**

```python
# 同一 Toolkit 內部（cache/ttl/ → cache/ttl/）— 相對 Import
from ._constants import DEFAULT_TTL

# 跨 Toolkit（cache → core 根層級）— 跨越分水嶺，絕對 Import
from gms.core.config import RuntimeConfig
```

**說明：**  
`<system>/core` 是 library-type module。  
System Core 的分水嶺為第一層 Toolkit（§4）：同一 Toolkit 內部使用相對 Import，跨 Toolkit 則使用絕對 Import。

---

### 8.7 任何模組需要 Project-Level Library

**正確：**

```python
from core.constants import Language
from wutils.time import DateRange
```

**說明：**  
Project-Level Library 應直接以正式絕對路徑導入。

---

### 8.8 任何模組需要 Third-party Package

**正確：**

```python
from sqlalchemy import select
from fastapi import APIRouter
```

**說明：**  
Third-party package 應直接導入。

---

### 8.9 `__init__.py` 從多層 private path 導出公開名稱

```text
gms/
└── db/
    └── market/
        └── stock/
            └── profile/                        ← FU Container
                ├── __init__.py                 ← [source]（邊界檔，此處承擔 Public API 組裝角色）
                └── _stock_profile/             ← 第一層 private（.）
                    └── _repository.py          ← 第二層 private（._stock_profile._repository）
```

**正確：**

```python
from ._stock_profile._repository import StockProfileRepository

__all__ = ["StockProfileRepository"]
```

**說明：**  
`__init__.py` 是 package 邊界檔；當其承擔 Public API 組裝角色時，可向內導入 private path 並整理為對外穩定介面。  
此特例僅限 `__init__.py`。

---

### 8.10 `__init__.py` 使用 alias 將私有實作名轉為公開 API 名稱

（同 8.9 結構）

```text
profile/                                        ← FU Container
├── __init__.py                                 ← [source]
└── _stock_profile/
    └── _repository.py                          ← 內含 _SqlStockProfileRepository
```

**正確：**

```python
from ._stock_profile._repository import _SqlStockProfileRepository as StockProfileRepository

__all__ = ["StockProfileRepository"]
```

**說明：**  
這是 `__init__.py` 特例最典型的合理用途：  
將技術實作名稱轉成對外穩定名稱。

---

### 8.11 一般實作模組不得模仿 `__init__.py` 做 private alias re-export

```text
profile/                                        ← FU Container
├── __init__.py
└── _stock_profile/
    ├── _repository.py                          ← 內含 _SqlStockProfileRepository
    └── _service.py                             ← [source]（不是 __init__.py）
```

你在 `_service.py` 中寫：

```python
from ._repository import _SqlStockProfileRepository as StockProfileRepository
```

**結論：禁止**

**說明：**  
這不是 `__init__.py`，不具公開介面組裝特權。  
若放行，將破壞 private component 邊界。

---

### 8.12 `__init__.py` 不應直接公開底線名稱

（同 8.9 結構）

**不建議：**

```python
from ._stock_profile._repository import _SqlStockProfileRepository

__all__ = ["_SqlStockProfileRepository"]
```

**說明：**  
`__init__.py` 特例的目的，是將私有實作整理為公開非底線名稱，而不是原樣暴露 private 名稱。

---

### 8.13 絕對 Import 路徑中出現 `_private`

```text
gms/
└── db/
    └── market/
        └── stock/
            └── profile/                        ← 公開容器（應從這裡的 __init__.py 取用）
                └── _stock_profile/             ← ❌ 絕對路徑穿透 private
                    └── _repository.py          ← ❌ 繼續穿透
```

**禁止：**

```python
from gms.db.market.stock.profile._stock_profile._repository import StockProfileRepository
```

**正確做法：**

```python
from gms.db.market.stock.profile import StockProfileRepository
```

**說明：**  
這是最典型違反 3.1 的情境。外部消費者應從公開容器的 `__init__.py` 取用。

---

### 8.14 一般模組穿透多層 private path

```text
profile/                                        ← FU Container
├── __init__.py                                 ← 只有這裡可以穿透
├── _some_module.py                             ← [source]（一般模組）
└── _stock_profile/                             ← 第一層 private
    └── _repository.py                          ← 第二層 private
```

若這句出現在 `_some_module.py` 中：

```python
from ._stock_profile._repository import StockProfileRepository
```

**結論：禁止**

**說明：**  
這屬於一般模組的深層 private 穿透（`._stock_profile._repository` = 兩層 private）。  
此類特權只保留給 `__init__.py`。

---

### 8.15 一般模組 import private component

```text
_stock_profile/
├── _utils.py                                   ← 內含公開的 helper 和私有的 _build_cache_key
└── _service.py                                 ← [source]
```

**禁止：**

```python
from ._utils import _build_cache_key
```

**同樣禁止：**

```python
from ._utils import _build_cache_key as build_cache_key
```

**但允許：**

```python
from ._utils import get_cache_key
```

**說明：**  
禁令的判定標的是 **component 名稱**上的底線，而非 module 名稱上的底線。  
`_utils` 是私有模組（同一邊界內可用相對 Import 存取），但其內部的 `_build_cache_key` 是 private component，僅限同一 `.py` 檔案內部使用（§3.3）。alias 不改變其 private 本質。

---

### 8.16 facade-like 模組整理外部依賴

```text
tej/
├── core/                                       ← 分水嶺之外（System Core）
│   ├── parser/                                 ← [target] A
│   └── constants.py                            ← [target] B
│
└── service/                                    ← 分水嶺（標準 Layer）
    └── market/
        └── stock/
            ├── _parsing.py                     ← facade-like 模組（兼任轉發與本地定義）
            └── _provider.py                    ← [source]
```

`_parsing.py` 的主要職責是提供解析相關工具，同時兼任跨分水嶺依賴的轉發入口：

```python
# _parsing.py — 本地定義 + 跨分水嶺依賴轉發
from tej.core.parser import PriceFieldNormalizer
from tej.core.constants import PRICE_SCALE

def stock_tick_parser(...):
    """本模組自身定義的解析工具"""
    ...
```

實作檔從同一處取得所有解析相關能力：

```python
# _provider.py — 同一分水嶺內部，使用相對 Import
from ._parsing import PriceFieldNormalizer, stock_tick_parser, PRICE_SCALE
```

**說明：**  
facade-like 模組的核心特徵是：一個有自身職責的私有模組，**同時**兼任依賴轉發的角色。  
它不是一個改了名字的 facade，而是一個本來就有存在理由的模組（如 `_parsing.py` 負責解析工具），順帶將相關的外部依賴整理在同一處。  
與 §8.17 的純 facade（`_facade.py`，僅負責轉發）形成對比。

---

### 8.17 若真的使用 `_facade.py`

```text
tej/
├── core/                                       ← 分水嶺之外（System Core）
│   ├── http_client/                            ← [target] A
│   └── mapping/                                ← [target] B
│
└── collector/                                  ← 分水嶺（標準 Layer）
    └── market/
        └── _facade.py                          ← Facade 檔案
```

**合理內容：**

```python
# _facade.py — 跨越分水嶺，使用絕對 Import；以轉發、alias、薄封裝為主
from tej.core.http_client import TejHttpClient
from tej.core.mapping import LegacyColumnMap
```

**不建議內容：**

```python
def transform_and_store_everything(...):
    ...
```

**說明：**  
若使用 `_facade.py` 這個名稱，其內容應以依賴轉發、alias、薄封裝為主，不應成為邏輯黑洞。

---

### 8.18 所有模組類型遵循同一套 import 原則

**錯誤理解：**  
「不同系統類型有不同的 import 機制。」

**正確認知：**  
所有模組類型（Library、Data Source、Business System）遵循同一套統一 import 原則：

- 跨公開邊界 → 正式絕對 import
- 邊界內部 → 相對 import
- 需要整理依賴 → facade-like private modules

差異僅在於常見的結構複雜度與 facade 使用頻率，而非適用不同的機制。

---

### 8.19 不是所有 private path 都不能被 import

**錯誤理解：**  
「只要 path 有 `_private`，任何地方都不能 import。」

**正確認知：**  
相對 Import 中，private path 出現在**第一層**是合法的（§3.2）。一般模組可以：

```python
# ✅ 合法：第一層 private module，取用公開 component
from ._utils import helper
from ._constants import DEFAULT_TIMEOUT
```

但不得穿透多層 private path，也不得取用 private component：

```python
# ❌ 禁止：多層 private 穿透（§3.2）
from ._feature_a._nested import helper

# ❌ 禁止：取用 private component（§3.3）
from ._utils import _build_cache_key
```

此外，`__init__.py` 作為 package 邊界檔，當承擔 Public API 組裝角色時，享有更寬的特例——可向內導入多層 private path 以組裝公開介面（§3.4）。

---

### 8.20 不是所有能用絕對 Import 的地方都應該用絕對 Import

**錯誤理解：**  
「只要寫得出合法絕對路徑，就應優先用絕對 Import。」

**正確認知：**  
本規範採用的是 **Bounded Absolute Imports**：  
跨公開邊界時使用絕對 Import；邊界內部仍應優先使用相對 Import 以維持內聚與封裝。

---

### 8.21 私有 sub-package 必須透過 `__init__.py` 匯出供兄弟模組使用

```text
parent_package/
├── __init__.py
├── _excel/
│   ├── __init__.py                             ← 匯出 Writer, Reader, RepairTool
│   ├── _writer.py
│   ├── _reader.py
│   └── _internal.py
└── _csv_converter.py                           ← [source]：需要 _excel 的 Writer
```

**正確：**

```python
# _excel/__init__.py — 匯出所有合法消費者可用的元件
from ._writer import Writer
from ._reader import Reader
from ._internal import RepairTool               # 僅供同 parent 內部使用
__all__ = ["Writer", "Reader", "RepairTool"]

# _csv_converter.py — 兄弟模組從 sub-package 的 __init__.py 取用
from ._excel import Writer
```

**錯誤：**

```python
# _csv_converter.py — 兩層 private 穿透，違反 §3.2
from ._excel._writer import Writer
```

**說明：**  
兄弟模組不享有 `__init__.py` 的穿透特例。私有 sub-package 必須透過其 `__init__.py` 匯出元件，才能讓同 parent 的兄弟模組合法取用。

---

### 8.22 父層 `__init__.py` 禁止整包 re-export 私有 sub-package

（承 8.21 結構）

**禁止：**

```python
# parent_package/__init__.py — 整包 re-export
import ._excel as excel
# 外部可存取 parent_package.excel.RepairTool → 意外暴露僅供內部使用的元件
```

**正確：**

```python
# parent_package/__init__.py — 逐一挑選 + 語意銜接
from ._excel import Writer as ExcelWriter, Reader as ExcelReader
# RepairTool 不在此列 → 外部看不見

__all__ = ["ExcelWriter", "ExcelReader"]
```

**說明：**  
sub-package 的 `__init__.py` 匯出的元件可能同時包含「對外開放」與「僅供內部使用」兩類。  
父層 `__init__.py` 必須從中二次篩選，不得以整包方式 re-export。  
攤平匯出時若元件名稱語意不足（如 `Writer` 在父層語境下過於模糊），應以 `as` alias 補充語境。

---

## `__init__.py` 作為 Package 邊界檔的情境範例

> 以下情境範例對應《架構篇》§4.4 與 `python_coding.md` §4 的擴充定義。
> `__init__.py` 不僅可以做 Public API 組裝，也可以承擔 metadata、輕量初始化等邊界職責——但嚴禁承擔實作邏輯。

---

### 8.23 允許的輕量初始化：`__version__` 與 metadata

```python
# wutils/__init__.py
"""wutils: General-purpose Python development toolkit."""

__version__ = "1.2.0"
__author__ = "wBiSa Team"
```

**結論：允許，可省略 `__all__`**

**說明：**  
`__init__.py` 僅包含 docstring 與 metadata，不承擔匯出角色。此時不強制要求 `__all__`。

---

### 8.24 允許的輕量初始化：package-level logger name

```python
# gms/service/__init__.py
"""GMS service layer."""

import logging

logger = logging.getLogger(__name__)
```

**結論：允許**

**說明：**  
`logging.getLogger(__name__)` 是可預測、無 I/O、無副作用的輕量初始化，屬於合法的邊界檔職責。

---

### 8.25 允許的輕量初始化：lazy import / compatibility alias

```python
# wutils/io/__init__.py
"""Tools for input/output operations."""

from ._json_io._json import json_dump, json_load
from ._pickle_io._pickle import pickle_dump, pickle_load

# Compatibility alias for legacy code
dump_json = json_dump

__all__ = ["json_dump", "json_load", "pickle_dump", "pickle_load", "dump_json"]
```

**結論：允許**

**說明：**  
Compatibility alias 是邊界檔的合法職責——為外部消費者提供穩定的命名過渡。此處有 re-export，因此必須定義 `__all__`。

---

### 8.26 禁止的壞味道：在 `__init__.py` 中定義實作 class

```python
# ❌ 禁止
# gms/service/market/stock/profile/__init__.py
class StockProfileService:
    """Stock profile business logic."""

    def __init__(self, repo):
        self._repo = repo

    def get_profile(self, symbol: str):
        return self._repo.find_by_symbol(symbol)

__all__ = ["StockProfileService"]
```

**結論：禁止**

**說明：**  
`StockProfileService` 是實作元件，應定義在 Feature 級私有目錄的私有模組中（如 `_stock_profile/_service.py`），再由 `__init__.py` re-export。`__init__.py` 嚴禁承擔實作定義。

---

### 8.27 禁止的壞味道：在 `__init__.py` 中放業務邏輯

```python
# ❌ 禁止
# gms/etl/market/__init__.py
from gms.core.interfaces import IStockPriceProvider

def sync_all_stock_prices(provider: IStockPriceProvider):
    """Synchronize all stock prices from provider."""
    symbols = provider.list_symbols()
    for symbol in symbols:
        data = provider.fetch(symbol)
        # ... complex processing ...

__all__ = ["sync_all_stock_prices"]
```

**結論：禁止**

**說明：**  
業務流程邏輯不得出現在 `__init__.py` 中，應搬移至私有模組。

---

### 8.28 禁止的壞味道：import-time 的重量級副作用

```python
# ❌ 禁止
# gms/db/__init__.py
from sqlalchemy import create_engine

# 在 import 時就建立 DB 連線
engine = create_engine("postgresql://localhost/gms")
Session = sessionmaker(bind=engine)
```

**結論：禁止**

**說明：**  
import-time 的 DB 連線是重量級副作用，會導致：僅 import 此 package 就觸發網路連線；測試環境被迫連接真實資料庫；模組載入順序造成不可預測的失敗。應改為延遲初始化或在 Composition Root 中處理。

---

### 8.29 `__all__` 要與不要：有 re-export 時必須有 `__all__`

```python
# ✅ 正確：有 re-export → 必須定義 __all__
# wutils/io/__init__.py
from ._json_io._json import json_dump, json_load

__all__ = ["json_dump", "json_load"]
```

```python
# ❌ 缺漏：有 re-export 但未定義 __all__
# wutils/io/__init__.py
from ._json_io._json import json_dump, json_load
# 缺少 __all__，外部消費者無法明確知道公開介面範圍
```

**說明：**  
當 `__init__.py` 承擔公開匯出角色（含有 re-export 語句），必須以 `__all__` 明確宣告對外介面，防止內部實作意外洩漏。

---

### 8.30 `__all__` 要與不要：僅 metadata / docstring 時可省略

```python
# ✅ 正確：無 re-export，僅 docstring + metadata → 可省略 __all__
# some_package/__init__.py
"""Internal utilities for data transformation."""

__version__ = "0.1.0"
```

**說明：**  
此 `__init__.py` 不承擔匯出角色，不存在需要控制的公開介面範圍，`__all__` 可省略。
