# -*- coding: utf-8 -*-
""" Configuration and command-line arguments
"""

# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
from builtins import *
import os
import shutil
from string import Template

import configargparse
from pkg_resources import Requirement, resource_filename


def get_config_file(basename):
    """ Looks for a configuration file in 3 locations:

        - the current directory
        - the user config directory (~/.config/tvdb_renamer)
        - the version installed with the package (using setuptools resource API)

    Args:
        basename (str): The base filename.

    Returns:
        str: The full path to the configuration file.
    """
    locations = [
        os.path.join(os.curdir, basename),
        os.path.join(
            os.path.expanduser("~"),
            ".config",
            "tvdb_renamer",
            basename),
        resource_filename(
            Requirement.parse("tvdb_renamer"),
            os.path.join('tvdb_renamer', basename))
    ]

    for location in locations:
        if os.path.isfile(location):
            return location

def copy_default_config_to_user_directory(
        basename,
        clobber=False,
        dst_dir='~/.config/tvdb_renamer'):
    """ Copies the default configuration file into the user config directory.

    Args:
        basename (str): The base filename.
        clobber (bool): If True, the default will be written even if a user
            config already exists.
        dst_dir (str): The destination directory.
    """
    dst_dir = os.path.expanduser(dst_dir)
    dst = os.path.join(dst_dir, basename)
    src = resource_filename(
        Requirement.parse("tvdb_renamer"),
        os.path.join('tvdb_renamer', basename))

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    if clobber or not os.path.isfile(dst):
        shutil.copy(src, dst)

def get_configuration(basename='tvdb_renamer.cfg', parents=None):
    """Parses and returns the program configuration options,
    taken from a combination of ini-style config file, and
    command line arguments.

    Args:
        basename (str): The base filename.
        parents (list): A list of ArgumentParser objects whose arguments
            should also be included in the configuration parsing. These
            ArgumentParser instances **must** be instantiated with the
            `add_help` argument set to `False`, otherwise the main
            ArgumentParser instance will raise an exception due to duplicate
            help arguments.

    Returns:
        The options object, and a function that can be called to print the help
        text.
    """
    copy_default_config_to_user_directory(basename)

    parser = configargparse.ArgParser(
        formatter_class=configargparse.ArgumentDefaultsRawHelpFormatter,
        add_help=False,
        parents=parents or [],
        default_config_files=[
            resource_filename(
                Requirement.parse("tvdb_renamer"),
                os.path.join('tvdb_renamer', basename)),
            os.path.join(
                os.path.expanduser("~/.config/tvdb_renamer"),
                basename),
            os.path.join(os.curdir, basename)])

    # logging config file
    parser.add(
        '-lc',
        '--logging-config',
        required=False,
        default='tvdb_renamer_logging.cfg',
        metavar='FILE',
        env_var='TVDB_RENAMER_LOGGING_CONFIG',
        help='Logging configuration file')

    parser.add(
        '-v',
        '--version',
        required=False,
        action='store_true',
        help='''Display tvdb_renamer version''')

    parser.add(
        '-dr',
        '--dry-run',
        required=False,
        action='store_true',
        help='''Conduct a dry run. No changes are written to file''')

    parser.add(
        '-h',
        '--help',
        required=False,
        action='store_true',
        help='''Print help''')

    return parser.parse_known_args()[0], parser.print_help