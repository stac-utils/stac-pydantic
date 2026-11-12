# Contributing

Issues and pull requests are more than welcome.

We recommand using [`uv`](https://docs.astral.sh/uv) as project manager for development.

See https://docs.astral.sh/uv/getting-started/installation/ for installation

```bash
git clone https://github.com/stac-utils/stac-pydantic.git
cd stac-pydantic
uv sync
```

You can then run the tests with the following command:

```sh
uv run pytest --cov stac_pydantic --cov-report term-missing
```

To run only tests that do not require access to the internet,
the following command can be used:

```sh
uv run pytest -m "not network"
```

**pre-commit**

This repo is set to use `pre-commit` to run *ruff*, *pydocstring* and mypy when committing new code.

```bash
uv run pre-commit install
```

## Commit messages and releases

Releases are automated with [release-please](https://github.com/googleapis/release-please), which reads the [Conventional Commit](https://www.conventionalcommits.org/) messages merged to `main`. Use them for your commits and your PR title, e.g. `fix: handle empty collections` or `feat: add a filter option`:

- `fix:`, `perf:`, `revert:` and `docs:` lead to a patch release, `feat:` to a minor one, and a breaking change (`feat!:` or a `BREAKING CHANGE:` footer) to a major one.
- `chore:`, `ci:`, `test:`, `build:`, `refactor:` and `style:` don't trigger a release on their own.
- release-please keeps a release PR open with the next version; merging it tags the release and publishes it.
- release-please also writes CHANGELOG.md from these messages, so don't edit it in your PR. Maintainers can adjust the wording in the release PR just before merging it.
