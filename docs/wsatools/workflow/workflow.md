# Workflow 規格文件

## 1. 概述

`Workflow` 是多步驟編排的 ABC，負責組合 `LlmTask`、自動化工具和子 Workflow 來完成複雜的工作流程。

**定位**：

```
wsatools/
├── llm/
│   ├── LlmTask              # 單次 LLM 互動
│   └── LlmQualityLoop       # 多次 LLM 互動的品質循環
│
└── workflow/
    ├── Workflow              # 多步驟編排（本文件）
    └── library/toolkit_restructure/ # 具體 workflow 實作
```

`Workflow` 是 `LlmTask` 的上層消費者。嚴格遵循 `workflow → llm` 的單向依賴——Workflow 呼叫 `LlmTask.run()`，但 `LlmTask` 不知道 Workflow 的存在。

**上位規範引用**：

- wsatools 架構定位與治理邊界：`docs/wsatools/architecture.md`
- 測試治理原則（含 framework-level test 判斷）：`docs/standards/testing.md`

---

## 2. 設計動機

### 2.1 問題

複雜的自動化流程（如 Toolkit 結構重構）需要串接多個步驟：LLM 任務、自動化解析、條件分支、子流程呼叫。如果每個流程各自實作入口和流程控制，會缺乏統一的擴展點。

### 2.2 解法

提供輕量的 `Workflow` ABC，子類在 `execute()` 中實作編排邏輯。`run()` 使用 Template Method Pattern 作為公開入口，預留未來 cross-cutting concerns（如 logging、timing、error handling）的注入點。

---

## 3. API 設計

```python
class Workflow(ABC):

    @abstractmethod
    def execute(self) -> Any:
        """子類實作編排邏輯。"""

    def run(self) -> Any:
        """公開入口。目前直接呼叫 execute()。

        預留 Template Method hook，未來可加入：
        - 執行前後的 logging
        - 計時
        - 全域 error handling

        子類不應覆寫此方法。
        """
        return self.execute()
```

### 3.1 設計決策

**為什麼 `run()` 和 `execute()` 分離？**

目前 `run()` 只是直接呼叫 `execute()`，看似多餘。但這是刻意的設計——當未來需要加入跨 workflow 的共用邏輯（如執行計時、錯誤上報）時，只需修改 `run()`，所有子類自動受益，不需要逐一修改。

**為什麼不定義建構參數？**

不同 workflow 的參數差異極大（`ToolkitCreationWorkflow` 只需要 `library + toolkit`，`FeatureMigrationWorkflow` 需要 `FeatureMapping`）。框架不限制參數結構，由子類自行定義。

---

## 4. 使用範例

```python
class ToolkitCreationWorkflow(Workflow):
    """Type 1: 新建 Toolkit 的完整流程。"""

    def __init__(self, model, library, toolkit):
        self.model = model
        self.library = library
        self.toolkit = toolkit

    def execute(self):
        # Step 1: 擷取 L1 context
        target_info = L1ToolkitInfo.extract(
            self.library, self.toolkit,
        )

        # Step 2: 初始化 L2 overview
        l2_content = InitL2OverviewTask(
            self.model, self.library, self.toolkit,
            target_info, parent_context=None,
        ).run()
        Path(l2_path).write_text(l2_content)

        # Step 3: 初始化 L3 overview
        l3_content = InitL3OverviewTask(
            self.model, self.library, self.toolkit,
            target_info, parent_context=None,
        ).run()
        Path(l3_path).write_text(l3_content)


# 使用
workflow = ToolkitCreationWorkflow(model, "wutils", "io")
workflow.run()
```

---

## 5. 依賴規則

```
invoke task (CLI 入口)
    → workflow (編排層)
        → workflow (Workflow ABC)
        → llm (LlmTask, LlmModel, LlmQualityLoop)
```

| 規則 | 說明 |
|:-----|:-----|
| Workflow → LlmTask | Workflow 可呼叫 `LlmTask.run()` |
| Workflow → LlmQualityLoop | Workflow 可呼叫 `LlmQualityLoop.run()` |
| Workflow → Workflow | Workflow 可呼叫子 Workflow 的 `run()` |
| LlmTask → Workflow | **禁止**。LlmTask 不得依賴 workflow |
| LlmQualityLoop → Workflow | **禁止**。QualityLoop 不得依賴 workflow |

---

## 6. 測試策略

`Workflow` 僅提供極輕量的 public entry / template shell。在目前設計下，其可驗證邏輯主要位於具體子類的 `execute()` 編排中，因此依 `docs/standards/testing.md` §6 可不設獨立的 framework-level base test；具體測試責任由各子類承擔。

---

## 7. 檔案配置

| 類型 | 檔案 | 路徑 |
|:-----|:-----|:-----|
| 規格文件 | `workflow.md` | `docs/wsatools/workflow/` |
| 實作 | `_base.py` | `wsatools/workflow/` |
| `__init__.py` 匯出 | `Workflow` | `wsatools/workflow/__init__.py` |
