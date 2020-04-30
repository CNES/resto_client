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

from resto_client_tests.tv.cli_accounts import USER_DRUPAL, PWD_DRUPAL


class VTestCliSearchWithAccount(TestRestoClientCli):
    """
    Validation Tests of the cli search module
    """

    def test_n_search_hidden(self) -> None:
        """
        Validation test of set server with account in nominal cases
        """
        crit_id = '1067991235229141'
        command = ['search', '--criteria=identifiers:{}'.format(crit_id),
                   '--collection=KALCNES', '--server=Kalideos']
        output = self.get_command_output(command)
        exp_crit = {'identifiers': crit_id, 'region': None}
        expt_output1 = "No result found with criteria : {}".format(exp_crit)
        self.assertIn(expt_output1, output)

        command += ['--username=' + USER_DRUPAL, '--password=' + PWD_DRUPAL]
        output = self.get_command_output(command)
        expt_output2 = "One result found with id : "
        self.assertIn(expt_output2, output)
        self.assertIn(crit_id, output)

    def test_n_search_download_product(self) -> None:
        """
        Validation test of search in nominal cases with download triggered after search
        """
        command = ['search', '--criteria=identifiers:1355444872323826,1355444867040321',
                   '--collection=ROHAITI', '--server=ro',
                   '--username=' + USER_DRUPAL, '--password=' + PWD_DRUPAL,
                   '--download']
        self.do_test_download_file(command, ['1355444872323826.zip', '1355444867040321.zip'])
