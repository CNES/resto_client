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
from resto_client_tests.resto_client_cli_test import TestRestoClientCli
from resto_client_tests.tv.test_accounts import (USER_THEIA, PWD_THEIA,
                                                 USER_PEPS, PWD_PEPS,
                                                 USER_DRUPAL, PWD_DRUPAL)


class VTestCliDownloadWithAccount(TestRestoClientCli):
    """
    Validation Tests of the cli download module
    """

    def test_n_down_prod_with_license(self) -> None:
        """
        Validation test of download product
        """
        command = ['download', 'product', '715640488937144',
                   '--username=' + USER_DRUPAL, '--password=' + PWD_DRUPAL,
                   '--collection=KALCNES', '--server=kalideos']
        self.do_test_download_file(command, ['715640488937144.zip'])

    def test_n_down_prod_via_drupal(self) -> None:
        """
        Validation test of download product with license via drupal using ro
        """
        command = ['download', 'product', '1187493693115353',
                   '--username=' + USER_DRUPAL, '--password=' + PWD_DRUPAL,
                   '--collection=ROHAITI', '--server=ro']
        self.do_test_download_file(command, ['1187493693115353.zip'])

    def test_n_down_prod_via_sso(self) -> None:
        """
        Validation test of download product with license via sso using pleiades
        """
        command = ['download', 'product', '591528478572749',
                   '--username=' + USER_THEIA, '--password=' + PWD_THEIA,
                   '--collection=PLEIADES', '--server=pleiades']
        self.do_test_download_file(command, ['591528478572749.zip'])

    def test_n_down_prod_wo_license(self) -> None:
        """
        Validation test of download product
        """
        id_kalideos = '161473090371773'
        id_theia = 'OSO_20180101_VECTOR_departement_92'
        id_peps = 'S2B_MSIL1C_20191202T134209_N0208_R124_T21JYL_20191202T151027'
        iterate = {'kalideos': {'id': id_kalideos, 'col': 'KALCNES',
                                'user': USER_DRUPAL, 'pwd': PWD_DRUPAL},
                   'theia': {'id': id_theia, 'col': 'OSO',
                             'user': USER_THEIA, 'pwd': PWD_THEIA},
                   'peps': {'id': id_peps, 'col': 'S2ST',
                            'user': USER_PEPS, 'pwd': PWD_PEPS},
                   }
        for server, criteria_dict in iterate.items():
            with self.subTest(server=server):
                command = ['download', 'product', criteria_dict['id'],
                           '--username=' + criteria_dict['user'],
                           '--password=' + criteria_dict['pwd'],
                           '--collection=' + criteria_dict['col'], '--server=' + server]
                self.do_test_download_file(command, ['{}.zip'.format(criteria_dict['id'])])
