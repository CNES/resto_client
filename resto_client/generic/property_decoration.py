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
import functools
from typing import Callable, Optional


def managed_getter(default: Optional[object]=None) -> Callable:
    """
    This function is a decorator which decorates another function, that is intended to be used as
    the true decorator.
    This trick is mandatory to allow passing parameters when used in conjunction with property
    decorators.

    :param object default: the default value to return when the property is None or does not exist.
    :returns: the decorator
    """

    def managed_getter_decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(instance: object) -> object:
            properties_storage = get_properties_storage(instance)
            key = get_internal_prop_name(instance, func)
            stored_value = properties_storage.get(key)
            if stored_value is not None:
                return stored_value
            if default is not None:
                properties_storage[key] = default
            return default
        return wrapper

    return managed_getter_decorator


def managed_setter(pre_set_func: Optional[Callable]=None) -> Callable:
    """
    This function is a decorator which decorates another function, that is intended to be used as
    the true decorator.
    This trick is mandatory to allow passing parameters when used in conjunction with property
    decorators.

    :param function pre_set_func: a function or method to normalize and check the provided value.
    :raises TypeError: if pre_set_func is not callable.
    :returns: a decorator
    """
    if pre_set_func is not None:
        if not isinstance(pre_set_func, str) and not callable(pre_set_func):
            msg = 'managed_setter pre_set_func argument must be a callable or the name of'\
                ' an instance method attribute.'
            raise TypeError(msg)

    def managed_setter_decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(instance: object, value: object) -> None:
            # Manage call to check function when defined
            if value is not None and pre_set_func is not None:
                if isinstance(pre_set_func, str):
                    real_pre_func = getattr(instance, pre_set_func)
                else:
                    real_pre_func = pre_set_func
                value = real_pre_func(value)

            # Retrieve storage information
            properties_storage = get_properties_storage(instance)
            key = get_internal_prop_name(instance, func)

            # Set value in storage
            previous_value = properties_storage.get(key)
            if value is None and key in properties_storage:
                del properties_storage[key]
            if value is not None:
                properties_storage[key] = value

            # If value has changed call the post_set function
            if value != previous_value:
                # Call the true setter to finalize value change.
                func(instance, value)
        return wrapper

    return managed_setter_decorator


def get_internal_prop_name(instance: object, func: Callable) -> str:
    """
    Build the name to use for storing the value of a property of an object.

    The internal property name is based on the function name (i.e. the decorated property name).
    If the object has an instance or class attribute named 'properties_name_prefix', the value of
    this attribute is extended by an underscore, and used as a prefix of the function name.

    :param instance: the instance of some class in which the property is living.
    :param function func: the function wrapping the property
    :returns: the property internal name
    """
    property_name = func.__name__
    prefix_attr_name = 'properties_name_prefix'
    try:
        prefix = getattr(instance, prefix_attr_name) + '_'
    except AttributeError:
        prefix = ''
    return '{}{}'.format(prefix, property_name)


def get_properties_storage(instance: object) -> dict:
    """
    Returns the dictionary into which the managed properties are recorded.

    If the object has an instance or class attribute named 'properties_storage', the value of
    this attribute is used as the storage for managed properties, provided that it is a dict.
    Otherwise an instance attribute with that name is created with an empty dictionary as its value.

    :param  instance: the instance of some class in which the property is living.
    :returns: the properties storage dictionary
    """
    storage_attr_name = 'properties_storage'
    try:
        storage = getattr(instance, storage_attr_name)
    except AttributeError:
        setattr(instance, storage_attr_name, {})
        storage = getattr(instance, storage_attr_name)
    return storage
