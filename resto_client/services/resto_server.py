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
from typing import Optional, TypeVar, Type, List, Union, Dict, Any

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_criteria import RestoCriteria, CriteriaDictType
from resto_client.entities.resto_feature import RestoFeature
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.settings.servers_database import DB_SERVERS, ServersDatabase

from .authentication_service import AuthenticationService
from .resto_service import RestoService


RestoServerType = TypeVar('RestoServerType', bound='RestoServer')


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server
    """

    # FIXME: Remove optionality on server_nam, when parser_search will not need it anymore.
    def __init__(self, server_name: Optional[str] = None, debug_server: bool = False) -> None:
        """
        Constructor

        :param server_name: the name of the server to use in the database
        :param debug_server: When True debugging information on server and requests is printed out.
        """
        self.debug_server = debug_server
        self.authentication_service: Optional[AuthenticationService] = None
        self.resto_service: Optional[RestoService] = None
        self._server_name: Optional[str] = None

        # set server_name which triggers server creation from the database if not None.
        self.server_name = server_name

    # TODO: rename this class method
    @classmethod
    def new_server(cls: Type[RestoServerType],
                   server_name: str,
                   current_collection: Optional[str] = None,
                   username: Optional[str] = None,
                   password: Optional[str] = None,
                   token: Optional[str] = None,
                   debug_server: bool = False) -> 'RestoServerType':
        """
        Build a new RestoServer instance from arguments.

        :param server_name: name of the server to build
        :param current_collection: name of the collection to use
        :param username: account to use on this server
        :param password: account password on the server
        :param token: an existing token associated to this account (will be checked prior its use)
        :param debug_server: When True debugging information on server and requests is printed out.
        :returns: a new resto server built from arguments and servers database
        """
        server = cls(server_name, debug_server)
        server.current_collection = current_collection
        server.set_credentials(username=username, password=password, token_value=token)
        return server

    def _init_from_db(self) -> None:
        """
        Initialize or reinitialize the server from the servers database
        """
        if self.server_name is None:
            raise RestoClientDesignError('Tring to initialize a server from DB without its name')
        server_description = DB_SERVERS.get_server(self.server_name)
        self.authentication_service = AuthenticationService(server_description.auth_access, self)
        self.resto_service = RestoService(server_description.resto_access,
                                          self.authentication_service, self)

# +++++++++++++++++++++++ server properties section ++++++++++++++++++++++++++++++++++++
    @property
    def server_name(self) -> Optional[str]:
        """
        :returns: the name of the server
        """
        return self._server_name

    @server_name.setter
    def server_name(self, server_name: Optional[str]) -> None:
        server_name = ServersDatabase.get_canonical_name(server_name)
        if server_name is not None:
            if server_name != self.server_name:
                self._server_name = server_name
                self._init_from_db()
                self.current_collection = None
                self.reset_credentials()
        else:
            self._server_name = None
            self.authentication_service = None
            self.resto_service = None

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the current collection
        """
        if self.server_name is None or self.resto_service is None:
            return None
        return self.resto_service.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str]) -> None:
        if self.resto_service is not None:
            self.resto_service.current_collection = collection_name

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
        if self.authentication_service is not None:
            self.authentication_service.set_credentials(username=username,
                                                        password=password,
                                                        token_value=token_value)

    def reset_credentials(self) -> None:
        """
        Reset the credentials used by the authentication service.
        """
        if self.authentication_service is not None:
            self.authentication_service.reset_credentials()

# +++++++++++ read only properties +++++++++++

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this server
        """
        if self.server_name is None or self.authentication_service is None:
            return None
        return self.authentication_service.username

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value currently active on this server, or None.
        """
        if self.server_name is None or self.authentication_service is None:
            return None
        return self.authentication_service.token

# +++++++++++++++++++++++ proxy to resto_service functions ++++++++++++++++++++++++++++++++++++

    def get_supported_criteria(self) -> CriteriaDictType:
        """
        :returns: the supported criteria definition
        """
        if self.resto_service is not None:
            return self.resto_service.get_supported_criteria()
        return RestoCriteria(None).supported_criteria

    def search_by_criteria(self, criteria: Dict[str, Any],
                           collection_name: Optional[str] = None) -> RestoFeatureCollection:
        """
        Search a collection using search criteria

        :param criteria: searching criteria
        :param collection_name: name of the collection to use. Default to the current collection.
        :returns: a collection of resto features
        :raises RestoClientUserError: when the resto service is not initialized
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        return self.resto_service.search_by_criteria(criteria, collection_name)

    def get_features_from_ids(self, features_ids: Union[str, List[str]],
                              collection_name: Optional[str] = None) -> List[RestoFeature]:
        """
        Get a list of resto features retrieved by their identifiers

        :param features_ids: Feature(s) identifier(s)
        :param collection_name: name of the collection to use. Default to the current collection.
        :returns: a list of Resto features
        :raises RestoClientUserError: when the resto service is not initialized
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        features_list = []
        if not isinstance(features_ids, list):
            features_ids = [features_ids]

        for feature_id in features_ids:
            feature = self.resto_service.get_feature_by_id(feature_id, collection_name)
            features_list.append(feature)

        return features_list

    def download_feature_file(self, feature: RestoFeature,
                              file_type: str, download_dir: Path) -> Optional[str]:
        """
        Download different files of a feature

        :param feature: a resto feature
        :param download_dir: the path to the directory where download must be done.
        :param file_type: type of file to download: product, quicklook, thumbnail or annexes
        :returns: the path of the downloaded file
        :raises RestoClientUserError: when the resto service is not initialized
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        return self.resto_service.download_feature_file(feature, file_type, download_dir)

    def download_features_file_from_ids(self,
                                        features_ids: Union[str, List[str]],
                                        file_type: str,
                                        download_dir: Path) -> List[str]:
        """
        Download different file types from feature id(s)

        :param features_ids: id(s) of the feature(s) which as a file to download
        :param download_dir: the path to the directory where download must be done.
        :param file_type: type of file to download: product, quicklook, thumbnail or annexes
        :returns: the list of downloaded files paths
        """
        # Issue a search request into the collection to retrieve features.
        features = self.get_features_from_ids(features_ids)

        downloaded_filenames: List[str] = []
        for feature in features:
            # Do download
            downloaded_filename = self.download_feature_file(feature, file_type, download_dir)
            if downloaded_filename is not None:
                downloaded_filenames.append(downloaded_filename)
        return downloaded_filenames

    def show_server(self, with_stats: bool=True) -> str:
        """
        :param  with_stats: if True the collections statistics are shown.
        :returns: The server description as a tabulated listing
        :raises RestoClientUserError: when the resto service is not initialized
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        return self.resto_service.show(with_stats=with_stats)

    def get_collection(self, collection: Optional[str]=None) -> RestoCollection:
        """
        Get a collection description from the resto service.

        :param collection: the name of the collection to retrieve
        :returns: the requested collection or the current one.
        :raises RestoClientUserError: if collection is None and no current collection defined.
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        return self.resto_service.get_collection(collection=collection)

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}, token: {}'
        return msg_fmt.format(self.server_name, self.current_collection, self.username, self.token)
