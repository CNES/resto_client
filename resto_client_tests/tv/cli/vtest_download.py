# -*- coding: utf-8 -*-
"""
.. admonition:: License

   Copyright 2019 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
from resto_client.base_exceptions import RestoClientUserError, AccessDeniedError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


class VTestCliDownload(TestRestoClientCli):
    """
    Validation Tests of the cli download module
    """

    def test_n_download_annexes(self) -> None:
        """
        Validation test of download annexes
        """
        command = ['download', 'annexes', '1363714904970542',
                   '--collection=KALCNES', '--server=kaliDEOS']
        self.do_test_download_file(command, ['1363714904970542_ann.htm'])

    def test_n_download_quicklook(self) -> None:
        """
        Validation test of download quicklook
        """
        id_kalideos = '1363714904970542'
        id_theia = 'OSO_20180101_VECTOR_departement_92'
        id_peps = 'S1B_EW_GRDM_1SDH_20191202T124407_20191202T124452_019186_02438D_F558'
        iterate = {'kalideos': {'id': id_kalideos, 'col': 'KALCNES', 'type': 'jpg'},
                   'theia': {'id': id_theia, 'col': 'OSO', 'type': 'png'},
                   'peps': {'id': id_peps, 'col': 'S1', 'type': 'jpg'},
                   }
        for server, criteria_dict in iterate.items():
            with self.subTest(server=server):
                command = ['download', 'quicklook', criteria_dict['id'],
                           '--collection=' + criteria_dict['col'], '--server=' + server]
                self.do_test_download_file(command, ['{}_ql.{}'.format(criteria_dict['id'],
                                                                       criteria_dict['type'])])

    def test_n_download_thumbnail(self) -> None:
        """
        Validation test of download thumbnail
        """
        id_kalideos = '1363714904970542'
        id_theia = 'OSO_20180101_VECTOR_departement_92'
        iterate = {'kalideos': {'id': id_kalideos, 'col': 'KALCNES', 'type': 'jpg'},
                   'theia': {'id': id_theia, 'col': 'OSO', 'type': 'png'},
                   }
        for server, criteria_dict in iterate.items():
            with self.subTest(server=server):
                command = ['download', 'thumbnail', criteria_dict['id'],
                           '--collection=' + criteria_dict['col'], '--server=' + server]
                self.do_test_download_file(command, ['{}_th.{}'.format(criteria_dict['id'],
                                                                       criteria_dict['type'])])

    def test_d_download_quicklook_no_ql(self) -> None:
        """
        Validation test of download quicklook if no quicklook for the given ID
        """
        id_creodias = '/eodata/Sentinel-1/SAR/RAW/2019/12/02/'\
            'S1B_EW_RAW__0SDH_20191202T133518_20191202T133616_019186_024392_47A1.SAFE'
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # latitude without longitude
        command = ['download', 'quicklook', id_creodias,
                   '--collection=Sentinel1', '--server=creodias']
        with self.assertRaises(RestoClientUserError) as excp:
            resto_client_run(arguments=command)
        exp_out = 'There is no quicklook to download for product {}.'.format(id_creodias)
        self. assertEqual(exp_out, str(excp.exception))

    def test_d_download_thumbnail(self) -> None:
        """
        Validation test of download thumbnail if no thumbnail for the given ID
        """
        id_creodias = '/eodata/Sentinel-1/SAR/RAW/2019/12/02/'\
            'S1B_EW_RAW__0SDH_20191202T133518_20191202T133616_019186_024392_47A1.SAFE'
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # latitude without longitude
        cmmand = ['download', 'thumbnail', id_creodias,
                  '--collection=Sentinel1', '--server=creodias']
        with self.assertRaises(RestoClientUserError) as excp:
            resto_client_run(arguments=cmmand)
        exp_out = 'There is no thumbnail to download for product {}.'.format(id_creodias)
        self. assertEqual(exp_out, str(excp.exception))

    def test_d_download_no_result(self) -> None:
        """
        Validation test of download annexes,thumbnail, quicklook with no result for a given id
        """
        for download_file in ['annexes', 'quicklook', 'thumbnail']:
            with self.subTest(file_type=download_file):
                command = ['download', download_file, '136371490492',
                           '--collection=KALCNES', '--server=kaliDEOS']
                with self.assertRaises(IndexError) as context:
                    resto_client_run(arguments=command)
                self.assertEqual('No result found for id 136371490492', str(context.exception))

    def test_d_down_prod_wrong_account(self) -> None:
        """
        Validation test of download product when wrong username/password given
        """
        command = ['download', 'product', '715640488937144',
                   '--username=wrong_username', '--password=wrong_password',
                   '--collection=KALCNES', '--server=kalideos']
        with self.assertRaises(AccessDeniedError) as excp:
            resto_client_run(arguments=command)
        exp_out = ('Access Denied : (username, password) does not fit the server: kalideos'
                   '\nFollowing denied access, credentials were reset.')
        self. assertEqual(exp_out, str(excp.exception))
