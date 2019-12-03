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
from typing import Any
import unittest

from resto_client.generic.property_decoration import managed_getter, managed_setter


def check_for_test(value: Any) -> str:
    """
    Function used in tests to verify that it is correctly called and handled.

    Just return the argument as lowercase or raise an exception if argument is not a str.

    :param str value: a test string
    :raises TypeError: if value is not an str
    :returns: value in lowercase
    """
    if not isinstance(value, str):
        raise TypeError('Wrong type for value: {}'.format(type(value)))
    return value.lower()


class PropertiesForTests():
    """
    Base class for tests, defining properties but not their management parameters.
    """

    @property  # type: ignore
    @managed_getter(default=10)
    def prop_with_default(self) -> int:
        """
        A property with a default value for tests purpose
        """

    @prop_with_default.setter  # type: ignore
    @managed_setter()
    def prop_with_default(self, value: int) -> None:
        pass

    @property  # type: ignore
    @managed_getter()
    def prop_without_default(self) -> int:
        """
        A property with no default value for tests purpose
        """

    @prop_without_default.setter  # type: ignore
    @managed_setter()
    def prop_without_default(self, value: Any) -> None:
        pass

    @property  # type: ignore
    @managed_getter()
    def prop_with_checker(self) -> str:
        """
        A property with a checker function for tests purpose
        """

    @prop_with_checker.setter  # type: ignore
    @managed_setter(pre_set_func=check_for_test)
    def prop_with_checker(self, value: Any) -> None:
        pass

    @property  # type: ignore
    @managed_getter()
    def prop_with_checker_method(self) -> str:
        """
        A property with a checker method for tests purpose
        """

    @prop_with_checker_method.setter  # type: ignore
    @managed_setter(pre_set_func='check_prop_with_checker')
    def prop_with_checker_method(self, value: Any) -> None:
        pass

    def check_prop_with_checker(self, value: Any) -> str:
        """
        The checker method associated to prop_with_checker_method
        """
        if not isinstance(value, str):
            raise TypeError('Wrong type for value: {} in {}'.format(type(value), self))
        return value.upper()


class UTestPropertyDecoration(unittest.TestCase):
    """
    Unit Tests of the property_decoration module
    """

    def test_n_init_with_class_attrs(self) -> None:
        """
        Unit test of class construction and initial state when management attributes defined
        at class level.
        """

        class PropertiesWithClassAttributes(PropertiesForTests):
            """
            Inner class for this test case with both attributes defined at class level
            """
            properties_storage = {'an_initial_key': 100}
            properties_name_prefix = 'in_class'

        instance = PropertiesWithClassAttributes()
        # Verify initial location and value of properties_name_prefix attribute
        self.assertTrue(hasattr(instance, 'properties_name_prefix'))
        self.assertTrue(hasattr(type(instance), 'properties_name_prefix'))
        self.assertEqual(instance.properties_name_prefix, 'in_class')
        # Verify initial location and value of properties_storage attribute
        self.assertTrue(hasattr(instance, 'properties_storage'))
        self.assertTrue(hasattr(type(instance), 'properties_storage'))
        self.assertEqual(sorted(list(instance.properties_storage.keys())), ['an_initial_key'])
        # Verify initial values of properties (and possibly trigger attributes creation)
        self.assertEqual(instance.prop_with_default, 10)
        self.assertEqual(instance.prop_without_default, None)
        # Verify that location and value of properties_name_prefix attribute did not change
        self.assertTrue(hasattr(instance, 'properties_name_prefix'))
        self.assertTrue(hasattr(type(instance), 'properties_name_prefix'))
        self.assertEqual(instance.properties_name_prefix, 'in_class')
        # Verify that location and value of properties_storage attribute did not change
        self.assertTrue(hasattr(instance, 'properties_storage'))
        self.assertTrue(hasattr(type(instance), 'properties_storage'))
        # but has been populated with defaults
        self.assertEqual(sorted(list(instance.properties_storage.keys())),
                         ['an_initial_key', 'in_class_prop_with_default'])

    def test_n_init_with_no_attrs(self) -> None:
        """
        Unit test of class construction and initial state when no management attributes defined
        at all.
        """

        class PropertiesWithNoAttributes(PropertiesForTests):
            """
            Inner class for this test case with no class attributes
            """

        instance = PropertiesWithNoAttributes()
        # No properties_name_prefix attribute defined neither at instance level nor at class level
        self.assertFalse(hasattr(instance, 'properties_name_prefix'))
        self.assertFalse(hasattr(type(instance), 'properties_name_prefix'))
        # No properties_storage attribute defined neither at instance level nor at class level
        self.assertFalse(hasattr(instance, 'properties_storage'))
        self.assertFalse(hasattr(type(instance), 'properties_storage'))
        # Verify initial values of properties (and possibly trigger attributes creation)
        self.assertEqual(instance.prop_with_default, 10)
        self.assertEqual(instance.prop_without_default, None)
        # Verify that no properties_name_prefix attribute was created
        self.assertFalse(hasattr(instance, 'properties_name_prefix'))
        self.assertFalse(hasattr(type(instance), 'properties_name_prefix'))
        # A properties_storage attribute has been created at instance level
        self.assertTrue(hasattr(instance, 'properties_storage'))
        self.assertFalse(hasattr(type(instance), 'properties_storage'))
        # and populated with defaults
        # pylint: disable= no-member
        self.assertEqual(sorted(list(instance.properties_storage.keys())), [
                         'prop_with_default'])

    def test_n_init_with_instance_attrs(self) -> None:
        """
        Unit test of class construction and initial state when management attributes defined
        at instance level.
        """

        class PropertiesWithInstanceAttributes(PropertiesForTests):
            """
            Inner class for this test case with attributes at instance level
            """

            def __init__(self) -> None:
                self.properties_storage = {'an_initial_key': 100}
                self.properties_name_prefix = 'in_instance'

        instance = PropertiesWithInstanceAttributes()
        # properties_name_prefix attribute defined at instance level only.
        self.assertTrue(hasattr(instance, 'properties_name_prefix'))
        self.assertFalse(hasattr(type(instance), 'properties_name_prefix'))
        self.assertEqual(instance.properties_name_prefix, 'in_instance')
        # properties_storage attribute defined at instance level only.
        self.assertTrue(hasattr(instance, 'properties_storage'))
        self.assertFalse(hasattr(type(instance), 'properties_storage'))
        self.assertEqual(sorted(list(instance.properties_storage.keys())), ['an_initial_key'])
        # Verify initial values of properties (and possibly trigger attributes creation)
        self.assertEqual(instance.prop_with_default, 10)
        self.assertEqual(instance.prop_without_default, None)
        # Verify that location and value of properties_name_prefix attribute did not change
        self.assertTrue(hasattr(instance, 'properties_name_prefix'))
        self.assertFalse(hasattr(type(instance), 'properties_name_prefix'))
        self.assertEqual(instance.properties_name_prefix, 'in_instance')
        # Verify that location and value of properties_storage attribute did not change
        self.assertTrue(hasattr(instance, 'properties_storage'))
        self.assertFalse(hasattr(type(instance), 'properties_storage'))
        # but has been populated with defaults
        self.assertEqual(sorted(list(instance.properties_storage.keys())),
                         ['an_initial_key', 'in_instance_prop_with_default'])

    def test_n_getter_setter(self) -> None:
        """
        Unit test of getter and setter
        """
        class PropertiesWithInstanceAttributes(PropertiesForTests):
            """
            Inner class for this test case with both attributes defined at class level
            """
            properties_storage = {'an_initial_key': 100}
            properties_name_prefix = 'header'

        instance = PropertiesWithInstanceAttributes()
        # Verify initial values of properties (and possibly trigger attributes creation)
        self.assertEqual(instance.prop_with_default, 10)
        self.assertEqual(instance.prop_without_default, None)
        self.assertEqual(instance.prop_with_checker, None)
        self.assertEqual(instance.prop_with_checker_method, None)
        # Verify that properties storage has been populated with the defaults
        self.assertEqual(sorted(list(instance.properties_storage.keys())),
                         ['an_initial_key', 'header_prop_with_default'])
        self.assertEqual(instance.properties_storage['an_initial_key'], 100)
        self.assertEqual(instance.properties_storage['header_prop_with_default'], 10)

        # Set properties values
        instance.prop_with_default = 'abcde'
        instance.prop_without_default = 36
        instance.prop_with_checker = 'AbCdEfG'
        instance.prop_with_checker_method = 'nopqrsT'
        # Verify that properties storage has been updated with the properties values
        self.assertEqual(sorted(list(instance.properties_storage.keys())),
                         ['an_initial_key', 'header_prop_with_checker',
                          'header_prop_with_checker_method',
                          'header_prop_with_default', 'header_prop_without_default'])
        self.assertEqual(instance.properties_storage['an_initial_key'], 100)
        self.assertEqual(instance.properties_storage['header_prop_with_default'], 'abcde')
        self.assertEqual(instance.properties_storage['header_prop_without_default'], 36)
        self.assertEqual(instance.properties_storage['header_prop_with_checker'], 'abcdefg')
        self.assertEqual(instance.properties_storage['header_prop_with_checker_method'], 'NOPQRST')
        # Check that getter provide the right values
        self.assertEqual(instance.prop_with_default, 'abcde')
        self.assertEqual(instance.prop_without_default, 36)
        self.assertEqual(instance.prop_with_checker, 'abcdefg')
        self.assertEqual(instance.prop_with_checker_method, 'NOPQRST')

        # Reset properties to None or to their default value if a default is defined
        instance.prop_with_default = None
        instance.prop_without_default = None
        instance.prop_with_checker = None
        instance.prop_with_checker_method = None
        # Verify that properties storage has been cleaned
        self.assertEqual(sorted(list(instance.properties_storage.keys())), ['an_initial_key'])
        self.assertEqual(instance.properties_storage['an_initial_key'], 100)
        # Check that the getter provides the right values
        self.assertEqual(instance.prop_with_default, 10)
        self.assertEqual(instance.prop_without_default, None)
        self.assertEqual(instance.prop_with_checker, None)
        self.assertEqual(instance.prop_with_checker_method, None)
