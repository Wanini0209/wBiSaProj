# LlmTask 規格文件

## 1. 概述

`LlmTask` 是 LLM 協作的基礎框架，定義「一次 LLM 互動」的完整生命週期：組裝 prompt → 人工操作 LLM → 解析回應。所有 LLM 相關的自動化任務都繼承此 ABC。

**定位**：

```
wsatools/llm/
├── LlmTask              # 單次 LLM 互動的基本單位（本文件）
├── LlmQualityLoop       # 多次 LLM 互動的編排模式（依賴 LlmTask）
└── load_prompt_tags     # Prompt tag 目錄載入工具
```

`LlmTask` 是最底層的建構單元。`LlmQualityLoop` 依賴它，`Workflow` 也依賴它，但 `LlmTask` 本身不知道上層的存在。

**上位規範引用**：

- wsatools 架構定位與治理邊界：`docs/wsatools/architecture.md`
- 測試治理原則（含 framework-level test 判斷）：`docs/standards/testing.md`

---

## 2. 設計動機

### 2.1 問題

專案中大量任務需要 LLM 協作（文件撰寫、程式碼修改、品質審核等），每個任務都需要：

- 從 prompt template 組裝最終 prompt
- 指定需要上傳的參考檔案
- 解析並驗證 LLM 的回應

如果每個任務各自實作這些流程，會產生大量重複程式碼，且操作流程不一致。

### 2.2 解法

將共用流程抽象為 `LlmTask`，子類只需定義四件事：

- `PROMPT_TEMPLATE`：prompt 模板
- `get_prompt_params()`：placeholder 替換值
- `get_uploads()`：上傳檔案清單
- `parse()`：回應解析與驗證

框架負責流程控制（prompt 組裝、編輯器互動、retry）。

---

## 3. 架構設計

### 3.1 核心元件

```
LlmTask (ABC)
├── PROMPT_TEMPLATE: str               # 類別屬性：prompt 模板
├── get_prompt_params() → dict         # 抽象：placeholder 替換值
├── get_uploads() → list[str]          # 抽象：上傳檔案清單
├── parse(response) → Any             # 抽象：回應解析
├── get_prompt_tags() → dict           # 可選覆寫：prompt tag 內容
├── build_prompt() → str               # Prompt 組裝（三階段處理）
└── run() → Any                        # Human-in-the-loop 執行流程
```

### 3.2 依賴方向

```
Workflow → LlmTask        # Workflow 呼叫 Task.run()
LlmQualityLoop → LlmTask  # QualityLoop 呼叫 Task.run()
LlmTask → (無依賴)         # Task 不知道上層的存在
```

---

## 4. build_prompt 三階段處理

`build_prompt()` 將 `PROMPT_TEMPLATE` 加工為最終 prompt，依序執行三個階段：

### 4.1 處理順序

```
PROMPT_TEMPLATE
    │
    ▼ Stage 1: Placeholder 替換
    │   {{KEY}} → get_prompt_params()[KEY]
    │
    ▼ Stage 2: Prompt-tag 注入
    │   ```prompt-tag:TAG_ID    → get_prompt_tags()[TAG_ID]
    │   ```
    │
    ▼ Stage 3: Human-only 移除
    │   ```human-only           → (removed)
    │   ...
    │   ```
    │
    ▼
  最終 prompt
```

### 4.2 Placeholder 替換

將 `{{KEY}}` 替換為 `get_prompt_params()` 回傳的對應值。

**Prompt Template 中**：

```markdown
為 Library `{{LIBRARY}}` 的 Toolkit `{{TOOLKIT_PATH}}` 初始化文件。
```

**LlmTask 子類中**：

```python
def get_prompt_params(self) -> dict[str, str]:
    return {
        "LIBRARY": self.library,
        "TOOLKIT_PATH": self.toolkit,
    }
```

### 4.3 Prompt-tag 注入

將空的 `prompt-tag` fenced block 替換為 `get_prompt_tags()` 回傳的對應內容。用於多個 Task 共用同一段 prompt 內容（如專案核心概念定義），避免重複維護。

**Prompt Template 中**：

````markdown
# Project Context & Standards

```prompt-tag:INIT_TOOLKIT_CONTEXT_L2
```

# Input Files
...
````

Tag 內容由子類透過 `get_prompt_tags()` 提供，儲存方式由子類自行決定。框架提供 `load_prompt_tags()` 工具函數支援目錄載入模式，但不強制使用。

未匹配的 tag ID 會被靜態移除，不會報錯。

### 4.4 Human-only 移除

移除 `human-only` fenced block。這些區塊用於在 prompt template 中標註來源資訊（如 `Ref: DESIGN.md §3.2`），僅供人類維護時參考，不應送入 LLM。

````markdown
## 1. 專案核心概念

```human-only
Ref: PROJECT_DESIGN-ARCHITECTURE.md §3.3
```

### Toolkit（技術功能分類）
...
````

---

## 5. Prompt-tag 機制

### 5.1 設計動機

當多個 LlmTask 需要相同的 prompt 內容（如專案核心概念定義）時，直接在各自的 prompt template 中複製會導致：

- 修改時需同步多份，容易遺漏
- 無法區分「偶然重複」與「本質共用」

Prompt-tag 將共用內容抽離為獨立檔案，由 framework 在 `build_prompt()` 時注入。

### 5.2 get_prompt_tags()

```python
def get_prompt_tags(self) -> dict[str, str]:
    """回傳 prompt tag 內容。預設為空 dict。"""
    return {}
```

子類按需覆寫。回傳的 dict 中，key 是 tag ID，value 是要注入的文字內容。

### 5.3 load_prompt_tags()

框架提供的目錄載入工具函數，非 `LlmTask` 的方法：

```python
def load_prompt_tags(tag_dir: str | Path) -> dict[str, str]:
    """從目錄載入 .md 檔案作為 prompt tag。

    檔名（不含 .md）為 tag ID，檔案內容為 tag 文字。
    """
```

**使用範例**：

```
wsatools/workflow/library/toolkit_restructure/
├── _prompt_tags/
│   ├── INIT_TOOLKIT_CONTEXT_L2.md
│   └── INIT_TOOLKIT_CONTEXT_L3.md
├── _init_l2/
│   ├── _gen.py
│   ├── _qa.py
│   └── _fix.py
```

```python
from .._tags import INIT_TOOLKIT_CONTEXT_L2

class InitL2OverviewTask(LlmTask):
    def get_prompt_tags(self) -> dict[str, str]:
        return {"INIT_TOOLKIT_CONTEXT_L2": INIT_TOOLKIT_CONTEXT_L2}
```

同一目錄下的多個 Task 共用同一組 tag，各自的 prompt template 引用需要的 tag ID。

### 5.4 儲存方式不限

`load_prompt_tags()` 是一個 helper，不是唯一選擇。子類可以用任何方式提供 tag 內容：

```python
# 方式 A：目錄載入
def get_prompt_tags(self):
    return load_prompt_tags(some_dir)

# 方式 B：inline
def get_prompt_tags(self):
    return {"MY_TAG": "inline content"}

# 方式 C：不用（預設）
# 不覆寫，回傳空 dict
```

---

## 6. Human-in-the-loop 執行流程

### 6.1 run() 流程

```
run()
 ├── build_prompt()                    # 組裝 prompt
 ├── get_uploads()                     # 收集上傳檔案清單
 ├── _prepare_request_file()           # 寫入 request temp file
 ├── 開啟編輯器（request）               # 操作者複製 prompt 到 LLM
 └── loop:
     ├── 開啟編輯器（response）           # 操作者貼上 LLM 回應
     ├── parse(response)               # 解析回應
     ├── 成功 → 清理 temp files → return
     └── 失敗 → 顯示錯誤 → retry
```

### 6.2 Request temp file 格式

```
=== LLM Model: Gemini 3 Pro ===

--- Upload Files (請依序上傳以下檔案) ---
(每行為一批，可直接複製整行貼入檔案總管)

"docs\standards\writing-guides\use-cases\ft-overview.md"

--- Prompt (請將以下內容貼入 LLM) ---

<組裝後的 prompt>
```

---

## 7. API 設計

### 7.1 LlmModel

```python
class LlmModel(StrEnum):
    GEMINI_PRO = "Gemini 3 Pro"
    GEMINI_THINK = "Gemini 3 Thinking"
    CLAUDE = "Claude"
```

### 7.2 LlmTask

```python
class LlmTask(ABC):
    PROMPT_TEMPLATE: str = ""

    def __init__(self, model: LlmModel):
        self.model = model

    # --- 抽象方法（子類必須實作）---
    @abstractmethod
    def get_prompt_params(self) -> dict[str, str]: ...

    @abstractmethod
    def get_uploads(self) -> list[str]: ...

    @abstractmethod
    def parse(self, response: str) -> Any: ...

    # --- 可選覆寫 ---
    def get_prompt_tags(self) -> dict[str, str]:
        return {}

    # --- 公開方法 ---
    def build_prompt(self) -> str: ...
    def run(self) -> Any: ...
```

### 7.3 load_prompt_tags

```python
def load_prompt_tags(tag_dir: str | Path) -> dict[str, str]:
    """從目錄載入 .md 檔案。檔名為 tag ID，內容為 tag 文字。"""
```

---

## 8. 測試設計

`LlmTask` 承載 prompt 組裝（placeholder 替換、prompt-tag 注入、human-only 移除）的 template method 邏輯，屬於具體可驗證行為的 framework-level 元件，依 `docs/standards/testing.md` §6 應提供 framework-level unit tests。

### 8.1 Unit Test — `test_llm_task.py`

#### A. Placeholder 替換

- 單一 / 多個 / 重複 placeholder 正確替換
- 無 placeholder 的模板原樣回傳
- 空 params 不影響未匹配的 placeholder

#### B. Human-only 移除

- 單一 / 多行 / 多個 human-only block 移除
- 四 backtick 的 human-only block 移除
- 非 human-only 的 fenced block 保留

#### C. Prompt-tag 注入

- 單一 / 多個 tag 正確注入
- 未匹配的 tag ID 靜態移除
- 四 backtick 的 tag block 匹配
- 預設 `get_prompt_tags()` 回傳空 dict

#### D. 三機制協作

- Placeholder + prompt-tag + human-only 同時正確處理

#### E. load_prompt_tags

- 單一 / 多個 .md 檔案載入
- 非 .md 檔案忽略
- 空目錄回傳空 dict
- 檔名為 tag ID（去 .md 副檔名）
- 接受 str 路徑

---

## 9. 檔案配置

| 類型 | 檔案 | 路徑 |
|:-----|:-----|:-----|
| 規格文件 | `llm-task.md` | `docs/wsatools/llm/` |
| 實作 | `_base.py` | `wsatools/llm/` |
| Unit test | `test_llm_task.py` | `tests/wsatools/llm/` |
| `__init__.py` 匯出 | `LlmTask`、`LlmModel`、`load_prompt_tags` | `wsatools/llm/__init__.py` |

---

## 10. 設計備忘

### 10.1 與 LlmQualityLoop 的關係

`LlmQualityLoop` 依賴 `LlmTask`，透過 factory methods 建立 Generate/QA/Fix 三個 Task。Task 本身不感知品質循環的存在。詳見 `quality-loop.md`。

### 10.2 Prompt Template 規範

所有 prompt template 遵循 `docs/standards/prompt-template.md` 的段落結構（§1 Role → §9 QA Checklist）。`build_prompt()` 的三階段處理與 prompt template 規範正交——前者是框架層面的文字替換機制，後者是內容層面的段落組織規範。

### 10.3 未來擴展方向

- **API 直連**：當 `run()` 改為 API 呼叫時，human-in-the-loop 流程可替換為自動化流程，`build_prompt()` 和 `parse()` 不受影響。
- **prompt-tag 架構演進**：目前 tag 管理由各模組自行負責。未來可建立集中式的 tag registry，但當前的輕量機制已足夠。
