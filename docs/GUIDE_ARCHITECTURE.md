# wBiSaProj 架構實作指引

本文件提供 wBiSaProj 專案**架構設計**的實作建議與範例，作為開發團隊的技術參考指南。

## 1. 核心依賴管理：`_imports.py` 依賴閘門機制

本章節詳細說明專案中用以管理依賴、確保模組封裝的核心組織模式。本章節聚焦於 `_imports.py` 依賴閘門的運作機制，以及它如何與層級內的私有共用模組協作，確保依賴管理清晰且無循環。

### 1.1 機制概述：`_imports.py` 依賴閘門

`_imports.py` 是專案中管理**系統內部依賴**的核心模式，配合自動化工具實現依賴的向下傳播。這個機制確保：

- 每個 FU Container 是獨立封裝的單元
- 依賴關係清晰且易於管理
- 避免循環依賴和混亂的導入路徑

#### 核心檔案職責

`__init__.py` 與 `_imports.py` 是一對「鏡像概念」，它們共同定義了 FU Container 的存取邊界：

| 檔案 | 職責 (存取方向) | 規範 |
|:-----|:-----|:-----|
| `__init__.py` | **對外**：定義該容器的**公開介面 (Public API)** | **必須**定義 `__all__`，明確宣告所有對外暴露的元件 |
| `_imports.py` | **對內**：作為該容器的**統一依賴入口** | **必須**定義 `__all__`，明確宣告此層級引入的所有依賴 |

#### 管理範圍

`_imports.py` 管理**同一系統內**的所有依賴，包括：

- **外部依賴**：同一系統內，標準模組間的依賴（如 `gms.core` 或跨層級依賴）
- **內部依賴**：同一標準模組內，子模組間的相對導入

`_imports.py` **不管理**：

- 專案層級函式庫（如 `core`, `wutils`）
- 第三方套件（如 `sqlalchemy`, `fastapi`）

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

#### 原則一：管理範圍

`_imports.py` **只管理**系統內部的依賴關係，**不管理**專案層級函式庫或第三方套件：

```python
# ✅ 應該管理的：系統內部依賴
from gms.core import exceptions  # 同系統不同模組
# (註：此行應在 _imports.py 中，而非實作檔案中)

# ❌ 不應該管理的：專案級或第三方套件
# 這些應在各自需要的 .py 檔案中被「絕對導入」
from core.constants import Language  # 專案級
from sqlalchemy import select        # 第三方套件
from fastapi import APIRouter        # 第三方套件
```

#### 原則二：FU Container 封裝性

`_imports.py` 是依賴的「閘門」，而 Feature 級私有目錄內的實作檔案（`_models.py`, `_repository.py` 等）是「受保護的實作」，它們必須遵循嚴格的單向依賴規則：

- **實作檔案 (如 `_models.py`)**：
    - **嚴禁**跳出所屬的 FU Container。所有外部依賴**必須**從 FU Container 層級的 `_imports.py` 取得。
    - 由於實作檔案位於 Feature 級私有目錄內，需使用 `..` 回到 FU Container 層級來存取 `_imports.py`。
    - `_imports.py` 未提供的依賴（如專案級 `core` 或第三方套件）應自行絕對導入（見原則一）。

- **`_imports.py` 檔案**：
    - 是此規則的**唯一例外**。
    - 其職責就是向外查找依賴：
        - 繼承父層 `_imports.py`（`from .._imports import ...`）
        - 導入父層私有共用模組（例如：`from .._validators import validate_symbol`）
        - 導入兄弟模組（例如：`from ..trading_data import StockData`）

```python
# === 在 _user_profile/_repository.py (Feature 級私有目錄內的實作檔案) 中 ===

# ✅ 正確：從 FU Container 的 _imports.py 取得所有依賴（回上一層）
from .._imports import exceptions, UserRepository

# ✅ 正確：從同一 Feature 私有目錄內的其他檔案導入
from ._models import UserModel

# ❌ 錯誤：實作檔案嚴禁跳出 FU Container！
from ..._imports import something
from ...dto.user import UserDTO
```

```python
# === 在 _imports.py (閘門檔案) 中 ===

# ✅ 正確：作為閘門，向外查找依賴
from .._imports import BaseRepository  # 繼承父層 _imports.py
from ..trading_data import StockData  # 導入兄弟模組
from .._validators import validate_symbol  # 導入父層私有共用模組
```

#### 原則三：防止循環依賴

`_imports.py` 檔案**嚴格禁止**從其同層級的 Feature 級私有目錄或實作檔案中導入任何內容。

- **原因**：這會立即導致循環依賴（實作檔案依賴 `_imports.py`，而 `_imports.py` 反過來依賴實作檔案）。

- **允許的導入規則**：`_imports.py` 只允許以下三種導入方式：
    1. `from .._imports import ...`（繼承父層 `_imports.py`）
    2. `from .._<module> import ...`（導入父層私有共用模組，如 `_orm`、`_rules`）
    3. `from [相對路徑] import ...`（導入兄弟模組）

```python
# === 在 _imports.py (閘門檔案) 中 ===

# ✅ 正確：繼承父層
from .._imports import Base, BaseRepository

# ✅ 正確：導入兄弟模組（相對路徑）
from ..trading_data import StockData

# ✅ 正確：導入父層私有共用模組（相對路徑）
from .._validators import validate_symbol

# ❌ 錯誤：嚴禁導入 Feature 級私有目錄內的實作檔案！
from ._user_profile._models import UserProfile
from ._user_profile._repository import UserRepository

# ❌ 錯誤：嚴禁導入更上層檔案！
from ..._imports import Base, BaseRepository
from ..._rules import is_market_open
from ...user.profile import UserRepository
```

#### 原則四：`__all__` 規範

**`__init__.py` 和 `_imports.py` 都必須定義 `__all__`**

```python
# __init__.py - 定義公開介面
__all__ = ['UserProfile', 'UserProfileRepository']

# _imports.py - 定義依賴清單
__all__ = ['Base', 'exceptions', 'validators']
```

這確保了：

- 自動化工具能正確識別和傳播依賴
- 公開介面明確且可控
- 避免意外暴露內部實作

#### 原則五：自動化傳播機制

自動化工具（`inv dev.imports-update`）會將上層 `_imports.py` 的所有導入**轉換為 `from .._imports import ...`** 形式：

```python
# db/_imports.py 定義：
from gms.core import exceptions

# 執行工具後，db/user/_imports.py 會包含：
from .._imports import (  # 從父層導入
    exceptions
)
# 加上 user 層級特定的依賴...
```

#### 原則六：手動維護與自動傳播的分工

- **手動維護**：每層 `_imports.py` 負責手動導入所需的父層私有共用模組元件、兄弟模組。
- **自動傳播**：工具會自動將父層 `_imports.py` 的依賴向下傳播至所有子容器。

-----

### 1.4 層級結構與協作範例

本節透過完整的結構圖，展示 `_imports.py` 如何與層級私有共用模組協同運作：

- **`_imports.py`**：負責**傳播依賴**（垂直繼承）
- **層級私有共用模組**（如 `_orm/`、`_rules.py`）：提供**層級共用元件**
- **協作關鍵**：`_imports.py` 與私有共用模組**完全解耦**。下游的 FU Container 在其 `_imports.py` 中，**按需**、**手動**、透過**相對路徑**導入這些模組的元件。

#### 完整結構圖

以 GMS 系統的 DB 層為例，展示 `_imports.py` 的依賴傳播與私有共用模組的協同運作：

```text
gms/db/
├── _imports.py              # 1. DB Layer 層級（根）
│                            #    -> 導入 gms.core（系統級跨Layer依賴）
│
├── _orm/                    #    (DB Layer 私有共用模組：ORM 基礎元件)
│   ├── __init__.py
│   ├── base.py              #    (Base, BaseRepository)
│   └── mixins.py            #    (TimestampMixin, SoftDeleteMixin)
│
├── user/
│   ├── _imports.py          # 2. User Domain 層級
│   │                        #    -> 繼承 (1)：自動從父層傳播
│   # (可視需求建立具語義的私有共用模組)
│   └── profile/
│       └── _imports.py      # 3. User-Profile FU Container 層級
│                            #    -> 繼承 (2)：自動從父層傳播
│                            #    -> (視需求)手動導入父層私有共用模組
│                            #    例如：from .._orm.base import Base, BaseRepository
│                            #          from .._orm.mixins import TimestampMixin, SoftDeleteMixin
│
└── market/
    ├── _imports.py          # 4. Market Domain 層級
    │                        #    -> 繼承 (1)：自動從父層傳播
    │
    ├── _rules.py            #    (Market Domain 私有共用模組：is_market_open)
    │
    └── stock/
        ├── _imports.py      # 5. Stock Sub-domain 層級
        │                    #    -> 繼承 (4)：自動從父層傳播
        │                    #    -> (視需求)手動導入父層私有共用模組
        │                    #    例如：from .._rules import is_market_open
        │
        ├── _calculators.py  #    (Stock Sub-domain 私有共用模組：calculate_moving_average)
        │
        ├── _validators.py   #    (Stock Sub-domain 私有共用模組：validate_symbol, StockDataValidator)
        │
        ├── profile/
        │   ├── __init__.py
        │   ├── _imports.py  # 6. Stock-Profile FU Container 層級
        │   │                #    -> 繼承 (5)：自動從父層傳播
        │   │                #    -> (視需求)手動導入父層私有共用模組
        │   │                #    例如：from .._validators import validate_symbol
        │   │                #    -> 手動導入兄弟模組 trading_data
        │   │                #    例如：from ..trading_data import StockData
        │   │
        │   └── _stock_profile/      # stock-profile Feature 的私有實作空間
        │       ├── _models.py
        │       └── _repository.py
        │
        └── trading_data/
            ├── __init__.py
            ├── _imports.py  # 7. Stock-Trading-Data FU Container
            │                #    -> 繼承 (5)：自動從父層傳播
            │                #    -> (視需求)手動導入父層私有共用模組
            │                #    例如：from .._calculators import calculate_moving_average
            │                #          from .._validators import StockDataValidator
            │
            └── _stock_trading_data/  # stock-trading-data Feature 的私有實作空間
                ├── _models.py
                └── _repository.py
```

#### 協作說明

從上述結構可以看到 `_imports.py` 的**累加傳播（Cumulative Propagation）協作模式**。此模式嚴格遵循 1.3 節所定義的導入原則（特別是原則三），確保 `_imports.py` 檔案的職責清晰且無循環依賴。

**1. 依賴傳播鏈的累加機制**

`_imports.py` 傳播鏈的內容**不是固定的**，而是**由上到下動態累加**的。在每一個層級，它會彙總三種來源的依賴：

1. **繼承父層依賴**：透過 `from .._imports import ...`（規則 1）繼承其父層 `_imports.py` 的所有依賴
2. **添加父層私有共用模組**：透過 `from .._<module> import ...`（規則 2）導入其直屬父層中具語義命名的私有共用元件
3. **添加兄弟模組**：透過 `from ..[sibling] import ...`（規則 3）導入其兄弟模組的公開介面

然後，它會將這三部分**合併**到自己的 `__all__` 中，再傳遞給下一層。

**2. 層級私有共用模組**

層級私有共用模組（如 `db/_orm/`）是層級私有的。它**不會**被其同層的 `_imports.py`（`db/_imports.py`）導入（因為這違反原則三），而是等待其**子層級**的 `_imports.py`（`market/_imports.py` 或 `user/_imports.py`）透過規則 2 來導入。

**3. 依賴彙總的完整流程（以檔案 6 為例）**

- **`db/_imports.py`（檔案 1 - 根）**
    - 職責：啟動傳播鏈。
    - 導入：`from gms.core import ...`（假設導入 `exceptions`，遵循原則一）。
    - `__all__ = ['exceptions']`
    - （它**不能**導入同層的 `db/_orm/`，遵循原則三）。

- **`market/_imports.py`（檔案 4 - Domain 層）**
    - **繼承父層依賴**：`from .._imports import exceptions`（來自檔案 1）。
    - **添加父層私有共用模組**：`from .._orm.base import Base`（來自 `db/_orm/`）。
    - `__all__ = ['exceptions', 'Base']`（內容累加了）。

- **`stock/_imports.py`（檔案 5 - Sub-domain 層）**
    - **繼承父層依賴**：`from .._imports import exceptions, Base`（來自檔案 4）。
    - **添加父層私有共用模組**：`from .._rules import is_market_open`（來自 `market/_rules.py`）。
    - `__all__ = ['exceptions', 'Base', 'is_market_open']`（內容再次累加）。

- **`profile/_imports.py`（檔案 6 - FU Container）**
    - **繼承父層依賴**：`from .._imports import exceptions, Base, is_market_open`（來自檔案 5）。
    - **添加父層私有共用模組**：`from .._validators import validate_symbol`（來自 `stock/_validators.py`）。
    - **添加兄弟模組**：`from ..trading_data import StockData`（來自 `stock/trading_data`）。
    - `__all__` 彙總了所有依賴，供 `_repository.py` 等實作檔案使用。

**關鍵理解**

`_imports.py` 傳播鏈**並非**只傳遞頂層的 `gms.core`，而是像一個滾雪球，**在每一層都會累加**來自「父層私有共用模組」和「兄弟模組」的依賴，使其內容越來越豐富，最終在 FU Container 層級提供所有需要的依賴。

此機制完美地遵守了「原則三」（沒有任何檔案導入同層的私有共用模組），同時實現了強大且清晰的依賴傳播，完全避免了循環依賴。

-----

### 1.5 實際範例

以下範例展示了在 1.4 節的結構圖與「累加傳播」模式下，各層級 `_imports.py` 的實際內容。

#### 1.5.1 DB 層的 `_imports.py`（Layer 根）

此檔案是 DB 層依賴傳播的「根源」，它**僅**導入 `[system]/core` 的依賴並向下傳播。

```python
# gms/db/_imports.py (對應結構圖檔案 1)
"""
DB 層的統一依賴管理（根）
職責：導入「系統級外部依賴」並向下傳播
"""
# 外部依賴：從系統級 core 導入
from gms.core import (
    constants,
    exceptions,
    utils,
    validators
)

# 嚴禁導入同層私有共用模組（違反原則三）
# from ._orm.base import Base  # ❌ 錯誤！

# 必須定義 __all__ 供自動化工具使用
__all__ = [
    # 從 gms.core 導入的
    'constants',
    'exceptions',
    'utils',
    'validators',
]
```

**關鍵理解**：

- `db/_imports.py` 作為根，啟動了依賴傳播鏈。
- 它**不能**導入其同層的 `db/_orm/`（違反原則三）。

-----

#### 1.5.2 Domain / Sub-domain 層的 `_imports.py`（累加層）

這些中間層的 `_imports.py` 是「累加傳播」的核心。它們繼承上層依賴，並**主動**導入其**直屬父層**的私有共用模組元件，使其內容「滾雪球」式地增長。

##### Market Domain 層級

```python
# gms/db/market/_imports.py (對應結構圖檔案 4)
"""Market Domain 的依賴管理（累加傳播）"""

# === (繼承) 自動化工具從 db/_imports.py (檔案 1) 傳播而來 ===
from .._imports import (
    constants,
    exceptions,
    utils,
    validators
)
# === 自動傳播內容結束 ===

# === (擴展) 手動導入「父層私有共用模組」的依賴（規則 2） ===
# 導入 db/_orm/ 內的元件
from .._orm.base import Base, BaseRepository
from .._orm.mixins import TimestampMixin, SoftDeleteMixin

# 必須定義 __all__（彙總 繼承 + 擴展）
__all__ = [
    # 1. 從父層傳播的 (gms.core)
    'constants',
    'exceptions',
    'utils',
    'validators',

    # 2. 本層加入的 (db/_orm)
    'Base',
    'BaseRepository',
    'TimestampMixin',
    'SoftDeleteMixin',
]
```

##### Stock Sub-domain 層級

```python
# gms/db/market/stock/_imports.py (對應結構圖檔案 5)
"""Stock Sub-domain 的依賴管理（累加傳播）"""

# === (繼承) 自動化工具從 market/_imports.py (檔案 4) 傳播而來 ===
from .._imports import (
    # 來自 gms.core
    constants,
    exceptions,
    utils,
    validators,

    # 來自 db/_orm（由檔案 4 累加而來）
    Base,
    BaseRepository,
    TimestampMixin,
    SoftDeleteMixin,
)
# === 自動傳播內容結束 ===

# === (擴展) 手動導入「父層私有共用模組」的依賴（規則 2） ===
# 導入 market/_rules.py 的元件
from .._rules import is_market_open

# 必須定義 __all__（彙總 繼承 + 擴展）
__all__ = [
    # 1. 從父層傳播的 (gms.core + db/_orm)
    'constants',
    'exceptions',
    'utils',
    'validators',
    'Base',
    'BaseRepository',
    'TimestampMixin',
    'SoftDeleteMixin',

    # 2. 本層加入的 (market/_rules)
    'is_market_open',
]
```

**關鍵理解**：

- `stock/_imports.py`（檔案 5）的 `__all__` 中，自動包含了來自 `gms.core` 和 `db/_orm/` 的所有依賴。
- 依賴鏈的內容在每一層都變得更豐富。

-----

#### 1.5.3 FU Container 的 `_imports.py`（最終彙總）

由於依賴鏈（檔案 5）已經攜帶了大部分的上層依賴，FU Container（檔案 6）的職責**大幅簡化**了。

```python
# gms/db/market/stock/profile/_imports.py (對應結構圖檔案 6)
"""Stock Profile FU 的依賴管理（最終彙總）"""

# === (繼承) 自動化工具從 stock/_imports.py (檔案 5) 傳播而來 ===
from .._imports import (
    # 來自 gms.core
    constants,
    exceptions,
    utils,
    validators,

    # 來自 db/_orm
    Base,
    BaseRepository,
    TimestampMixin,
    SoftDeleteMixin,

    # 來自 market/_rules
    is_market_open,
)
# === 自動傳播內容結束 ===

# === (擴展) 手動導入「父層私有共用模組」的依賴（規則 2） ===
# 導入 stock 層級的私有共用模組
from .._calculators import calculate_moving_average
from .._validators import (
    validate_symbol,
    StockDataValidator,
)

# === (擴展) 手動導入「兄弟模組」依賴（規則 3） ===
# 導入兄弟模組 trading_data
from ..trading_data import StockTradingData

# 必須定義 __all__（彙總 繼承 + 擴展）
__all__ = [
    # 1. 從父層傳播的 (gms.core + db/_orm + market/_rules)
    'constants',
    'exceptions',
    'utils',
    'validators',
    'Base',
    'BaseRepository',
    'TimestampMixin',
    'SoftDeleteMixin',
    'is_market_open',

    # 2. 本層加入的 (stock/_calculators + stock/_validators)
    'calculate_moving_average',
    'validate_symbol',
    'StockDataValidator',

    # 3. 本層加入的 (兄弟模組)
    'StockTradingData'
]
```

**關鍵理解**：

- `profile/_imports.py` 成為依賴彙總點。
- 它繼承了 `gms.core`、`db/_orm/`、`market/_rules.py` 的所有依賴。
- 它**僅需**手動導入其**直屬父層**的私有共用模組（`stock/_calculators.py`、`stock/_validators.py`）和**兄弟模組** `trading_data`。
- 導入路徑變得非常簡潔，不再有 `....` 或 `...` 的複雜相對路徑。

-----

#### 1.5.4 FU Container 內部實作檔案範例

此範例展示了 Feature 級私有目錄中的實作檔案（`_models.py`）如何體現「依賴來源清晰性」原則。**`_imports.py` 體系的抽象，確保了此檔案無需關心依賴管理的具體模式。**

```python
# gms/db/market/stock/profile/_stock_profile/_models.py
"""Stock Profile FU 的 ORM 模型定義（位於 stock-profile Feature 的私有實作空間內）"""

# 體現原則一：第三方套件（sqlalchemy）必須在此直接導入
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date
from typing import List

# 體現原則一：專案級依賴（core）也必須在此直接導入（如果需要的話）
# from core.interfaces import ISomeInterface

# 體現原則二：系統內部依賴全部來自 FU Container 的 _imports，來源清晰
# 注意：由於實作檔案位於 Feature 級私有目錄內，需使用 `..` 回到 FU Container 層級
from .._imports import (
    Base,                 # 來自 db/_orm（由繼承取得）
    TimestampMixin,       # 來自 db/_orm（由繼承取得）
    is_market_open,       # 來自 market/_rules（由繼承取得）
    validate_symbol,      # 來自 stock/_validators（由本層 _imports 導入）
    StockTradingData,     # 來自兄弟模組（由本層 _imports 導入）
)

class StockProfile(Base, TimestampMixin):
    """股票基本資料模型"""
    __tablename__ = "stock_profiles"

    symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    listing_date: Mapped[Date] = mapped_column(Date)

    # 關聯：一對多關係
    trading_data: Mapped[List["StockTradingData"]] = relationship(
        back_populates="stock"
    )

    def __post_init__(self):
        """初始化後驗證"""
        # 驗證 symbol
        if not validate_symbol(self.symbol):
            raise ValueError(f"Invalid stock symbol: {self.symbol}")

        # 驗證市場狀態（範例）
        if self.market == 'TWSE' and not is_market_open(self.listing_date):
            # 處理邏輯
            pass
```

**關鍵理解**：

- `_models.py` 檔案**完全不需要**知道 `_imports.py` 內部的依賴管理發生了多大的變化。
- 它只需要 `from .._imports import ...`（回到 FU Container 層級）就能獲取所需的一切。
- 這體現了「封裝性」原則：實作檔案不會跳出 FU Container，`_imports.py` 成功地將架構的複雜性對內隱藏。

-----

#### 1.5.5 協作模式小結

透過上述範例，我們可以看到**「累加傳播」**協作流程：

1. **`_imports.py` 傳播鏈（檔案 1）**：
    - `db/_imports.py` 作為根，僅導入 `gms.core` 並啟動傳播鏈。

2. **層級私有共用模組**：
    - 以具語義名稱命名（如 `_orm/`、`_rules.py`），作為獨立的、**層級私有**的元件庫存在。

3. **`_imports.py` 累加層（檔案 4, 5）**：
    - 中間層（Domain, Sub-domain）的 `_imports.py` 成為「累加器」。
    - 它們**繼承父層依賴**：`from .._imports import ...` 來獲取已有的依賴。
    - 它們**添加父層私有共用模組**：透過 `from .._<module> import ...` 來主動導入其直屬父層的私有共用元件。
    - 它們將兩者彙總到 `__all__` 中，使依賴鏈「滾雪球」式地增長。

4. **FU Container 的 `_imports.py`（檔案 6）**：
    - 作為**最終的依賴消費者**。
    - **繼承父層依賴**：透過 `from .._imports import ...` 獲取包含 `gms.core` 和所有父層私有共用模組元件的豐富依賴。
    - **添加父層私有共用模組**：僅需導入其直屬父層的私有共用模組和兄弟模組（`trading_data`）的依賴。

5. **實作檔案**（`_models.py`）：
    - **保持簡潔**。透過 `from .._imports import ...`（回到 FU Container 層級）取得所有依賴，完全不受架構變革影響。

**這形成了一個更清晰、更健壯、無循環依賴的依賴管理體系**。它透過在中間層主動彙總私有共用模組的元件，換取了 FU Container 層依賴導入的極大簡潔性。

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
        decimal_places=2,
        description="開盤價"
    )
    high_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="最高價"
    )
    low_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="最低價"
    )
    close_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
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
├── _imports.py                 # 根依賴管理
├── _orm/                       # DB 層私有共用模組（ORM 基礎元件）
│   ├── base.py                 # Base, BaseRepository
│   └── mixins.py               # TimestampMixin
└── market/                     # Domain
    └── stock/                  # Sub-domain
        └── price/              # FU Container (股價功能單元)
            ├── __init__.py     # 公開介面
            ├── _imports.py     # 內部依賴管理
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
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from .._imports import BaseRepository
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
├── _imports.py                 # 根依賴管理 (統一導入 DB 介面)
├── _validators.py              # 業務驗證器
├── _calculators.py              # 業務計算器
│
└── market/
    └── stock/
        └── analysis/           # FU Container: 股價分析服務
            ├── __init__.py
            ├── _imports.py     # 內部依賴
            └── _stock_analysis_api/  # Feature 級私有實作空間
                ├── _service.py     # 業務邏輯實作
                └── _dto.py         # Service 層 DTO
```

-----

### 5.2 Service 層依賴管理

Service 層的 `_imports.py` 統一管理對外部層級的依賴。

**檔案位置**：`gms/service/_imports.py`

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

# 從 FU Container 的 _imports 取得介面（DIP）
from .._imports import (
    IStockPriceRepository,
    BusinessLogicError,
    DataValidationError,
    StockPriceDTO
)

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
├── _imports.py                 # 根依賴管理
├── _validators.py              # 資料驗證器
├── _transformers.py             # 資料轉換器
│
└── market/
    └── stock/
        └── sync_job/           # FU Container: 每日同步作業
            ├── __init__.py
            ├── _imports.py
            └── _daily_sync_job/    # Feature 級私有實作空間
                ├── _pipeline.py    # ETL 流程控制
                ├── _extractor.py   # 抽取邏輯
                └── _loader.py      # 載入邏輯
```

-----

### 6.2 ETL 層依賴管理

ETL 層需要同時依賴資料源介面與資料庫介面。

**檔案位置**：`gms/etl/_imports.py`

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

# 從 FU Container 的 _imports 取得兩個關鍵介面
from .._imports import (
    IStockPriceProvider,     # 來自 Core（代表 TEJ）
    IStockPriceRepository,   # 來自 DB（代表 GMS DB）
    StockPriceDTO,
    DataSourceError,
    BusinessLogicError
)

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
from .._imports import IStockPriceRepository

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

本章節展示如何建立 RESTful API 層，並正確運用 `_imports.py` 機制管理依賴。

### 7.1 架構定位：HTTP Interface Adapter

API 層的核心職責：

- **HTTP 處理**：處理請求與回應的轉換
- **參數驗證**：驗證並轉換輸入參數
- **錯誤轉換**：將業務異常轉為適當的 HTTP 狀態碼
- **依賴注入**：透過 FastAPI 的 Depends 機制注入服務

> **實作重點**：利用 `dependencies.py` 定義依賴注入工廠，並透過 `_imports.py` 的傳播鏈將其傳遞給 Router 使用。

#### 目錄結構

展示 API 層如何組織，特別注意 `dependencies.py` 與 `_imports.py` 的配置。

```text
gms/api/
├── _imports.py                 # API 層根依賴管理（不含 dependencies）
├── dependencies.py             # 依賴注入工廠（Composition Root）
├── middleware.py               # 中間件配置
│
└── market/                     # Domain 層
    ├── _imports.py             # 中間層依賴管理（在此導入 dependencies）
    └── stock/                  # Sub-domain 層 (FU Container)
        ├── _imports.py         # 末端依賴管理（自動繼承）
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

### 7.3 依賴管理傳播鏈

為了避免循環依賴，我們採用「根層忽略、中層導入、末端繼承」的策略來傳遞 dependencies。

#### 傳播策略說明

| 層級 | 策略 | 說明 |
|:-----|:-----|:-----|
| **根層** | 忽略 dependencies | 避免 `_imports.py` 與 `dependencies.py` 循環依賴 |
| **中層** | 手動導入 | 使用相對路徑 `..dependencies` 導入 |
| **末端** | 自動繼承 | 從父層 `_imports.py` 獲得所有依賴 |

#### 層級 1：根層依賴管理

**檔案位置**：`gms/api/_imports.py`

```python
"""
API 層根依賴管理

關鍵設計：
- 不導入同層的 dependencies.py（避免循環依賴）
- 只導入 FastAPI 元件與 Service 型別
- dependencies 將在下一層被導入
"""

# FastAPI 核心元件
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# HTTP 狀態碼
from starlette import status

# Service 層型別（供 Type Hint 使用）
from gms.service.market.stock.analysis import (
    StockAnalysisService,
    VolumeAnalysisResult,
    TechnicalIndicators
)

# Core 異常
from core.exceptions import (
    BusinessLogicError,
    DataValidationError
)

__all__ = [
    # FastAPI 元件
    'APIRouter',
    'Depends',
    'HTTPException',
    'Query',
    'Body',
    'JSONResponse',
    'HTTPBearer',
    'HTTPAuthorizationCredentials',

    # HTTP 狀態
    'status',

    # Service 型別
    'StockAnalysisService',
    'VolumeAnalysisResult',
    'TechnicalIndicators',

    # 異常
    'BusinessLogicError',
    'DataValidationError',
]
```

#### 層級 2：中間層依賴管理

**檔案位置**：`gms/api/market/_imports.py`

```python
"""
Market Domain API 的依賴管理

關鍵設計：
- 繼承父層所有依賴
- 手動導入 dependencies（關鍵步驟！）
- 將 dependencies 加入傳播鏈
"""

# === 自動繼承：從父層 _imports.py 獲得 ===
from .._imports import (
    # FastAPI 元件
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Body,
    JSONResponse,
    status,

    # Service 型別
    StockAnalysisService,
    VolumeAnalysisResult,
    TechnicalIndicators,

    # 異常
    BusinessLogicError,
    DataValidationError,
)

# === 手動導入：父層的 dependencies.py ===
# 關鍵！在中間層導入 dependencies
from ..dependencies import (
    get_db_session,
    get_stock_price_repository,
    get_analysis_service,
    get_tej_provider,
)

__all__ = [
    # === 繼承的元件 ===
    'APIRouter',
    'Depends',
    'HTTPException',
    'Query',
    'Body',
    'JSONResponse',
    'status',

    'StockAnalysisService',
    'VolumeAnalysisResult',
    'TechnicalIndicators',

    'BusinessLogicError',
    'DataValidationError',

    # === 新增的依賴工廠（關鍵！）===
    'get_db_session',
    'get_stock_price_repository',
    'get_analysis_service',
    'get_tej_provider',
]
```

#### 層級 3：末端依賴管理

**檔案位置**：`gms/api/market/stock/_imports.py`

```python
"""
Stock API 的依賴管理

關鍵設計：
- 完全繼承父層
- 不需要額外導入
- 已包含所有需要的依賴工廠
"""

# === 完整繼承：包含 dependencies ===
from .._imports import (
    # FastAPI 元件
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Body,
    JSONResponse,
    status,

    # Service 型別
    StockAnalysisService,
    VolumeAnalysisResult,
    TechnicalIndicators,

    # 異常
    BusinessLogicError,
    DataValidationError,

    # 依賴工廠（從中間層傳播而來）
    get_analysis_service,
    get_tej_provider,
)

# （注意：_schemas.py 已移入 Feature 級私有目錄 _stock_analysis_api/ 中，
#  依原則三，_imports.py 不從 Feature 目錄導入。
#  _router.py 直接在 Feature 目錄內以 from ._schemas import ... 取得。）

__all__ = [
    # === 繼承的元件 ===
    'APIRouter',
    'Depends',
    'HTTPException',
    'Query',
    'Body',
    'JSONResponse',
    'status',

    'StockAnalysisService',
    'VolumeAnalysisResult',
    'TechnicalIndicators',

    'BusinessLogicError',
    'DataValidationError',

    'get_analysis_service',
    'get_tej_provider',
]
```

-----

### 7.4 Router 實作

Router 透過 `_imports.py` 取得所有依賴，保持程式碼簡潔且易於維護。

#### 設計原則

- **雙重來源**：外部依賴從 `._imports` 取得，同 Feature 的 Schemas 從 `._schemas` 取得
- **依賴注入**：使用 FastAPI 的 Depends 機制
- **錯誤處理**：將業務異常轉換為 HTTP 回應

#### 實作範例：股票分析 Router

**檔案位置**：`gms/api/market/stock/_stock_analysis_api/_router.py`

```python
"""
股票市場 API Router
透過 _imports.py 取得所有依賴
"""

from datetime import date
from typing import List, Optional
import logging

# 單一 import 來源：從 FU Container 的 _imports 取得一切
from .._imports import (
    # FastAPI 元件
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,

    # Service 與型別
    StockAnalysisService,
    VolumeAnalysisResult,

    # 依賴工廠（關鍵！）
    get_analysis_service,

    # 異常
    BusinessLogicError,
    DataValidationError,
)

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
    description="分析指定股票的成交量是否出現異常（暴量或縮量）"
)
async def analyze_stock_volume(
    symbol: str,
    check_date: date = Query(..., description="分析日期"),
    service: StockAnalysisService = Depends(get_analysis_service)
):
    """
    成交量異常分析端點

    透過 Depends(get_analysis_service) 注入服務，
    get_analysis_service 是從 _imports.py 傳播而來
    """
    try:
        # 呼叫 Service 層邏輯
        result = await service.check_abnormal_volume(symbol, check_date)
        return result

    except DataValidationError as e:
        # 資料驗證錯誤 -> 400 Bad Request
        logger.warning(f"Validation error for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message)
        )

    except BusinessLogicError as e:
        # 業務邏輯錯誤 -> 404 Not Found
        logger.warning(f"Business logic error for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message)
        )

    except Exception as e:
        # 未預期錯誤 -> 500 Internal Server Error
        logger.error(f"Unexpected error analyzing {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@router.get(
    "/{symbol}/moving-averages",
    summary="計算移動平均線",
    description="計算指定股票的多期移動平均線"
)
async def calculate_moving_averages(
    symbol: str,
    end_date: date = Query(..., description="計算截止日期"),
    periods: List[int] = Query(
        default=[5, 10, 20, 60],
        description="MA 期間列表"
    ),
    service: StockAnalysisService = Depends(get_analysis_service)
):
    """
    移動平均線計算端點

    展示如何處理複雜參數與回應
    """
    try:
        ma_values = await service.calculate_moving_averages(
            symbol=symbol,
            end_date=end_date,
            periods=periods
        )

        return {
            "symbol": symbol,
            "date": end_date,
            "moving_averages": ma_values,
            "periods": periods
        }

    except Exception as e:
        logger.error(f"Error calculating MA for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate moving averages"
        )

@router.get(
    "/{symbol}/golden-cross",
    summary="黃金交叉檢測",
    description="檢測股票是否出現黃金交叉訊號"
)
async def detect_golden_cross(
    symbol: str,
    check_date: date = Query(..., description="檢測日期"),
    service: StockAnalysisService = Depends(get_analysis_service)
) -> dict:
    """
    黃金交叉檢測端點

    黃金交叉：短期均線向上突破長期均線
    """
    try:
        has_golden_cross = await service.detect_golden_cross(
            symbol=symbol,
            check_date=check_date
        )

        return {
            "symbol": symbol,
            "date": check_date,
            "has_golden_cross": has_golden_cross,
            "signal": "bullish" if has_golden_cross else "neutral"
        }

    except Exception as e:
        logger.error(f"Error detecting golden cross for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect golden cross"
        )
```

#### API Schemas

**檔案位置**：`gms/api/market/stock/_stock_analysis_api/_schemas.py`

```python
"""
API 請求與回應模型
"""

from pydantic import BaseModel, Field
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

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """錯誤回應"""
    error_code: str
    message: str
    detail: Optional[Dict] = None
```

-----

### 7.5 依賴傳播機制總結

本節總結 API 層如何透過 `_imports.py` 機制管理依賴注入。

#### 傳播流程圖

```text
dependencies.py（工廠定義）
        ↓
    [被忽略]        # 根層 api/_imports.py 不導入
        ↓
  手動導入         # 中層 api/market/_imports.py
        ↓
  自動繼承         # 末層 api/market/stock/_imports.py
        ↓
   使用注入        # _router.py 透過 Depends() 使用
```

#### 關鍵理解

1. **避免循環依賴**：根層 `_imports.py` 故意不導入 `dependencies.py`
2. **中層橋接**：在 Domain 層級（market）手動導入並加入傳播鏈
3. **末端享用**：Router 所在的層級自動獲得所有依賴工廠
4. **依賴來源明確**：Router 透過 `from .._imports import ...` 取得外部依賴，透過 `from ._schemas import ...` 取得同 Feature 的元件

這個設計確保了：
- 依賴管理的一致性
- 避免循環依賴問題
- 保持程式碼的簡潔性
- 支援依賴注入的靈活性

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
            await session.execute("SELECT 1")
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
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """
    應用程式設定
    使用環境變數覆寫預設值
    """

    # === Database ===
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:pass@localhost/gms",
        env="DATABASE_URL"
    )

    # === TEJ Database ===
    TEJ_DB_URL: str = Field(
        default="postgresql+asyncpg://tej_user:pass@tej-db/tej",
        env="TEJ_DB_URL"
    )

    # === Application ===
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # === API ===
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    # === ETL ===
    ETL_BATCH_SIZE: int = Field(default=1000, env="ETL_BATCH_SIZE")
    ETL_RETRY_COUNT: int = Field(default=3, env="ETL_RETRY_COUNT")

    class Config:
        env_file = ".env"
        case_sensitive = True
```

-----

## 9. 測試策略實作

本章節詳述 wBiSaProj 專案的測試實作細節，採用 **`pytest` + `pytest-asyncio`** 框架，並依據「測試金字塔」原則，針對不同系統與層級採用相應的隔離策略。

### 9.1 測試環境配置

建立所有系統共用的基礎測試環境，此處僅配置最核心的框架行為與共用工具，避免特定業務邏輯耦合。

#### 框架配置

**檔案位置**：`pytest.ini`

```ini
[tool:pytest]
# 指定測試目錄，避免掃描虛擬環境或無關目錄
testpaths = tests

# 啟動 pytest-asyncio 的自動模式（支援 async def 測試）
asyncio_mode = auto

# 測試執行選項
addopts = -v --tb=short --strict-markers

# 定義測試標記（對應測試金字塔的分類）
markers =
    unit: 單元測試（快速執行，無外部 I/O）
    integration: 整合測試（需要資料庫或外部連線）
```

#### 通用 Fixtures

**檔案位置**：`tests/conftest.py`

```python
"""
全域測試配置
僅提供最基礎的共用工具，避免特定業務邏輯耦合
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

@pytest.fixture(scope="session")
def event_loop():
    """
    設定 Event Loop
    針對 Windows/特定環境的 Async 測試穩定性
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

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

**檔案位置**：`tests/gms/db/market/stock/test_price_repository.py`

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

**檔案位置**：`tests/gms/service/market/stock/test_analysis_service.py`

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

**檔案位置**：`tests/gms/api/market/stock/test_router.py`

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

**檔案位置**：`tests/gms/etl/market/stock/test_sync_pipeline.py`

```python
"""
ETL Pipeline 單元測試
測試重點：資料流控制、轉換邏輯、錯誤處理
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from decimal import Decimal

from gms.etl.market.stock.sync_job._pipeline import DailyStockSyncPipeline
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

驗證 DB → Service → API 的完整路徑。

**測試重點**：
- 多層協作
- 完整資料流
- 真實業務場景

**策略**：使用 SQLite 覆蓋 DB，但不 Mock Service 與 Repository

**檔案位置**：`tests/gms/integration/test_market_flow.py`

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

**檔案位置**：`tests/tej/service/test_provider.py`

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

**檔案位置**：`tests/tej/collector/test_db_client.py`

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

### 9.4 測試執行與報告

提供測試執行的實用工具與腳本。

#### 執行腳本

**檔案位置**：`scripts/run_tests.sh`

```bash
#!/bin/bash
# 測試執行腳本

# 執行所有測試
run_all() {
    echo "Running all tests..."
    pytest
}

# 只執行 GMS 測試
run_gms() {
    echo "Running GMS tests..."
    pytest tests/gms -v
}

# 只執行 TEJ 測試
run_tej() {
    echo "Running TEJ tests..."
    pytest tests/tej -v
}

# 只執行單元測試
run_unit() {
    echo "Running unit tests..."
    pytest -m unit --tb=short
}

# 執行整合測試
run_integration() {
    echo "Running integration tests..."
    export TEJ_TEST_DB_URL="${TEJ_TEST_DB_URL:-postgresql+asyncpg://test:test@localhost/tej}"
    pytest -m integration -v
}

# 產生覆蓋率報告
run_coverage() {
    echo "Generating coverage report..."
    pytest --cov=gms --cov=tej \
           --cov-report=html \
           --cov-report=term-missing
    echo "Coverage report: htmlcov/index.html"
}

# 主選單
case "${1}" in
    all)         run_all ;;
    gms)         run_gms ;;
    tej)         run_tej ;;
    unit)        run_unit ;;
    integration) run_integration ;;
    coverage)    run_coverage ;;
    *)
        echo "Usage: $0 {all|gms|tej|unit|integration|coverage}"
        exit 1
        ;;
esac
```

#### Makefile 整合

**檔案位置**：`Makefile`

```makefile
.PHONY: test test-gms test-tej test-unit test-integration test-coverage

# 執行所有測試
test:
	@pytest

# GMS 業務系統測試
test-gms:
	@pytest tests/gms -v

# TEJ 資料源測試
test-tej:
	@pytest tests/tej -v

# 單元測試
test-unit:
	@pytest -m unit --tb=short

# 整合測試
test-integration:
	@pytest -m integration -v

# 覆蓋率報告
test-coverage:
	@pytest --cov=gms --cov=tej \
	        --cov-report=html \
	        --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

# 清理測試產物
clean-test:
	@rm -rf .pytest_cache htmlcov .coverage
```

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
