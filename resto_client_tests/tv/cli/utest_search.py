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


class UTestCliSearch(TestRestoClientCli):
    """
    Unit Tests of the cli search module
    """

    def do_search_one_feature(self, server_name: str, collection: str, feature_id: str) -> None:
        """
        Lauch search request with given parameters

        :param server_name: nickname of server as in server settings
        :param collection : server's collection
        :param feature_id : identifier of a resto feature
        """
        output = self.get_command_output(['search', '--criteria=identifier:{}'.format(feature_id),
                                          '--collection={}'.format(collection),
                                          '--server={}'.format(server_name)])
        self.assertIn('One result found with id : ', output)
        self.assertIn('{}'.format(feature_id), output)

    def test_n_search_kalideos(self) -> None:
        """
        Unit test of search in nominal cases for kalideos
        """
        self.do_search_one_feature('kalideos', 'KALCNES', '2482882741373125')

    def test_n_search_peps(self) -> None:
        """
        Unit test of search in nominal cases for peps
        """
        self.do_search_one_feature(
            'peps', 'S2',
            'S2A_OPER_PRD_MSIL1C_PDMC_20161206T135131_R031_V20161206T013712_20161206T013712')

    def test_n_search_creodias(self) -> None:
        """
        Unit test of search in nominal cases for creodias
        """
        id_creo = ('/eodata/Envisat/Meris/FRS/2012/04/08/' +
                   'MER_FRS_1PPEPA20120408_105857_000005063113_00267_52867_0978.N1')
        self.do_search_one_feature('creodias', 'Envisat', id_creo)

    def test_n_search_theia(self) -> None:
        """
        Unit test of search in nominal cases for theia
        """
        self.do_search_one_feature('theia', 'SENTINEL2',
                                   'SENTINEL2B_20190917-113018-467_L2A_T30STJ_D')

    def test_n_search_cop_nci(self) -> None:
        """
        Unit test of search in nominal cases for cop_nci
        """
        id_cop_nci = ('S3B_SL_2_WST____20191203T063311_20191203T063611_' +
                      '20191203T073554_0179_033_006_0540_MAR_O_NR_003')
        self.do_search_one_feature('cop_nci', 'S3', id_cop_nci)

    def test_n_search_sent_hub(self) -> None:
        """
        Unit test of search in nominal cases for sent_hub
        """
        self.do_search_one_feature(
            'sent_hub', 'Sentinel2',
            'S2B_OPER_MSI_L1C_TL_SGS__20191203T062142_A014316_T46RDR_N02.08')

    def test_n_search_case_unsensitive(self) -> None:
        """
        Unit test of search in nominal cases when criteria has a wrong case
        """
        id_kalideos = '2482882741373125'
        output = self.get_command_output(['search', '--criteria=idenTIFier:{}'.format(id_kalideos),
                                          '--collection=KALCNES', '--server=kalideos'])
        self.assertIn('One result found with id : ', output)
        self.assertIn('{}'.format(id_kalideos), output)

    def test_n_search_multi(self) -> None:
        """
        Unit test of search with multi criteria in nominal cases
        """
        command = ['search', '--criteria', 'platform:SPOT 4', 'platform:DRONE',
                   '--collection=KALCNES', '--server=Kalideos']
        output = self.get_command_output(command)
        ids_out = ['718546971960888', '2193469539462683', '2193246286290231', '2193020092357640']
        text_out = '{}\n4 results shown on a total of'
        self.assertIn(text_out.format(str(ids_out)), output)
        self.assertIn(' 4 results ', output)
        self.assertIn('beginning at index 1', output)

    def test_n_search_several_result(self) -> None:
        """
        Unit test of set server with several result in nominal cases
        """
        command = ['search', '--criteria=productMode:SBS', '--collection=KALCNES',
                   '--server=Kalideos']
        output = self.get_command_output(command)
        ids_out = ['127387459591469', '313788470150102', '312422352833026', '377704677444208']
        text_out = '{}\n4 results shown on a total of'
        self.assertIn(text_out.format(str(ids_out)), output)
        self.assertIn(' 4 results ', output)
        self.assertIn('beginning at index 1', output)

    def test_n_search_several_res_page(self) -> None:
        """
        Unit test of set server with several result in nominal cases
        with page and maxrecords
        """
        command = ['search', '--criteria=productMode:SBS', '--page=2', '--maxrecords=2',
                   '--collection=KALCNES', '--server=Kalideos']
        output = self.get_command_output(command)
        ids_out = ['312422352833026', '377704677444208']
        text_out = '{}\n2 results shown on a total of'
        self.assertIn(text_out.format(str(ids_out)), output)
        self.assertIn(' 4 results ', output)
        self.assertIn('beginning at index 3', output)

    def test_d_search_several_pages(self) -> None:
        """
        Unit test of set server with several result in degraded cases
        """
        command = ['search', '--criteria=productMode:SBS', '--page=3', '--maxrecords=2',
                   '--collection=KALCNES', '--server=Kalideos']
        output = self.get_command_output(command)
        self.assertIn('No result', output)
        self.assertIn('at page 3, try a lower page number', output)

    def test_n_search_with_radius(self) -> None:
        """
        Unit test of search with raidus in degraded cases
        """
        # radius without longitude or latitude
        command = ['search', '--criteria', 'radius:1485', 'lon:-1.76', 'lat:48.15',
                   'productMode:FBD', '--collection=KALCNES', '--server=kalideos']
        output = self.get_command_output(command)
        ids_out = ['399183522347555', '399184189945956', '399377909654471']
        text_out = '{}\n3 results shown on a total of'
        self.assertIn(text_out.format(str(ids_out)), output)
        self.assertIn(' 3 results ', output)
        self.assertIn('beginning at index 1', output)

    def test_d_search(self) -> None:
        """
        Unit test of search in degraded cases (no result found)
        """
        # No result found
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        command = ['search', '--criteria=identifiers:wrong_id', '--collection=KALCNES']
        output = self.get_command_output(command)
        exp_crit = {'identifiers': 'wrong_id', 'region': None}
        expt_output = "No result found with criteria : {}".format(exp_crit)
        self.assertIn(expt_output, output)

        # Wong type of criteria given
        command = ['search', '--criteria=resolution:d0,15]', '--collection=KALCNES']
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=command)
        exp_out = 'Criterion resolution has an unexpected type : str, expected : SquareInterval'
        self.assertEqual(exp_out, str(context.exception))

    def test_d_search_bad_criteria(self) -> None:
        """
        Unit test of search in degraded cases (criteria not found)
        """
        # No result found
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        with self.assertRaises(RestoClientUserError) as ctxt:
            command = ['search', '--criteria=bad_criteria:hello', '--collection=KALCNES']
            resto_client_run(arguments=command)
        expected_msg = 'Criterion bad_criteria not supported by this resto server,'
        self.assertIn(expected_msg, str(ctxt.exception))
        self.assertIn("'incidenceAngle", str(ctxt.exception))

    def test_d_search_lat_and_long(self) -> None:
        """
        Unit test of search in degraded cases (latitude present without longitude)
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # latitude without longitude
        command = ['search', '--criteria', 'lat:10',
                   '--collection=S2', '--server=peps']
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=command)
        exp_out = 'lat AND lon must be present simultaneously'
        self.assertEqual(exp_out, str(context.exception))

    def test_d_search_with_radius(self) -> None:
        """
        Unit test of search in degraded cases (with radius)
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # radius without longitude or latitude
        command = ['search', '--criteria', 'radius:10',
                   '--collection=KALCNES', '--server=kalideos']
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=command)
        exp_out = 'With radius, latitude AND longitude must be present'
        self.assertEqual(exp_out, str(context.exception))

    def test_n_search_download_ql(self) -> None:
        """
        Unit test of search in nominal cases when quicklook download is triggered after search
        """
        command = ['search', '--criteria=identifiers:1355444872323826',
                   '--collection=ROHAITI', '--server=ro',
                   '--download=quicklook']
        self.do_test_download_file(command, ['1355444872323826_ql.jpg'])

    def test_n_search_download_th(self) -> None:
        """
        Unit test of search in nominal cases when thumbnail download is triggered after search
        """
        command = ['search', '--criteria=identifiers:1355444872323826',
                   '--collection=ROHAITI', '--server=ro',
                   '--download=thumbnail']
        self.do_test_download_file(command, ['1355444872323826_th.jpg'])

    def test_n_search_download_ann(self) -> None:
        """
        Unit test of search in nominal cases when annexes download is triggered after search
        """
        command = ['search', '--criteria=identifiers:10159402351973898',
                   '--collection=KALCNES', '--server=kalideos',
                   '--download=annexes']
        self.do_test_download_file(command, ['10159402351973898_ann.htm'])
