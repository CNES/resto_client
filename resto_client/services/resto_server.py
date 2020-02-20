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
from pathlib import Path
from typing import Optional, TypeVar, List, Union, Dict, Any

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_criteria import RestoCriteria
from resto_client.entities.resto_criteria_definition import CriteriaDictType
from resto_client.entities.resto_feature import RestoFeature
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.settings.servers_database import DB_SERVERS

from .authentication_service import AuthenticationService
from .resto_service import RestoService


RestoServerType = TypeVar('RestoServerType', bound='RestoServer')


class RestoClientNoRestoService(RestoClientUserError):
    """
    Execption raised by RestoServer when resto service is undefined is undefined
    """

    def __init__(self) -> None:
        super(RestoClientNoRestoService, self).__init__('No resto service currently defined.')


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server or an empty one
    """

    def __init__(self,
                 server_name: str,
                 current_collection: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 token: Optional[str] = None,
                 debug_server: bool = False) -> None:
        """
        Build a new RestoServer instance from arguments and database.

        :param server_name: the name of the server to use in the database
        :param current_collection: name of the collection to use
        :param username: account to use on this server
        :param password: account password on the server
        :param token: an existing token associated to this account (will be checked prior its use)
        :param debug_server: When True debugging information on server and requests is printed out.
        """
        self.debug_server = debug_server
        self._authentication_service: Optional[AuthenticationService] = None
        self._resto_service: Optional[RestoService] = None
        self._server_name: Optional[str] = None

        # set server_name which triggers server creation from the database if not None.
        self.server_name = server_name

        self.current_collection = current_collection
        self.set_credentials(username=username, password=password, token_value=token)

    def _init_from_db(self, server_name: str) -> None:
        """
        Initialize or reinitialize the server from the servers database

        :param server_name: name of the server to retrieve in the database
        """
        server_description = DB_SERVERS.get_server(server_name)
        self._authentication_service = AuthenticationService(server_description.auth_access, self)
        self._resto_service = RestoService(server_description.resto_access,
                                           self._authentication_service, self)

# +++++++++++++++++++++++ server properties section ++++++++++++++++++++++++++++++++++++
    @property
    def server_name(self) -> Optional[str]:
        """
        :returns: the name of the server
        """
        return self._server_name

    @server_name.setter
    def server_name(self, server_name: Optional[str]) -> None:
        if server_name is not None:
            canonical_server_name = DB_SERVERS.check_server_name(server_name)
            if canonical_server_name is not None and canonical_server_name != self._server_name:
                self._init_from_db(canonical_server_name)
                self._server_name = canonical_server_name
                self.current_collection = None  # Not None in case there is a single collection
                self.reset_credentials()
        else:
            self._server_name = None
            self._authentication_service = None
            self._resto_service = None

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the current collection
        """
        if self._resto_service is None:
            return None
        return self._resto_service.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str]) -> None:
        if self._resto_service is not None:
            self._resto_service.current_collection = collection_name

    def set_credentials(self,
                        username: Optional[str]=None,
                        password: Optional[str]=None,
                        token_value: Optional[str]=None) -> None:
        """
        Set the credentials to be used by the authentication service.

        :param username: name of the account on the server
        :param password: account password
        :param token_value: a token associated to these credentials
        """
        if self._authentication_service is not None:
            self._authentication_service.set_credentials(username=username,
                                                         password=password,
                                                         token_value=token_value)

    def reset_credentials(self) -> None:
        """
        Reset the credentials used by the authentication service.
        """
        if self._authentication_service is not None:
            self._authentication_service.reset_credentials()

# +++++++++++ read only properties +++++++++++

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this server
        """
        if self._authentication_service is None:
            return None
        return self._authentication_service.username

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value currently active on this server, or None.
        """
        if self._authentication_service is None:
            return None
        return self._authentication_service.token

# +++++++++++++++++++++++ proxy to resto_service functions ++++++++++++++++++++++++++++++++++++

    def get_supported_criteria(self) -> CriteriaDictType:
        """
        :returns: the supported criteria definition
        """
        if self._resto_service is not None:
            return self._resto_service.get_supported_criteria()
        return RestoCriteria(None).supported_criteria

    def search_by_criteria(self, criteria: Dict[str, Any],
                           collection_name: Optional[str] = None) -> RestoFeatureCollection:
        """
        Search a collection using search criteria

        :param criteria: searching criteria
        :param collection_name: name of the collection to use. Default to the current collection.
        :returns: a collection of resto features
        :raises RestoClientNoRestoService: when the resto service is not initialized
        """
        if self._resto_service is None:
            raise RestoClientNoRestoService()
        return self._resto_service.search_by_criteria(criteria, collection_name)

    def get_features_from_ids(self, features_ids: Union[str, List[str]],
                              collection_name: Optional[str] = None) -> List[RestoFeature]:
        """
        Get a list of resto features retrieved by their identifiers

        :param features_ids: Feature(s) identifier(s)
        :param collection_name: name of the collection to use. Default to the current collection.
        :returns: a list of Resto features
        :raises RestoClientNoRestoService: when the resto service is not initialized
        """
        if self._resto_service is None:
            raise RestoClientNoRestoService()
        features_list = []
        if not isinstance(features_ids, list):
            features_ids = [features_ids]

        for feature_id in features_ids:
            feature = self._resto_service.get_feature_by_id(feature_id, collection_name)
            features_list.append(feature)

        return features_list

    def download_feature_file(self, feature: RestoFeature,
                              file_type: str, download_dir: Path) -> Path:
        """
        Download different files of a feature

        :param feature: a resto feature
        :param download_dir: the path to the directory where download must be done.
        :param file_type: type of file to download: product, quicklook, thumbnail or annexes
        :returns: the path of the downloaded file
        :raises RestoClientNoRestoService: when the resto service is not initialized
        """
        if self._resto_service is None:
            raise RestoClientNoRestoService()
        return self._resto_service.download_feature_file(
            feature, file_type, self.ensure_server_directory(download_dir))

    def download_features_file_from_ids(self,
                                        features_ids: Union[str, List[str]],
                                        file_type: str,
                                        download_dir: Path) -> List[Path]:
        """
        Download different file types from feature id(s)

        :param features_ids: id(s) of the feature(s) which as a file to download
        :param download_dir: the path to the directory where download must be done.
        :param file_type: type of file to download: product, quicklook, thumbnail or annexes
        :returns: the list of downloaded files paths
        """
        # Issue a search request into the collection to retrieve features.
        features = self.get_features_from_ids(features_ids)

        downloaded_file_paths: List[Path] = []
        for feature in features:
            # Do download
            downloaded_file_path = self.download_feature_file(feature, file_type, download_dir)
            downloaded_file_paths.append(downloaded_file_path)
        return downloaded_file_paths

    def ensure_server_directory(self, data_dir: Path) -> Path:
        """
        Build the server data directory path by appending the server name to the provided argument.
        Creates also that directory if it does not exist yet.

        :param data_dir: the directory where the data directory for this server must be located.
        :returns: the path to the server data directory
        :raises RestoClientDesignError: when called while this server parameters are undefined.
        """
        if self.server_name is None:
            raise RestoClientDesignError('cannot ensure data_dir when RestoServer is undefined')
        real_data_dir = data_dir / self.server_name
        real_data_dir.mkdir(parents=True, exist_ok=True)
        return real_data_dir

    def show_server(self, with_stats: bool=True) -> str:
        """
        :param  with_stats: if True the collections statistics are shown.
        :returns: The server description as a tabulated listing
        :raises RestoClientNoRestoService: when the resto service is not initialized
        """
        if self._resto_service is None:
            raise RestoClientNoRestoService()
        return self._resto_service.show(with_stats=with_stats)

    def get_collection(self, collection: Optional[str]=None) -> RestoCollection:
        """
        Get a collection description from the resto service.

        :param collection: the name of the collection to retrieve
        :returns: the requested collection or the current one.
        :raises RestoClientNoRestoService: when the resto service is not initialized.
        """
        if self._resto_service is None:
            raise RestoClientNoRestoService()
        return self._resto_service.get_collection(collection=collection)

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}, token: {}'
        return msg_fmt.format(self._server_name, self.current_collection, self.username, self.token)
