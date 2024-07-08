import click
import requests
from pydantic import ValidationError

from stac_pydantic.extensions import validate_extensions
from stac_pydantic.item import Item

try:
    import requests
except ImportError:  # pragma: nocover
    requests = None  # type: ignore

try:
    import jsonschema
except ImportError:  # pragma: nocover
    jsonschema = None  # type: ignore


@click.group(short_help="Validate STAC")
def app() -> None:
    """stac-pydantic cli group"""
    pass


@app.command(short_help="Validate STAC Item")
@click.argument("infile")
def validate_item(infile: str) -> None:
    """Validate stac item"""
    assert requests is not None, "requests must be installed to validate items"
    assert jsonschema is not None, "jsonschema must be installed to validate items"

    r = requests.get(infile)
    r.raise_for_status()

    stac_item = r.json()
    try:
        item = Item.model_validate(stac_item)
        validate_extensions(item, reraise_exception=True)
    except ValidationError as e:
        click.echo(str(e))
        return

    click.echo(f"{infile} is valid")
    return
