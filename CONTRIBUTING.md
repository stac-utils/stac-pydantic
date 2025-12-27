# Contributing

Issues and pull requests are more than welcome.

**dev install**

```bash
git clone https://github.com/stac-utils/stac-pydantic.git
cd stac-pydantic
python -m pip install -e ".[dev]"
```

You can then run the tests with the following command:

```sh
python -m pytest --cov stac_pydantic --cov-report term-missing
```

To run only tests that do not require access to the internet,
the following command can be used:

```sh
$ python3 -m pytest -m "not network"
```

**pre-commit**

This repo is set to use `pre-commit` to run *ruff*, *pydocstring* and mypy when committing new code.

```bash
pre-commit install
```
