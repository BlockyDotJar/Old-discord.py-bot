import getpass
import sys

import click

from pag.app import app
from pag.utils import (
    assert_local_repo,
    configured,
    in_git_repo,
)
from pag.client import client


@app.command('upload')
@click.argument('tarball',
                type=click.Path(exists=True, dir_okay=False))
@configured
@assert_local_repo
def upload(conf, tarball):
    """Upload new file to releases."""
    name = in_git_repo()
    click.echo('Trying to upload %r' % tarball)
    if not client.is_logged_in:
        password = getpass.getpass("Fas password for %r" % conf['username'])
        client.login(username=conf['username'], password=password)

    error = client.upload(name, tarball)
    if error:
        click.echo("Upload failed: %s" % error, sys.stderr)
        sys.exit(1)
    else:
        click.echo('Upload successful.')
