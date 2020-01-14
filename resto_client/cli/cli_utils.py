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


from resto_client.services.resto_server import RestoServer

from .resto_client_parameters import RestoClientParameters
from .server_parameters import ServerParameters, RestoClientNoPersistedServer


def build_resto_server(args: Optional[argparse.Namespace] = None) -> RestoServer:
    """
    Build a RestoServer instance from parsed arguments, suitable for further processing
    in CLI context.

    :param args: arguments as parsed by argparse
    :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters and
                                          no server name defined.
    :returns: RestoServer instance suitable for further processing in CLI context
    """
    if args is None:
        server_name = None
        username = None
        password = None
    else:
        server_name = args.server_name if hasattr(args, 'server_name') else None
        username = args.username if hasattr(args, 'username') else None
        password = args.password if hasattr(args, 'password') else None

    try:
        persisted_server_parameters = ServerParameters.persisted()
        if server_name is not None and server_name != persisted_server_parameters.server_name:
            new_server = RestoServer(server_name, username=username, password=password)
            persisted_server_parameters.server_name = server_name  # type: ignore
            return new_server
        # No server name specified or server name corresponds to the persistes server
        persisted_resto_server = persisted_server_parameters.resto_server
        if username is not None or password is not None:
            resto_service = persisted_resto_server.resto_service
            resto_service.auth_service.set_credentials(username=username, password=password)
        return persisted_resto_server
    except RestoClientNoPersistedServer:
        if server_name is None:
            msg = 'No server name specified and no server currently set in the parameters.'
            raise RestoClientNoPersistedServer(msg)
        new_server = RestoServer(server_name, username=username, password=password)
        persisted_server_parameters = ServerParameters(server_name)
        persisted_server_parameters.resto_server = new_server
        return new_server


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
