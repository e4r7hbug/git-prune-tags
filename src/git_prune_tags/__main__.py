#!/usr/bin/env python
"""Remove undesired Tags from local and remote repositories."""
import logging

import click
import git
from git import Repo

LOG = logging.getLogger(__name__)


def progress(op_code, cur_count, max_count=None, message=''):
    """Remote action progress."""
    LOG.debug('Progress: %s', locals())


def delete_local_tags(prune_tags=None, repo=None):
    """Remove matched Tags from local Repository."""
    repo.delete_tag(prune_tags)
    return prune_tags


def delete_remote_tags(prune_tags=None, repo=None):
    """Remove matched Tags from Remote Repository."""
    removed_tags = []

    remote = repo.remote()

    try:
        for prune_tag in prune_tags:
            remote.push(refspec=':{ref}'.format(ref=prune_tag), progress=progress)
            LOG.info('Removed remote tag: %s', prune_tag)
            removed_tags.append(prune_tag)
    except git.exc.GitCommandError as error:
        click.secho('Verify you are allowed to delete tags through pushes.', bg='red', fg='white')

    LOG.debug('Removed tags from remote: %s', removed_tags)
    return removed_tags


def set_verbosity(ctx, param, value):
    """Set logging verbosity."""
    verbose = len([option for option in value if option])

    verbosity = (logging.root.getEffectiveLevel() - (10 * verbose)) or 1

    if value:
        logging.basicConfig()
        LOG.setLevel(verbosity)

    return verbosity


def prune_tags(starts_with=''):
    """Find tags to prune."""
    repo = Repo('.')

    prune_tags = [tag for tag in repo.tags if tag.name.startswith(starts_with)]
    LOG.debug('Matching Tags: %s', prune_tags)

    delete_remote_tags(prune_tags=prune_tags, repo=repo)
    # delete_local_tags(prune_tags=prune_tags, repo=repo)


@click.command()
@click.option('-s', '--starts-with', default='')
@click.option('-v', '--verbose', envvar='GIT_TRACE', is_flag=True, multiple=True, callback=set_verbosity)
def main(starts_with, verbose):
    """Remove tags."""
    prune_tags(starts_with=starts_with)


if __name__ == '__main__':
    logging.basicConfig()

    LOG.setLevel(logging.INFO)

    main()
