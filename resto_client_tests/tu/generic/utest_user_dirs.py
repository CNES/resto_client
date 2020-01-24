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
from pathlib import Path
import shutil
import unittest

from resto_client.generic.user_dirs import (user_config_dir, user_download_dir, user_dir,
                                            MSWINDOWS, USER_DIRS_XDG, USER_DIRS_WINDOWS)
from resto_client.settings.resto_client_config import RESTO_CLIENT_APP_NAME


class UTestUserConfigDir(unittest.TestCase):
    """
    Unit Tests of the user_config_dir function
    """

    def test_n_user_config_dir(self) -> None:
        """
        Unit test of user_config_dir in nominal cases
        """
        author = 'Fake Author'
        appname = 'Fake App'
        home = Path.home()

        # Directory may exist of not (only way to get its name without tricks)
        config_dir = user_config_dir(app_author=author, app_name=appname)
        config_path = Path(config_dir)
        author_path = config_path.parent

        # Verify that it is an existing directory
        self.assertTrue(config_path.is_dir())
        self.assertTrue(config_path.exists())
        # Verify that it is inside the user name space
        self.assertTrue(home in config_path.parents)

        # Delete application directory and retry test
        shutil.rmtree(config_dir)
        self.assertFalse(config_path.exists())
        config_dir = user_config_dir(app_author=author, app_name=appname)
        # Verify that it is an existing directory
        self.assertTrue(config_path.is_dir())
        self.assertTrue(config_path.exists())
        # Verify that it is inside the user name space
        self.assertTrue(home in config_path.parents)

        # Delete author and application directory and retry test
        shutil.rmtree(author_path)
        self.assertFalse(author_path.exists())
        config_dir = user_config_dir(app_author=author, app_name=appname)
        # Verify that the config directory exists
        self.assertTrue(config_path.is_dir())
        self.assertTrue(config_path.exists())
        # Verify that it is inside the author directory
        self.assertTrue(author_path in config_path.parents)
        # Verify that it is inside the user name space
        self.assertTrue(home in config_path.parents)


class UTestUserDir(unittest.TestCase):
    """
    Unit Tests of the user_dir() function and its derivatives
    """

    def test_n_user_download_dir(self) -> None:
        """
        Unit test of user_download_dir() in nominal cases
        """
        # Directory is set by the system and must exist
        download_path = user_download_dir(RESTO_CLIENT_APP_NAME)
        self.assertTrue(download_path.is_dir())
        # Verify that it is inside the user name space (is it really mandatory ?)
        self.assertTrue(Path.home() in download_path.parents)

    def test_n_user_dir(self) -> None:
        """
        Unit test of user_dir() in nominal cases
        """
        if MSWINDOWS:
            # Warning: following lists depend on the account under which tests are run
            defined_dirs = ['Contacts', 'Downloads', 'Libraries', 'Links', 'LocalAppDataLow',
                            'RoamingTiles', 'SavedGames', 'SavedSearches']
            for dir_key in USER_DIRS_WINDOWS:
                if dir_key in defined_dirs:
                    user_dir_path = user_dir(dir_key, RESTO_CLIENT_APP_NAME)
                    self.assertTrue(user_dir_path.is_dir())
                else:
                    self.assertRaises(FileNotFoundError)

        else:
            # Warning: following lists depend on the account under which tests are run
            defined_dirs = ['Desktop', 'Documents', 'Downloads', 'Music', 'Pictures',
                            'PublicShare', 'Templates', 'Videos']
            for dir_key in USER_DIRS_XDG:
                if dir_key in defined_dirs:
                    user_dir_path = user_dir(dir_key, RESTO_CLIENT_APP_NAME)
                    self.assertTrue(user_dir_path.is_dir())
                else:
                    self.assertRaises(FileNotFoundError)

    def test_d_user_dir(self) -> None:
        """
        Unit test of user_dir() in degraded cases
        """
        # Unexisting directory key, on any system
        with self.assertRaises(KeyError):
            _ = user_dir('fake', RESTO_CLIENT_APP_NAME)
