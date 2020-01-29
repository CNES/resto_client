# -*- coding: utf-8 -*-
"""
   Copyright 2019 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
import argparse
from pathlib import Path
from typing import Optional

from resto_client.base_exceptions import RestoClientUserError
from resto_client.functions.aoi_utils import list_all_geojson
from resto_client.generic.property_decoration import managed_getter, managed_setter
from resto_client.generic.user_dirs import user_download_dir

from .cli_utils import get_from_args
from .parser.parser_settings import (DIRECTORY_ARGNAME, REGION_ARGNAME, VERBOSITY_ARGNAME)
from .persistence import PersistedAttributes
from .resto_client_settings import RESTO_CLIENT_SETTINGS


def _check_download_dir(download_dir: str) -> str:
    """
    Check function used by download_dir setter as a callback.

    :param download_dir: directory where downloaded files must be recorded
    :raises NotADirectoryError: when the argument does not point to a valid directory
    :returns: the download_directory unchanged.
    """
    if not Path(download_dir).is_dir():
        raise NotADirectoryError(download_dir)
    return download_dir


ALLOWED_VERBOSITY = ['NORMAL', 'DEBUG']


def _check_verbosity(verbosity: str) -> str:
    """
    Check function used by verbosity setter as a callback.

    :param verbosity: verbosity level to apply to resto_client.
    :raises ValueError: when verbosity has a wrong value
    :returns: the uppercase verbosity level
    """
    if verbosity is not None:
        verbosity = verbosity.upper()
        if verbosity not in ALLOWED_VERBOSITY:
            msg_err = 'Verbosity level must be in {} or None'.format(ALLOWED_VERBOSITY)
            raise ValueError(msg_err)
    return verbosity


def _check_region(key_region: str) -> str:
    """
    Check function used by region setter as a callback. Check that the region key belongs to
    the list of known regions, and normalize it.

    :param key_region: key of region geojson file to register
    :returns: the normalized key (lowercase ending with .geojson).
    :raises RestoClientUserError: when no geojson file found with key_region.
    """
    # Normalize key_region: lowercase which ends with .geojson
    key_region = key_region.lower()
    if not key_region.endswith('.geojson'):
        key_region = key_region + '.geojson'
    # verify that normalized key exists in the list of known regions
    if key_region not in list_all_geojson():
        msg = 'No {} file found in configuration directory.'
        raise RestoClientUserError(msg.format(key_region))
    return key_region


DOWNLOAD_DIR_KEY = 'download_dir'
REGION_KEY = 'region'
VERBOSITY_KEY = 'verbosity'


class RestoClientParameters(PersistedAttributes):
    """
    Class implementing parameters used by resto client.
    """
    properties_storage = RESTO_CLIENT_SETTINGS
    persisted_attributes = [DOWNLOAD_DIR_KEY, REGION_KEY, VERBOSITY_KEY]

    @classmethod
    def build_from_argparse(cls, args: argparse.Namespace) -> 'RestoClientParameters':
        """
        Build a RestoClientParameters instance from arguments parsed by argparse,
        suitable for further processing in CLI context.

        :param args: arguments as parsed by ArgParse
        :returns: a RestoClientParameters instance, suitable for further processing in CLI context.
        """
        instance = cls()

        # Attribute holding the download directory
        download_dir = get_from_args(DIRECTORY_ARGNAME, args)
        if download_dir is not None:
            instance.download_dir = download_dir  # type: ignore

        # attribute to handle the region criterion with search
        region = get_from_args(REGION_ARGNAME, args)
        if region is not None:
            instance.region = region  # type: ignore

        # attribute to handle the verbosity level
        verbosity = get_from_args(VERBOSITY_ARGNAME, args)
        if verbosity is not None:
            instance.verbosity = verbosity  # type: ignore

        return instance

    @property  # type: ignore
    @managed_getter()
    def region(self) -> Optional[str]:
        """

        :returns: the AOI name
        """

    @region.setter  # type: ignore
    @managed_setter(pre_set_func=_check_region)
    def region(self, key_region: str) -> None:
        """
        Set region field in resto_client settings and locally

        :param str key_region: key of region geojson file to register
        """

    @property  # type: ignore
    @managed_getter(default=str(user_download_dir()))
    def download_dir(self) -> Optional[str]:
        """
        :returns: The current download directory
        """

    @download_dir.setter  # type: ignore
    @managed_setter(pre_set_func=_check_download_dir)
    def download_dir(self, download_dir: str) -> None:
        """
        Set the current download directory
        :param download_dir: directory where downloaded files must be recorded
        """

    @property  # type: ignore
    @managed_getter()
    def verbosity(self) -> Optional[str]:
        """
        :returns: The current verbosity level
        """

    @verbosity.setter  # type: ignore
    @managed_setter(pre_set_func=_check_verbosity)
    def verbosity(self, verbosity: str) -> None:
        """
        Set the current verbosity level

        :param verbosity: verbosity level to apply to resto_client.
                          Can be one of None, 'NORMAL', 'DEBUG', case insensitive.
        """

    @classmethod
    def is_debug(cls) -> bool:
        """
        :returns: True if verbosity is set to DEBUG, false otherwise
        """
        return RestoClientParameters.properties_storage.get(VERBOSITY_KEY) == 'DEBUG'

    @classmethod
    def is_verbose(cls) -> bool:
        """
        :returns: True if verbosity is set
        """
        return RestoClientParameters.properties_storage.get(VERBOSITY_KEY) is not None
