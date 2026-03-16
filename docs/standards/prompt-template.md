# Prompt Template Standard — Meta-Template

> **本文件定義專案所有 Prompt Template 的通用結構規範。**
> 所有新建或翻新的 Prompt Template 必須遵循此 Meta-Template 的段落結構與撰寫原則。

---

## 語言策略 (Language Strategy)

| 層級 | 語言 | 說明 |
|:--|:--|:--|
| H1 Header | English | 作為 LLM 理解 section 用途的強指引標記，使用業界慣用英文術語 |
| H2 Sub-Header | English | 功能性分類標題（如 `## 1. Architectural Principles`）維持英文 |
| 描述性內容 | 繁體中文 | Prompt 主體內容使用繁中，兼顧團隊審查與維護便利性 |
| 技術術語 / API / Code | English | 專有名詞、程式碼片段、變數名稱等一律英文，不強行翻譯 |

**原則**：英文骨架、中文血肉。Header 和技術語彙用英文確保 LLM 精準理解語意；說明文字用繁中確保團隊可讀性。

---

## 段落結構定義 (Section Structure)

以下定義 9 個標準段落。每個段落標記為：
- **[REQUIRED]**：所有 Prompt Template 必須包含
- **[CONDITIONAL]**：依任務性質決定是否納入

段落**必須依照下方定義的順序排列**，不得任意調換。若某段落不適用，整段省略即可，不留空標題。

---

### §1. Role `[REQUIRED]`

```markdown
# Role

<角色職稱，英文>。
<1-3 句話定義此角色的專長、職責範圍、以及明確的職責邊界（什麼不做）。>
```

**撰寫規範**：
- 第一行為角色職稱（英文），採用「Senior {Domain} Specialist」或等效格式。
- 後續說明此角色**負責什麼**與**不負責什麼**。明確劃定邊界可避免 LLM 越權產出。
- Role 段落控制在 3-5 行內。過長的背景知識應移至 §2。

**範例**：
```markdown
# Role

Senior Requirement Analyst & Architecture Mapper.
你負責分析 input REQ-BIZ items 並將其分解為 atomic Requirement Items (Capabilities)。
你必須嚴格依據 Architecture Overview 中定義的結構 (System / Domain / Toolkit) 進行映射。
你不負責定義 Feature 名稱、FU 名稱或具體 component signatures。
```

---

### §2. Project Context & Standards `[CONDITIONAL]`

```markdown
# Project Context & Standards

<以 H2 子標題組織，將 LLM 執行任務所需的專案知識 Hard-Code 於此。>
```

**定位**：將 LLM 完成任務所必需的**專案領域知識**預先擷取並寫死在 Prompt 中，避免依賴上傳整份文件帶來的上下文噪音。

**撰寫規範**：
- 使用 `## N. <English Topic Title>` 分段（如 `## 1. Architectural Principles`）。
- 每個子段落聚焦單一主題，避免混雜。
- 僅納入**執行本任務必需**的知識片段。不相關的專案知識不應出現。
- **來源標記 (Mandatory)**：每個 H2 子段落必須緊接在標題下方以 `` ```human-only `` 區塊標註其來源文件與章節。此標記是日後專案文件更新時追溯同步的唯一依據，不得省略。

**適用時機**：
- 任務涉及專案特有的架構規範、命名規則、方法論或 PNFRs。
- LLM 需要具備特定領域知識才能正確執行任務。

**不適用時機**：
- 任務所需知識已完全包含在 Input Files 中，不需額外 Hard-Code。
- 任務為純格式轉換或簡單文字處理，無專案規範依賴。

**範例**：
````markdown
# Project Context & Standards

## 1. Architectural Principles

```human-only
Ref: PROJECT_DESIGN-ARCHITECTURE.md §3.2
```

* **Public Container Pattern**：
    * `__init__.py` 是 FU Container 的唯一公開入口。
    * 具體實作必須位於私有模組（以 `_` 開頭）。
* **Dependency Rule**：
    * Library 位於架構最底層。嚴禁依賴 `businesssys` 或 `datasource`。

## 2. Naming & Path Standards

```human-only
Ref: PROJECT_DESIGN-ARCHITECTURE.md §5.3
```

| Variable | Definition | Example |
|:--|:--|:--|
| `<fu_path>` | FU Container 相對於專案根目錄的完整路徑 | `wutils/io` |
| `<fu_name>` | 功能單元的邏輯名稱 (kebab-case) | `pickle-io` |
````

---

### §3. Input Files `[CONDITIONAL]`

```markdown
# Input Files

<列出 LLM 需要接收的所有輸入檔案。>
```

**撰寫規範**：

每個 Input File 必須包含以下三要素：
1. **Prompt 內引用名稱 (Bold)**：後續段落中引用此檔案時使用的名稱。
2. **實際路徑**：Hard-Code 常數路徑 或 `{{PLACEHOLDER}}` 動態變數。
3. **說明**：檔案用途與重點閱讀指引。

**格式範本**：
```markdown
# Input Files

1. **AnalysisSOP** (Real Path: `docs/standards/req-analysis/biz-req-analysis-sop.md`)
   分析方法論與標準作業程序。
   - **§0**: 術語定義與核心規範（務必先閱讀）
   - **§1-§6**: 分析步驟與驗證檢查清單

2. **TargetReqSpec** (Real Path: `{{FU_REQ_FILE}}`)
   待設計的 Library FU 技術需求規格文件。

3. **FormatGuide** (Real Path: `docs/standards/library-design.md`)
   Design Spec 的格式規範與撰寫指引。
```

**路徑類型**：
- **Hard-Code 路徑**：適用於整個流程固定不變的參考文件（如 SOP、Format Guide）。
- **Placeholder 路徑 (`{{VAR}}`)**：適用於每次執行時動態替換的檔案。

---

### §4. Input Context `[CONDITIONAL]`

```markdown
# Input Context

<動態注入的執行期上下文資料。>
```

**定位**：承載每次執行時不同的**動態資料**。與 §3 (Input Files) 的區別在於：Input Files 是完整檔案的引用，Input Context 是結構化或非結構化的資料片段。

**撰寫規範**：
- 使用 `{{PLACEHOLDER}}` 標記所有動態內容。
- 若有多個不同性質的輸入（如參數 + 資料），使用 H2 子標題分隔。
- 針對資料邊界保護，遵循下方的 **XML 標籤規則**。

#### XML 標籤資料邊界規則 (Data Boundary Tags)

**核心原則**：當 `{{PLACEHOLDER}}` 承載的是**不可預期的外部內容**（如使用者輸入、業務端撰寫的文本、上游流程產出物），**必須**在 Template 中使用具語意的 XML 標籤包裹，以物理隔離「系統指令」與「外部資料」，防止 Prompt Injection。

**XML 標籤必須寫在 Template 中，不寫在替換程式中。**
替換程式（`build_prompt()`）只負責執行 `replace()`，不負責判斷或附加 XML 標籤。資料邊界是 Prompt 設計決策，由 Template 作者在撰寫時決定，集中管理於 Template 文件中。

**何時必須使用 XML 標籤**：
- `{{PLACEHOLDER}}` 的內容來自外部、不可預期（如原始需求文本、使用者描述、程式碼片段）。
- 多個變數並列時，需要語意區分各自的邊界。

**何時不需要 XML 標籤**：
- `{{PLACEHOLDER}}` 僅替換簡單的純量值（如日期、名稱、路徑），且周圍已有明確的 Markdown 結構框定。

**XML 標籤命名規範**：
- 使用 `snake_case`，名稱應反映資料的語意（如 `<source_code>`、`<raw_requirements>`、`<upstream_report>`）。
- 避免過於泛化的名稱（如 `<data>`、`<input>`）。

**格式範本 — 帶 XML 邊界的動態資料**：
```markdown
# Input Context

## Input Parameters

- **Date**: {{TODAY}}
- **Target Library**: {{LIBRARY_NAME}}

## Input Data

<raw_requirements>
{{RAW_REQ_DESC}}
</raw_requirements>
```

**格式範本 — 多變數語意區分**：
```markdown
# Input Context

<source_init_py>
{{SOURCE_INIT_CONTENT}}
</source_init_py>

<target_init_py>
{{TARGET_INIT_CONTENT}}
</target_init_py>
```

**格式範本 — 簡單參數（不需 XML 標籤）**：
```markdown
# Input Context

- **Date**: {{TODAY}}
- **Feature Name**: {{FEATURE_NAME}}
```

---

### §5. Objective `[REQUIRED]`

```markdown
# Objective

<明確定義 LLM 在本次任務中需要達成的目標與交付物。>
```

**定位**：定義 **What** — 任務的最終目的與交付物。此段落只回答「要達成什麼」，不描述「怎麼做」。

**撰寫規範**：
- 以一句話概述任務目標，建立 Input → Output 的因果鏈（如「請依據 **AnalysisSOP** 分析 Input Context 中的 REQ-BIZ，產出結構化的需求分析報告。」）。
- 若任務有多個子目標，以編號清單列出，但每項描述的是**目標 (Goal)**，不是步驟 (Step)。
- **嚴禁在此段落列出執行步驟或推理流程**。所有「先做 A → 再做 B → 最後做 C」的描述一律放入 §6 Execution Steps。
- Objective 不應包含輸出格式的細節（那屬於 §7）。

**§5 與 §6 的分界原則**：
> **§5 回答 "What"**：要分析什麼、要產出什麼、要達成什麼效果。
> **§6 回答 "How to think"**：LLM 應按什麼順序推理、從哪裡提取什麼、對照什麼規則驗證。

**範例**：
```markdown
# Objective

請依據 **AnalysisSOP** 分析 Input Context 中的 REQ-BIZ 清單，並依照 **ReportStd** 的格式規範，產出完整的需求分析報告。

分析目標：
1. 驗證輸入的 REQ-BIZ 清單完整性與 Map Location 有效性。
2. 識別並拆離隱含的 Library Requirement 與 Database Requirement。
3. 建立需求間的依賴鏈與依賴契約。
```

---

### §6. Execution Steps `[CONDITIONAL]`

```markdown
# Execution Steps

**（在 Thinking 區塊中執行，不對外輸出）**

<引導 LLM 內部推理的思考步驟。>
```

**定位**：定義 **How to think** — LLM 的內部推理路徑與步驟拆解 (Chain-of-Thought Guidance)。此段落的內容不應出現在最終輸出中。

**適用時機**：
- 任務涉及多步驟推理、對照驗證或複雜轉換邏輯。
- 需要確保 LLM 在產出前先完成特定的前置分析或品質檢查。
- **只要任務需要步驟描述（「先做 A → 再做 B」），就必須使用此段落**，而非塞入 §5 Objective。

**不適用時機**：
- 任務目標單一且明確，LLM 不需要額外的推理引導即可直接產出。

**撰寫規範**：
- 使用編號清單，每步驟以動詞開頭（如「解析」、「轉換」、「驗證」）。
- 每個步驟應引用對應的 Input File 或 Context（如 `依據 AnalysisSOP §2`）。
- 步驟描述應具體指出 LLM 需要從哪裡提取什麼、對照什麼規則、產出什麼中間結果。

---

### §7. Output Specifications `[REQUIRED]`

```markdown
# Output Specifications

<定義輸出的結構、格式與內容要求。>
```

**定位**：描述 LLM 需要「建構什麼」— 輸出的完整樣貌。這是**建構性 (Constructive)** 的指引。

**撰寫規範**：
- 若輸出為檔案，先指定檔案路徑與格式：`**Output File**: docs/specs/<fu_path>/<fu_name>/design.md`
- 列出輸出的章節結構或資料欄位。
- 定義內容層面的要求（如語言規則、ID 格式、引用格式）。
- 若輸出有條件分支（如 Pass/Fail 兩種結果），以 `**Condition 1 / Condition 2**` 分別定義。

---

### §8. Output Constraints `[REQUIRED]`

```markdown
# Output Constraints

<定義輸出的硬性限制與禁止事項。>
```

**定位**：定義 LLM「不可以做什麼」— 輸出的邊界紅線。這是**限制性 (Restrictive)** 的規則。

**撰寫規範**：
- 使用編號清單，每條規則獨立一項。
- 每條 Constraint 應為一個可獨立驗證的「是/否」判斷。
- 優先列出最容易被違反的 Constraint。
- 常見 Constraint 類型：
  - **格式限制 (Format)**：僅輸出 Markdown / JSON / 純文字，不使用 code block 包裹。
  - **內容邊界 (Content Boundary)**：不包含開場白、結尾問候、思考過程。
  - **語言規則 (Language)**：技術術語用英文、描述用繁中。
  - **輸出起始規則 (Start Rule)**：第一行必須是 `File: ...` / 直接以 `# Title` 開頭。
  - **保護限制 (Preservation)**：嚴禁修改未被指定的既有程式碼；嚴禁竄改上游傳入的 ID 或 Map Location；嚴禁刪除與當前任務無關的內容。此類型在重構、分析、Checking 任務中尤為關鍵，用以防止 LLM 擅自「改善」不屬於其職責範圍的內容。

**與 §7 的分界原則**：
> 如果一條規則描述的是「輸出應該包含什麼」→ 放 §7 Output Specifications。
> 如果一條規則描述的是「輸出不可以做什麼」或「必須嚴格遵守的硬約束」→ 放 §8 Output Constraints。

---

### §9. Quality Assurance Checklist `[CONDITIONAL]`

```markdown
# Quality Assurance Checklist

<LLM 在生成輸出前必須逐一核對的檢查項目。>
```

**定位**：作為 LLM 產出前的最終防線。要求 LLM 在 output 前自行逐項核對，攔截常見的遺漏與錯誤。

**撰寫規範**：
- 使用 `## <Letter>. <Category Name>` 分類組織（如 `## A. 語言規範`、`## B. 架構對應`）。
- 每條檢查項目使用 `- [ ]` checkbox 格式，構成可勾選的清單。
- 每條 item 應對應一個具體、可驗證的條件，而非模糊的「是否正確」。
- 檢查項目應引用對應的規範來源（如 `(AnalysisSOP §2)`, `(ReportStd §4.A)`）。

**適用時機**：
- 輸出涉及多項規範交叉驗證（如需求分析報告、設計規格書）。
- 歷史經驗中 LLM 容易在特定項目犯錯，需明確列出防範。

**不適用時機**：
- 輸出結構簡單且 §8 Output Constraints 已足以涵蓋所有品質要求。

---

## Prompt Template 骨架 (Copy-Paste Skeleton)

以下為可直接複製使用的空白骨架。請依據上方各段落的規範填入內容，並刪除不適用的 `[CONDITIONAL]` 段落。

````markdown
# Role

<角色職稱 (English)>.
<職責描述與邊界定義。>

# Project Context & Standards

<!-- [CONDITIONAL] 僅在任務需要專案特定知識時納入 -->

## 1. <Topic Title>

```human-only
Ref: <Source Document.md> §<Section>
```

<相關規範與知識。>

# Input Files

<!-- [CONDITIONAL] 僅在任務需要參考外部檔案時納入 -->

1. **<RefName>** (Real Path: `<hard-code path>` | `{{PLACEHOLDER}}`)
   <檔案用途說明。>

# Input Context

<!-- [CONDITIONAL] 僅在任務需要動態輸入資料時納入 -->
<!-- 不可預期的外部內容必須使用 XML 標籤包裹 -->

<raw_input>
{{INPUT_CONTEXT}}
</raw_input>

# Objective

<目標與交付物定義。嚴禁在此列出執行步驟。>

# Execution Steps

<!-- [CONDITIONAL] 任務涉及多步驟推理時必須納入 -->

**（在 Thinking 區塊中執行，不對外輸出）**

1. <步驟一>
2. <步驟二>

# Output Specifications

<輸出結構、格式與內容要求。>

# Output Constraints

1. <限制一>
2. <限制二>

# Quality Assurance Checklist

<!-- [CONDITIONAL] 僅在輸出涉及多項規範交叉驗證時納入 -->

## A. <Category>

- [ ] <檢查項目>
````

---

## 附錄：段落速查表

| 順序 | Header | 必要性 | 核心問題 |
|:--:|:--|:--:|:--|
| §1 | `# Role` | REQUIRED | 你是誰？負責什麼？不負責什麼？ |
| §2 | `# Project Context & Standards` | CONDITIONAL | LLM 需要哪些專案知識才能正確執行？ |
| §3 | `# Input Files` | CONDITIONAL | 需要參考哪些檔案？ |
| §4 | `# Input Context` | CONDITIONAL | 每次執行時的動態資料是什麼？ |
| §5 | `# Objective` | REQUIRED | 要做什麼？達成什麼目標？ |
| §6 | `# Execution Steps` | CONDITIONAL | LLM 應如何推理？（內部思考引導） |
| §7 | `# Output Specifications` | REQUIRED | 輸出長什麼樣？ |
| §8 | `# Output Constraints` | REQUIRED | 輸出不可以做什麼？ |
| §9 | `# Quality Assurance Checklist` | CONDITIONAL | 產出前需要核對什麼？ |
