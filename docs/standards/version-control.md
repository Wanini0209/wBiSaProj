# wBiSaProj 版本控制規範

## 文件定位

本文件定義 wBiSaProj 專案的版本控制標準 (Version Control Standards)。
本規範整合了 [方法論篇](docs/PROJECT_DESIGN-METHODOLOGY.md) 的核心原則與 Git 社群主流慣例（Conventional Commits），旨在建立一套嚴謹、可追溯的工作流程。

**適用對象**：所有參與開發的架構師 (SA)、開發者 (Developer) 與協作操作者 (Operator)。

**與其他規範文件的關係**：

- [Pull Request Workflow 操作說明](pull-request-workflow.md) 為本規範的操作型補充文件，指導 PR 建立、review 與合併流程。
- [GitHub Issue 治理規範](github-issue-governance.md) 定義 issue 結構、撰寫要求、PR linkage 規則與 auto-close 前提。本文件不重複展開完整的 issue governance 規則。

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
| `develop` | Protected | 開發主線分支 | 所有工作分支的合併目標。原則上禁止直接 Commit，所有變更需透過 PR 合併。 |

#### `develop` 本地同步定位

本地 `develop` 僅作為 `origin/develop` 的同步副本，不應作為長期承載未正式整合變更的工作分支。同步 `develop` 時應採 **fast-forward only**，確保本地 `develop` 始終與遠端保持一致，不以同步行為額外產生 merge commit：

```bash
git checkout develop
git fetch origin
git merge --ff-only origin/develop
```

此處的 fast-forward only 與分支整合時的 Merge Commit（`--no-ff`）是不同概念：前者用於保持本地同步副本乾淨，後者用於保留分支邊界與 Task 歷史。

### 2.2 工作分支 (Working Branches)

所有開發工作都必須在獨立的工作分支上進行，**嚴禁直接在 `develop` 上修改**。

本專案定義以下 7 種工作分支類型：

| Branch Type | 定位 | 適用情境 |
|:------------|:-----|:---------|
| `feature/*` | 新增功能、能力、正式規格落地 | 新功能開發、新模組、`wsatools` 的功能性增修 |
| `fix/*` | 一般錯誤修正與 merge 後 follow-up 修補 | bug fix、規範合規修正、小範圍回補、merge 後遺漏修正 |
| `hotfix/*` | 正式環境 / 穩定線緊急修補 | 已上線版本的緊急錯誤修復，需高優先級處理 |
| `refactor/*` | 不改外部行為的結構重整 | 模組拆分 / 搬移、命名調整、架構整理、內部結構重構 |
| `experiment/*` | 探索性、試驗性、尚未定案的工作 | 原型、spike、技術驗證、AI / workflow / toolchain 試驗 |
| `docs/*` | 純文件工作分支 | 架構文件修訂、standards 修訂、writing guides 修訂、純文件性 propagation 更新 |
| `chore/*` | 非功能性的專案維運與開發基礎設施調整 | invoke tasks、pre-commit hooks、dependencies、CI / lint / build config |

#### 分支類型使用要點

**`feature/*`**：`wsatools` 雖然是開發輔助工具，但它本身也是有功能、有介面的程式碼體系，因此 `wsatools` 的功能開發屬於 `feature`，不是 `chore`。

**`fix/*` vs `hotfix/*`**：`fix/*` 用於一般開發流程中的錯誤修正；`hotfix/*` 僅在需要對正式環境 / 穩定線進行緊急修補時使用。

**`experiment/*`**：產出不一定會直接 merge 成正式功能。必要時可在實驗完成後，另開正式 `feature/*` 或 `docs/*` 分支落地結果。

**`docs/*` 的使用邊界**：若分支交付物僅為文件，使用 `docs/*`；若分支交付物包含程式碼實作，則應使用 `feature/*`、`fix/*`、`refactor/*` 等較合適的 branch type。

**`chore/*`**：非功能性的專案維運工作也必須開分支，不應直接在 `develop` 上修改。

### 2.3 分支命名規則

所有工作分支統一採用階層式命名格式：

```text
<branch_type>/<root>/<hierarchy>/<work_name>
```

| Branch Type | 命名邏輯 | 範例 |
|:------------|:---------|:-----|
| `feature/*` | 對應 Feature 在 `use-cases` 的路徑，或以受影響模組範圍命名 | `feature/gms/user/user-registration`<br>`feature/wutils/io/pickle-io`<br>`feature/wsatools/llm/prompt-quality-loop` |
| `fix/*` | 對應受影響模組的最小共同範圍 | `fix/wsatools/init-relative-imports`<br>`fix/gms/service/user/profile-lookup` |
| `hotfix/*` | 可偏 issue / incident 導向 | `hotfix/gms/login-session-expiry` |
| `refactor/*` | 對應重構範圍 | `refactor/gms/service/user/profile-container` |
| `experiment/*` | 對應探索主題 | `experiment/wsatools/llm/auto-context-packing` |
| `docs/*` | 對應文件修訂範圍 | `docs/project/update-version-control-standards`<br>`docs/standards/testing-checklist-alignment` |
| `chore/*` | 對應工具 / 配置 / 基礎設施範圍 | `chore/build/update-poetry-lock`<br>`chore/devtools/pre-commit-hooks` |

> **說明**：建立分支的主要目的是為了 Pull Request (Code Review)，確保變更已取得團隊共識。

### 2.4 Branch Type 與 Commit Type 的關係

Branch type 與 commit type 是兩個不同維度的概念：

- **Branch type**：描述整個分支工作的**主要目的**
- **Commit type**：描述單一提交的**變更性質**

兩者通常相關，但**不要求一一對應**。一個分支上可能包含多種 commit types。

| Branch Type | 常見 Commit Types | 說明 |
|:------------|:------------------|:-----|
| `feature/*` | `feat`, `docs`, `test`, `refactor` | 功能開發過程可能包含文件與測試提交 |
| `fix/*` | `fix`, `docs`, `test` | 修錯過程常伴隨測試與文件修正 |
| `hotfix/*` | `fix`, `docs`, `chore` | 緊急修補通常以 fix 為主 |
| `refactor/*` | `refactor`, `docs`, `test` | 重構過程常伴隨測試與文件更新 |
| `experiment/*` | `feat`, `refactor`, `docs`, `chore`, `test` | 依實驗內容決定 |
| `docs/*` | `docs` | 純文件工作通常以 docs 為主 |
| `chore/*` | `chore`, `docs`, `fix` | 工具 / 配置 / 基礎設施調整 |

> **注意**：`hotfix` 與 `experiment` 是 branch type，不是 commit type。`hotfix/*` 分支上的 commit 通常使用 `fix` 作為 commit type；`experiment/*` 分支上的 commit 依實際變更性質選用適當的 commit type。此外，`docs/*` 為 branch type（表示分支工作性質為純文件修訂），`docs` 為 commit type（表示單一提交的變更性質為文件更新），兩者相關但不相同。

---

## 3. 提交規範 (Commit Convention)

本專案嚴格遵循 Conventional Commits 1.0.0 規範。

> **注意：Type 與 Scope 是兩個不同維度的決策。**
>
> - **Type** 用於描述變更性質（如 `docs`, `feat`, `fix`, `refactor`）
> - **Scope** 用於描述本次提交的影響範圍
>
> 因此，`docs` 類提交也可能使用路徑型 Scope（如 `use-cases/...`、`specs/...`）；
> 而功能實作類提交則依最小共同實作範圍決定 Scope。

### 3.1 訊息結構

一個標準的 Commit Message 包含三個部分，中間必須保留空行：

```text
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### 3.2 Header 規範 (Line 1)

Header 總長度原則上不超過 72 字元。

撰寫者應優先維持 header 精簡，使其在 `git log --oneline`、GitHub commit 列表等常見介面中保持良好的可讀性與辨識性。

若為保留必要的核心語意，header 可在有節制的前提下超出 72 字元，但應同時滿足以下條件：

- 已嘗試精簡措辭，確認無法在不損失核心語意的情況下進一步縮短
- 超出部分僅為保留必要的 scope 路徑、專有名詞或關鍵動詞，而非塞入額外細節
- 補充說明、背景資訊與變更清單等內容，應移至 body 而非擠進 header

此彈性不得常態化使用。若多數 commit 的 header 都超出 72 字元，應重新檢視 scope 設計或 subject 寫法是否過於冗長，而非以例外機制作為迴避精簡的依據。

#### 1. Type (類型)

> **核心原則**：Commit type 反映的是單一提交的**主要意圖**。一個 commit 可以附帶少量其他性質的變更（例如 `fix` commit 附帶少量文件修正），但應以該次提交最核心的目的選擇 type。若提交內容同時包含多種大型變更，應優先考慮拆分 commit，而非勉強以單一 type 包裝過多不相關內容。

##### 快速參照表

| Type | 說明 | 觸發版本號更新 (SemVer) |
|:-----|:-----|:------------------------|
| `feat` | 新增功能 (Feature) | MINOR |
| `fix` | 修復錯誤 (Bug Fix) | PATCH |
| `docs` | 文件變更 (包含內容修訂與文件排版) | PATCH (通常不觸發) |
| `style` | 程式碼格式調整 (不影響程式邏輯，如空白、縮排) | PATCH (通常不觸發) |
| `refactor` | 程式碼重構 (既非新增功能也非修復錯誤) | PATCH |
| `test` | 新增或修正測試 | PATCH (通常不觸發) |
| `chore` | 建構過程或輔助工具的變動 (如 dependencies) | PATCH (通常不觸發) |

> **注意**：`hotfix` 與 `experiment` 是 **branch type**，不是 commit type。`hotfix/*` 分支上的 commit 通常使用 `fix` 作為 commit type；`experiment/*` 分支上的 commit 依實際變更性質選用適當的 commit type。

##### 各 Type 的詳細使用指引

**`feat` — 新增功能**

- **定位**：新增功能、新能力、對外可感知的行為增量
- **適用情境**：新功能開發、新模組能力、新 API / 新工具能力、`wsatools` 的功能性增修
- **不適用**：單純修錯 → `fix`；單純結構重整 → `refactor`；純工具 / 配置 / 依賴維護 → `chore`
- **專案示例**：`feat(wsatools/llm): implement prompt quality loop`

**`fix` — 修復錯誤**

- **定位**：錯誤修正、缺陷修補
- **適用情境**：bug fix、合規性錯誤修正、merge 後 follow-up 小修補
- **不適用**：新功能 → `feat`；結構重整 → `refactor`；純文件工作 → `docs`
- **專案示例**：`fix(wsatools): use relative import for private modules in __init__.py`

**`docs` — 文件變更**

- **定位**：文件內容修訂（包含排版與結構調整）
- **適用情境**：standards / architecture / use-cases / specs / guides 的文字與結構修訂
- **不適用**：真正程式碼功能改動 → `feat` 或 `fix`
- **注意**：`docs/*` 是 branch type（分支工作性質），`docs(...)` 是 commit type（單一提交性質），兩者相關但不相同
- **專案示例**：`docs(project): revise branch type definitions`

**`style` — 格式調整**

- **定位**：不影響語義與行為的格式 / 風格調整
- **適用情境**：排版、空白 / 換行 / 格式化、無語義變更的樣式整理
- **不適用**：結構重整 → `refactor`；文件內容修訂 → `docs`
- **專案示例**：`style(wutils/io): apply black formatting`

**`refactor` — 程式碼重構**

- **定位**：不改外部行為的程式碼結構重整
- **適用情境**：模組拆分、命名重整、內部實作重構
- **不適用**：修正錯誤行為 → `fix`；新增能力 → `feat`
- **專案示例**：`refactor(core/validator): split format rules into dedicated module`

**`test` — 測試變更**

- **定位**：測試新增或測試修訂
- **適用情境**：新增測試、調整測試案例、改善測試覆蓋
- **不適用**：若同一提交的主要意圖是修錯或加功能，而只是附帶更新測試，則不必強行改用 `test`，仍以主要意圖為準
- **專案示例**：`test(wutils/io/pickle-io): add invalid payload edge cases`

**`chore` — 專案維運**

- **定位**：非功能性的專案維運與開發基礎設施調整
- **適用情境**：invoke tasks、pre-commit hooks、requirements / lockfile、tooling / CI / build / pyproject
- **不適用**：真正功能行為增修 → `feat`；真正錯誤修正 → `fix`
- **專案示例**：`chore(devtools): update pre-commit hooks`

##### 容易混淆的 Commit Types 對照

| 情境 | 正確選擇 | 原因 |
|:-----|:---------|:-----|
| 新增一個全新的 API 端點 | `feat` | 對外可感知的新功能 |
| 修正現有 API 端點的計算錯誤 | `fix` | 修正既有錯誤行為 |
| 將 service 模組拆分為更小的子模組 | `refactor` | 不改外部行為，只調整內部結構 |
| 修正 import 路徑以符合新規範 | `fix` | 修正合規性錯誤 |
| 更新 `pyproject.toml` 中的依賴版本 | `chore` | 工具 / 配置 / 依賴維護 |
| 修訂架構設計文件的章節結構 | `docs` | 文件本身的修訂 |
| 對程式碼做 Black 格式化 | `style` | 純格式調整，不影響語義 |
| 修錯順便補了對應的測試 | `fix` | 主意圖是修錯，測試是附帶 |
| 純粹為既有功能補充測試覆蓋 | `test` | 主意圖是補測試 |

#### 2. Scope (範圍)

Scope 必須精準反映變更的影響範圍。本專案依提交情境區分為以下規則：

| 提交情境 | 對象文件/代碼 | Scope 規則 | 範例 |
|:---------|:--------------|:-----------|:-----|
| 專案規範文件（Project-Level） | `docs/` 根目錄文件、`docs/standards/` 下所有文件 | 固定使用 `project` | `docs(project): update version control standards` |
| 功能定義文件（Feature Use Cases） | `docs/use-cases/...`，且屬於 Feature 開發流程的一部分 | 使用完整 `use-cases` 路徑 | `docs(use-cases/gms/user/user-reg): define registration requirements` |
| 純文件性 `use-cases` 修訂 | 僅修改 `docs/use-cases/...`，不伴隨功能與實作變更 | 使用 `docs/` 下共同上層路徑 | `docs(use-cases/gms/user): standardize requirements headings` |
| 純文件性 `specs` 修訂 | 僅修改 `docs/specs/...`，不伴隨功能與實作變更 | 使用 `docs/` 下共同上層路徑 | `docs(specs/wutils): align library test specs with revised testing rules` |
| 功能實作類提交（Code / Tests / Specs 一併提交） | `<fu_path>` 下的實作、測試與伴隨的 specs 修訂 | 使用能完整涵蓋本次所有受影響實作的最小共同容器路徑 | `feat(gms/api/user/profile): add user profile endpoint` |
| 專案級工具 | 根目錄設定檔、建構工具 | 使用模組名稱 | `chore(build): update poetry.lock` |

##### 純文件性 propagation 更新的 Scope 原則

當一次提交同時修改多份 `docs/use-cases/**` 或 `docs/specs/**` 文件，且這些修改：

- 不涉及功能與實作變更
- 修改模式一致
- 應共同審查與共同回滾

則可將其視為單一批次文件修訂提交。

此時 Scope 應使用該批文件在 `docs/` 下的共同上層路徑，
而非強制拆分為每個單一路徑各自一個 Commit。

例如：

- `docs(specs/wutils): align library test specs with revised testing rules`
- `docs(use-cases/gms/user): standardize section headings`

#### 3. Subject (主旨)

- 使用英文撰寫。
- 使用祈使句 (Imperative mood)：例如用 `add` 而非 `added`。
- **Subject 應優先描述本次提交帶來的具體變更結果，並使用與 Scope 抽象層級一致的精準動詞**。建議根據變更性質選用：
  - `add`：新增能力、介面、元件、配置、支援或流程。
  - `implement`：強調將既定設計、核心邏輯或演算法落地。
  - `define`：用於需求、規格、契約或用例定義。
  - `update`：用於既有內容調整。
  - `refactor`：用於不改變外部行為的內部重構。
  - `rename`、`remove`、`correct`：依實際變更選用更精準動詞。
- **避免使用未定義的縮寫動詞**（如 `impl`）。正式提交應使用完整拼寫。
- **動詞開頭小寫 (Lower case start)。**
- **內文大小寫原則**：
  - 原則上採全小寫。
  - **例外**：專有名詞（如 `AWS`, `JSON`）、類別名稱（如 `UserProfile`）、常數或特定術語應保留其慣用的大小寫格式，以維持可讀性。
- 結尾不加句號。

### 3.3 Body 與 Footer 規範

當變更較為複雜時，強烈建議填寫 Body。

- **Body**：
  - 必須與 Header 隔開一行。
  - 每行長度建議限制在 72 字元內（自動換行）。由於 body 可自由換行，此處不適用 header 的有條件放寬邏輯；撰寫者應以適當換行維持可讀性。
  - 說明變更的動機 (Motivation) 以及與之前行為的差異。
  - 支援 Markdown 列表格式（使用 `-` 或 `*`）。

- **Footer**：
  - 用於參照 Issue（如 `Closes #123`）。
  - Breaking Changes 必須在此標註，以 `BREAKING CHANGE:` 開頭。
  - 關於 `Closes` / `Related to` 的完整使用規則與 PR description 中的 issue linkage 模板，請參閱 [GitHub Issue 治理規範](github-issue-governance.md)。

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

- Refine commit header length rule with principled limit and restrained exceptions
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

當需要修改 `docs/` 根目錄或 `docs/standards/` 下的規範文件時，屬於純文件工作，使用 `docs/*` 分支：

1. **建立分支**：使用 `docs/project/` 作為路徑前綴。

   ```bash
   # 範例：更新版本控制規範
   git checkout -b docs/project/update-vcs-rules
   ```

2. **提交變更**：

   - Scope 必須為 `project`。
   - Type 必須為 `docs`。

   ```bash
   git add docs/standards/version-control.md
   git commit -m "docs(project): add complete branch type system"
   ```

3. **發起 Pull Request**：

   - 團隊成員進行審核 (Review)。
   - 確認規範變更的合理性與共識。

4. **合併**：

   - 審核通過後採用 Merge Commit 合併至 `develop`。
   - 例外：若僅為修正錯字 (Typo) 或格式 (Style)，允許使用 Squash Merge 以保持主線簡潔。

### 場景 C：純文件性修訂（Use Cases / Specs Propagation）

當需要批量修訂 `docs/use-cases/**` 或 `docs/specs/**` 文件，且這些修改：

- 不涉及功能變更
- 不伴隨 code / tests 實作變更
- 屬於格式、模板、命名、欄位、追溯規則等同步更新

則可視為單一批次文件修訂處理：

1. **建立分支**
   依修改範圍選擇合理的分支名稱。若修訂屬於 project-level 規範的全面同步，可使用 `docs/project/...`；若修訂明確侷限於某個較小的文件範圍，也可依共同上層路徑選擇更貼切的分支名稱。

   ```bash
   # 範例一：跨範圍的規範同步修訂
   git checkout -b docs/project/revise-testing-standards

   # 範例二：僅限於特定 specs 範圍的 propagation
   git checkout -b docs/wutils/align-test-specs
   ```

2. **提交變更**
   Scope 應使用該批文件在 `docs/` 下的共同上層路徑，例如：

   ```bash
   git add docs/specs/wutils/
   git commit -m "docs(specs/wutils): align library test specs with revised testing rules"
   ```

3. **發起 Pull Request**

   - 進行整批文件修訂的審核
   - 確認其修改模式一致，且應共同回滾

4. **合併**

   - 採用 Merge Commit 合併至 `develop`

### 場景 D：一般錯誤修正 (Fix)

當需要修正 bug、規範合規問題、或 merge 後的遺漏時：

1. **建立分支**：使用 `fix/` 前綴，對應受影響模組的最小共同範圍。

   ```bash
   git checkout -b fix/wsatools/init-relative-imports
   ```

2. **提交變更**：

   ```bash
   git add wsatools/llm/__init__.py wsatools/workflow/__init__.py
   git commit -m "fix(wsatools): use relative import for private modules in __init__.py"
   ```

3. **合併**：

   - 推送並發起 PR 合併至 `develop`。
   - 採用 Merge Commit 合併。

### 場景 E：Shared Library Propagation 與原子提交

當 shared library（如 `wutils`、`core`）的公開契約先演進，下游 systems（如 `gms`、`tej`）需要後續分批適配時，應以分 commit 方式保留原子歷史，而非將上游變更與下游 propagation 混入同一個 commit。

#### 原則

- **Task ↔ Commit 原子性優先**：commit 不應因全域測試的粗粒度而被迫混入後續 propagation 修正。
- **局部測試是例外機制**：開發人員在此情境下，可以 `inv test --project <project>` 驗證當次 commit 的主體品質，但這不是常態捷徑，也不是允許長期維持 broken branch 的藉口。
- **Push 前必須全域綠燈**：所有 propagation 修正完成後，branch head 必須恢復全域測試通過，才可 push。

關於主體測試的合法使用時機與完整規則，請參閱 [測試規範 §1.5](testing.md#15-提交與推送的測試責任分層)。

#### 分批提交示例

```text
1. feat(wutils/...): 調整 shared library 的公開契約
   → 提交前執行 inv test --project wutils
2. refactor(gms/...): 適配 gms 至新契約
   → 提交前執行 inv test --project gms
3. refactor(tej/...): 適配 tej 至新契約
   → 提交前執行 inv test --project tej
4. push 前確認 inv test 全域綠燈
```

#### 邊界聲明

- 此模式**僅允許短暫的中間局部綠燈**，用於保留原子歷史。
- 不允許以此模式長期維持 broken branch 或跳過全域整合驗證。
- 本規範不涵蓋自動依 dependency graph 推導受影響 systems 的功能。

### 通則：Pull Request、合併策略與整合流程

#### A. 正式流程

所有正式變更應透過以下流程進入 `develop`：

```text
同步 develop → 建立工作 branch → 開發與 commit → push branch → 建立 PR → review → Merge Commit 合併 → 本地同步 develop
```

不得以多條未驗證 branch 先行本地整合、最後一次性 push 取代分支級品質關卡。每條 branch 都應獨立經過 push → PR → review → merge 流程。

#### B. 合併策略

分支合併至 `develop` 時，必須採用 **Merge Commit**（`--no-ff`），以保留分支邊界與 Task 提交歷史。

禁止使用 Squash Merge（除場景 B 中明確列出的例外情形）與 Rebase Merge，因為這些策略會壓縮或重寫分支內的提交歷史，破壞「文件先行」與「原子化實作」的對應脈絡。

#### C. `develop` 同步方式

本地同步 `develop` 時，應採 fast-forward only（見 §2.1）。不得將「同步 `develop`」與「branch merge into `develop`」視為同一類 merge 行為。

#### D. 單人維護情境下的 Review 機制

若當前無其他可用 reviewer，允許採用 **Self Review + LLM-Assisted Review** 作為過渡 review 機制。在此情境下：

- 仍必須建立 PR、保留 review 留痕與 Merge Commit。
- 建議在 PR comment 中留下 self-review 或 LLM-assisted review 的審查記錄，確保決策可追溯。
- 當團隊恢復多人協作時，應回歸正式的人工 review 流程。

#### E. 操作指引

上述流程的具體操作步驟、Git 指令、GitHub UI 操作與常見錯誤排除，請參閱 [Pull Request Workflow 操作說明](pull-request-workflow.md)。

#### F. Issue 對應

當工作涉及 GitHub issue 時，branch 與 PR 應與對應 issue 建立明確的對應關係。Issue 的建立方式、結構定義、PR linkage 寫法與 auto-close 前提，請參閱 [GitHub Issue 治理規範](github-issue-governance.md)。

---

## 5. 品質閘道 (Quality Gates)

在執行 `git commit` 前，應確認：

1. **Scope 正確性**：修改 `docs/` 根目錄或 `docs/standards/` 下的文件時，Scope 是否為 `project`？純文件性 `use-cases/specs` 修訂時，Scope 是否使用了共同上層路徑？
2. **流程合規**：是否已建立獨立分支？
3. **格式檢查**：
   - Header 是否維持精簡？若超出 72 字元，是否屬於必要且有節制的例外？
   - （若為複雜變更）是否有撰寫 Body 描述？
   - 是否符合 `<type>(<scope>): <subject>` 格式？

---

## 6. 範例對照表

| 場景 | 錯誤範例 ❌ | 正確範例 ✅ |
|:-----|:-----------|:-----------|
| 修改版本控制規範 | `docs: update git doc`（缺少 scope） | `docs(project): update version control standards`（scope 為 project） |
| 修改架構設計總表 | 直接 Commit 到 develop（違反流程） | 建立 `docs/project/...` 分支並發起 PR（確保共識） |
| Project-Level 規範修訂 | `docs(standards): update testing rules`（scope 不應使用子目錄名） | `docs(project): update testing rules`（project-level 文件統一使用 `project`） |
| Feature Use Cases 定義 | `docs(project): add user use-case`（Scope 混淆） | `docs(use-cases/gms/user/user-reg): define registration requirements`（Scope 對應完整路徑） |
| 純文件性 specs propagation | `docs(specs/wutils/io/json-io): align test spec wording`（若本次同時改了多份 specs，則過細） | `docs(specs/wutils): align library test specs with revised testing rules`（使用共同上層路徑） |
| 功能實作提交 (API 層) | `feat(api): add login`（Scope 太籠統，無 Body） | `feat(gms/api/auth): add login endpoint`（Scope 精確，動詞反映 API 層新增，建議附 Body） |
| 功能實作提交 (邏輯層) | `feat(auth): implement login`（Scope 太籠統） | `feat(gms/service/auth): implement login authentication`（Scope 精確，動詞反映邏輯落地） |
| 一般錯誤修正 | 直接 Commit 到 develop | 建立 `fix/...` 分支，commit type 使用 `fix` |
| 專案維運工作 | 直接在 develop 上改 `pyproject.toml` | 建立 `chore/build/...` 分支並發起 PR |

---

## 7. 規範生效日

**本規範之 branch type 與相關流程修訂，自 2026-04-11 起生效。**

在此日期前建立之歷史分支與提交紀錄，可能不完全符合現行規範；原則上不追溯重寫既有共享歷史，但自生效日起之新分支與新提交應全面遵守本規範。
