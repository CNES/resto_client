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
import atexit
from typing import Iterable
from typing import List  # @UnusedImport
from resto_client.settings.dict_settings import DictSettingsJson

from .resto_client_parameters import RestoClientParameters


def persist_settings(settings: Iterable[DictSettingsJson]) -> None:
    """
    Initialize the settings from file(s) and register their recording at exit time.

    :param settings: an iterable containing settings for the application
    """
    persisted_settings: List[DictSettingsJson] = []

    def _save_settings() -> None:
        """
        Function to save the application settings in a file. To be called once at exit time.
        """
        for setting in persisted_settings:
            if RestoClientParameters.is_debug():
                print(setting)
            setting.save()

    for setting in settings:
        if RestoClientParameters.is_debug():
            print(setting)
        persisted_settings.append(setting)

    atexit.register(_save_settings)
