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
from resto_client.settings.dict_settings import DictSettingsJson
from resto_client.settings.resto_client_config import RESTO_CLIENT_CONFIG_DIR


RESTO_CLIENT_SETTINGS = DictSettingsJson(RESTO_CLIENT_CONFIG_DIR / 'resto_client_settings.json')

# persisted attributes from different classes are listed here, as versions updating reminders.
DOWNLOAD_DIR_KEY = 'download_dir'
REGION_KEY = 'region'
VERBOSITY_KEY = 'verbosity'
PERSISTED_CLIENT_PARAMETERS = [DOWNLOAD_DIR_KEY, REGION_KEY, VERBOSITY_KEY]

COLLECTION_KEY = 'current_collection'
SERVER_KEY = 'server_name'
TOKEN_KEY = 'token'
USERNAME_KEY = 'username'
PERSISTED_SERVER_PARAMETERS = [COLLECTION_KEY, SERVER_KEY, TOKEN_KEY, USERNAME_KEY]

# Process resto_client_settings versions

# Settings written previously to setting version introduction
if 'settings_version' not in RESTO_CLIENT_SETTINGS:
    RESTO_CLIENT_SETTINGS['settings_version'] = 'V0'

if RESTO_CLIENT_SETTINGS['settings_version'] == 'V0':
    if 'auth_base_url' in RESTO_CLIENT_SETTINGS:
        del RESTO_CLIENT_SETTINGS['auth_base_url']
    if 'auth_protocol' in RESTO_CLIENT_SETTINGS:
        del RESTO_CLIENT_SETTINGS['auth_protocol']
    if 'resto_base_url' in RESTO_CLIENT_SETTINGS:
        del RESTO_CLIENT_SETTINGS['resto_base_url']
    if 'resto_protocol' in RESTO_CLIENT_SETTINGS:
        del RESTO_CLIENT_SETTINGS['resto_protocol']
    RESTO_CLIENT_SETTINGS['settings_version'] = 'V1'
# TODO: FInish V0->V1 upgrade
