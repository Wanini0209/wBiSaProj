# Pull Request Workflow 操作說明

## 1. 文件目的與適用範圍

本文件為操作型說明文件，指導開發人員依版本控制規範執行完整的 branch → push → PR → merge 流程。

**適用情境**：一般多人開發，以及暫時單人維護的情境。

**與規範文件的關係**：本文件是操作手冊，正式制度以 [版本控制規範](version-control.md) 為準。測試閘道規則以 [測試規範](testing.md) 為準。Issue 結構、撰寫規範與 PR linkage 規則以 [GitHub Issue 治理規範](github-issue-governance.md) 為準。

---

## 2. 流程總覽

一次完整的開發交付流程如下：

```text
1.  同步 develop
2.  建立工作 branch
3.  開發與 commit
4.  執行適當測試
5.  push branch（觸發 pre-push gate）
6.  在 GitHub 建立 PR
7.  review / self-review
8.  使用 Merge Commit 合併
9.  本地同步 develop
10. 刪除已完成 branch
```

以下各節依此順序逐步說明。

---

## 3. 開始前：同步 `develop`

每次開始新工作前，先將本地 `develop` 同步至最新狀態：

```bash
git checkout develop
git fetch origin
git merge --ff-only origin/develop
```

**為何採用 `fetch` + `merge --ff-only`**：本文件統一使用 `fetch` + `merge --ff-only` 作為標準操作寫法。這種寫法會將同步意圖明確寫在指令中，不依賴本機 Git 設定，也較不易與 branch integration 的 merge commit 混淆。若此 repository 已正確設定 `pull.ff=only`，則 `git pull` 亦可達成相同效果；但為避免歧義，本文件不以其作為標準示例。

**若 `--ff-only` 失敗**：代表本地 `develop` 不是遠端的乾淨副本（可能曾在本地 `develop` 上直接提交過變更）。此時應先檢查本地 `develop` 的狀態，將任何不應存在的本地變更移至獨立 branch，再重新同步。

---

## 4. 建立工作 branch

從最新 `develop` 建立工作分支：

```bash
git checkout -b <branch-name>
```

分支命名應遵循版本控制規範 §2.3 的階層式命名格式：

```text
<branch_type>/<root>/<hierarchy>/<work_name>
```

範例：

```bash
git checkout -b feature/gms/user/user-registration
git checkout -b fix/wsatools/init-relative-imports
git checkout -b docs/project/update-testing-standards
git checkout -b chore/devtools/pre-commit-hooks
```

---

## 5. 開發、commit 與測試

### 5.1 提交前測試

原則上，每次提交前應先執行全域一般測試：

```bash
inv test
```

僅在刻意維持 Task ↔ Commit 原子性時，才允許例外使用主體測試：

```bash
inv test --project wutils
inv test --project gms
```

主體測試不是省時捷徑。使用後應立即回到全域測試，逐步修正剩餘問題。完整規則請參閱 [測試規範 §1.5](testing.md#15-提交與推送的測試責任分層)。

### 5.2 LLM 測試

若本次變更涉及 prompt template、parse/schema 契約、Quality Loop 流程等 LLM 相關內容，應手動執行 LLM 測試：

```bash
inv test.llm
inv test.llm --project wsatools
```

### 5.3 提交

使用 `git commit`（不帶 `-m`）開啟編輯器撰寫完整的多行 commit message，格式遵循版本控制規範 §3：

```bash
git add <files>
git commit
```

---

## 6. 安裝 hooks

本專案使用 `pre-commit` 框架管理三種 Git hooks。首次 clone 或 hook 設定有變更時，須執行安裝：

```bash
pipenv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

各 hook 的職責：

| Hook 階段 | 驗證內容 |
|:----------|:---------|
| `pre-commit` | 格式化（Black）、linting（Ruff）、檔案衛生檢查 |
| `commit-msg` | commit message convention（commitizen） |
| `pre-push` | 全域一般測試（`inv test`） |

**注意**：若 shell 找不到 `pre-commit` 指令，應使用 `pipenv run pre-commit ...` 執行，確保在正確的虛擬環境中運行。

---

## 7. push branch

將工作分支推送至遠端：

```bash
git push -u origin <branch-name>
```

push 時會自動觸發 `pre-push` hook，執行全域一般測試。若測試失敗，push 會被阻擋，應先修正問題再重新 push。

**不應跳過此步驟直接做本地整合**。每條 branch 都應獨立經過 push → PR → review → merge 流程。

---

## 8. 在 GitHub 建立 PR

1. 登入 GitHub，進入專案 repository 頁面。
2. 進入 **Pull requests** 頁籤，點選 **New pull request**。
3. 設定 base 與 compare：
   - **base**：`develop`（一般情況下的合併目標）
   - **compare**：選擇剛推送的工作 branch
4. 確認 diff 內容正確，檢查變更檔案與行數是否符合預期。
5. 填寫 PR 資訊：
   - **Title**：簡明描述本次交付的整體目的。
   - **Description**：列出各 commit 摘要、關鍵決策、與審查重點。
   - **Issue linkage**：若本次 PR 對應 GitHub issue，應在 description 最後加入 `Issue linkage` 區塊。基本使用脈絡為：`Closes`（PR merge 後完整完成 issue 時使用）、`Related to`（僅推進 issue、尚未完整完成時使用）、`Parent issue`（當 PR 對應子 issue，且需保留與主 issue 的父子脈絡時使用）。完整的 linkage 模板與使用規則，請參閱 [GitHub Issue 治理規範](github-issue-governance.md)。
6. 點選 **Create pull request**。

---

## 9. PR Review

### 9.1 多人開發情境

- 在 PR 頁面右側指定 reviewer。
- 等待 review 完成、討論解決後再合併。
- 若 reviewer 要求修改，在同一 branch 上補 commit 後 push，PR 會自動更新。

### 9.2 單人維護情境

若當前無其他可用 reviewer，允許採用 **Self Review + LLM-Assisted Review** 作為過渡 review 機制。

**操作方式**：

1. 在 GitHub PR 頁面的 **Files changed** 頁籤中，逐檔檢視自己的變更。
2. 可搭配 LLM 協助審查 commit 範圍、規範一致性與 PR 文案。
3. 在 PR 的 comment 中留下審查記錄，說明已確認的項目。

**建議 comment 範例**：

```text
Self Review + LLM-Assisted Review checklist:

- [ ] Commit scope and message convention
- [ ] Cross-file consistency (testing.md ↔ version-control.md)
- [ ] No unintended changes in diff
- [ ] Pre-push gate passed
```

當團隊恢復多人協作時，應回歸正式的人工 review 流程。

---

## 10. 合併 PR

在 GitHub PR 頁面底部的合併區域：

1. 點選合併按鈕旁的下拉選單。
2. 選擇 **Create a merge commit**。
3. 確認 merge commit message 正確後，點選確認合併。

**禁止使用 Squash and merge 或 Rebase and merge**（版本控制規範場景 B 中明確列出的 typo/style 例外除外）。

Merge Commit 的目的是保留分支邊界與 Task 提交歷史，這與本地同步 `develop` 的 fast-forward only 是不同概念。

---

## 11. 合併後同步本地 `develop`

PR 合併完成後，回到本機同步 `develop`：

```bash
git checkout develop
git fetch origin
git merge --ff-only origin/develop
```

確認同步成功後，刪除已完成的本地與遠端 branch：

```bash
git branch -d <branch-name>
git push origin --delete <branch-name>
```

---

## 12. 常見錯誤與排除

### A. `pre-commit: command not found`

`pre-commit` 安裝在 pipenv 虛擬環境中，直接在 shell 呼叫可能找不到。使用以下方式執行：

```bash
pipenv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

### B. `git pull` 跳出 merge editor 或產生非預期 merge commit

本文件在同步 `develop` 時，統一使用顯式的 `fetch` + `merge --ff-only` 作為標準做法：

```bash
git checkout develop
git fetch origin
git merge --ff-only origin/develop
```

若需要讓 repo 預設採用安全的同步行為，可設定 repo-local Git config：

```bash
git config --local pull.ff only
git config --local pull.rebase false
git config --local merge.ff false
```

以上設定的效果：`pull.ff only` 使 `git pull` 在無法 fast-forward 時直接失敗而非建立 merge commit；`merge.ff false` 使 `git merge` 預設產生 merge commit（用於分支整合時保留邊界）。兩者搭配可避免操作混淆。

### C. 在 GitHub 找不到 **Create pull request** 按鈕

常見原因：

- 尚未登入 GitHub，或帳號無此 repository 的寫入權限。
- 工作 branch 尚未 push 至遠端（需先執行 `git push -u origin <branch-name>`）。
- base 與 compare 設定不正確，確認 base 為 `develop`、compare 為工作 branch。

### D. PR base branch 選錯

一般開發情境下，PR 的 base branch 應為 `develop`。若選成 `master` 或其他分支，合併後變更會進入錯誤的目標分支。建立 PR 時務必確認 base 設定。
