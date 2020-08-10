import click
import requests
from pydantic import ValidationError

from stac_pydantic import item_model_factory


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
        item_model_factory(stac_item, skip_remote_refs=True)(**stac_item)
    except ValidationError as e:
        click.echo(str(e))
        return
    click.echo(f"{infile} is valid")
    return
