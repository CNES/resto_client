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
from abc import abstractmethod
import atexit
from typing import Iterable, Optional, Callable
from typing import List  # @UnusedImport

from resto_client.settings.dict_settings import DictSettingsJson
from resto_client.settings.resto_client_config import resto_client_print


def persist_settings(settings: Iterable[DictSettingsJson],
                     print_settings: Optional[bool] = False,
                     last_chance_update_func: Optional[Callable] = None) -> None:
    """
    Initialize the settings from file(s) and register their recording at exit time.

    :param settings: an iterable containing settings for the application
    :param last_chance_update_func: called at exit time with the settings as parameter
    :param print_settings: flag to print the settings either at load or at save time
    """
    persisted_settings: List[DictSettingsJson] = []

    def _save_settings() -> None:
        """
        Function to save the application settings in a file. To be called once at exit time.
        """
        for setting in persisted_settings:
            if last_chance_update_func is not None:
                last_chance_update_func(setting)
            if print_settings:
                resto_client_print(setting)
            setting.save()

    for setting in settings:
        if print_settings:
            resto_client_print(setting)
        persisted_settings.append(setting)

    atexit.register(_save_settings)


class PersistedAttributes():
    """
    A class for persisting declared attributes of inheriting classes
    """

    @property
    @abstractmethod
    def persisted_attributes(self) -> List[str]:
        """
        :returns: the attributes to persist, defined at the inheriting class level.
        """

    def update_persisted(self, persisted_params: dict) -> None:
        """
        Update the dictionary given as argument by recording the (attribute_name, attribute_value)
        pairs in it or removing the attribute_name entry if attribute_value is  None.

        :param persisted_params: dictionary to update with peristed attributes
        """
        for attr_name in self.persisted_attributes:
            persisted_params[attr_name] = getattr(self, attr_name)
            if persisted_params[attr_name] is None:
                del persisted_params[attr_name]
