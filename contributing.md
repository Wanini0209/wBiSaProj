## Contributing

### Step 1. Fork this repository to your GitHub

### Step 2. Clone the repository from your GitHub

```sh
git clone [https://github.com/](https://github.com/)[YOUR GITHUB ACCOUNT]/wBiSaProj.git
```

### Step 3. Add this repository to the remote in your local repository

```sh
git remote add upstream "https://github.com/Wanini0209/wBiSaProj"
```

You can pull the latest code in master branch through `git pull upstream master` afterward.

### Step 4. Check out a branch for your new feature

```sh
git checkout -b [YOUR FEATURE]
```

### Step 5. Install Prerequisites

```sh
python -m pip install pipx
python -m pipx install pipenv invoke
python -m pipx ensurepath
```

### Step 6. Create Your Own Python Virtual Environment and Install Dependencies

```sh
inv env.init-dev
```

### Step 7. Work on your new feature

### [Optional] Step 8. Install project for local test

If you want to develop it, please run:

```sh
inv build.develop
```

### Step 9. Run test cases

Make sure all test cases pass.

```sh
inv test
```

### Step 10. Run test coverage

Check the test coverage and see where you can add test cases.

```sh
inv test.cov
```

### Step 11. Format source code

Format your code using `black` and fix linting issues with `ruff`.

```sh
inv style.format
```

### Step 12. Run style check

Make sure your coding style passes all enforced linters.

```sh
inv style.check
```

### [Optional] Step 13. Run security check

Check for common security vulnerabilities using Ruff's built-in bandit rules:

```sh
inv secure.security-report
```

### [Optional] Develop on Conda Environment

Update local Conda information:

```sh
inv conda.update
```

Create Conda develop environment

```sh
inv conda.create
```

Remove Conda develop environment

```sh
inv conda.remove
```

Activate Conda develop environment

```sh
inv conda.activate
```
