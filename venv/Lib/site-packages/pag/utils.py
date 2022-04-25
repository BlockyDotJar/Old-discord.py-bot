import functools
import os
import subprocess as sp
import sys

import click
import requests
import yaml

try:
    from colorama import Style
    DIM = Style.DIM
    RESET = Style.RESET_ALL
except ImportError:
    DIM = RESET = ''


CONF_FILE = os.path.expanduser('~/.config/pag')


def run(cmd, echo=True, graceful=True, silent=False):
    if not silent:
        click.echo('  $ ' + " ".join(cmd))
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
    output, _ = proc.communicate()
    output = output.decode('utf-8')
    if echo and not silent:
        click.echo(DIM + output + RESET)
    if not graceful and proc.returncode != 0:
        sys.exit(1)
    return proc.returncode, output


def die(msg, code=1):
    click.echo(msg)
    sys.exit(code)


def in_git_repo():
    # TODO -- would be smarter to look "up" the tree, too.
    if not os.path.exists('.git') or not os.path.isdir('.git'):
        return None
    return os.getcwd().split('/')[-1]


def assert_local_repo(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not in_git_repo():
            die("fatal:  Not a git repository")
        return func(*args, **kwargs)
    return inner


def eager_command(func):
    """Decorator for an option callback that should abort man command.

    Useful when an option completely changes the execution flow.
    """
    @functools.wraps(func)
    def inner(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        func(ctx)
        ctx.exit()
    return inner


def get_default_upstream_branch():
    """The default branch is whatever HEAD points to in the remote repo.
    Usually the main repo will be either `upstream` or `origin`, so try both.
    Returns ``None`` if no default branch could be found.
    """
    # TODO We should instead use `git ls-remote --symref REMOTE_URL HEAD`, but
    # that does not currently work.
    #   https://pagure.io/pagure/issue/2955
    for remote in ('upstream', 'origin'):
        ref = '%s/HEAD' % remote
        ret, stdout = run(['git', 'rev-parse', '--abbrev-ref', ref], silent=True)
        if ret == 0:
            real_ref = stdout.strip()
            assert real_ref.startswith('%s/' % remote)
            return real_ref[len(remote) + 1:]


def get_current_local_branch():
    _, stdout = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    branch = stdout.strip()
    if branch == 'HEAD':
        raise RuntimeError('Repo in detached HEAD state.')
    return branch


def repo_url(name, ssh=False, git=False, domain='pagure.io', force_no_fork=False):
    """Generate a URL to a project.

    :param ssh: whether to use ssh or https protocol
    :param git: whether to append .git suffix
    :param domain: Pagure instance we are interested in
    :param force_no_fork: whether to check if the name could actually be a fork
    """
    if ssh:
        prefix = 'ssh://git@'
    else:
        prefix = 'https://'

    suffix = '%s' % name
    if not force_no_fork and '/' in name:
        if git:
            suffix = 'forks/%s' % name
        else:
            suffix = 'fork/%s' % name

    if git:
        suffix = suffix + '.git'

    return prefix + domain + '/' + suffix


def create_config():
    username = input("FAS username:  ")
    conf = dict(
        username=username,
    )

    with open(CONF_FILE, 'wb') as f:
        f.write(yaml.dump(conf).encode('utf-8'))

    click.echo("Wrote %r" % CONF_FILE)


def load_config():
    with open(CONF_FILE, 'rb') as f:
        return yaml.load(f.read().decode('utf-8'))

def load_or_create_config():
    if not os.path.exists(CONF_FILE):
        click.echo("%r not found.  Creating..." % CONF_FILE)
        create_config()
    return load_config()


def configured(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        config = load_or_create_config()
        return func(config, *args, **kwargs)
    return inner
