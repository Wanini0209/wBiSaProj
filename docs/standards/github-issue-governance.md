# wBiSaProj GitHub Issue 治理規範

## 文件定位

本文件定義 wBiSaProj 專案的 GitHub Issue 治理標準 (GitHub Issue Governance Standard)。

本規範涵蓋 issue 的建立方式、結構定義、撰寫要求、與 branch / PR 的對應關係、PR linkage 標準寫法，以及 auto-close 前提與補救機制。

**適用對象**：所有參與開發的架構師 (SA)、開發者 (Developer) 與協作操作者 (Operator)。

**與其他規範文件的關係**：

- [版本控制規範](version-control.md) 定義 branch / commit / merge 策略與提交規範。
- [Pull Request Workflow 操作說明](pull-request-workflow.md) 定義 PR 建立、review 與合併流程。
- 本文件定義 issue 治理本體，包含 issue 結構、撰寫規範與 PR linkage 規則。三份文件各有明確的責任範圍，不應重複展開彼此的完整規則。

---

## 1. 導入目的

本專案導入 GitHub issue 治理規範，目的在於：

1. **可審查性 (Reviewability)**：每個 issue 應具備清楚的目標、範圍與完成條件，使其本身即可作為審查與驗收的依據。

2. **可追溯性 (Traceability)**：issue、branch 與 PR 之間應建立明確的對應關係，確保任何變更的動機、範圍與執行結果都能從 issue 歷史中回溯。

3. **邊界控制 (Scope Control)**：透過明確的結構與撰寫要求，避免 issue 範圍無限擴張、主 issue 與子 issue 角色混淆、或 PR linkage 斷裂導致歷史鏈結遺失。

---

## 2. Issue 類型與結構

本專案採用 **主 issue + sub-issues** 作為正式的父子階層機制。

### 2.1 主 issue (Parent Issue)

主 issue 用於追蹤一組相關子任務的整體計畫。

其職責為：

- 說明整體任務背景與目標
- 管理子 issue 的父子關係（透過 GitHub sub-issues 機制）
- 提供執行順序與相依關係的總覽
- 定義整體完成條件

主 issue 不應被單一 PR 直接關閉，而應在所有子 issue 完成後，由管理人員確認整體完成條件後關閉。

### 2.2 子 issue (Child Issue)

子 issue 對應單一可執行的工作目標。

其職責為：

- 描述該子任務的具體目標與範圍
- 定義邊界（包含明確不處理的事項）
- 定義可驗證的完成條件
- 對應一個主要 branch 與 PR

### 2.3 Standalone Issue

當工作主題高度聚焦、不需拆分為多個子任務時，可建立 standalone issue，不另設主 issue。

判斷原則：若需要修改的正式文件數量有限、且執行上屬於單一治理主題的落地，拆成主 issue + sub-issues 的管理成本可能高於實際收益。

### 2.4 Task List 的定位

主 issue 內可放置 task list，但其角色僅為**輔助展示**，不是第二套正式追蹤機制。

使用原則：

- task list 用於顯示 phase / milestone 分組與快速總覽進度。
- 正式的父子結構與狀態追蹤，以 sub-issues 為準。
- 不應手動維護 task list 勾選狀態；應讓 GitHub 依 linked issue 的狀態自動更新。

> **區分**：sub-issues = 正式結構，task list = 輔助展示。兩者不應形成兩套平行狀態來源。

---

## 3. Issue 撰寫要求

### 3.1 最小必要欄位

#### 主 issue

主 issue 至少應包含以下欄位：

| 欄位 | 用途 |
|:-----|:-----|
| `Background` | 說明為何需要這組工作 |
| `Goal` | 說明整體要達成的結果 |
| `Scope` | 列出子任務與 phase 分組 |
| `Dependency order` | 說明建議執行順序與相依關係 |
| `Completion criteria` | 定義整體完成條件 |

#### 子 issue / Standalone issue

子 issue 或 standalone issue 至少應包含以下欄位：

| 欄位 | 用途 |
|:-----|:-----|
| `Background` | 說明為何需要這次工作 |
| `Goal` | 說明本次要達成的結果 |
| `Scope` | 列出本次處理內容 |
| `Out of scope` | 明確列出本次不處理的內容 |
| `Completion criteria` | 定義可驗證的完成條件 |

#### 建議欄位

以下欄位非強制，但在適用情境下建議納入：

- `Dependency`：標示本 issue 是否需等待其他 issue 先完成。
- `Notes`：補充說明。

### 3.2 Issue 標題格式

建議 issue 標題遵循與 commit message 一致的語意化格式：

```text
<type>(<scope>): <subject>
```

子 issue 建議在標題中加註任務編號，方便排序與辨識：

```text
<type>(<scope>): [Task X] <subject>
```

範例：

```text
docs(project): define GitHub issue governance standard
docs(project): [Task 1] align ETL public structure model
docs(project): [Task 2] define and align domain naming policy
```

---

## 4. 撰寫原則

### 4.1 單一目標原則

一個子 issue 應只描述一個可審查的核心工作目標。不應將性質不同的工作混入同一個 issue。

若一個 issue 同時包含政策定義、範例清理與文件全面重寫，則應考慮拆分。

### 4.2 `Out of scope` 必填

`Out of scope` 是最重要的邊界控制欄位之一。

凡是容易「順手一起改」的議題，都應明確寫進 `Out of scope`，以避免在執行過程中不自覺擴張範圍。

### 4.3 `Goal` 應描述結果

`Goal` 應描述預期達成的結果，而非僅描述動作。

| 不建議寫法 | 建議寫法 |
|:-----------|:---------|
| revise docs | align ETL public structure with the approved domain-first model |
| clean up wording | define navigation as a governance-oriented core document |

### 4.4 `Completion criteria` 必須可驗證

完成條件應寫成可被審查或客觀驗證的結果，而非模糊描述。

| 不建議寫法 | 建議寫法 |
|:-----------|:---------|
| looks good | no formal document still uses `etl/jobs/...` as a public path model |
| updated | `PROJECT_DESIGN.md` provides an explicit entry to `PROJECT_DESIGN-NAVIGATION.md` |
| aligned | PR linkage section is present in `pull-request-workflow.md` and references this standard |

### 4.5 主文應保持可執行摘要

Issue 主文應保持為可直接執行的摘要，不應將大量討論歷程、聊天記錄或來回辯論塞進主文。

討論與決策過程可放在 issue comment 中；主文應持續維護為反映當前共識的精簡內容。

---

## 5. Issue / Branch / PR 對應原則

### 5.1 建議對應關係

本專案建議維持以下對應關係：

```text
1 子 issue → 1 branch → 1 主要 PR → 1 merge 記錄
```

這種一致的對應關係有助於追蹤與審查。

### 5.2 例外處理

若某 issue 因範圍較大，需拆成多個 PR 處理，應在 issue comment 中清楚記錄各 PR 的對應關係與處理範圍。

### 5.3 標題一致性

Issue title 應能對應至 branch name 與 PR title，使三者在追蹤時容易辨識。

例如：

| Issue title | Branch name | PR title |
|:------------|:------------|:---------|
| `docs(project): define GitHub issue governance standard` | `docs/project/define-github-issue-governance-standard` | `docs(project): define GitHub issue governance standard` |

---

## 6. PR Linkage 規則

### 6.1 PR 完整完成子 issue 時

當一個 PR 完整解決某個子 issue 時，在 PR description 最後加入：

```md
## Issue linkage

Closes #<child-issue-number>

Parent issue: #<parent-issue-number>
```

- `Closes #<child-issue-number>`：PR merge 後，GitHub 會自動關閉該子 issue（需符合 default branch 條件，見第 7 章）。
- `Parent issue: #<parent-issue-number>`：保留與主 issue 的關聯，但不會觸發主 issue 的自動關閉。

若為 standalone issue，省略 `Parent issue` 行即可：

```md
## Issue linkage

Closes #<issue-number>
```

### 6.2 PR 僅推進 issue、尚未完整完成時

若 PR 只完成部分工作，不應使用 `Closes`，改用一般 reference：

```md
## Issue linkage

Related to #<child-issue-number>

Parent issue: #<parent-issue-number>
```

這會建立 PR 與 issue 的關聯，但不會觸發自動關閉。

### 6.3 不建議的 linkage 寫法

以下做法不建議：

- 使用 `Closes #<parent-issue-number>` 直接關閉主 issue。主 issue 應在所有子 issue 完成後手動關閉。
- 一個 PR 同時 `Closes` 多個不相關的 issue。
- PR 只完成部分工作，卻使用 `Closes`。
- PR description 中完全不提對應 issue。

### 6.4 PR 連接對象原則

PR 應連到**當次實際完成的子 issue**，而非主 issue。主 issue 僅保留作為總追蹤入口。

---

## 7. Default Branch 與 Auto-Close 前提

### 7.1 Auto-Close 的必要條件

GitHub 的 `Closes #<issue-number>` 關鍵字，只有在 PR **target 為 repository 的 default branch** 時，才會在 merge 後自動關閉對應 issue。

因此，若日常 PR 的 merge 目標為 `develop`，但 repository 的 default branch 設為 `master`，則 `Closes` 關鍵字不會按預期運作。

### 7.2 建議配置

若本專案的日常整合主幹為 `develop`，建議將 GitHub repository 的 default branch 設為 `develop`，使下列行為與實際開發流程一致：

- PR 預設目標分支
- Issue auto-close
- Linked PR 行為

### 7.3 確認方式

確認 default branch 設定：

1. 進入 repository **Settings**。
2. 找到 **Default branch** 區段。
3. 確認目前設定的 branch 與日常整合主幹一致。

確認 auto-close 設定：

1. 進入 repository **Settings** → **General**。
2. 找到 **Auto-close issues with merged linked pull requests**。
3. 確認已啟用。

> **注意**：上述為 repository 層級的設定操作，不屬於本文件定義的文件治理範圍。本文件僅說明 auto-close 的前提條件與建議配置方向。

---

## 8. Missed Linkage 的補救方式

### 8.1 適用情境

若 PR 已 merge，但當時未正確建立與子 issue 的 linkage（例如未寫 `Closes` 或寫錯對象），此時無法再透過 PR 自動關閉 issue。

### 8.2 建議補救流程

最穩定的補救方式為在**子 issue** 中留下 comment，補上 PR 與主 issue 的關聯，然後手動關閉：

```md
Completed by PR #<PR_NUMBER>: <SHORT_PR_TITLE>.

Parent issue: #<PARENT_ISSUE_NUMBER>
```

comment 貼完後，手動按 `Close issue` 關閉該子 issue。

### 8.3 不建議作為標準流程的做法

上述補救機制僅用於事後修正。不應將「先 merge 再手動補 linkage」作為日常標準流程，因為這會削弱 PR 與 issue 的自動連動效益，增加遺漏風險。

正常流程中，linkage 應在 PR 建立時就寫入 description。

---

## 9. 建立 Issue 的建議流程

### 9.1 主 issue + sub-issues 的建立順序

當一個任務需要拆分為主 issue + 多個子 issue 時，建議依下列順序操作：

1. **先建立所有子 issue**，並記下各自的 issue 編號。
2. **再建立主 issue**，將 task list 中的 `#ISSUE_NUMBER` 替換為實際子 issue 編號。
3. **將子 issue 掛為主 issue 的 sub-issues**：在主 issue 的 sub-issues 區塊中，使用 `Add existing issue` 將各子 issue 加入。

### 9.2 後續維護

建立完成後，追蹤方式為：

- 以 **sub-issues** 為正式結構與狀態來源。
- 以 issue open / closed 為正式狀態。
- task list 僅供總覽參考，不手動維護勾選。

---

## 10. 建議管理規則

1. **每個子 issue 對應一個主要 PR**：這是最容易追蹤的對應方式。

2. **主 issue 不使用 `Closes`**：主 issue 僅用於追蹤整體進度，不應被單一 PR 意外關閉。

3. **Task list 不手動維護勾選**：避免形成兩套狀態來源。

4. **Issue、branch、PR 三者應對齊**：維持 1 子 issue → 1 branch → 1 PR → 1 merge 記錄的對應關係。

5. **Merged PR 若未正確 linkage，應立即補救**：避免 issue 與 PR 歷史鏈結斷裂。

6. **何時應開 issue**：建議在以下情境先建立 issue，而非直接修改：
   - 需要先討論定位、政策或架構決策。
   - 涉及多份文件同步修改。
   - 涉及明確的相依順序。
   - 需要審查、回顧或後續追蹤。
   - 需要與 branch / PR 建立正式對應關係。

---

## 11. 模板

### 11.1 主 issue 模板

```md
# <type>(<scope>): <title>

## Background
<為什麼要做這組工作>

## Goal
<這組工作整體要達成什麼>

## Scope

### Phase 1
- [ ] #<ISSUE_NUMBER>
- [ ] #<ISSUE_NUMBER>

### Phase 2
- [ ] #<ISSUE_NUMBER>
- [ ] #<ISSUE_NUMBER>

> Note:
> - The parent/child structure is managed formally through GitHub sub-issues.
> - The checklist above is used only as a progress dashboard.
> - Do not manually maintain checklist state; let GitHub sync it from linked issue status.

## Dependency order
1. <task 1>
2. <task 2>
3. <task 3>

## Completion criteria
- <整體完成條件 1>
- <整體完成條件 2>

## Notes
<補充說明>
```

### 11.2 子 issue 模板

```md
# <type>(<scope>): [Task X] <title>

## Background
<為什麼要做這件事>

## Goal
<這次要達成什麼>

## Dependency
- Depends on: <issue number / none>

## Scope
- <本次處理內容 1>
- <本次處理內容 2>

## Out of scope
- <這次明確不處理的內容 1>
- <這次明確不處理的內容 2>

## Completion criteria
- <完成判準 1>
- <完成判準 2>
```

### 11.3 Standalone issue 模板

Standalone issue 不使用 `[Task X]` 標記。其餘欄位結構與子 issue 相同。

```md
# <type>(<scope>): <title>

## Background
<為什麼要做這件事>

## Goal
<這次要達成什麼>

## Dependency
- Depends on: <issue number / none>

## Scope
- <本次處理內容 1>
- <本次處理內容 2>

## Out of scope
- <這次明確不處理的內容 1>
- <這次明確不處理的內容 2>

## Completion criteria
- <完成判準 1>
- <完成判準 2>
```

### 11.4 PR Issue Linkage 模板

#### 完整完成子 issue

```md
## Issue linkage

Closes #<child-issue-number>

Parent issue: #<parent-issue-number>
```

#### 僅推進、未完整完成

```md
## Issue linkage

Related to #<child-issue-number>

Parent issue: #<parent-issue-number>
```

#### Standalone issue

```md
## Issue linkage

Closes #<issue-number>
```

#### Missed linkage 補救 comment

```md
Completed by PR #<PR_NUMBER>: <SHORT_PR_TITLE>.

Parent issue: #<PARENT_ISSUE_NUMBER>
```

---

## 12. 常見錯誤

| 常見錯誤 | 問題 | 建議做法 |
|:---------|:-----|:---------|
| Issue 範圍過大 | 看起來像一份小型專案，無法單次 PR 處理 | 拆分為主 issue + sub-issues |
| 未填寫 `Out of scope` | 無法判斷哪些事項不應順手處理 | `Out of scope` 必填 |
| `Completion criteria` 過於抽象 | 審查者無法客觀判斷是否完成 | 寫成可驗證的具體結果 |
| Issue title 與 branch / PR 對不上 | 後續追蹤困難 | 維持 title 一致性 |
| 主 issue 與子 issue 角色混淆 | 主 issue 被用來管落地、子 issue 被用來管整體 | 主 issue 管整體，子 issue 管落地 |
| 使用 `Closes` 關閉主 issue | 主 issue 被單一 PR 意外關閉 | PR 只 `Closes` 子 issue |
| PR description 不寫 issue linkage | issue 與 PR 歷史鏈結斷裂 | 建立 PR 時一律寫入 linkage |
| 手動維護 task list 勾選 | 形成兩套狀態來源 | 讓 GitHub 自動同步 |

---

## 13. 規範生效日

**本規範自 2026-04-14 起生效。**

在此日期前建立之歷史 issue 與 PR，可能不完全符合現行規範。原則上不追溯修改既有歷史紀錄，但自生效日起之新 issue、新 PR 與新 linkage 應全面遵守本規範。
