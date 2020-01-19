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
from resto_client.services.resto_server import RestoServer

from .resto_client_parameters import RestoClientParameters
from .resto_client_settings import RESTO_CLIENT_SETTINGS
from .resto_server_parameters import RestoServerParameters, RestoClientNoPersistedServer


def build_resto_server_parameters(args: Optional[argparse.Namespace] = None
                                  ) -> RestoServerParameters:
    """
    Build a RestoServerParameters instance from parsed arguments and persisted parameters, suitable
    for further processing in CLI context.

    :param args: arguments as parsed by argparse
    :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters and
                                          no server name defined.
    :raises RestoClientUserError: when arguments are inconsistent with persisted parameters.
    :returns: RestoServerParameters instance suitable for further processing in CLI context
    """
    if args is None:
        server_name = None
        username = None
        password = None
        collection_name = None
    else:
        server_name = args.server_name if hasattr(args, 'server_name') else None
        username = args.username if hasattr(args, 'username') else None
        password = args.password if hasattr(args, 'password') else None
        collection_name = args.collection_name if hasattr(args, 'collection_name') else None
    try:
        server_parameters = RestoServerParameters.persisted(RESTO_CLIENT_SETTINGS)
        if server_name is not None and server_name != server_parameters.server_name:
            # Persisted server does not fit requested server. Drop it.
            raise RestoClientNoPersistedServer()

        if collection_name is not None:
            # ensure to delete previous collection in case it was equal to this one
            server_parameters.current_collection = None  # type: ignore
            server_parameters.current_collection = collection_name  # type: ignore

        if username is not None or password is not None:
            if username is not None:
                # ensure to delete previous username in case it was equal to this one
                server_parameters.username = None  # type: ignore
                server_parameters.username = username  # type: ignore
            resto_service = server_parameters.resto_server.resto_service
            resto_service.auth_service.set_credentials(username=username, password=password)

    except RestoClientNoPersistedServer:
        # No persisted server or persisted one does not fit requested server_name
        if server_name is None:
            msg = 'No server name specified and no server currently set in the parameters.'
            raise RestoClientNoPersistedServer(msg)
        server_parameters = _new_server_parameters(server_name, collection_name, username, password)

    except RestoClientUserError:
        raise

    except Exception as excp:
        print('other problem when dealing with persistence : {}'.format(str(excp)))

    return server_parameters


def _new_server_parameters(server_name: str,
                           collection_name: Optional[str] = None,
                           username: Optional[str] = None,
                           password: Optional[str] = None) -> RestoServerParameters:
    """
    Build a new RestoServer instance from arguments, suitable for further processing
    in CLI context.

    :param server_name: name of the server to build
    :param collection_name: name of the collection to use
    :param username: account to use on this server
    :param password: account password on the server
    :returns: RestoServer instance suitable for further processing in CLI context
    """
    new_server = RestoServer(server_name, username=username, password=password)
    server_parameters = RestoServerParameters(server_name)
    if collection_name is None:
        # Use current_collection from the new server (None or collection name is there is only one).
        collection_name = new_server.current_collection  # type: ignore
    server_parameters.current_collection = collection_name  # type: ignore

    return server_parameters


def build_resto_client_params(args: argparse.Namespace) -> RestoClientParameters:
    """
    Build a RestoClientParameters instance from parsed arguments, suitable for further processing
    in CLI context.

    :param args: arguments as parsed by ArgParse
    :returns: a RestoClientParameters instance, suitable for further processing in CLI context.
    """
    download_dir = args.download_dir if hasattr(args, 'download_dir') else None
    region = args.region if hasattr(args, 'region') else None
    verbosity = args.verbosity if hasattr(args, 'verbosity') else None

    return RestoClientParameters(download_dir=download_dir, region=region, verbosity=verbosity)
