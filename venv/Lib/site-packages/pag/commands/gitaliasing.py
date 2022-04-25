import click

from pag.app import app
from pag.utils import run

# FIXME: click master has added a hidden parameter that would allow
# us to hide this fallback command from generated help. 
# hidden paramter was added in commit 8f4c34f69554d3397627ef16adb1b1f9b83c381e
# https://github.com/pallets/click/commit/8f4c34f69554d3397627ef16adb1b1f9b83c381e
@app.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument('cli_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def default(ctx, cli_args):
    """"""
    git_cmd = ctx.info_name
    myargs = ['git', git_cmd]
    myargs.extend(cli_args)
    run(myargs)
