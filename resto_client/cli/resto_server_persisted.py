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
import argparse
from typing import Dict, Any  # @UnusedImport
from typing import Optional

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.parser.parser_settings import (SERVER_ARGNAME, ACCOUNT_ARGNAME,
                                                     PASSWORD_ARGNAME, COLLECTION_ARGNAME)
from resto_client.services.resto_server import RestoServer
from resto_client.settings.servers_database import DB_SERVERS

from .cli_utils import get_from_args
from .persistence import PersistedAttributes
from .resto_client_settings import RESTO_CLIENT_SETTINGS


COLLECTION_KEY = 'current_collection'
SERVER_KEY = 'server_name'
TOKEN_KEY = 'token'
USERNAME_KEY = 'username'
PASSWORD_KEY = 'password'


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServerPersisted(RestoServer, PersistedAttributes):
    """
    A class for building a RestoServer whose parameters can be persisted
    """

    persisted_attributes = [COLLECTION_KEY, SERVER_KEY, TOKEN_KEY, USERNAME_KEY]

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
        super(RestoServerPersisted, self).__init__(server_name,
                                                   current_collection=current_collection,
                                                   username=username,
                                                   password=password,
                                                   token=token,
                                                   debug_server=debug_server)
        self.server_on = True

    def switch_off(self) -> None:
        """
        Switch off the server. After calling this method the persisted fields are reset to None.
        """
        self.server_on = False

# +++++++++++++++++++++++ persisted server properties section ++++++++++++++++++++++++++++++++++++

    @property
    def server_name(self) -> Optional[str]:  # type:ignore
        """
        :returns: the name of the server
        """
        return self._server_name if self.server_on else None

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the current collection
        """
        return self._resto_service.current_collection if self.server_on else None

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str]) -> None:
        self._resto_service.current_collection = collection_name

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this server
        """
        return self._authentication_service.username if self.server_on else None

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value currently active on this server, or None.
        """
        return self._authentication_service.token if self.server_on else None

    @classmethod
    def build_from_defaults(cls,
                            default_params: dict,
                            server_name: Optional[str] = None,
                            current_collection: Optional[str] = None,
                            username: Optional[str] = None,
                            password: Optional[str] = None,
                            debug_server: bool=False) -> 'RestoServerPersisted':
        """
        Build a RestoServer instance from default parameters and arguments.

        :param default_params: a dictionary containing default server parameters
        :param server_name: name of the server to build
        :param current_collection: name of the collection to use
        :param username: account to use on this server
        :param password: account password on the server
        :param debug_server: When True debugging information on server and requests is printed out.
        :returns: RestoServer instance suitable for further processing in CLI context
        :raises KeyError: when no server name can be found in the defaults or the arguments
        """
        if server_name is not None:
            server_name = DB_SERVERS.check_server_name(server_name)
        default_server_name = default_params.get(SERVER_KEY)
        if default_server_name is not None:
            default_server_name = DB_SERVERS.check_server_name(default_server_name)
        if server_name is None and default_server_name is None:
            raise KeyError('Requested server name is None and no default server specified')

        server_parameters: Dict[str, Any] = {'debug_server': debug_server}
        if server_name is not None and default_server_name is not None:
            # Both server names are available. Choose to build one of them.
            if server_name != default_server_name:
                # Requested server name is different from default.
                # Build from requested server name without using any default.
                server_parameters[SERVER_KEY] = server_name
            else:
                # Requested server name is the same than the default
                # Build from default parameters in order to keep all of them.
                server_parameters.update(default_params)
        elif server_name is None:
            # No requested server name but a server name is present in the default
            # Build from default parameters in order to keep all of them.
            server_parameters.update(default_params)
        else:
            # Requested server name and no significant default server.
            # Build from requested server name without using any default.
            server_parameters[SERVER_KEY] = server_name

        # Update current_collection if specified
        if current_collection is not None:
            server_parameters[COLLECTION_KEY] = current_collection
        # Create server from parameters
        server = RestoServerPersisted(**server_parameters)
        # Update credentials if specified
        if username is not None or password is not None:
            server.set_credentials(username=username, password=password)
        return server

    @classmethod
    def build_from_argparse(cls, args: Optional[argparse.Namespace] = None,
                            debug_server: bool=False) -> 'RestoServerPersisted':
        """
        Build a RestoServerPersisted instance from arguments provided by argparse and persisted
        parameters, suitable for further processing in CLI context.

        :param args: arguments as parsed by argparse
        :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters
                                              and no server name defined.
        :param debug_server: When True debugging information on server and requests is printed out.
        :returns: a RestoServer instance suitable for further processing in CLI context
        """
        server_name = get_from_args(SERVER_ARGNAME, args)
        username = get_from_args(ACCOUNT_ARGNAME, args)
        password = get_from_args(PASSWORD_ARGNAME, args)
        collection_name = get_from_args(COLLECTION_ARGNAME, args)

        persisted_server_args = dict((key, RESTO_CLIENT_SETTINGS[key])
                                     for key in cls.persisted_attributes
                                     if key in RESTO_CLIENT_SETTINGS)
        try:
            server = cls.build_from_defaults(persisted_server_args,
                                             server_name=server_name,
                                             current_collection=collection_name,
                                             username=username,
                                             password=password,
                                             debug_server=debug_server)

        except KeyError:
            # No persisted server or persisted one does not fit requested server_name
            msg = 'No persisted server and {} is not a valid server name.'.format(server_name)
            raise RestoClientNoPersistedServer(msg)

        return server

    @classmethod
    def get_persisted_server_name(cls) -> Optional[str]:
        """

        :returns: the name of the persisted server or None if no persisted server
        """
        return RESTO_CLIENT_SETTINGS.get(SERVER_KEY)
