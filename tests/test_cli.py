from stac_pydantic.scripts.cli import app


def test_valid_stac_item(cli_runner):
    result = cli_runner.invoke(
        app,
        [
            "validate-item",
            "https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0/examples/extended-item.json",
        ],
    )

    if result.exception:
        raise result.exception

    assert result.exit_code == 0
