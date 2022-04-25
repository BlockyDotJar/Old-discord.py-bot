import getpass

import click

from pag.app import app
from pag.utils import (
    configured,
    assert_local_repo,
    in_git_repo,
    repo_url,
    run,
)
from pag.client import client


@app.command()
@assert_local_repo
@configured
def fork(conf):
    username = conf['username']
    name = in_git_repo()

    click.echo("Trying to fork %r in pagure.io" % name)
    if not client.is_logged_in:
        password = getpass.getpass("FAS password for %r" % username)
        client.login(username=username, password=password)
    url = client.fork(name)
    click.echo("Created %s" % url)

    name = username + '/' + name
    url = repo_url(name, ssh=True, git=True)
    name = name.split('/')[0]
    run(['git', 'remote', 'add', name, url])
