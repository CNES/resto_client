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
from contextlib import redirect_stdout
import io
import unittest

from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS


class UTestCliShow(unittest.TestCase):
    """
    Unit Tests of the cli show module
    """

    def test_n_show_server(self) -> None:
        """
        Unit test of show server in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        with redirect_stdout(io.StringIO()) as out_string_io1:
            resto_client_run(arguments=['show', 'server'])
        output1 = out_string_io1.getvalue().strip()  # type: ignore
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io2:
            resto_client_run(arguments=['show', 'server', 'kalideos'])
        output2 = out_string_io2.getvalue().strip()  # type: ignore
        # verify integrity betwen show server X and show current server
        self.assertEqual(output1, output2)
        # Test on first phrase of print only
        first_line = out_string_io2.getvalue().splitlines()[0]  # type: ignore
        self.assertEqual(first_line, 'Server URL: https://www.kalideos.fr/resto2/')

        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'server', 'kalideos', '--stats'])
        expect_out = (['No statistics available for KALCNES',
                       'No statistics available for KALHAITI',
                       'STATISTICS for all collections'])
        self.assertEqual(out_string_io.getvalue().splitlines()[7:10], expect_out)  # type: ignore

    def test_n_show_collections(self) -> None:
        """
        Unit test of show collections in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'collection', 'KALHAITI', '--server=kalideos'])
        second_line = out_string_io.getvalue().splitlines()[1]  # type: ignore
        self.assertEqual(second_line[1:-1].strip(), "Collection's Characteristics")

    def test_n_show_settings(self) -> None:
        """
        Unit test of show settings in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'settings'])
        second_line = out_string_io.getvalue().splitlines()[1]  # type: ignore
        self.assertEqual(second_line[1:-1].strip(), 'Settings from : resto_client_settings.json')

    def test_n_show_feature(self) -> None:
        """
        Unit test of show feature in nominal cases
        With Kalideos and Creodias
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'feature', '1363714904970542',
                                        '--collection=KALCNES', '--server=kalideos'])
        second_line = out_string_io.getvalue().splitlines()[1]  # type: ignore
        self.assertEqual(second_line, 'Metadata available for product 1363714904970542')

        id_prod = ('/eodata/Envisat/Meris/FRS/2012/04/08/' +
                   'MER_FRS_1PPEPA20120408_105857_000005063113_00267_52867_0978.N1')
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'feature', id_prod, '--collection=Envisat',
                                        '--server=creodias'])
        second_line = out_string_io.getvalue().splitlines()[1]  # type: ignore
        self.assertEqual(second_line, 'Metadata available for product {}'.format(id_prod))

    def test_d_show_server(self) -> None:
        """
        Unit test of show server in degraded cases (no result found)
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'server'])
        output = out_string_io.getvalue()  # type: ignore
        expected_msg = 'No persisted server and None is not a valid server name.'
        self.assertIn(expected_msg, output)

    def test_d_show_collection(self) -> None:
        """
        Unit test of show collection in degraded cases (no result found)
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['show', 'collection', 'oups', '--server=kalideos'])
        output = out_string_io.getvalue()  # type: ignore
        self.assertIn('No collection found with name oups', output)
