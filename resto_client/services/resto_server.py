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
from typing import Optional

from resto_client.settings.servers_database import DB_SERVERS

from .authentication_service import AuthenticationService
from .resto_service import RestoService


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server
    """

    def __init__(self, server_name: str) -> None:
        """
        Constructor

        :param server_name: the name of the server to use in the database
        """
        server_description = DB_SERVERS.get_server(server_name)
        self.authentication_service = AuthenticationService(server_description.auth_access,
                                                            server_name)
        self.resto_service = RestoService(server_description.resto_access,
                                          self.authentication_service, server_name)
        self.server_name = server_name

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the current collection
        """
        return self.resto_service.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str]) -> None:
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
        self.authentication_service.set_credentials(username=username,
                                                    password=password,
                                                    token_value=token_value)

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this server
        """
        return self.authentication_service.username

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value currently active on this server, or None.
        """
        return self.authentication_service.token

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}, token: {}'
        return msg_fmt.format(self.server_name, self.current_collection, self.username, self.token)
