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
import unittest

from resto_client.base_exceptions import RestoClientUserError
from resto_client.entities.resto_criteria import RestoCriteria, test_criterion
from resto_client.generic.basic_types import GeometryWKT
from resto_client.services.resto_server import RestoServer


class UTestTestCriterion(unittest.TestCase):
    """
    Unit Tests of the test_criterion function
    """

    def test_n_test_criterion(self) -> None:
        """
        Unit test of test_criterion function in nominal cases
        """
        # Following calls to test_criterion should not raise a RestoClientUserError exception.
        try:
            test_criterion('key', 10, int)
            test_criterion('key', 10, float)
            test_criterion('key', 10.1, float)
            test_criterion('key', 'toto', str)
        except RestoClientUserError as excp:
            self.fail('Exception <{}> raised during test_criterion'.format(str(excp)))

    def test_d_test_criterion(self) -> None:
        """
        Unit test of test_criterion function in degraded cases
        """
        with self.assertRaises(RestoClientUserError) as context:
            test_criterion('key', 'oups', float)
        expected_msg = 'Criterion key has an unexpected type : str, expected : float'
        self.assertEqual(expected_msg, str(context.exception))

        with self.assertRaises(RestoClientUserError) as context:
            test_criterion('key', 'wrong_geo', GeometryWKT)
        expected_msg = 'Criterion key has an unexpected type : str, expected : GeometryWKT'
        self.assertEqual(expected_msg, str(context.exception))


class UTestRestoCriteria(unittest.TestCase):
    """
    Unit Tests of the RestoCriteria class
    """

    def test_n_init_of_resto_criteria(self) -> None:
        """
        Unit test of class construction
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service, identifier='2010')
        self.assertDictEqual(resto_criteria, {'identifier': '2010'})

    def test_n_setitem_standard(self) -> None:
        """
        Unit test of __setitem__ with standard criterion
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        resto_criteria['identifier'] = '2010'
        self.assertEqual(resto_criteria['identifier'], '2010')
        del resto_criteria['identifier']
        resto_criteria['startDate'] = '2010-01-01'
        self.assertEqual(resto_criteria['startDate'], '2010-01-01')
        del resto_criteria['startDate']
        self.assertDictEqual(resto_criteria, {})

    def test_n_setitem_list(self) -> None:
        """
        Unit test of __setitem__ with criterion accepting list
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        resto_criteria['platform'] = ['SPOT 5', 'SPOT 6']
        # Verify that 2 criteria are created and not a single one
        self.assertFalse('platform' in resto_criteria)
        self.assertEqual(resto_criteria['platform[0]'], 'SPOT 5')
        self.assertEqual(resto_criteria['platform[1]'], 'SPOT 6')
        del resto_criteria['platform[0]']
        del resto_criteria['platform[1]']
        # Verify when only one is given, it s created as a standard criterion
        resto_criteria['platform'] = 'SPOT 5'
        self.assertEqual(resto_criteria['platform'], 'SPOT 5')

    def test_n_setitem_group(self) -> None:
        """
        Unit test of __setitem__ with criterion accepting group
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        geom_point = {'lat': 1, 'lon': 2}
        geom_surface = {'radius': 120, 'lat': 1, 'lon': 2}
        resto_criteria['geomPoint'] = geom_point
        self.assertDictEqual(resto_criteria, geom_point)
        resto_criteria['geomSurface'] = geom_surface
        self.assertDictEqual(resto_criteria, geom_surface)

    def test_d_setitem_standard(self) -> None:
        """
        Unit test of __setitem__ in degraded cases
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        with self.assertRaises(RestoClientUserError) as context:
            resto_criteria['startDate'] = 1
        expected_msg = 'Criterion startDate has an unexpected type : int, expected : DateYMD'
        self.assertEqual(expected_msg, str(context.exception))

        with self.assertRaises(RestoClientUserError) as context:
            resto_criteria['wrong_crit'] = 1
        expected_msg = 'Criterion wrong_crit not supported by this resto server'
        self.assertIn(expected_msg, str(context.exception))

    def test_d_setitem_group(self) -> None:
        """
        Unit test of __setitem__ in degraded cases with criterion accepting group
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        geom_surface = {'radius': 120, 'latitude': 1, 'longitude': 2}
        with self.assertRaises(RestoClientUserError) as context:
            resto_criteria['geomPoint'] = geom_surface
        expected_msg = 'Criterion radius in geomPoint not supported by this resto server'
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_region(self) -> None:
        """
        Unit test of the region management
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        resto_criteria['region'] = 'alpes.geojson'
        polygon = ('POLYGON ((6.415462310782316 44.82087811129371, 5.778714073194358 '
                   '45.02470208405131, 5.795052210906652 45.07160632574142, 6.890476066073996 '
                   '46.08021155414759, 7.05533677339133 46.02448680467278, 7.10308598762563 '
                   '45.97394449848603, 7.193475382947295 45.26866443040745, 6.415462310782316 '
                   '44.82087811129371))')
        self.assertEqual(resto_criteria['geometry'], polygon)
        # Verify that region criteria is not created by only geometry one
        self.assertFalse('region' in resto_criteria)

        # Verify that geometry criteria is erased when identifier criteria is specified.
        resto_criteria1 = RestoCriteria(resto_server.resto_service, **{'region': 'alpes.geojson'})
        resto_criteria1['identifier'] = 'alpes.geojson'
        self.assertFalse('geometry' in resto_criteria1)

    def test_n_retrieve_criterion(self) -> None:
        """
        Unit test of _retrieve_criterion with standard criterion
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        resto_criteria['idenTIFier'] = '2010'
        self.assertEqual(resto_criteria['identifier'], '2010')

    def test_d_retrieve_criterion(self) -> None:
        """
        Unit test of the _retrieve_criterion management in degraded cases
        """
        resto_server = RestoServer('kalideos')
        resto_criteria = RestoCriteria(resto_server.resto_service)
        with self.assertRaises(RestoClientUserError) as context:
            resto_criteria['wrong_crit'] = 1
        expected_msg = 'Criterion wrong_crit not supported by this resto server'
        self.assertIn(expected_msg, str(context.exception))
