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

from shapely.errors import WKTReadingError

from resto_client.generic.basic_types import (GeometryWKT, DateYMD, SquareInterval, TestList,
                                              AscOrDesc, Polarisation)


class UTestBasicTypes(unittest.TestCase):
    """
    Unit Tests of differents basic types
    """

    def test_n_date_ymd(self) -> None:
        """
        Unit test of DateYMD in nominal cases
        """
        self.assertEqual(type(DateYMD("2019-01-01")), DateYMD)

    def test_d_date_ymd(self) -> None:
        """
        Unit test of DateYMD in degraded cases
        """
        with self.assertRaises(ValueError) as context:
            DateYMD("2019-01-81")
        expected_msg = 'unconverted data remains: 1'
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            DateYMD("2019-30-81")
        expected_msg = 'time data \'2019-30-81\' does not match format \'%Y-%m-%d\''
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            DateYMD("2019-30-01")
        expected_msg = 'time data \'2019-30-01\' does not match format \'%Y-%m-%d\''
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            DateYMD("dert")
        expected_msg = 'time data \'dert\' does not match format \'%Y-%m-%d\''
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_geometry_wkt(self) -> None:
        """
        Unit test of GeometryWKT in nominal cases
        """
        polygon = ('POLYGON ((6.415462310782316 44.82087811129371, 5.778714073194358 '
                   '45.02470208405131, 5.795052210906652 45.07160632574142, 6.890476066073996 '
                   '46.08021155414759, 7.05533677339133 46.02448680467278, 7.10308598762563 '
                   '45.97394449848603, 7.193475382947295 45.26866443040745, 6.415462310782316 '
                   '44.82087811129371))')
        self.assertEqual(type(GeometryWKT(polygon)), GeometryWKT)

    def test_d_geometry_wkt(self) -> None:
        """
        Unit test of GeometryWKT in degraded cases
        """
        with self.assertRaises(WKTReadingError) as context:
            GeometryWKT("test")
        expected_msg = 'Geometry criterion accept WKT geometry, this criterion does not fit : test'
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_square_interval(self) -> None:
        """
        Unit test of SquareInterval in nominal cases
        """
        self.assertEqual(type(SquareInterval("[0,10]")), SquareInterval)
        self.assertEqual(type(SquareInterval("]0,10]")), SquareInterval)
        self.assertEqual(type(SquareInterval("[0,10[")), SquareInterval)
        self.assertEqual(type(SquareInterval("]0,10[")), SquareInterval)

    def test_d_square_interval(self) -> None:
        """
        Unit test of SquareInterval in degraded cases
        """
        with self.assertRaises(ValueError) as context:
            SquareInterval("string")
        expected_msg = 'string has a wrong format, expected : [n1,n2['
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            SquareInterval("[0.10]")
        expected_msg = '[0.10] has a wrong format, expected : [n1,n2['
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            SquareInterval("[0,test]")
        msg = '{} in interval {} has an unexpected type, should be convertible in float'
        expected_msg = msg.format("test", "[0,test]")
        self.assertEqual(expected_msg, str(context.exception))
        with self.assertRaises(ValueError) as context:
            SquareInterval("[test,0]")
        expected_msg = msg.format("test", "[test,0]")
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_test_list(self) -> None:
        """
        Unit test of TestList in nominal cases
        """

        self.assertEqual(type(TestList("str_input", ("str_input"))), TestList)
        self.assertEqual(type(TestList("str_input", ("str_input", "str2_input"))), TestList)

    def test_d_test_list(self) -> None:
        """
        Unit test of TestList in degraded cases
        """
        with self.assertRaises(ValueError) as context:
            TestList("str_wrong", (1, 2))
        expected_msg = 'str_wrong has a wrong value, expected in (1, 2)'
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_asc_or_desc(self) -> None:
        """
        Unit test of AscOrDesc in nominal cases
        """

        self.assertEqual(type(AscOrDesc("ascending")), AscOrDesc)
        self.assertEqual(type(AscOrDesc("descending")), AscOrDesc)

    def test_d_asc_or_desc(self) -> None:
        """
        Unit test of AscOrDesc in degraded cases
        """
        with self.assertRaises(ValueError) as context:
            AscOrDesc("str_wrong")
        accpt_tuple = ('ascending', 'descending')
        expected_msg = 'str_wrong has a wrong value, expected in {}'.format(accpt_tuple)
        self.assertEqual(expected_msg, str(context.exception))

    def test_n_polarisation(self) -> None:
        """
        Unit test of Polarisation in nominal cases
        """

        self.assertEqual(type(Polarisation("HH")), Polarisation)
        self.assertEqual(type(Polarisation("VV")), Polarisation)
        self.assertEqual(type(Polarisation("HH HV")), Polarisation)
        self.assertEqual(type(Polarisation("VV VH")), Polarisation)

    def test_d_polarisation(self) -> None:
        """
        Unit test of TestList in degraded cases
        """
        with self.assertRaises(ValueError) as context:
            Polarisation("str_wrong")

        accpt_tuple = ('HH', 'VV', 'HH HV', 'VV VH')
        expected_msg = 'str_wrong has a wrong value, expected in {}'.format(accpt_tuple)
        self.assertEqual(expected_msg, str(context.exception))
