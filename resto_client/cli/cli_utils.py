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
from typing import Optional

from resto_client.base_exceptions import RestoClientUserError

from .parser.parser_settings import (CLI_SERVER_NAME, CLI_USERNAME, CLI_PASSWORD,
                                     CLI_COLLEC_NAME, CLI_DIR_NAME, CLI_REGION_NAME,
                                     CLI_VERBOSITY)
from .resto_client_parameters import RestoClientParameters
from .resto_client_settings import RESTO_CLIENT_SETTINGS, SERVER_KEY
from .resto_server_persistable import RestoServerPersistable, RestoClientNoPersistedServer


def build_resto_server_persistable(args: Optional[argparse.Namespace] = None
                                   ) -> RestoServerPersistable:
    """
    Build a RestoServerPersistable instance from parsed arguments and persisted parameters, suitable
    for further processing in CLI context.

    :param args: arguments as parsed by argparse
    :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters and
                                          no server name defined.
    :raises RestoClientUserError: when arguments are inconsistent with persisted parameters.
    :returns: a RestoServer instance suitable for further processing in CLI context
    """
    if args is None:
        server_name = None
        username = None
        password = None
        collection_name = None
    else:
        server_name = getattr(args, CLI_SERVER_NAME) if hasattr(args, CLI_SERVER_NAME) else None
        username = getattr(args, CLI_USERNAME) if hasattr(args, CLI_USERNAME) else None
        password = getattr(args, CLI_PASSWORD) if hasattr(args, CLI_PASSWORD) else None
        collection_name = getattr(args, CLI_COLLEC_NAME) if hasattr(args, CLI_COLLEC_NAME) else None
    try:
        server = build_persisted_server(server_name=server_name, collection_name=collection_name,
                                        username=username, password=password)

    except RestoClientNoPersistedServer:
        # No persisted server or persisted one does not fit requested server_name
        if server_name is None:
            msg = 'No server name specified and no server currently set in the parameters.'
            raise RestoClientNoPersistedServer(msg)
        server = RestoServerPersistable.new_server(server_name=server_name,
                                                   current_collection=collection_name,
                                                   username=username, password=password)

    except RestoClientUserError:
        raise

    except Exception as excp:
        print('other problem when dealing with persistence : {}'.format(str(excp)))

    return server


def build_persisted_server(server_name: Optional[str] = None,
                           collection_name: Optional[str] = None,
                           username: Optional[str] = None,
                           password: Optional[str] = None) -> RestoServerPersistable:
    """
    Build a RestoServer instance from arguments and perisited parameters,
    suitable for further processing in CLI context.

    :param server_name: name of the server to build
    :param collection_name: name of the collection to use
    :param username: account to use on this server
    :param password: account password on the server
    :returns: RestoServer instance suitable for further processing in CLI context
    :raises RestoClientNoPersistedServer: when no persisted server can be found
    """
    # Firstly discard the case where a server is persisted and is not the requested server
    persisted_server_name = RESTO_CLIENT_SETTINGS.get(SERVER_KEY)
    if server_name is not None and persisted_server_name is not None:
        if server_name.lower() != persisted_server_name.lower():
            # Persisted server does not fit requested server. Drop it.
            raise RestoClientNoPersistedServer()

    # build the server from the persisted parameters
    try:
        server = RestoServerPersistable.build_from_dict(RESTO_CLIENT_SETTINGS)
    except KeyError:
        raise RestoClientNoPersistedServer()

    # update the server with parameters specified as arguments
    if collection_name is not None:
        server.current_collection = collection_name
    if username is not None or password is not None:
        server.set_credentials(username=username, password=password)
    return server


def build_resto_client_params(args: argparse.Namespace) -> RestoClientParameters:
    """
    Build a RestoClientParameters instance from parsed arguments, suitable for further processing
    in CLI context.

    :param args: arguments as parsed by ArgParse
    :returns: a RestoClientParameters instance, suitable for further processing in CLI context.
    """
    download_dir = getattr(args, CLI_DIR_NAME) if hasattr(args, CLI_DIR_NAME) else None
    region = getattr(args, CLI_REGION_NAME) if hasattr(args, CLI_REGION_NAME) else None
    verbosity = getattr(args, CLI_VERBOSITY) if hasattr(args, CLI_VERBOSITY) else None

    return RestoClientParameters(download_dir=download_dir, region=region, verbosity=verbosity)
