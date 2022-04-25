import click


class PassthroughGroup(click.Group):
    """This subclass adds two features
    - allow resolving command names given to the command-line to the closest
    existing command (e.g clo -> clone)
    - if it doesn't exist, redirect to the default handlers and pass arguments
    to the git binary.
    """
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return click.Group.get_command(self, ctx, 'default')
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
            ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


@click.group(cls=PassthroughGroup)
def app():
    pass


__all__ = [
    'app',
]

from .commands import create
from .commands import createissue
from .commands import clone
from .commands import fork
from .commands import remote
from .commands import pullrequest
from .commands import gitaliasing
from .commands import review
from .commands import upload
