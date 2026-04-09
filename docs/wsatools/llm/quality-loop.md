# LlmQualityLoop 規格文件

## 1. 概述

`LlmQualityLoop` 是 LLM 協作的品質循環框架，實作「生成 → 審核 → 修正」的迭代品質保證模式。它依賴 `LlmTask`，是其上層的編排機制，位於同一個 package 中作為 LLM 基礎設施的一部分，可被任何 workflow 使用。

**定位**：

```
wsatools/llm/
├── LlmTask              # 單次 LLM 互動的基本單位
└── LlmQualityLoop       # 多次 LLM 互動的編排模式（依賴 LlmTask）
```

`LlmTask` 定義「一次 LLM 互動怎麼做」，`LlmQualityLoop` 定義「多次 LLM 互動怎麼串」。`LlmQualityLoop` 嚴格單向依賴 `LlmTask`——它呼叫 Task 的 `run()` 方法，但 `LlmTask` 不知道 `LlmQualityLoop` 的存在。

**上位規範引用**：

- wsatools 架構定位與治理邊界：`docs/wsatools/architecture.md`
- 測試治理原則（含 framework-level test 判斷）：`docs/standards/testing.md`

---

## 2. 設計動機

### 2.1 問題

LLM 生成的內容品質不穩定。即使 prompt 設計精良，LLM 仍可能：

- 從錯誤的來源提取資訊
- 遺漏特定的檢查維度
- 產出格式不符合規範

人工 reviewer 可以發現這些問題，但逐項檢查耗時且容易遺漏。

### 2.2 解法

將品質檢查也交給 LLM，形成自動化的品質循環：

```
Generate → QA → (PASS) → 完成
                (FAIL) → Fix → QA → (PASS) → 完成
                                     (FAIL) → 重試或人工介入
```

**關鍵設計原則**：

- **Task 獨立性**：Generate、QA、Fix 都是獨立的 `LlmTask`，不感知自己被用在品質循環中。可以單獨使用。
- **框架負責編排**：`LlmQualityLoop` 負責流程控制、draft file 管理、重試邏輯。
- **資料流由 workflow 層管理**：三個 Task 共享的建構參數由 QualityLoop 子類持有，透過 factory methods 傳遞。

---

## 3. 架構設計

### 3.1 核心元件

```
LlmQualityLoop (abstract base)
├── create_generate_task()    → LlmTask    # 產出 str
├── create_qa_task()          → LlmTask    # 產出 QaResult
├── create_fix_task(report)   → LlmTask    # 產出 str
├── run()                     → str        # Template Method
└── _write_draft(content)                  # Draft file 管理

QaResult (dataclass)
├── passed: bool              # True = PASS, False = FAIL
└── report: str               # 完整的 QA 輸出文字
```

### 3.2 資料流

Generate、QA、Fix 三個 Task 的參數呈單向累加關係：

- **Generate** 的參數由場景決定（如生成所需的上下文資訊）。
- **QA** 的參數 = Generate 的參數 + 待審文件（draft_path）。
- **Fix** 的參數 = QA 的參數 + QA 報告（qa_report）。

具體參數由各場景的子類在 factory methods 中定義，框架本身不限制參數的種類與數量。框架只保證呼叫順序和資料傳遞的時機。

### 3.3 Draft File 策略

- Generate 和 Fix 的 `run()` 回傳 `str`，框架負責將內容寫入 `draft_path`。
- QA Task 和 Fix Task 透過 `get_uploads()` 上傳 `draft_path` 指向的檔案。
- `run()` 最終回傳通過 QA 的 `str` 內容，不負責寫入目標路徑。呼叫端自行決定寫去哪。
- Task 本身不知道 draft file 的存在——draft_path 是在 QualityLoop 子類的 factory method 中作為建構參數傳給 Task 的。

---

## 4. API 設計

### 4.1 QaResult

```python
@dataclass
class QaResult:
    """品質審核結果。

    Attributes
    ----------
    passed : bool
        True 表示通過，False 表示有問題需要修正。
    report : str
        完整的 QA 輸出文字。PASS 時為簡短確認，
        FAIL 時包含問題清單與修正方向。
    """

    passed: bool
    report: str
```

### 4.2 LlmQualityLoop

```python
class LlmQualityLoop(ABC):
    """LLM 品質循環的 abstract base class。

    子類透過覆寫 factory methods 提供具體的三個 LlmTask。
    run() 以 Template Method Pattern 控制循環流程。

    Parameters
    ----------
    draft_path : str
        Draft file 的路徑。框架將 Generate/Fix 的產出
        寫入此路徑，供 QA/Fix Task 上傳使用。
    max_retries : int, optional
        QA 不通過後的最大修正重試次數，預設為 2。
        總共最多執行 1 次 Generate + (max_retries + 1) 次 QA
        + max_retries 次 Fix。
    """

    def __init__(self, draft_path: str, max_retries: int = 2):
        self.draft_path = draft_path
        self.max_retries = max_retries
```

### 4.3 Factory Methods（子類必須覆寫）

```python
    @abstractmethod
    def create_generate_task(self) -> LlmTask:
        """建立生成 Task。回傳的 Task.run() 應產出 str。"""

    @abstractmethod
    def create_qa_task(self) -> LlmTask:
        """建立審核 Task。

        此時 draft_path 已有內容可供上傳。
        回傳的 Task.run() 應產出 QaResult。
        """

    @abstractmethod
    def create_fix_task(self, qa_report: str) -> LlmTask:
        """建立修正 Task。

        此時 draft_path 有待修正內容，qa_report 有問題描述。
        回傳的 Task.run() 應產出 str。
        """
```

### 4.4 Hook Methods（子類可選覆寫）

```python
    def on_generate_complete(self, content: str) -> None:
        """Generate 完成後的 hook。預設不做事。"""

    def on_qa_complete(self, qa_result: QaResult, attempt: int) -> None:
        """每次 QA 完成後的 hook。預設不做事。"""

    def on_fix_complete(self, content: str, attempt: int) -> None:
        """Fix 完成後的 hook。預設不做事。"""
```

**使用場景**：子類可在 hook 中加入日誌記錄、進度回報、或特殊的中間處理步驟（如程式碼風格檢查）。

### 4.5 Template Method

```python
    def run(self) -> str:
        """執行品質循環，回傳通過 QA 的最終內容。

        流程：
        1. 呼叫 Generate Task 產出初版內容
        2. 將內容寫入 draft_path
        3. 呼叫 QA Task 審核
        4. 若 PASS → 回傳內容
        5. 若 FAIL → 呼叫 Fix Task 修正 → 寫入 draft_path → 回到 3
        6. 超過 max_retries → 拋出 QualityCheckError

        Returns
        -------
        str
            通過 QA 的最終內容。

        Raises
        ------
        QualityCheckError
            超過最大重試次數仍未通過 QA。
        """
```

### 4.6 QualityCheckError

```python
class QualityCheckError(Exception):
    """品質循環超過最大重試次數仍未通過。

    Attributes
    ----------
    report : str
        最後一次 QA 的問題報告。
    """

    def __init__(self, report: str):
        self.report = report
        super().__init__(
            f"Quality check failed after max retries. "
            f"Last report:\n{report}"
        )
```

---

## 5. 使用範例

### 5.1 定義 QualityLoop 子類

```python
class InitL2OverviewQualityLoop(LlmQualityLoop):
    """Init L2 Feature Overview 的品質循環。"""

    def __init__(self, model, library, toolkit,
                 toolkit_context, parent_context, draft_path,
                 max_retries=2):
        super().__init__(draft_path=draft_path, max_retries=max_retries)
        self.model = model
        self.library = library
        self.toolkit = toolkit
        self.toolkit_context = toolkit_context
        self.parent_context = parent_context

    def create_generate_task(self):
        return InitL2OverviewTask(
            self.model, self.library, self.toolkit,
            self.toolkit_context, self.parent_context,
        )

    def create_qa_task(self):
        return QaL2Task(
            self.model, self.library, self.toolkit,
            self.toolkit_context, self.parent_context,
            self.draft_path,
        )

    def create_fix_task(self, qa_report):
        return FixL2Task(
            self.model, self.library, self.toolkit,
            self.toolkit_context, self.parent_context,
            self.draft_path, qa_report,
        )
```

### 5.2 在 Workflow 中使用

```python
# Init Toolkit Docs Workflow
target_info = L1ToolkitInfo.extract(library, toolkit)
parent_context = None
if target_info.parent_toolkit:
    parent_info = L1ToolkitInfo.extract(library, target_info.parent_toolkit)
    parent_context = parent_info.raw_section

l2_draft = f"docs/use-cases/{library}/{toolkit}/overview.draft.md"
l2_loop = InitL2OverviewQualityLoop(
    model, library, toolkit, target_info, parent_context, l2_draft,
)
l2_content = l2_loop.run()

# QA 通過，寫入目標路徑
l2_target = f"docs/use-cases/{library}/{toolkit}/overview.md"
Path(l2_target).write_text(l2_content, encoding="utf-8")
```

### 5.3 單獨使用 QA Task

```python
# 不經過品質循環，直接檢查一份既存文件
qa_task = QaL2Task(
    model, library, toolkit,
    toolkit_context, parent_context,
    target_file="docs/use-cases/wutils/io/overview.md",
)
qa_result = qa_task.run()
if not qa_result.passed:
    print(qa_result.report)
```

---

## 6. 測試設計

`LlmQualityLoop` 承載迭代控制、收斂判斷、draft file 管理等 template method 邏輯，屬於具體可驗證行為的 framework-level 元件，依 `docs/standards/testing.md` §6 應提供 framework-level unit tests。

### 6.1 Unit Test — `test_quality_loop.py`

#### A. QaResult

- `QaResult(passed=True, report="...")` 的欄位存取
- `QaResult(passed=False, report="...")` 的欄位存取

#### B. QualityCheckError

- 建構時 `report` 正確儲存
- `str(error)` 包含 report 內容

#### C. run() 流程 — Generate → QA PASS

- 使用 mock Task（Generate 回傳固定字串，QA 回傳 PASS）
- 驗證 `run()` 回傳 Generate 的產出
- 驗證 draft_path 檔案存在且內容正確
- 驗證 `create_fix_task` 未被呼叫

#### D. run() 流程 — Generate → QA FAIL → Fix → QA PASS

- QA 第一次回傳 FAIL，第二次回傳 PASS
- 驗證 `run()` 回傳 Fix 的產出
- 驗證 `create_fix_task` 被呼叫一次，且 qa_report 正確傳入

#### E. run() 流程 — 超過重試上限

- QA 持續回傳 FAIL
- 驗證拋出 `QualityCheckError`
- 驗證 error 的 report 為最後一次 QA 的報告

#### F. Hook methods

- 驗證 `on_generate_complete` 在 Generate 後被呼叫
- 驗證 `on_qa_complete` 在每次 QA 後被呼叫，attempt 遞增
- 驗證 `on_fix_complete` 在每次 Fix 後被呼叫

#### G. Draft file 管理

- Generate 後 draft_path 內容為 Generate 產出
- Fix 後 draft_path 內容更新為 Fix 產出
- draft_path 的父目錄不存在時自動建立

### 6.2 測試策略

使用具體的 mock 子類測試，不依賴真實的 LLM 互動：

```python
class MockQualityLoop(LlmQualityLoop):
    """測試用的具體子類。"""

    def __init__(self, draft_path, gen_output, qa_results, fix_outputs, ...):
        super().__init__(draft_path)
        self._gen_output = gen_output
        self._qa_results = iter(qa_results)
        self._fix_outputs = iter(fix_outputs)

    def create_generate_task(self):
        return MockTask(output=self._gen_output)

    def create_qa_task(self):
        return MockQaTask(output=next(self._qa_results))

    def create_fix_task(self, qa_report):
        return MockTask(output=next(self._fix_outputs))
```

---

## 7. 檔案配置

| 類型 | 檔案 | 路徑 |
|:-----|:-----|:-----|
| 規格文件 | `quality-loop.md` | `docs/wsatools/llm/` |
| 實作 | `_base.py` | `wsatools/llm/` |
| Unit test | `test_quality_loop.py` | `tests/wsatools/llm/` |
| `__init__.py` 匯出 | `LlmQualityLoop`、`QaResult`、`QualityCheckError` | `wsatools/llm/__init__.py` |

---

## 8. 設計備忘

### 8.1 未來擴展方向

- **程式碼品質循環**：除了內容正確性的 QA，可在 hook 中加入程式碼風格檢查（如 Ruff/Black），形成多維度的品質保證。
- **API 直連**：當 LlmTask 改為 API 呼叫時，品質循環可全自動執行，`max_retries` 的設定將更為重要。
- **通用化 QA 報告格式**：目前 QA 報告格式由各 QA Task 自行定義，未來可考慮標準化報告結構。

### 8.2 max_retries 的預設值

預設為 2，表示最多 3 次 QA（1 次初始 + 2 次修正後）。在 human-in-the-loop 模式下，每次 QA 和 Fix 各需一次人工操作，最壞情況為 7 次操作（Gen + QA + Fix + QA + Fix + QA + 最終寫入）。此數值可在子類建構時覆寫。
