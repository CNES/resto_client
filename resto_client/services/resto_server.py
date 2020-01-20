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
from typing import Optional, TypeVar, Type

from resto_client.base_exceptions import RestoClientUserError
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.functions.resto_criteria import RestoCriteria
from resto_client.settings.servers_database import DB_SERVERS

from .authentication_service import AuthenticationService
from .resto_service import RestoService

RestoServerType = TypeVar('RestoServerType', bound='RestoServer')


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server
    """

    def __init__(self, server_name: Optional[str] = None) -> None:
        """
        Constructor

        :param server_name: the name of the server to use in the database
        """
        self.authentication_service: Optional[AuthenticationService] = None
        self.resto_service: Optional[RestoService] = None

        self._server_name: Optional[str] = None

        # set server_name which triggers server creation from the database if not None.
        self.server_name = server_name

    @classmethod
    def new_server(cls: Type[RestoServerType],
                   server_name: str,
                   current_collection: Optional[str] = None,
                   username: Optional[str] = None,
                   password: Optional[str] = None,
                   token: Optional[str] = None) -> 'RestoServerType':
        """
        Build a new RestoServer instance from arguments.

        :param server_name: name of the server to build
        :param current_collection: name of the collection to use
        :param username: account to use on this server
        :param password: account password on the server
        :param token: an existing token associated to this account (will be checked prior its use)
        :returns: a new resto server built from arguments and servers database
        """
        server = cls(server_name)
        server.set_credentials(username=username, password=password, token_value=token)
        server.current_collection = current_collection
        return server

    @classmethod
    def build_from_dict(cls: Type[RestoServerType],
                        server_parameters: dict) -> 'RestoServerType':
        """
        Build an instance from a set of parameters defined in a dictionary.

        :param server_parameters: the set of parameters needed for building the server
        :raises KeyError: when no server name is found in the parameters
        :returns: a RestoServer built from server parameters
        """
        # Retrieve the server name in the dictionary
        server_name = server_parameters.get('server_name')
        if server_name is None:
            msg = 'No server name defined in the server parameters.'
            raise KeyError(msg)

        # Retrieve other server parameters in the dictionary
        collection_name = server_parameters.get('current_collection')
        username = server_parameters.get('username')
        token = server_parameters.get('token')

        # Build a new_server with these parameters
        return cls.new_server(server_name, current_collection=collection_name,
                              username=username, token=token)

    def _init_from_db(self, server_name: str) -> None:
        """
        Initialize or reinitialize the server from the servers database

        :param server_name: the name of the server to use in the database
       """
        server_description = DB_SERVERS.get_server(server_name)
        self.authentication_service = AuthenticationService(server_description.auth_access,
                                                            server_name)
        self.resto_service = RestoService(server_description.resto_access,
                                          self.authentication_service, server_name)

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
            server_name = server_name.lower()
            if server_name != self.server_name:
                self._init_from_db(server_name)
                self.current_collection = None
                self.set_credentials(username=None)
        else:
            self.authentication_service = None
            self.resto_service = None
        self._server_name = server_name

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

    def search_current_collection(self, criteria: RestoCriteria) -> RestoFeatureCollection:
        # TODO: change to pass a dict instead of a RestoCriteria and build RestoCriteria internally
        """
        Search the current collection using search criteria
        """
        if self.resto_service is None:
            raise RestoClientUserError('No resto service currently defined.')
        return self.resto_service.search_collection(criteria, self.current_collection)

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}, token: {}'
        return msg_fmt.format(self.server_name, self.current_collection, self.username, self.token)
