#!/usr/bin/env python
"""Installation."""
from setuptools import find_packages, setup

setup(
    name='git-prune-tags',
    description='Git command for pruning undesired tags.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=[
        'click',
        'gitpython',
    ],
    entry_points={
        'console_scripts': [
            'git-prune-tags=git_prune_tags.__main__:main',
        ],
    },
)
