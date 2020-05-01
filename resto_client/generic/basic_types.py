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
from typing import Sequence, Optional  # @NoMove
from datetime import datetime
from urllib.parse import urlparse

from shapely import wkt
from shapely.errors import WKTReadingError

from resto_client.base_exceptions import RestoClientDesignError


class DateYMD():  # pylint: disable=too-few-public-methods
    """
    A class to test input Date in order to have a proper YYYY-MM-DD format
    """

    def __init__(self, date_text: str) -> None:
        """
        Test the input in order to have a proper %Y-%m-%d format

        :param date_text: date in str format to test
        """
        datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d')


class DateYMDInterval():  # pylint: disable=too-few-public-methods
    """
    A class to test input Date Interval in order to have a proper format
    """

    def __init__(self, date_interval_text: str) -> None:
        """
        Test the input in order to have a proper %Y-%m-%d:%Y-%m-%d format

        :param date_interval_text: date interval in str format to test
        :raises ValueError: when argument does not have 2 components or when one of them is not
                            a DateYMD.
        """
        interval = date_interval_text.split(':')
        # Test that two numbers are given
        if len(interval) != 2:
            msg_error = '{} has a wrong format, expected : Date1:Date2'
            raise ValueError(msg_error.format(date_interval_text))
        for date_unic in interval:
            try:
                DateYMD(date_unic)
            except ValueError:
                msg = '{} in interval {} has an unexpected type, should be DateYMD'
                raise ValueError(msg.format(date_unic, date_interval_text))
        date1 = datetime.strptime(interval[0], "%Y-%m-%d")
        date2 = datetime.strptime(interval[1], "%Y-%m-%d")
        if date1 > date2:
            msg_error = 'First date must be anterior to Second one in interval, Here :{}>{}'
            raise ValueError(msg_error.format(date1, date2))


class GeometryWKT():  # pylint: disable=too-few-public-methods
    """
    A class to test input geometry in order to have a proper WKT format
    """

    def __init__(self, geometry_input: str) -> None:
        """
        Test the input in order to have a proper %Y-%m-%d format

        :param geometry_input: geometry in str format to test
        :raises WKTReadingError: geometry has not a wkt format
        """
        try:
            wkt.loads(geometry_input)
        except WKTReadingError:
            msg = 'Geometry criterion accept WKT geometry, this criterion does not fit : {}'
            raise WKTReadingError(msg.format(geometry_input))


class SquareInterval():  # pylint: disable=too-few-public-methods
    """
    A class to test input Interval in order to have a proper format surounded by square backet
    ex : [n1,n2[
    """

    def __init__(self, str_interval: str) -> None:
        """
        Constructor

        :param str_interval: interval in str format to test
        :raises ValueError: if format not respected
        """
        accpt_car = ('[', ']')
        # Test beginning and end for interval
        if not str_interval.startswith(accpt_car) or not str_interval.endswith(accpt_car):
            raise ValueError('{} has a wrong format, expected : [n1,n2['.format(str_interval))

        interval = str_interval[1:-1].split(',')
        # Test that two numbers are given
        if len(interval) != 2:
            raise ValueError('{} has a wrong format, expected : [n1,n2['.format(str_interval))
        for number in interval:
            try:
                float(number)
            except ValueError:
                msg = '{} in interval {} has an unexpected type, should be convertible in float'
                raise ValueError(msg.format(number, str_interval))


class TestList():  # pylint: disable=too-few-public-methods
    """
    A class to test input exist in tuple
    """

    def __init__(self, str_input: str, accepted: Sequence[str]) -> None:
        """
        Constructor
        :param str_input: input to test
        :param accepted: accepted values for input
        :raises ValueError: if format not respected
        """
        if str_input not in accepted:
            raise ValueError('{} has a wrong value, expected in {}'.format(str_input, accepted))


class AscOrDesc(TestList):  # pylint: disable=too-few-public-methods
    """
    A class to test input is 'ascending' or 'descending'
    """

    def __init__(self, str_input: str) -> None:
        """
        Constructor

        :param str_input: input to test
        """
        accpt_tuple = ('ascending', 'descending')
        super(AscOrDesc, self).__init__(str_input=str_input, accepted=accpt_tuple)


class Polarisation(TestList):  # pylint: disable=too-few-public-methods
    """
    A class to test input has a accepted polarisation type
    """

    def __init__(self, str_input: str) -> None:
        """
        Constructor

        :param str str_input: input to test
        """
        accpt_tuple = ('HH', 'VV', 'HH HV', 'VV VH')
        super(Polarisation, self).__init__(str_input=str_input, accepted=accpt_tuple)


class URLType():  # pylint: disable=too-few-public-methods
    """
    A class to make sure input is an url
    """

    def __init__(self, url: str, url_purpose: Optional[str]="Unknown") -> None:
        """
        Test the input in order to have a proper URL

        :param url: URL in str format to test
        :param url_purpose: purpose of the URL
        :raises RestoClientDesignError: if url is not a proper URL
        """
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError()
        except ValueError:
            error_msg = 'Given url for {} is not a valid URL: {}.'
            raise RestoClientDesignError(error_msg.format(url_purpose, url))
