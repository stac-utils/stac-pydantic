from stac_pydantic.scripts.cli import app


def test_valid_stac_item(cli_runner):
    result = cli_runner.invoke(
        app,
        [
            "validate-item",
            "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/eo/examples/example-landsat8.json",
        ],
    )
    assert not result.exception
    assert result.exit_code == 0
