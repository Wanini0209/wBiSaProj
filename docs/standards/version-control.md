# wBiSaProj 版本控制規範

## 文件定位

本文件定義 wBiSaProj 專案的版本控制標準 (Version Control Standards)。
本規範整合了 [方法論篇](docs/PROJECT_DESIGN-METHODOLOGY.md) 的核心原則與 Git 社群主流慣例（Conventional Commits），旨在建立一套嚴謹、可追溯的工作流程。

**適用對象**：所有參與開發的架構師 (SA)、開發者 (Developer) 與協作操作者 (Operator)。

---

## 1. 核心哲學

本專案的版控策略建立在以下三大核心哲學之上：

1. **原子化與可追溯性 (Atomicity & Traceability)**

   - Feature ↔ Branch：一個功能對應一個分支。
   - Task ↔ Commit：一個任務對應一個 Commit。
   - 確保版本歷史能精確反映「業務價值」到「技術實作」的演進過程。

2. **文件先行 (Document-First History)**

   - 開發功能時，分支的第一個 Commit 必須是定義「What & Why」的 `use-cases` 文件。
   - 這確保了任何查看歷史的人，都能先理解「為什麼要做」再看「怎麼做」。

3. **語意化通訊 (Semantic Communication)**

   - 採用 Conventional Commits 標準，讓 Commit Message 本身即具備機器可讀性與人類可讀性。

---

## 2. 分支策略 (Branching Strategy)

本專案採用基於 Gitflow 的簡化模型，並針對專案架構進行了路徑優化。

### 2.1 常駐分支

| 分支名稱 | 權限 | 用途 | 規範 |
|:---------|:-----|:-----|:-----|
| `master` | Read-Only | 生產環境分支 | 僅接受從 `develop` 或 `hotfix` 的合併。代表當前線上穩定版本。 |
| `develop` | Protected | 開發主線分支 | 所有 `feature` 分支的合併目標。原則上禁止直接 Commit，所有變更需透過 PR 合併。 |

### 2.2 開發分支 (Feature Branches)

所有開發工作（包含功能實作與規範修訂）都必須在獨立的 `feature` 分支上進行。

**分支命名格式**：
`feature/<root>/<hierarchy>/<feature_name>`

**命名規則**：
分支路徑必須採用**階層式命名**，且其結構應與該 Feature 在 `docs/use-cases/` 中的相對路徑完全一致（不含 `docs/use-cases/` 前綴）。這確保了 Git 分支、文件目錄與程式碼架構三者的高度對應。

| Feature 類型 | 命名邏輯 | 分支命名範例 |
|:-------------|:---------|:-------------|
| **Business Feature** | `<system>/<domain>/...` | `feature/gms/user/user-registration` |
| **Data Pipeline Feature** | `<system>/etl/<domain>/...` | `feature/gms/etl/market/stock/daily-sync` |
| **Data Source Feature** | `<system>/<domain>/...` | `feature/twseprice/price/daily-price` |
| **Library Feature** | `<library>/<toolkit>/...` | `feature/core/validator/format-rules`<br>`feature/wutils/io/pickle-io` |
| **Project Standards** | `project` | `feature/project/update-vcs-standards` |

> **說明**：即使是修訂文件，建立分支的主要目的是為了 Pull Request (Code Review)，確保規範的變更已取得團隊共識。

---

## 3. 提交規範 (Commit Convention)

本專案嚴格遵循 Conventional Commits 1.0.0 規範。

### 3.1 訊息結構

一個標準的 Commit Message 包含三個部分，中間必須保留空行：

```text
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### 3.2 Header 規範 (Line 1)

Header 總長度不得超過 72 字元。

#### 1. Type (類型)

| Type | 說明 | 觸發版本號更新 (SemVer) |
|:-----|:-----|:------------------------|
| `feat` | 新增功能 (Feature) | MINOR |
| `fix` | 修復錯誤 (Bug Fix) | PATCH |
| `docs` | 文件變更 (包含內容修訂與文件排版) | PATCH (通常不觸發) |
| `style` | 程式碼格式調整 (不影響程式邏輯，如空白、縮排) | PATCH (通常不觸發) |
| `refactor` | 程式碼重構 (既非新增功能也非修復錯誤) | PATCH |
| `test` | 新增或修正測試 | PATCH (通常不觸發) |
| `chore` | 建構過程或輔助工具的變動 (如 dependencies) | PATCH (通常不觸發) |

#### 2. Scope (範圍)

Scope 必須精準反映變更的影響範圍。本專案採用三軌制 Scope：

| 提交情境 | 對象文件/代碼 | Scope 規則 | 範例 |
|:---------|:--------------|:-----------|:-----|
| 專案規範文件（獨立於功能外） | 1. `docs/` 根目錄文件<br>2. `docs/standards/` 下所有文件 | 固定使用 `project` | `docs(project): update vcs standards` |
| 功能定義文件（Use Cases） | `docs/use-cases/...` | 對應 `use-cases` 的分類路徑 | `docs(use-cases/gms/user): define requirements` |
| 功能實作（Code & Specs） | `<fu_path>` 下的程式碼、Specs 與測試 | 對應受影響的 FU Container 路徑 | `feat(gms/api/user/profile): impl user api` |
| 專案級工具 | `wutils`, 根目錄設定檔 | 使用模組名稱 | `chore(build): update poetry.lock` |

#### 3. Subject (主旨)

- 使用英文撰寫。
- 使用祈使句 (Imperative mood)：例如用 "add" 而非 "added"。
- **動詞開頭小寫 (Lower case start)。**
- **內文大小寫原則**：
  - 原則上採全小寫。
  - **例外**：專有名詞（如 `AWS`, `JSON`）、類別名稱（如 `UserProfile`）、常數或特定術語應保留其慣用的大小寫格式，以維持可讀性。
- 結尾不加句號。

### 3.3 Body 與 Footer 規範

當變更較為複雜時，強烈建議填寫 Body。

- **Body**：
  - 必須與 Header 隔開一行。
  - 每行長度建議限制在 72 字元內（自動換行）。
  - 說明變更的動機 (Motivation) 以及與之前行為的差異。
  - 支援 Markdown 列表格式（使用 `-` 或 `*`）。

- **Footer**：
  - 用於參照 Issue（如 `Closes #123`）。
  - Breaking Changes 必須在此標註，以 `BREAKING CHANGE:` 開頭。

### 3.4 完整範例集 (Comprehensive Examples)

LLM 或開發者在撰寫 Commit Message 時，應參考以下範例的完整度：

#### 範例 A：標準功能實作 (含 Body)

```text
feat(gms/service/user): implement user registration logic

This adds the core registration flow including:
- Password hashing using bcrypt
- Email uniqueness validation
- Creation of default user profile

The logic is decoupled from the API layer to allow future reuse.
```

#### 範例 B：修復錯誤 (含 Issue Reference)

```text
fix(tej/collector/price): correct date parsing format

The previous parser assumed 'YYYY/MM/DD' but the source
changed to 'YYYY-MM-DD', causing data sync failures.

Closes #45
```

#### 範例 C：重大變更 (Breaking Change)

```text
refactor(core/interfaces): rename stock provider method

BREAKING CHANGE: `get_price` has been renamed to `get_daily_price`
to better distinguish it from the new `get_realtime_price` method.
All implementation classes must be updated.
```

#### 範例 D：專案規範修訂

```text
docs(project): update version control standards

- Enforce 72-character limit for commit headers
- Add detailed examples for multi-line commit messages
- Clarify branch naming rules for project standards
```

---

## 4. 開發工作流程 (Workflow Lifecycle)

### 場景 A：開發一般功能 (Feature Development)

遵循標準的 Gitflow 與「1+N 提交結構」：

1. **建立分支**：
   分支名稱需包含完整的領域階層路徑。

   ```bash
   git checkout develop
   # 範例：在 GMS 系統 User Domain 下的註冊功能
   git checkout -b feature/gms/user/user-reg
   ```

2. **提交 1 (Docs)**：定義需求
   Scope 需對應 `use-cases` 的完整目錄路徑。

   ```bash
   git add docs/use-cases/gms/user/user-reg/
   git commit -m "docs(use-cases/gms/user/user-reg): define registration requirements"
   ```

3. **提交 N (Impl)**：實作任務

   ```bash
   # 這裡僅為 CLI 簡寫，實際建議使用 git commit 開啟編輯器撰寫多行訊息
   git add gms/db/user/profile/
   git commit
   ```

4. **合併 (Merge Strategy)**：

   - 推送並發起 PR 合併至 `develop`。
   - 關鍵規範：必須採用 Merge Commit (`--no-ff`) 進行合併。
      - 禁止使用 Squash Merge，因為這會導致 Feature 分支內的 Task 提交歷史被壓縮，丟失「文件先行」與「原子化實作」的對應脈絡。

### 場景 B：修訂專案規範 (Project Standards Update)

當需要修改 `docs/` 根目錄或 `docs/standards/` 下的規範文件時，視同一個 Project Feature 處理：

1. **建立分支**：使用 `project` 作為路徑，並使用 `feature/` 作為前綴。

   ```bash
   # 範例：更新版本控制規範
   git checkout -b feature/project/update-vcs-rules
   ```

2. **提交變更**：

   - Scope 必須為 `project`。
   - Type 必須為 `docs`。

   ```bash
   git add docs/standards/version-control.md
   git commit -m "docs(project): enforce feature branch for standards update"
   ```

3. **發起 Pull Request**：

   - 團隊成員進行審核 (Review)。
   - 確認規範變更的合理性與共識。

4. **合併**：

   - 審核通過後採用 Merge Commit 合併至 `develop`。
   - 例外：若僅為修正錯字 (Typo) 或格式 (Style)，允許使用 Squash Merge 以保持主線簡潔。

---

## 5. 品質閘道 (Quality Gates)

在執行 `git commit` 前，應確認：

1. **Scope 正確性**：修改 `docs/` 或 `docs/standards/` 下的文件時，Scope 是否為 `project`？
2. **流程合規**：是否已建立獨立分支？
3. **格式檢查**：
   - Header 是否 < 72 字元？
   - （若為複雜變更）是否有撰寫 Body 描述？
   - 是否符合 `<type>(<scope>): <subject>` 格式？

---

## 6. 範例對照表

| 場景 | 錯誤範例 ❌ | 正確範例 ✅ |
|:-----|:-----------|:-----------|
| 修改版本控制規範 | `docs: update git doc`（缺少 scope） | `docs(project): update version control standards`（scope 為 project） |
| 修改架構設計總表 | 直接 Commit 到 develop（違反流程） | 建立 `feature/project/...` 分支並發起 PR（確保共識） |
| 功能文件提交 | `docs(project): add user use-case`（Scope 混淆） | `docs(use-cases/gms/user/user-reg): define requirements`（Scope 對應完整路徑） |
| 功能實作提交 | `feat(api): add login`（Scope 太籠統，無 Body） | `feat(gms/api/auth): add login endpoint`（Scope 精確，建議附 Body） |
