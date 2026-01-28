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
