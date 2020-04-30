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

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_parameters import VERBOSITY_KEY, REGION_KEY, DOWNLOAD_DIR_KEY
from resto_client.cli.resto_client_settings import RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


HERE = Path(__file__).parent
TEST_PATH = HERE.parent.parent.parent / 'resto_client' / 'zones' / 'Alpes.geojson'


class VTestSetClientParams(TestRestoClientCli):
    """
    Validation Tests of the cli set of RestoClientParameters
    download_dir, region, verbosity
    """

    def test_n_set_region(self) -> None:
        """
        Validation test of set region in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'region', 'bretagne'])
        self.assert_setting_equal(REGION_KEY, 'bretagne')
        # With region already persisted and test unsesitivity
        resto_client_run(arguments=['set', 'region', 'aLpes'])
        self.assert_setting_equal(REGION_KEY, 'alpes')
        # With a path as args
        resto_client_run(arguments=['set', 'region', str(TEST_PATH)])
        self.assert_setting_equal(REGION_KEY, str(TEST_PATH))

    def test_n_set_download_dir(self) -> None:
        """
        Validation test of set download directory in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # get an existing directory for test
        directory_test_1 = Path.home()
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_1)])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(directory_test_1))
        # With download directory already persisted
        directory_test_2 = directory_test_1.parent
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_2)])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(directory_test_2))

    def test_n_set_verbosity(self) -> None:
        """
        Validation test of set verbosity in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        self.assert_setting_equal(VERBOSITY_KEY, 'DEBUG')
        # With verbosity already persisted
        resto_client_run(arguments=['set', 'verbosity', 'NORMAL'])
        self.assert_setting_equal(VERBOSITY_KEY, 'NORMAL')

    def test_d_set_download_dir(self) -> None:
        """
        Validation test of set download directory in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(NotADirectoryError) as context:
            resto_client_run(arguments=['set', 'download_dir', 'ICI'])
        self.assertEqual('ICI', str(context.exception))

    # Following errors are processed by argparse directly.

    def test_d_set_region(self) -> None:
        """
        Validation test of set region in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=['set', 'region', 'JaimeLaBretagne'])
        expect_output = 'JaimeLaBretagne is not a valid geojson file path'
        self.assertEqual(expect_output, str(context.exception))

    def test_d_set_verbosity(self) -> None:
        """
        Validation test of set verbosity in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(SystemExit) as context:
            resto_client_run(arguments=['set', 'verbosity', 'Parle_Moi'])
        # should raise this exception after a argparse.ArgumentError
        # because argument verbosity: invalid choice
        self.assertEqual('2', str(context.exception))


class VTestUnsetClientParams(TestRestoClientCli):
    """
    Validation Tests of the cli unset of RestoClientParameters
    download_dir, region, verbosity
    """

    def test_n_unset_region(self) -> None:
        """
        Validation test of unset region in nominal cases
        """
        # With region already persisted
        resto_client_run(arguments=['set', 'region', 'bretagne'])
        resto_client_run(arguments=['unset', 'region'])
        self.assert_not_in_settings(REGION_KEY)
        # With no region persisted
        resto_client_run(arguments=['unset', 'region'])
        self.assert_not_in_settings(REGION_KEY)

    def test_n_unset_download_dir(self) -> None:
        """
        Validation test of unset download directory in nominal cases
        """
        # With download directory already persisted
        directory_test = str(Path.home())
        resto_client_run(arguments=['set', 'download_dir', directory_test])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, directory_test)
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR))
        # With default directory persisted
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR))

    def test_n_unset_verbosity(self) -> None:
        """
        Validation test of unset verbosity in nominal cases
        """
        # With verbosity already persisted
        resto_client_run(arguments=['set', 'verbosity', 'NORMAL'])
        resto_client_run(arguments=['unset', 'verbosity'])
        self.assert_not_in_settings(VERBOSITY_KEY)
        # With no verbosity persisted
        resto_client_run(arguments=['unset', 'verbosity'])
        self.assert_not_in_settings(VERBOSITY_KEY)
