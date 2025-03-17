## Contributing

### Clone the repository

```bash
git clone -b develop https://github.com/fuxiAIlab/CivAgent.git

```

### Environment Setup

1. Install `uv` and `poetry`
    - Install `uv`: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
    - Install `poetry`: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

2. Install Python
    - Install Python3.10(at least) in your system: `brew install python@3.10`(for macOS)
    - Create a virtual environment with Python 3.10(at least): `uv venv -p python3.10`(run in repo root directory)
    - Activate the virtual environment: `source .venv/bin/activate`

3. Install Dependencies
    - `poetry install`

4. Testing(Make sure all tests pass)
    - `poetry shell`: activate the virtual environment
    - `pre-commit install`, `pre-commit run --all-files`
    - `pytest tests` or `make test`

### Commit & Push & Merge

1. Create a new branch from `main` branch
2. Make changes
    - Add dependencies with poetry: [`poetry add`](https://python-poetry.org/docs/cli/#add)]
    - Add code with code style: Ruff, Black, Isort, MyPy
        - `pre-commit` will check the code style automatically when you commit
    - Add doc with docstring style: [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
        - We use [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) to build the documentation
        - You can run `mkdocs serve` to preview the documentation locally
    - Add tests with pytest or unittest
    - (If necessary)Add changelog with [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
3. Commit&Push your changes
    - [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): Use [commitizen](https://commitizen-tools.github.io/commitizen/) to commit your changes(you can use `cz c` directly after you run `poetry shell` as stated above.)
    - Every commit change will be checked by `pre-commit` automatically, make sure all checks pass before you push.
        - If you want to skip the `pre-commit` checks, you can use `git commit -m "your message" --no-verify` to commit your changes.(Not recommended)
4. Create a merge request to `main` branch
    - If you are not ready for code review, you can make a [draft merge request](https://docs.gitlab.com/ee/user/project/merge_requests/drafts.html)
5. Wait for code review
    - (GitLab)Merge request review tools:
      [VSCode: GitLab Workflow](https://marketplace.visualstudio.com/items?itemName=GitLab.gitlab-workflow),
      [PyCharm: Work with GitLab merge requests](https://www.jetbrains.com/help/pycharm/work-with-gitlab-merge-requests.html)

6. Merge your changes

## Conventions

### Versions

[Semantic Versioning](https://semver.org/spec/v2.0.0.html)

### Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

### Branches

[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)

### Commits

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
