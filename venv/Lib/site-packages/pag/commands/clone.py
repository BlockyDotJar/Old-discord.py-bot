import click
import requests

from pag.app import app
from pag.utils import (
    repo_url,
    run,
)

def _check_repo(namespace, name):
    """Check if a repo with this name exists in given namespace."""
    url = 'https://pagure.io/api/0/projects'
    response = requests.get(url, {'namespace': namespace, 'name': name})
    return bool(response.json()['projects'])


@app.command()
@click.argument('name')
@click.option('--anonymous', '-a', is_flag=True)
def clone(name, anonymous):
    """
    Clone an existing repo. Use the '-a' option when you don't have commit
    access to the repository.
    """

    force_no_fork = False
    if name.count('/') == 1:
        # There's exactly one slash in the name given. It could be fork or a
        # repo in namespace. We have no way of telling them apart other than
        # asking Pagure itself.
        force_no_fork = _check_repo(*name.split('/'))

    use_ssh = False if anonymous else True
    url = repo_url(name, ssh=use_ssh, git=True, force_no_fork=force_no_fork)
    run(['git', 'clone', url, name.split('/')[-1]])
