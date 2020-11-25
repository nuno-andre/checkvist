from typing import List, Optional
from pathlib import Path
import logging

from typer import echo, Context, Typer, Option
from checkvist.app.app import App

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
)

JOBS_DIR = Path(__file__).parent.joinpath('jobs')

cli = Typer()
app = App()


@cli.command()
def run(
    jobs: List[str],
    lists: Optional[List[str]] = Option(None, '--list', '-l'),
):
    '''Run jobs over your Checklists.
    '''
    msg = "Running jobs ({})".format(', '.join(map("'{}'".format, jobs)))
    if lists:
        msg += " over lists ({})".format(', '.join(map("'{}'".format, lists)))
    echo(msg)
    app.run_jobs(jobs, lists)


@cli.command('show')
def sh(what: str):
    '''Show info about: 'jobs', 'lists', or 'user'.
    '''
    what = what.lower()

    if what == 'jobs':
        width = max(len(str(j)) for j in app.jobs.values()) + 5

        for job in app.jobs.values():
            echo('{:{width}}{}'.format(str(job), job.doc, width=width))

    elif what == 'lists':
        lists = sorted(app.lists, key=lambda x: x.name.lower())
        echo("ID     '<name>' (items)")
        echo('-----------------------')
        for l in lists:
            echo(f"{l.id} '{l.name}' ({l.item_count})")

    elif what == 'user':
        echo(app.show_user_info())

    else:
        echo("You must specify one of: 'jobs', 'lists', 'user'")
        exit(1)


@cli.command('import')
def im(filepath: Path):
    '''(NOT IMPLEMENTED)
    '''
    filepath = filepath.absolute()
    if not filepath.exists():
        echo(f"'{filepath}' not found, but anyway...")
    raise NotImplementedError


@cli.callback()
def main(
    ctx: Context,
    username: Optional[str] = Option(
        None, '--username', '-u',
        envvar='CHECKVIST_USERNAME',
        help="User's email address."
    ),
    secret: Optional[str] = Option(
        None, '--secret', '-s',
        envvar='CHECKVIST_SECRET',
        help='User password or API key.'
    ),
):
    '''
    '''
    app.username = username
    app.secret = secret


if __name__ == "__main__":
    cli(prog_name='checkvist')
