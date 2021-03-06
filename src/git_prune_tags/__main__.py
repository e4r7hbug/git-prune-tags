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


def delete_local_and_remote_tags(prune_tags=None, repo=None):
    """Remove matched tags from local and remote repository."""
    removed_tags = []

    remote = repo.remote()

    for prune_tag in prune_tags:
        try:
            push_results = remote.push(refspec=':{ref}'.format(ref=prune_tag.path), progress=progress)
        except git.exc.GitCommandError as error:
            LOG.debug('Git push error: %s', error)

            if 'does not exist' in error.stderr:
                LOG.debug('Remote does not contain tag: %s', prune_tag)
                continue
            else:
                click.secho('Verify you are allowed to delete tags through pushes.', bg='red', fg='white')
                break
        else:
            for push_result in push_results:
                LOG.debug('Push flags: %d', push_result.flags)
                LOG.debug('Push summary: %s', push_result.summary)

                if push_result.flags != push_result.DELETED:
                    raise SystemExit('Exit code {0:d}: {1}'.format(push_result.flag, push_result.summary))

            LOG.info('Removed remote tag: %s', prune_tag)
            removed_tags.append(prune_tag)

            repo.delete_tag(prune_tag)
            LOG.info('Removed local tag: %s', prune_tag)
    else:
        LOG.info('Tags deleted.')

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
    if not starts_with and not click.confirm('No start string for searching provided will delete all tags, continue?'):
        raise SystemExit()

    repo = Repo('.')

    prune_tags = [tag for tag in repo.tags if tag.name.startswith(starts_with)]
    LOG.info('Number of tags to remove: %d', len(prune_tags))
    LOG.debug('Matching Tags: %s', prune_tags)

    delete_local_and_remote_tags(prune_tags=prune_tags, repo=repo)


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
