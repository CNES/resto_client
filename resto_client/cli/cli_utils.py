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

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.services.resto_server import RestoServer
from resto_client.services.resto_service import RestoService
from resto_client.settings.resto_client_parameters import RestoClientParameters


class RestoClientParserError(RestoClientDesignError):
    """
    Exception raised when a parser design error has been detected.
    """


def build_resto_service(args: argparse.Namespace) -> RestoService:
    """
    Build a RestoService instance from parsed arguments, suitable for further processing
    in CLI context.

    :param args: arguments as parsed by ArgParse
    :raises RestoClientParserError: when no server_name specified in the argparse namespace.
    :returns: RestoService instance suitable for further processing in CLI context
    """
    if not hasattr(args, 'server_name'):
        msg = 'Trying to build RestoService without server_name defined in the parsed arguments'
        raise RestoClientParserError(msg)
    server_name = args.server_name
    username = args.username if hasattr(args, 'username') else None
    password = args.password if hasattr(args, 'password') else None

    if server_name is not None:
        resto_server = RestoServer(server_name, username=username, password=password)
        return resto_server.resto_service

    persisted_resto_service = RestoServer.persisted().resto_service
    if username is not None or password is not None:
        persisted_resto_service.auth_service.set_credentials(username=username,
                                                             password=password)
    return persisted_resto_service


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
