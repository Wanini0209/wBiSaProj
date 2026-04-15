## Contributing

This project follows formal governance standards for version control, pull requests, and issue management. This document provides a contributor entry point and minimum necessary guidance. For complete rules, please refer to the formal standards listed at the end of this document.

### Step 1. Clone the Repository

```sh
git clone https://github.com/Wanini0209/wBiSaProj.git
cd wBiSaProj
```

### Step 2. Sync the Latest `develop`

This project uses `develop` as the integration trunk. Before starting any work, sync your local `develop` to the latest state:

```sh
git checkout develop
git fetch origin
git merge --ff-only origin/develop
```

### Step 3. Create a Working Branch

Create a branch from the latest `develop`. Do not work directly on `develop`.

```sh
git checkout -b <branch_type>/<root>/<hierarchy>/<work_name>
```

Branch naming follows hierarchical conventions defined in the version control standards. For example:

```sh
git checkout -b feature/gms/user/user-registration
git checkout -b docs/project/update-testing-standards
git checkout -b fix/wsatools/init-relative-imports
```

### Step 4. Install Prerequisites

```sh
python -m pip install pipx
python -m pipx install pipenv invoke
python -m pipx ensurepath
```

### Step 5. Create Your Python Virtual Environment and Install Dependencies

```sh
inv env.init-dev
```

### Step 6. Install Git Hooks

This project uses `pre-commit` to manage Git hooks (pre-commit, commit-msg, and pre-push). Install them before your first commit:

```sh
pipenv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

### Step 7. Develop and Commit

Write your changes and commit using the Conventional Commits format required by this project:

```sh
git add <files>
git commit
```

Use `git commit` (without `-m`) to open your editor for writing a properly formatted multi-line commit message.

### Step 8. Run Tests

Make sure all test cases pass before pushing:

```sh
inv test
```

When working on changes that affect a specific project and you need to preserve commit atomicity, you may run project-scoped tests during intermediate commits:

```sh
inv test --project <project_name>
```

However, the full test suite must pass before pushing. For LLM-related changes, also run:

```sh
inv test.llm
```

### Step 9. Format and Lint

Format your code and check for style issues:

```sh
inv style.format
inv style.check
```

### [Optional] Step 10. Run Security Check

```sh
inv secure.security-report
```

### Step 11. Push, Open a Pull Request, and Review

Push your branch to the remote:

```sh
git push -u origin <branch-name>
```

Then open a Pull Request on GitHub with `develop` as the base branch. The standard flow is: push branch → open PR → review → Merge Commit. PRs must be reviewed and retain review trace before merge. The merge strategy is **Merge Commit** (`--no-ff`); squash merge and rebase merge are not permitted under normal circumstances.

If your work corresponds to a GitHub issue, include the appropriate issue linkage in the PR description. For details on linkage format, see the GitHub issue governance standard.

### Formal Standards

For complete rules on branching, commit conventions, PR workflow, and issue governance, please refer to:

- [Version Control Standards](docs/standards/version-control.md)
- [Pull Request Workflow](docs/standards/pull-request-workflow.md)
- [GitHub Issue Governance](docs/standards/github-issue-governance.md)
