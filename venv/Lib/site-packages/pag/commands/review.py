import click
import requests
import textwrap

from pag.app import app
from pag.utils import (
    assert_local_repo,
    die,
    eager_command,
    in_git_repo,
    repo_url,
    run
)

try:
    # If colorama is available, let's use it to print prettier output. If not,
    # fall back to boring monochrome.
    from colorama import Fore, Style
    GREEN = Fore.GREEN
    DIM = Style.DIM
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = DIM = RESET = ''


def list_pull_requests(name):
    """Get a list of opened pull requests for a project.

    For an exact description of the return value see Pagure API documentation.

    :param str name: name of the project
    :returns: a list of dicts describing opened pull requests
    """
    url = 'https://pagure.io/api/0/{name}/pull-requests'.format(name=name)
    response = requests.get(url)
    return response.json()['requests']


def get_repo(pr_info):
    """Find url for repo that the response belongs to.

    :param dict pr_info: Information about a pull request as returned by Pagure
                         API
    :returns: git repo url
    :rtype: str
    """
    name = pr_info['repo_from']['fullname'].replace('forks/', '', 1)
    return repo_url(name, git=True)


def get_local_branch(pr):
    """Get a branch name for the new review.

    Finds latest branch for this particular pull request and bumps the
    revision. The branch name is in the format of ``review/PR_ID/REV`` where
    ``REV`` is an automatically incremented number starting at 1.

    :param int pr: identifier of a pull request
    :returns: name of a new branch
    :rtype: str
    """
    _, out = run(['git', 'branch', '--list', 'review/{}/*'.format(pr)],
                 echo=False, graceful=False)
    existing = [int(x.rsplit('/', 1)[-1])
                for x in out.strip().split('\n')
                if x]
    num = max(existing + [0]) + 1
    return 'review/{}/{}'.format(pr, num)


@eager_command
def cleanup_branches(ctx):
    """Delete all branches that correspond to merged or closed pull requests.

    This function never returns due to the decorator exiting the whole program.

    :param ctx: Click context. Passed automatically by the decorator
    """
    repo = in_git_repo()
    opened_requests = set(str(pr['id']) for pr in list_pull_requests(repo))

    _, out = run(['git', 'branch', '--list', 'review/*'], echo=False)
    branches = [b for b in out.split() if b.split('/', 3)[1] not in opened_requests]
    if branches:
        run(['git', 'branch', '-D'] + branches)


@eager_command
def list_pulls(ctx):
    """Print information about opened pull requests.

    This function never returns due to the decorator exiting the whole program.

    :param ctx: Click context. Passed automatically by the decorator
    """
    repo = in_git_repo()
    pulls = list_pull_requests(repo)
    if pulls:
        longest_name = max((pr['user']['name'] for pr in pulls), key=len)
    for pr in pulls:
        prefix = '{green}{id: >5}{rst} {dim}{user[name]:{width}}{rst}'.format(
            width=len(longest_name), green=GREEN, dim=DIM, rst=RESET, **pr)
        width = 79 - len(prefix) + len(GREEN) + len(DIM) + 2 * len(RESET)
        for line in textwrap.wrap(pr['title'], width=width):
            click.echo('{}  {}'.format(prefix, line))
            prefix = ' ' * (79 - width)


@eager_command
def open_current(ctx):
    """Open pull request page in web browser.

    If not called when review branch is checked out, an error will be reported.

    This function never returns due to the decorator exiting the whole program.

    :param ctx: Click context. Passed automatically by the decorator
    """
    _, branch = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], echo=False)
    branch = branch.strip()
    if not branch.startswith('review/'):
        click.echo('Not on a review branch, aborting...', err=True)
        ctx.exit(1)

    url = '{}/pull-request/{}'.format(repo_url(in_git_repo()),
                                      branch.split('/')[1])

    run(['xdg-open', url])


@app.command()
@click.argument('pr', metavar='PR_ID')
@click.option('-l', '--list', is_flag=True, callback=list_pulls,
              expose_value=False, is_eager=True,
              help='List opened pull requests on this repo')
@click.option('-c', '--cleanup', is_flag=True, callback=cleanup_branches,
              expose_value=False, is_eager=True,
              help='Delete branches corresponding to merged/closed pull '
                   'requests. WARNING: This can potentially delete useful '
                   'data!')
@click.option('-o', '--open', is_flag=True, callback=open_current,
              expose_value=False, is_eager=True,
              help='Open currently reviewed PR in browser')
@assert_local_repo
def review(pr):
    """Check out a pull request locally."""
    name = in_git_repo()
    url = 'https://pagure.io/api/0/{name}/pull-request/{id}'.format(
        name=name, id=pr)
    response = requests.get(url).json()
    try:
        branch = response['branch_from']
        repo = response.get('remote_git') or get_repo(response)
    except KeyError:
        die('Bad pull request id')

    # Find review branches that include the last commit in the pull request.
    ret, branches = run(['git', 'branch',
                         '--contains', response['commit_stop'],
                         'review/{}/*'.format(pr)], echo=False)

    if ret == 0 and branches:
        # There is a branch with that commit, find the latest one and check it
        # out. There really should be only one.
        latest_branch = branches.strip().split('\n')[-1].split(' ')[-1]
        click.echo('Pull request {} already checked out as {}'.format(
            pr, latest_branch))
        run(['git', 'checkout', latest_branch], graceful=False)
    else:
        # Download the commits from the branch.
        run(['git', 'fetch', repo, branch], graceful=False)
        # Find a suitable name for local branch and create it.
        local_branch = get_local_branch(pr)
        run(['git', 'checkout', '-b', local_branch, 'FETCH_HEAD'],
            graceful=False)
