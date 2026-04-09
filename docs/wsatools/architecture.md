# wsatools Package Architecture Specification

## 0. 治理定位與邊界

### 0.1 wsatools 的角色

wsatools 是協助專案設計、管理、開發、LLM 協作的**工具庫**。它不是 project library、business system 或 data source system 的交付內容本體。

因此，wsatools **不直接套用**專案本體的 Feature / Use-case / FU / FU Container 治理模型。wsatools 的內部組織由本規格書定義，與專案本體的架構篇（`PROJECT_DESIGN-ARCHITECTURE.md`）互為獨立。

### 0.2 與專案本體治理模型的差異

| 面向 | 專案本體 | wsatools |
|:-----|:---------|:---------|
| 組織驅動力 | 業務領域 (Domain) 或技術功能 (Toolkit) | 工具操作對象的專案架構位置 |
| 最小邏輯單元 | FU (Functional Unit) | 組織單元（toolkit / task category / workflow） |
| 封裝規範 | FU Container + Feature 級私有目錄 | 組織單元 + private sub-package |
| 依賴管理 | `_imports.py` 機制 | 不適用 |
| 文件結構 | `docs/specs/<fu_path>/<fu_name>/` | `docs/wsatools/<package>/<system>/<unit>/` |

### 0.3 工具操作對象的定義

`library / biz / ds` 路徑代表的是工具所服務的**專案上下文 / 產物類型**，不是工具抽象能力的分類：

- `library/`：工具操作的對象屬於 Project Library 層的產物（如 wutils 的 toolkit 文件）
- `biz/`：工具操作的對象屬於 Business System 層的產物（如業務系統的 API 規格）
- `ds/`：工具操作的對象屬於 Data Source System 層的產物（如資料源的 collector 規格）

例如：為 library-type FU 撰寫文件的 workflow 放在 `workflow/library/`，為 biz/db 類型 FU 撰寫文件的 workflow 放在 `workflow/biz/db/`。

### 0.4 與測試規範的引用關係

wsatools 的測試應遵循以下規範：

- **測試命名與測試結構**：依 `docs/standards/testing.md` §2（檔案組織規範）
- **LLM 測試執行方式**：依 `docs/standards/testing.md` §1.4（LLM 測試執行）
- **Framework-level 測試治理原則**：依 `docs/standards/testing.md` §6（Framework-level 測試治理原則）
- **測試標記**：依 `docs/standards/testing.md` §1.3，特別是 `@pytest.mark.llm` 的使用

---

## 1. 頂層 Package 與依賴約束

wsatools 由三個頂層 package 組成：

| Package | 職責 |
|:--------|:-----|
| `wsatools/utils/` | 共用工具集 |
| `wsatools/llm/` | LLM 互動框架與 LlmTask |
| `wsatools/workflow/` | 多步驟編排邏輯（Workflow） |

依賴約束：

- `utils` 是最底層的共用工具集，不依賴任何同層的 package
- `llm` 可依賴 `utils`，不可依賴 `workflow`
- `workflow` 可依賴 `utils` 和 `llm`

```text
utils ← llm ← workflow
```

---

## 2. 系統分類與路徑結構

wsatools 是協助專案開發的工具庫。各 package 下的子路徑代表工具**操作的對象**在專案架構中的位置（參見 §0.3）。

### 2.1 系統分類路徑

專案架構分為三大類，wsatools 以下列路徑區分：

| 專案架構 | wsatools 路徑 | 說明 |
|:---------|:-------------|:-----|
| Project Library | `library/` | 專案級共用函式庫 |
| Business System | `biz/` | 業務系統 |
| Data Source System | `ds/` | 資料源系統 |

業務系統與資料源系統下各有 System Core 與主幹 layer：

| 系統 | 路徑 | 組成 |
|:-----|:-----|:-----|
| `biz/` | `core/`、`db/`、`service/`、`api/`、`etl/` | System Core + 四層主幹 |
| `ds/` | `core/`、`service/`、`collect/` | System Core + 兩層主幹 |

### 2.2 組織單元與 scope 邊界

每個頂層 package 有各自的**組織單元**——以一個公開 sub-package 封裝的一組相關元件：

| Package | 組織單元 | 內容 |
|:--------|:---------|:-----|
| `utils` | **toolkit** | 一組相關的共用工具 |
| `llm` | **task category** | 一組相關的 LlmTask 與 Quality Loop |
| `workflow` | **workflow** | 一個獨立的多步驟編排邏輯 |

**scope 邊界規則**：組織單元是 scope 的邊界。在系統分類路徑的**任何一層**（含頂層 package 直下），都可以直接放置組織單元。組織單元以下全部為 private。

此規則決定三件事：

1. **外部 import 入口**：只到組織單元層級
2. **docs 路徑深度**：鏡射到組織單元層級
3. **git commit scope**：對應組織單元層級

### 2.3 跨上下文高階 Workflow 規則

若某 workflow 同時橫跨多種產物上下文（例如同時操作 library、biz、ds 的產物），應置於 `wsatools/workflow/` 頂層（不歸入任何系統分類路徑）。此類高階 workflow 的主要角色應是**編排** `library/`、`biz/`、`ds/` 下的獨立 workflow，而不是吸納所有下層邏輯於自身。

### 2.4 utils

```text
wsatools/utils/
├── _base.py                    # 框架層
├── <toolkit>/                  # 不限系統
├── library/
│   └── <toolkit>/              # Project Library 專用
├── biz/
│   ├── <toolkit>/              # 業務系統通用（跨 layer）
│   ├── core/<toolkit>/         # System Core 專用
│   ├── db/<toolkit>/           # db layer 專用
│   └── ...
└── ds/
    ├── <toolkit>/              # 資料源系統通用（跨 layer）
    └── ...
```

### 2.5 llm

```text
wsatools/llm/
├── _base.py                    # 框架層
├── <task_category>/            # 不限系統
├── library/
│   └── <task_category>/        # Project Library 專用
├── biz/
│   ├── <task_category>/        # 業務系統通用（跨 layer）
│   └── ...
└── ds/
    └── ...
```

### 2.6 workflow

```text
wsatools/workflow/
├── _base.py                    # 框架層
├── <workflow>/                 # 不限系統（含跨上下文高階 workflow，見 §2.3）
├── library/
│   └── <workflow>/             # Project Library 專用
├── biz/
│   ├── <workflow>/             # 業務系統通用（跨 layer）
│   └── ...
└── ds/
    └── ...
```

### 2.7 隔離規則

不同系統分類之間不互相依賴（`library/` 不依賴 `biz/`，`biz/` 不依賴 `ds/` 等）。框架層（`_base.py` 等）是跨系統分類共用的基礎設施。

---

## 3. 歸屬判斷規則

### 3.1 歸屬範圍：共用層 vs 消費者內部

**先判斷歸屬範圍**。依據是「離開消費者後是否仍有完整的功能定義」：

| 情況 | 歸屬 |
|:-----|:-----|
| 被多個消費者使用 | 共用層 |
| 只被一個消費者使用，但離開消費者後仍有獨立意義 | 共用層 |
| 只被一個消費者使用，且離開消費者後無獨立意義 | 消費者內部 |

**判斷標準的澄清**：「獨立意義」的判斷標準是**功能定義是否獨立**，不是**目前有多少消費者**。一個功能只要在概念上具備完整的定義（不依附於特定消費者的語境即可被理解和使用），即使當前只有一個消費者，也應歸入共用層。

**輔助判斷問題**：當「獨立意義」不易判斷時，可依以下問題輔助決策：

1. 該元件能否脫離特定 workflow 語境被描述？
2. 是否有穩定的輸入 / 輸出契約？
3. 若被其他 workflow 引用，是否不改其核心語意？
4. 是否適合擁有自己的文件？

若上述問題的答案多為「是」，則該元件具備獨立意義，應歸入共用層。

若判定為「消費者內部」，直接放在該消費者的實作檔或實作 package 中，**不進入 3.2 判斷**。

### 3.2 歸屬 Package：放到哪個頂層 package

若判定為「共用層」，依其本質決定歸屬：

| 它是什麼 | 歸屬 |
|:---------|:-----|
| LlmTask 或 QualityLoop | `llm` |
| Workflow | `workflow` |
| 都不是 | `utils` |

### 3.3 歸屬系統分類

依據工具操作的對象所屬的系統分類決定。操作 Project Library 的文件結構 → `library/`。操作業務系統 API 層 → `biz/api/`。不限於特定系統的通用工具 → 直接放在頂層 package 下。

### 3.4 跨工具的共用邏輯提取

當多個工具存在相同的底層邏輯時，該邏輯應提取為獨立的共用元件。提取後的元件依 §3.1 → §3.2 → §3.3 規則決定歸屬。

### 3.5 公開 sub-package 的准入

系統分類路徑之下，每個公開 sub-package 必須通過 §3.1 的獨立意義檢驗。不通過的為 private sub-package（以 `_` 前綴命名），由上層 `__init__.py` 統一 re-export。

判斷時不應因為多個元件被同一個高階消費者編排，就將它們綁在該消費者的 package 下。如果每個元件離開消費者後仍有完整的功能定義，它就應該是獨立的公開 package。

---

## 4. 文件組織

### 4.1 路徑規則

程式碼的 import 路徑由 §3 的歸屬判斷鏈決定：§3.2（頂層 package）→ §3.3（系統分類）→ §3.5（公開 vs private sub-package）。只有公開 sub-package 構成外部消費者的 import 入口。

文件路徑鏡射程式碼路徑，到組織單元層級為止：

| Package | 組織單元 | 文件路徑範例 |
|:--------|:---------|:-----------|
| `utils` | toolkit | `docs/wsatools/utils/library/<toolkit>/` |
| `llm` | task category | `docs/wsatools/llm/library/<task_category>/` |
| `workflow` | workflow | `docs/wsatools/workflow/library/<workflow>/` |

簡單模組（單一 `.py`）可以用單檔 `<module-name>.md` 放在對應的父目錄下，不需要建立子目錄。

消費者的文件中不保留共用工具的規格內容，僅保留引用。

### 4.2 所有權原則

子元件的文件在其 owner 的文件中描述，不另建獨立文件：

- Quality Loop 的 gen/qa/fix → 寫在該 Quality Loop 的文件中
- Workflow 專屬的 Quality Loop / LlmTask / utility / sub-workflow → 寫在該 Workflow 的文件中
- LlmTask 專屬的 utility → 寫在該 LlmTask 的文件中

### 4.3 文件內容

每個元件的文件涵蓋需求、設計、測試三個面向。依複雜度決定拆分方式：

| 拆法 | 檔案 |
|:-----|:-----|
| 單一文件 | `spec.md` |
| 拆兩份 | `requirements.md` + `design.md` |
| 拆三份 | `requirements.md` + `design.md` + `tests.md` |

以下為各類元件的文件內容規範：

**Workflow**

- 需求：這個 workflow 做什麼、怎麼做（步驟流程）
- 設計：元件規格（含專屬子元件的 spec）、架構決策
- 測試：單元測試規劃；整合測試（optional）
- 依複雜度選擇單一文件或拆分

**LlmTask**

- 需求：做什麼、注意事項
- 設計：prompt、parse、pre/post processing
- 測試：單元測試 + LLM test（必要）
- 單一文件，每個 LlmTask 一份，放在所屬 task category 目錄下

**Quality Loop**

- 涵蓋 loop 本身 + gen/qa/fix 三個 LlmTask 的需求、設計、測試
- 單一文件，每個 Quality Loop 一份，放在所屬 task category 目錄下

**Utility**

- 需求、設計、測試寫在一起
- 單一文件，粒度由開發人員判斷（一個 utility 一份，或一組相關 utilities 一份）
- 放在所屬 toolkit 目錄下

---

## 5. 測試結構規則

### 5.1 目錄結構

測試目錄對應到組織單元（workflow / task category / toolkit）層級，不鏡射 private sub-package 結構。與 `docs/standards/testing.md` §2.1–§2.2 的結構對應性原則一致。

### 5.2 測試檔案命名

以公開元件名稱或組織單元名稱為導航主體，不以 private file 名稱為主體。命名規範詳見 `docs/standards/testing.md` §2.4。

### 5.3 範例

以 `create_toolkit` workflow 為例：

```text
tests/wsatools/workflow/library/create_toolkit/
├── test_workflow.py
├── test_init_l2__gen.py
├── test_init_l2__qa.py
├── test_init_l2__fix.py
├── test_init_l2__loop.py
├── test_init_l3__gen.py
└── ...
```

### 5.4 測試範圍

wsatools 中由 **public package 的 `__init__.py`** 對外公開的元件，原則上應有對應的測試覆蓋；是否需要獨立的 framework-level base test，依 §5.7 與 `docs/standards/testing.md` §6 判斷。

### 5.5 Fixture

- fixture 的歸屬跟的是測試目錄，不是程式碼的可見性。本質上共用的 fixture 提取至共同上層測試目錄，不跨不相關的測試目錄引用
- 搬出的模組必須有獨立的測試覆蓋，不依賴原消費者的測試

### 5.6 LLM 測試

LLM 測試（需要實際呼叫 LLM 的端到端測試）必須標記 `@pytest.mark.llm`，並遵循 `docs/standards/testing.md` §1.4 的分流與人工觸發原則。

LLM 測試不納入 `inv test` 與 `inv test.cov` 的執行範圍，僅透過 `inv test.llm` 手動執行。

### 5.7 Framework-level 測試

wsatools 的 framework-level 元件（如 `LlmTask`、`LlmQualityLoop`、`Workflow`）的測試需求判斷，依 `docs/standards/testing.md` §6 的原則進行。具體而言：

- `LlmTask`：承載 prompt 組裝、呼叫、parse 的 template method 邏輯，需要 base test
- `LlmQualityLoop`：承載迭代控制、收斂判斷邏輯，需要 base test
- `Workflow`：僅提供極輕量的 public entry / template shell，實質可驗證邏輯位於具體子類的 `execute()` 編排中，可不設 base test

---

## 6. 共用工具 API 設計原則

### 6.1 一般化功能定義

共用工具的 API 應提供**一般化的功能單元**，其語意由功能本身決定，不受特定消費者的使用情境影響。

例如：「從 L2 overview 中提取 §2 的內容」是一個一般化的功能——它的意義不依附於「Rewrite 要用它來做比對」這個消費情境。提取的邊界（不含 header）、回傳值（raw text）都由「提取內容」這個功能本質決定，不由消費者的需求驅動。

### 6.2 消費者端組合

消費者依自身需求，組合一般化的共用工具來實現特定邏輯。共用工具不應為了遷就某個消費者的使用方式而偏離一般化語意。

例如：某消費者需要「§2 header + §2 內容」一起比對，這是消費者的特定需求，由消費者自行組合「固定字串比對 header」和「提取 §2 內容比對」兩個步驟，而非讓提取函式回傳包含 header 的內容。

---

§7–§10 描述 LlmTask、Quality Loop 的實作結構與命名慣例。其中：

- **規範**（必須遵守）：歸屬判斷（§3）、文件組織（§4）、task-name 命名規則（§10）
- **慣例**（一般性情境的實作指引，可依實際需求調整）：§7–§9 的內部檔案結構與命名

---

## 7. LlmTask 實作結構

### 7.1 典型結構

獨立 LlmTask 以 private sub-package 封裝，內含實作與 prompt：

```text
_<task_name>/
├── _task.py                   # LlmTask 實作
└── _prompt.md                 # Prompt template
```

### 7.2 變體

實際結構依需求調整。例如多個 LlmTask 共享 Base class 與單一 Prompt 時：

```text
_<task_name>/
├── _tasks.py                  # Base + 子類（如 DoXxxTask, DoXxxInAaaTask, DoXxxInBbbTask）
└── _prompt.md                 # 共用 Prompt template
```

### 7.3 Sub-package 命名

Sub-package 名稱為 task-name 的 snake_case 加 `_` 前綴（見 §10）。

---

## 8. Quality Loop 實作結構

### 8.1 Sub-package 模式

每一組 Quality Loop（Generate + QA + Fix + QualityLoop）形成一個 **sub-package**。

```text
_<task_name>/                  # Quality Loop sub-package
├── __init__.py                # 匯出 4 個公開類別
├── _gen.py                    # Generate Task
├── _gen_prompt.md             # Generate prompt template
├── _qa.py                     # QA Task
├── _qa_prompt.md              # QA prompt template
├── _fix.py                    # Fix Task
├── _fix_prompt.md             # Fix prompt template
└── _loop.py                   # QualityLoop
```

### 8.2 檔案命名

Quality Loop 內部的四個模組使用**固定檔名**：`_gen.py`、`_qa.py`、`_fix.py`、`_loop.py`。Prompt template 與對應 task 同名：`_gen_prompt.md`、`_qa_prompt.md`、`_fix_prompt.md`。

Sub-package 名稱為 task-name 的 snake_case 加 `_` 前綴（見 §10），如 `_init_l2`、`_rewrite_l2_context`。

### 8.3 匯出規則

- Sub-package 的 `__init__.py` 匯出全部 4 個公開類別（Generate Task、QA Task、Fix Task、QualityLoop）
- 父層 `__init__.py` 從 sub-package re-export 所有公開類別

---

## 9. Prompt Tag 導入機制

Prompt tag 機制將 prompt 中具有明確概念歸屬的區塊內容提取為獨立的 `.md` 檔案，便於管理與複用。當同一區塊被多個 Task 使用時，提取為 prompt tag 是必要的——避免大量複本導致維護困難。

### 9.1 Prompt Tag 准入原則

只有語意在所屬層級所有使用情境中都穩定時，才可提取為共用 prompt tag。偶然重複不得共用。對共用性有疑慮時，預設不共用。

具體而言：

- 若一段 prompt 內容在多個 Task 中的語意完全一致且穩定（如通用的 coding standard、通用的文件格式要求），應提取為共用 prompt tag
- 若一段 prompt 內容目前恰好在多個 Task 中相似，但其語意可能因消費者需求不同而各自演化，則應各自維護副本，不提取為共用 tag
- 當無法確定共用性是否穩定時，預設不共用，待需求明確後再提取

### 9.2 放置層級

`_prompt_tags/` 目錄和對應的 `_tags.py` 存放在區塊內容**概念歸屬**的層級。例如：

| 概念歸屬 | 放置位置 |
|:---------|:---------|
| 特定 task category 內共用 | `llm/library/l2_entry/_prompt_tags/` |
| 特定 workflow 內共用 | `workflow/library/create_toolkit/_prompt_tags/` |
| 所有 library LlmTask 共用 | `llm/library/_prompt_tags/` |
| 所有 LlmTask 通用 | `llm/_prompt_tags/` |

### 9.3 `_tags.py` 常數化

在對應層級建立 `_tags.py`，負責載入本層 `_prompt_tags/` 並 re-export 上層 tag 常數。下層只從直接上一層的 `_tags.py` 取用，不跳層：

```python
"""Prompt tag constants for create-toolkit tasks."""

from pathlib import Path

from wsatools.llm import load_prompt_tags

from .._tags import PYTHON_CODING_STANDARDS  # 從上一層 facade 取用

_ALL = load_prompt_tags(Path(__file__).parent / "_prompt_tags")

ENTITY_HIERARCHY = _ALL["ENTITY_HIERARCHY"]
```

### 9.4 消費端按需 import

每個 Task 統一從 local `_tags.py` import，不需要知道 tag 定義在哪一層：

```python
from .._tags import ENTITY_HIERARCHY, PYTHON_CODING_STANDARDS

class SomeTask(LlmTask):
    def get_prompt_tags(self) -> dict[str, str]:
        return {
            "PYTHON_CODING_STANDARDS": PYTHON_CODING_STANDARDS,
            "ENTITY_HIERARCHY": ENTITY_HIERARCHY,
        }
```

每個 Task 的 `get_prompt_tags()` 精確表達「我用了哪些 tag」，不依賴整包 dict 的隱式過濾。

---

## 10. 命名慣例

### 10.1 task-name

每個 LlmTask 或 Quality Loop 有一個 **task-name**——清楚描述任務做什麼，不強制語法結構。task-name 在不同場合套用對應慣例：

- Class 名稱（PascalCase）：附加角色後綴

```text
{TaskName}Task          — Generate Task / 獨立 LlmTask
{TaskName}QaTask        — QA Task
{TaskName}FixTask       — Fix Task
{TaskName}QualityLoop   — QualityLoop
```

- Sub-package 名稱（snake_case）：加 `_` 前綴（見 §7.3、§8.2）

### 10.2 範例

| task-name | Generate | QA | Fix | Sub-package |
|:---------|:---------|:---|:----|:------------|
| `init-l2` | `InitL2Task` | `InitL2QaTask` | `InitL2FixTask` | `_init_l2` |
| `rewrite-l2-context` | `RewriteL2ContextTask` | `RewriteL2ContextQaTask` | `RewriteL2ContextFixTask` | `_rewrite_l2_context` |
| `add-feature-to-l2` | `AddFeatureToL2Task` | `AddFeatureToL2QaTask` | `AddFeatureToL2FixTask` | `_add_feature_to_l2` |

---

## 11. 綜合範例

以下範例說明 §2–§10 的規則如何套用到具體情境。

### 11.1 Workflow

**獨立 Workflow**

`CreateToolkitWorkflow` 為新 toolkit 初始化 L2/L3 overview，可獨立使用（如手動為既有 toolkit 補建文件）。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 離開 `toolkit_restructure` 後仍有獨立意義 → 公開 package（§3.5） |
| 程式碼路徑 | `workflow/library/create_toolkit/_workflow.py` |
| 外部 import | `from wsatools.workflow.library.create_toolkit import CreateToolkitWorkflow` |
| 文件路徑 | `docs/wsatools/workflow/library/create-toolkit/` |
| commit scope | `wsatools/workflow/library/create-toolkit` |

**高階編排 Workflow**

`ProcessImpactItemWorkflow` 將自然語言影響描述解析為結構化任務，派發給 `CreateToolkitWorkflow`、`UpdateToolkitWorkflow` 等獨立 workflow 執行。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 獨立意義 → 公開 package |
| 程式碼路徑 | `workflow/library/toolkit_restructure/_workflow.py` |
| 外部 import | `from wsatools.workflow.library.toolkit_restructure import ProcessImpactItemWorkflow` |
| 文件路徑 | `docs/wsatools/workflow/library/toolkit-restructure/` |
| 與子 workflow 的關係 | 依賴但不擁有——子 workflow 是獨立的公開 package |

### 11.2 LlmTask

**共用 LlmTask**

`FixPythonPathTask` 修正 Python 檔案中的 import 路徑，被 MigrateToolkitWorkflow 和 MigrateFeatureWorkflow 使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 獨立意義 → `llm/library/`（§3.2） |
| 程式碼路徑 | `llm/library/py_refs/_fix_python_path/_task.py` + `_prompt.md` |
| 外部 import | `from wsatools.llm.library.py_refs import FixPythonPathTask` |
| 文件路徑 | `docs/wsatools/llm/library/py-refs/fix-python-path.md` |

**Workflow 專屬 LlmTask**

`ParseImpactItemTask` 將自然語言影響描述解析為結構化的 `ImpactItem`，僅由 `ProcessImpactItemWorkflow` 使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 消費者內部 |
| 程式碼路徑 | `workflow/library/toolkit_restructure/_parse_impact_item/_task.py` + `_prompt.md` |
| 文件 | 寫在 `toolkit-restructure/` 的 spec 中 |

### 11.3 Quality Loop

**共用 Quality Loop**

`AddFeatureToL2QualityLoop` 將 Feature 條目新增至 L2 overview，含品質循環，被多個 workflow 使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 獨立意義 → `llm/library/`（§3.2） |
| 程式碼路徑 | `llm/library/l2_entry/_add_feature_to_l2/`（內含 `_gen.py`、`_qa.py`、`_fix.py`、`_loop.py` + prompts） |
| 外部 import | `from wsatools.llm.library.l2_entry import AddFeatureToL2QualityLoop` |
| 文件路徑 | `docs/wsatools/llm/library/l2-entry/add-feature-to-l2.md` |

**Workflow 專屬 Quality Loop**

`InitL2QualityLoop` 初始化 L2 overview，僅由 `CreateToolkitWorkflow` 使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 消費者內部 |
| 程式碼路徑 | `workflow/library/create_toolkit/_init_l2/`（內含 `_gen.py`、`_qa.py`、`_fix.py`、`_loop.py` + prompts） |
| 文件 | 寫在 `create-toolkit/` 的 spec 中 |

### 11.4 Utility

**共用 toolkit（Library scope）**

`scan_code_dependencies`、`scan_doc_references` 是 Library scope 的掃描工具，被多個 workflow 使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 獨立意義 → `utils/library/`（§3.3） |
| 程式碼路徑 | `utils/library/scan.py` |
| 外部 import | `from wsatools.utils.library import scan_code_dependencies` |
| 文件路徑 | `docs/wsatools/utils/library/scan.md` |

**不限系統的通用工具**

`scan_files` 是不含 domain 知識的通用檔案掃描，供各系統分類下的工具使用。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 不限系統 → 頂層 package 下（§3.3） |
| 程式碼路徑 | `utils/_scan.py` |
| 文件路徑 | `docs/wsatools/utils/scan.md` |

**Workflow 專屬 utility**

`_utils.py` 是 `toolkit_restructure` 專屬的 re-export facade + 自有工具入口。

| 項目 | 值 |
|:-----|:---|
| 歸屬判斷 | 消費者內部 |
| 程式碼路徑 | `workflow/library/toolkit_restructure/_utils.py` |
| 文件 | 寫在 `toolkit-restructure/` 的 spec 中 |
