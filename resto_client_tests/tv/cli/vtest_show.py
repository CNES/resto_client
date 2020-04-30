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
from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


class VTestCliShow(TestRestoClientCli):
    """
    Validation Tests of the cli show module
    """

    def test_n_show_server(self) -> None:
        """
        Validation test of show server in nominal cases
        """
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        output1 = self.get_command_output(['show', 'server'])
        output2 = self.get_command_output(['show', 'server', 'kalideos'])
        # verify integrity betwen show server X and show current server
        self.assertEqual(output1, output2)
        # Test on first phrase of print only
        first_line = output2.splitlines()[0]
        self.assertEqual(first_line, 'Server URL: https://www.kalideos.fr/resto2/')

    def test_n_show_server_stats(self) -> None:
        """
        Validation test of show server in nominal cases
        """
        output = self.get_command_output(['show', 'server', 'kalideos', '--stats'])
        expect_out = (['No statistics available for KALCNES',
                       'No statistics available for KALHAITI',
                       'STATISTICS for all collections'])
        self.assertEqual(output.splitlines()[7:10], expect_out)

    def test_n_show_collection(self) -> None:
        """
        Validation test of show collection in nominal cases: nothing persisted
        """
        output = self.get_command_output(['show', 'collection',
                                          'KALHAITI', '--server=kalideos'])
        second_line = output.splitlines()[1]
        self.assertEqual(second_line[1:-1].strip(), "Collection's Characteristics")

    def test_n_show_current_collection(self) -> None:
        """
        Validation test of show collection in nominal cases : current collection
        """
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        output = self.get_command_output(['show', 'collection'])
        second_line = output.splitlines()[1]
        self.assertEqual(second_line[1:-1].strip(), "Collection's Characteristics")

    def test_n_show_other_collection(self) -> None:
        """
        Validation test of show collection in nominal cases : another collection on the current
        server
        """
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        output = self.get_command_output(['show', 'collection', 'KALHAITI'])
        second_line = output.splitlines()[1]
        self.assertEqual(second_line[1:-1].strip(), "Collection's Characteristics")

    def test_n_show_settings(self) -> None:
        """
        Validation test of show settings in nominal cases
        """
        output = self.get_command_output(['show', 'settings'])
        second_line = output.splitlines()[1]
        self.assertEqual(second_line[1:-1].strip(), 'Settings from : resto_client_settings.json')

    def test_n_show_feature(self) -> None:
        """
        Validation test of show feature in nominal cases
        With Kalideos and Creodias
        """
        output = self.get_command_output(['show', 'feature', '1363714904970542',
                                          '--collection=KALCNES', '--server=kalideos'])
        first_line = output.splitlines()[0]
        self.assertEqual(first_line, 'Metadata available for product 1363714904970542')

        id_prod = ('/eodata/Envisat/Meris/FRS/2012/04/08/' +
                   'MER_FRS_1PPEPA20120408_105857_000005063113_00267_52867_0978.N1')
        output = self.get_command_output(['show', 'feature', id_prod, '--collection=Envisat',
                                          '--server=creodias'])
        first_line = output.splitlines()[0]
        self.assertEqual(first_line, 'Metadata available for product {}'.format(id_prod))

    def test_d_show_server(self) -> None:
        """
        Validation test of show server in degraded cases (no result found)
        """
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['show', 'server'])
        expected_msg = 'No persisted server and None is not a valid server name.'
        self.assertEqual(expected_msg, str(ctxt.exception))

    def test_d_show_collection(self) -> None:
        """
        Validation test of show collection in degraded cases (no result found)
        """
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['show', 'collection', 'oups', '--server=kalideos'])
        expected_msg = 'No collection found with name oups'
        self.assertEqual(expected_msg, str(ctxt.exception))
