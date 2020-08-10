import click
import requests
from pydantic import ValidationError

from stac_pydantic import validate_item as validate


@click.group(short_help="Validate STAC")
def app():
    """stac-pydantic cli group"""
    pass


@app.command(short_help="Validate STAC Item")
@click.argument("infile")
def validate_item(infile):
    """Validate stac item"""
    r = requests.get(infile)
    r.raise_for_status()
    stac_item = r.json()
    try:
        validate(stac_item, skip_remote_refs=True, reraise_exception=True)
    except ValidationError as e:
        click.echo(str(e))
        return
    click.echo(f"{infile} is valid")
    return
