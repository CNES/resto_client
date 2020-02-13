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
# Names of the arguments as found in argparse.NameSpace after parsing

# Arguments persisted by RestoClientParameters
DIRECTORY_ARGNAME = 'download_dir'
REGION_ARGNAME = 'region'
VERBOSITY_ARGNAME = 'verbosity'

# Arguments persisted by RestoServerPersisted
SERVER_ARGNAME = 'server_name'
ACCOUNT_ARGNAME = 'username'
PASSWORD_ARGNAME = 'password'
COLLECTION_ARGNAME = 'collection_name'

# Arguments for configure_server
RESTO_URL_ARGNAME = 'resto_url'
RESTO_PROTOCOL_ARGNAME = 'resto_protocol'
AUTH_URL_ARGNAME = 'auth_url'
AUTH_PROTOCOL_ARGNAME = 'auth_protocol'

# Arguments for feature(s)
FEATURES_IDS_ARGNAME = 'feature_id'

# Argument for show
WITH_STATS_ARGNAME = 'stats'
NO_STATS_ARGNAME = 'nostats'

# Arguments for search
CRITERIA_ARGNAME = 'criteria'
MAXRECORDS_ARGNAME = 'maxrecords'
PAGE_ARGNAME = 'page'
DOWNLOAD_ARGNAME = 'download'
JSON_ARGNAME = 'save_json'

# Arguments for download
DOWNLOAD_TYPE_ARGNAME = 'download_type'
