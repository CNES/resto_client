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
from resto_client.generic.user_dirs import user_config_dir, user_download_dir

RESTO_CLIENT_APP_NAME = 'resto_client'
RESTO_CLIENT_APP_AUTHOR = 'CNES'
RESTO_CLIENT_CONFIG_DIR = user_config_dir(app_author=RESTO_CLIENT_APP_AUTHOR,
                                          app_name=RESTO_CLIENT_APP_NAME)

RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR = user_download_dir('resto_client_files', ensure_exists=True)
