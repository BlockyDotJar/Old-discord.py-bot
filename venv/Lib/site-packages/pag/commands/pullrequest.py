import getpass
import sys

import click

from pag.app import app
from pag.utils import (
    configured,
    assert_local_repo,
    in_git_repo,
    get_default_upstream_branch,
    get_current_local_branch,
    run,
    die,
)
from pag.client import client

HEADER = "Pull request title goes here."
MARKER = "# All lines below this marker are ignored."


def split_input(branch, default_repo):
    tokens = branch.split(':')
    if len(tokens) > 2:
        die("%r is a malformed repo:branch expression." % branch)
    elif len(tokens) == 1:
        repo, branch = default_repo, tokens[0]
    elif len(tokens) == 2:
        repo, branch = tokens
        repo = repo + '/' + default_repo
    else:
        raise RuntimeError('Should not be possible to get here...')
    return repo, branch


@app.command('pull-request')
@assert_local_repo
@click.option('-b', '--base', help='Branch to merge the changes in')
@click.option('-h', '--head')
@configured
def pullrequest(conf, base, head):
    """
    Open a new pull request. Default behaviour is to open pull request from
    current branch to default upstream branch (usually 'master' or 'develop').

    The '--head' option can be used to specify other branch than the current
    one. You can open a pull request from a fork using
    'YOUR_USERNAME:BRANCH_NAME' as argument to '--head'.
    """

    name = in_git_repo()

    if base is None:
        try:
            base = get_default_upstream_branch()
        except Exception:
            click.echo("Failed to find default upstream branch for %r" % name)
            click.echo("Please specify a base branch explicitly.")
            sys.exit(1)
    else:
        name, base = split_input(base, name)

    if head is None:
        head = get_current_local_branch()
    else:
        name, head = split_input(head, name)
        if '/' in name:
            name = 'fork/' + name

    cmd = ['git', 'log', '{base}..{head}'.format(base=base, head=head)]
    _, log = run(cmd, echo=False)

    def modify(line):
        if not line:
            return line
        if line[0].isspace():
            return line.strip()
        return '# ' + line

    log = '\n'.join([modify(line) for line in log.split('\n')])
    edited = click.edit(
        "\n\n".join([HEADER, MARKER, log]),
        env=dict(VIMINIT='set filetype="gitcommit"'),
    )
    if not edited.strip():
        click.echo("Aborting due to empty pull request message.")
        sys.exit(1)
    title, comment = edited.split('\n', 1)
    if not title:
        click.echo("Aborting due to empty pull request message.")
        sys.exit(1)
    comment = comment.split(MARKER)[0]
    comment = comment.strip()

    username = conf['username']
    if not client.is_logged_in:
        password = getpass.getpass("FAS password for %r" % username)
        client.login(username=username, password=password)
    url = client.submit_pull_request(name, base, head, title, comment)
    click.echo(url)
