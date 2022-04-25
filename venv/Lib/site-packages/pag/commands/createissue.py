import getpass

import click

from pag.app import app
from pag.utils import (
    configured,
    assert_local_repo,
    in_git_repo
)
from pag.client import client

@app.command('create-issue')
@click.option('-t', '--title', prompt=True)
@click.option('-d', '--description', prompt=True)
@click.option('-p', '--private', is_flag=True)
@configured
@assert_local_repo
def createissue(conf, title, description, private):
    name = in_git_repo()

    click.echo("Trying to create issue for %r in pagure.io" % name)
    if not client.is_logged_in:
        password = getpass.getpass("Fas password for %r" % conf['username'])
        client.login(username=conf['username'], password=password)

    message = client.create_issue(name, title, description, private)
    click.echo("Created issue %s" % message)
