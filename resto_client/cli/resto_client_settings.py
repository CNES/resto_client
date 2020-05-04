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
from resto_client.generic.user_dirs import user_download_dir
from resto_client.settings.dict_settings import DictSettingsJson
from resto_client.settings.resto_client_config import RESTO_CLIENT_CONFIG_DIR


RESTO_CLIENT_SETTINGS = DictSettingsJson(RESTO_CLIENT_CONFIG_DIR / 'resto_client_settings.json')

# Process resto_client_settings versions

CURRENT_SETTINGS_VERSION = 'V1'
SETTING_VERSION_KEY = 'settings_version'
if SETTING_VERSION_KEY not in RESTO_CLIENT_SETTINGS:
    # Settings written previously to setting version introduction: delete all of them
    RESTO_CLIENT_SETTINGS.clear()
    RESTO_CLIENT_SETTINGS[SETTING_VERSION_KEY] = CURRENT_SETTINGS_VERSION

if RESTO_CLIENT_SETTINGS[SETTING_VERSION_KEY] != CURRENT_SETTINGS_VERSION:
    # Do some processing here to upgrade the settings to the current version
    # Process sequentially RestoClientParameters and RestoServerPersisted parameters
    pass


RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR = user_download_dir(app_name='resto_client_files',
                                                      ensure_exists=True)
