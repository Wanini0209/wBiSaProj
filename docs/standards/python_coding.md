# 程式碼撰寫規範 (Coding Standards & Guidelines)

## 1. 基本原則

本專案嚴格遵守 **PEP 8** 規範，並配合自動化工具 (Black, Ruff) 進行格式檢查。

### 行長度限制 [IMPORTANT]

為配合專案設定檔 (`pyproject.toml`) 中的 Black 與 Ruff 設定：

- **最大行長度**: **88 字元**
- **文件字串與註解**: 建議保持在 72-80 字元以便閱讀
- **長行處理**: 優先使用括號 `()` 進行邏輯分行，避免使用反斜線 `\`

```python
# 正確的長行處理方式 (Black style)
result = some_function_with_long_name(
    parameter_one,
    parameter_two,
    parameter_three,
)

# 長字串處理
long_message = (
    "This is a very long message that needs to be broken "
    "into multiple lines to comply with PEP 8 standards."
)
```

**例外豁免 (Readability over Rigid Rules)**:
若為了符合 88 字元限制而強制換行，導致程式碼**極度難讀**或**破壞語意完整性**，請**優先保留單行**，並在行尾加上 `# noqa: E501` 以略過 Linter 檢查。

**適用情境**：

1. **長網址 (URLs)**: 切斷網址會導致無法直接點擊或複製。
2. **複雜的正則表達式 (Regex)**: 除非使用 `re.VERBOSE`，否則切斷 Regex 會嚴重破壞可讀性。
3. **無法分割的長字串**: 具有特定格式要求的字串常數。

```python
# ✅ 正確：使用 noqa 保持完整性
API_ENDPOINT = "[https://very-long-domain.com/api/v1/resource/specific-id/action?query=param](https://very-long-domain.com/api/v1/resource/specific-id/action?query=param)"  # noqa: E501

# ❌ 避免：為了換行而破壞結構
API_ENDPOINT = (
    "[https://very-long-domain.com/api/v1/resource/](https://very-long-domain.com/api/v1/resource/)"
    "specific-id/action?query=param"
)
```

### 命名規範

除了標準的 PEP 8 命名外，需遵守本專案的架構命名約定：

| 項目 | 命名風格 | 範例 | 說明 |
| :--- | :--- | :--- | :--- |
| **模組/套件** | snake_case | `market_data`, `utils` | |
| **類別 (Class)** | PascalCase | `StockPriceCollector` | |
| **函數/變數** | snake_case | `calculate_ma`, `user_id` | |
| **常數** | UPPER_CASE | `MAX_RETRY_COUNT` | |
| **私有屬性** | _leading_underscore | `_cache`, `_connect()` | |
| **介面 (Interface)** | **I**PascalCase | `IStockPriceProvider` | **架構約定**：介面類別建議以 `I` 開頭 |

#### 檔案命名與架構約定 (Architecture Alignment) [IMPORTANT]

本專案依據功能單元 (Functional Unit) 結構有特定的檔案命名規則：

- **公開容器 (Public Container)**:
  - 目錄名稱**不使用**底線開頭。
  - 例如: `api`, `service`, `db`
- **私有實作 (Private Implementation)**:
  - 實作細節檔案**必須**以底線 `_` 開頭，表示不應被外部直接導入。
  - 例如: `_models.py`, `_repository.py`, `_utils.py`

---

## 2. 導入規範 (Import Rules) [CRITICAL]

本專案包含多種系統類型（Library, Data Source, Business System），不同類型有不同的導入策略。

### 2.1 通用原則 (適用於所有系統)

- **禁止循環依賴**: 嚴格禁止模組間的循環引用。
- **分組順序**: 依序為 (1) 標準函式庫, (2) 第三方套件, (3) 本地專案模組。
- **封裝性**: 嚴禁跨越容器直接導入其內部的私有檔案 (例如: 禁止 `from other_pkg._models import Model`)。

### 2.2 業務系統專用機制 (`_imports.py` Pattern)

**適用範圍**: 僅限於 **Business Systems** (如 `gms`) 內部的 `api`, `service`, `db`, `etl` 四大模組層級。

**不適用**: Library (`core`, `wutils`) 或 Data Source Systems (`tej`)。

在適用範圍內，需遵守以下依賴管理規則：

1. **依賴閘門**: 每個 FU Container (如 `gms/service/user`) 的 `_imports.py` 負責管理該層級的所有外部依賴。
2. **實作檔案限制**: 內部的實作檔案 (如 `_service.py`) **嚴禁**跳出容器去 import 父層或兄弟層的內容，必須統一從同層的 `._imports` 取得依賴。
3. **內部協作例外**: 同一容器內的私有檔案（如 `_x.py` 導入 `_y.py`）屬於內部協作，**允許**直接使用相對導入。

```python
# ✅ 正確 (在 gms/service/user/_service.py 中)
# 透過同層 _imports 取得所有外部依賴 (包含 core, db 介面等)
from ._imports import IUserRepository, BusinessLogicError

# ✅ 正確 (在 gms/service/user/_service.py 中)
# 從同容器內的私有檔案導入 (內部協作)
from ._utils import validate_email

# ❌ 錯誤 (違反架構封裝)
from ...db.user import IUserRepository  # 禁止跳出容器
from core.exceptions import BusinessLogicError  # 禁止繞過 _imports
```

---

## 3. 類型提示規範 (Type Hinting)

本專案目標版本為 Python 3.12+，請使用現代語法：

```python
# ✅ 正確 - 使用內建類型與 | 運算子
def process_data(items: list[dict[str, str | int]]) -> dict[str, any]:
    pass

# ❌ 錯誤 - 避免使用 typing 模組的舊式類型
from typing import Dict, List, Optional, Union
```

**推薦對照表**:

- `typing.List` → `list`
- `typing.Dict` → `dict`
- `typing.Tuple` → `tuple`
- `typing.Union[A, B]` → `A | B`
- `typing.Optional[T]` → `T | None`

---

## 4. `__all__` 聲明規範

為確保封裝邊界清晰，以下檔案 **必須** 定義 `__all__`：

1. **`__init__.py`**: 定義該模組/容器對外暴露的 Public API。
2. **`_imports.py`**: 定義該容器向下傳播的依賴清單。

**注意**: 一般內部的私有實作檔案 (如 `_models.py`) **不需要** 定義 `__all__`，除非有特殊的 Meta-programming 需求。

```python
# __init__.py 範例
__all__ = [
    'StockAnalysisService',  # 僅暴露需要的類別
    'analyze_volume',        # 僅暴露需要的函數
]
```

---

## 5. 文件與註解規範

採用 **NumPy Style** 格式。為確保 API 文件生成的通用性，**Docstrings 必須使用英文撰寫**。

### 文件字串 (Docstrings)

#### 1. 摘要行 (Summary Line)

- **要求**: 第一行必須是簡短的摘要，且**必須以句號 (.) 結尾** (Ruff D400) [CRITICAL]。
- **語氣區分**:
  - **函數與方法 (Functions & Methods)**: 必須使用 **祈使句 (Imperative Mood)**。
    - ✅ Correct: "Calculate the weighted portfolio return."
    - ❌ Incorrect: "Calculates the weighted portfolio return."
  - **模組與類別 (Modules & Classes)**: 使用 **名詞片語** 或 **描述性語句**。
    - ✅ Correct (Module): "Tools for input/output operations."
    - ✅ Correct (Class): "A strict coding standard checker."
    - ❌ Incorrect: "Initialize the tools." (除非該物件本身就是一個 Action)

#### 2. 詳細區塊 (Sections)

Implementation File (`IMPL`) 中的 Public Function/Method 必須包含：

- **Parameters**: 參數說明。
- **Returns**: 回傳值說明。
- **Raises**: 拋出的異常說明 (若有)。

```python
def calculate_portfolio_return(weights: list[float], returns: list[float]) -> float:
    """
    Calculate the weighted portfolio return.  <-- ✅ 祈使句 + 句號 (D400)

    Parameters
    ----------
    weights : list[float]
        List of asset weights in the portfolio.
    returns : list[float]
        List of individual asset returns.

    Returns
    -------
    float
        The calculated weighted portfolio return.
    """
    pass
```

### 內聯註解 (Inline Comments)

- **原則**: 註解應解釋「為什麼 (Why)」這樣做，而非「做了什麼 (What)」。
- **語言**:
  - **預設**: 建議使用 **英文**。
  - **例外**: 涉及**專有名詞 (如「融資融券」、「三大法人」)、特定演算法、複雜業務邏輯或法規細節**時，為避免因強制翻譯造成語意流失或增加閱讀門檻，允許且建議 直接使用**繁體中文**或**原生語言**。

```python
# 使用 NumPy 進行向量化運算以提升效能 (Why)
portfolio_return = np.average(returns, weights=weights)

# [TW-Rule] 根據證交所規定，若個股當日暫停交易，需使用前一日收盤價作為計算基準
# 這裡處理補值邏輯...
if is_suspended:
    price = last_close_price
```

---

## 6. 工具與檢查

本專案使用以下工具強制執行上述規範，請確保您的開發環境已安裝 `pre-commit`：

- **Black**: 程式碼格式化 (Line length: 88)
- **Ruff**: Linter (Import sorting, Code style, Bug detection)
- **Mypy**: 靜態類型檢查

在提交程式碼前，請務必執行：

```bash
inv style  # 執行格式化與檢查
```

---

## 7. 品質保證與自我檢查 (Quality Assurance & Self-Check)

在提交 Pull Request (PR) 之前，請務必對照以下清單進行自我審查。本專案強調「品質內建」，自動化工具僅能攔截語法錯誤，**架構合規性**必須由開發者主動維護。

### 7.1 自動化檢查 (Automated Checks)

確保程式碼通過所有 CI/CD 流水線的靜態檢查：

- [ ] 已執行 `inv style` 並修正所有 Black 格式化與 Ruff Linter 錯誤。
- [ ] 已執行 Mypy 靜態類型檢查，且無 `Any` 濫用或類型錯誤。
- [ ] 新增或修改的功能已有對應的測試，且全數通過 (Green Light)。

### 7.2 架構合規性檢查 (Architectural Compliance) [CRITICAL]

針對 **Business Systems** (如 `gms`) 的開發者，請嚴格檢查以下架構紅線：

**依賴管理 (`_imports.py` 機制)**

- [ ] **無越級導入**：確認沒有任何程式碼跳過容器邊界去 import 私有實作 (例如：沒有出現 `from ..other_pkg._models import ...`)。
- [ ] **單一入口 (外部依賴)**：確認所有**來自容器外部**的依賴 (如父層、兄弟層、System Core)，是否統一從同層的 `._imports` 取得？(同一容器內的私有檔案互調不在此限，如 `from ._models import ...` 是允許的)。
- [ ] **無循環依賴**：確認 `_imports.py` 沒有反向導入同層的實作檔案 (這會導致 Circular Import)。

**依賴反轉 (DIP)**

- [ ] **介面依賴**：Service 層是否只依賴 Repository 的 **介面 (Interface)**，而非具體類別？(例如：Type Hint 應為 `IStockPriceRepository` 而非 `StockPriceRepository`)。
- [ ] **資料源隔離**：確認 Service 層**沒有**直接呼叫外部資料源 (TEJ/Crawler)，而是透過 Repository 存取已落地的資料。

### 7.3 實作細節檢查 (Implementation Details)

- [ ] **檔案命名**：私有實作檔案是否已加上底線前綴 (如 `_service.py`, `_utils.py`)。
- [ ] **公開介面**：若新增了對外公開的元件，是否已在 `__init__.py` 的 `__all__` 中註冊？
- [ ] **類型提示**：是否使用了現代語法 (如 `list[str]`, `str | None`) 而非舊式 `typing` 模組？
- [ ] **文件語言**：
  - [ ] Docstrings (API 文件) 是否為 **英文**？
  - [ ] Inline Comments (邏輯說明) 若涉及複雜業務或法規，是否已用清晰的語言 (可含繁體中文) 解釋 **Why**？

---

## 8. LLM 協作檢查清單 (LLM Checklist) [IMPORTANT]

**此清單專為 LLM 協作設計，生成程式碼時請務必對照以下規則：**

### 8.1 格式與語法 (Format & Syntax)

- [ ] **Line Length**: 限制 88 字元。URL 或 Regex 可例外並加上 `# noqa: E501`。
- [ ] **Imports**: 標準庫 -> 第三方 -> 本地，嚴禁循環依賴。

### 8.2 文件字串檢查 (Docstrings) [CRITICAL]

- [ ] **D400 規則**: 檢查所有 Docstring 的第一行摘要（Summary Line），是否已用 **句號 (.)** 結尾？
  - ✅ `"""Calculate value."""`
  - ❌ `"""Calculate value"""`
- [ ] **語氣檢查**: Function/Method 必須使用祈使句 ("Calculate", not "Calculates")。

### 8.3 單行長度處理策略

```python
# ✅ Good: 一般情況使用括號換行
result = some_function(
    arg1,
    arg2,
    arg3
)

# ✅ Good: 例外情況 (URL 或 Regex)，使用 noqa 保持可讀性
pattern = r"^(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9-._?,'+&%$=~]*)?$"  # noqa: E501
```
