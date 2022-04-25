import getpass

import click

from pag.app import app
from pag.utils import (
    configured,
    in_git_repo,
    repo_url,
    run,
)
from pag.client import client


@app.command()
@click.argument('name')
@click.argument('description')
@click.confirmation_option(prompt="Are you sure you want to create a new repo?")
@configured
def create(conf, name, description):
    """
    Create a new repo. When run in an existing local git repository, this
    command will also set up remotes.
    """

    click.echo("Trying to create %r in pagure.io" % name)
    if not client.is_logged_in:
        password = getpass.getpass("FAS password for %r" % conf['username'])
        client.login(username=conf['username'], password=password)
    url = client.create(name, description)
    click.echo("Created %s" % url)

    local_repo = in_git_repo()
    if local_repo is None or local_repo != name:
        url = repo_url(name, ssh=True, git=True)
        run(['git', 'clone', url, name.split('/')[-1]])
    else:
        url = repo_url(name, ssh=True, git=True)
        name = name.split('/')[0]
        run(['git', 'remote', 'add', name, url])
        run(['git', 'remote', 'add', 'origin', url])
