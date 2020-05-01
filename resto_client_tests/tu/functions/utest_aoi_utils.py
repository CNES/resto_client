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
import unittest

from resto_client.functions.aoi_utils import LowerList, list_all_geojson, str_region_choice


class UTestAOIUtils(unittest.TestCase):
    """
    Unit Tests of the aoi_utils module
    """

    def test_n_lower_list(self) -> None:
        """
        Unit test of lower_list class in nominal cases
        """
        test_lower_list = LowerList(['thisisatest'])
        self.assertEqual(type(test_lower_list), LowerList)
        self.assertTrue('ThisIsATest' in test_lower_list)
        self.assertFalse('ThisIsATest' in LowerList(['thisISsatest']))

    def test_n_test_list_all_geojson(self) -> None:
        """
        Unit test of list_all_geojson function in nominal cases
        """
        test_geojson_list = list_all_geojson()
        expected_list = ['alpes', 'alsace', 'bretagne', 'reunion']
        # prevent bad sortet list
        test_geojson_list.sort()
        expected_list.sort()
        self.assertEqual(type(test_geojson_list), list)
        self.assertEqual(test_geojson_list, expected_list)

    def test_n_test_str_region_choice(self) -> None:
        """
        Unit test of str_region_choice function in nominal cases
        """
        test_region_list = str_region_choice()
        expected_list = sorted(['alpes', 'alsace', 'bretagne', 'reunion'])
        # prevent bad sortet list
        self.assertIn(str(expected_list), test_region_list)

    def test_d_lower_list(self) -> None:
        """
        Unit test of lower_list class in degraded cases
        """
        # We can only test membership of a str in a LowerList
        test_lower_list = LowerList(['henry', 'damieN'])
        other_list = ['henry', 'damien']
        self.assertTrue(other_list not in test_lower_list)
