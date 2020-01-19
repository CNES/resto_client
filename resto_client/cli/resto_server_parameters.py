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

from resto_client.base_exceptions import RestoClientUserError
from resto_client.services.resto_server import RestoServer


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServerParameters():
    """
    A class holding the persisted server parameters
    """

    def __init__(self, server_name: str) -> None:
        """
        Constructor

        :param server_name: the name of the server.
        """
        server_name = server_name.lower()
        self.resto_server = RestoServer(server_name)
        self._server_name: Optional[str] = server_name

    @classmethod
    def persisted(cls, persisted_params: dict) -> 'RestoServerParameters':
        """
        Build an instance from the persisted server parameters.

        :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters
        :returns: an instance of RestoServerParameters built from persisted parameters
        """
        # Retrieve persisted server name and build an empty server parameters instance
        persisted_server_name = persisted_params.get('server_name')
        if persisted_server_name is None:
            msg = 'No server currently set in the persisted parameters.'
            raise RestoClientNoPersistedServer(msg)
        persisted_server_parameters = cls(persisted_server_name)

        # Retrieve persisted collection name
        persisted_collection_name = persisted_params.get('current_collection')
        # Update server parameters instance to trigger RestoServer update.
        persisted_server_parameters.current_collection = persisted_collection_name

        # Retrieve persisted username
        persisted_username = persisted_params.get('username')
        # Update server parameters instance to trigger RestoServer update.
        persisted_server_parameters.username = persisted_username

        return persisted_server_parameters

    @property
    def server_name(self) -> Optional[str]:
        """
        :returns: the name of the server
        """
        return self._server_name

    @server_name.setter
    def server_name(self, server_name: Optional[str]) -> None:
        if server_name is None:
            self.current_collection = None
            self.username = None
        else:
            server_name = server_name.lower()
            if server_name != self._server_name:
                self.resto_server = RestoServer(server_name)
                self.current_collection = None
                self.username = None
        self._server_name = server_name

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the name of the current collection
        """
        return self.resto_server.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: str) -> None:
        self.resto_server.current_collection = collection_name

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this server
        """
        return self.resto_server.username

    @username.setter
    def username(self, username: Optional[str]) -> None:
        self.resto_server.set_credentials(username=username)

    def update_persisted(self, persisted_params: dict) -> None:
        self._update_persisted_attr(persisted_params, 'server_name')
        self._update_persisted_attr(persisted_params, 'current_collection')
        self._update_persisted_attr(persisted_params, 'username')

    def _update_persisted_attr(self, persisted_params: dict, attr_name: str) -> None:
        persisted_params[attr_name] = getattr(self, attr_name)
        if persisted_params[attr_name] is None:
            del persisted_params[attr_name]

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}'
        return msg_fmt.format(self.server_name, self.current_collection, self.username)
