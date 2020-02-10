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


resto_client Command Line Interface (CLI)

Implemented commands (without options):

SET:
    > resto_client set server <server_url> ...
    > resto_client set account <account_id> ...
    > resto_client set collection <collection> ...

UNSET:
    > resto_client unset server
    > resto_client unset account
    > resto_client unset collection

SHOW:
    > resto_client show collections ...
    > resto_client show collection <collection> ...
    > resto_client show feature <collection> <feature_id> ...

DOWNLOAD:
    > resto_client download product <collection> <feature_id> ...
    > resto_client download quicklook <collection> <feature_id> ...
    > resto_client download thumbnail <collection> <feature_id> ...
    > resto_client download annexes <collection> <feature_id> ...

SEARCH:
    > resto_client search <collection> ...


Expected commands (without options):

    TBD
"""
import sys
from typing import Sequence, Optional  # @NoMove

from colorama import Fore, Style, colorama_text

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.parser.resto_client_parser import build_parser
from resto_client.cli.persistence import persist_settings
from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.settings.resto_client_config import resto_client_print


def resto_client_run(arguments: Optional[Sequence[str]]=None) -> None:
    """
    Command line interface to access collections from resto.

    :param arguments: list of arguments
    :raises RestoClientUserError: when in debug mode to check the whole exception.
    """
    arg_parser = build_parser()

    args = arg_parser.parse_args(args=arguments)

    if hasattr(args, 'func'):
        try:
            client_params, resto_server = args.func(args)
            # Retrieve client and server parameters to be persisted before exiting.
            if client_params is not None:
                client_params.update_persisted(RESTO_CLIENT_SETTINGS)
            if resto_server is not None:
                resto_server.update_persisted(RESTO_CLIENT_SETTINGS)
        except RestoClientUserError as excp:
            # Print a clean message for exceptions generated by resto_client itself,
            # except for debug.
            if RestoClientParameters.is_verbose():
                raise
            with colorama_text():
                resto_client_print(Fore.RED + Style.BRIGHT + str(excp) + Style.RESET_ALL)


def main(arguments: Optional[Sequence[str]]=None) -> None:
    """
    Command line interface to access collections from resto.

    :param arguments: list of arguments
    """
    persist_settings([RESTO_CLIENT_SETTINGS], RestoClientParameters.is_debug())
    resto_client_run(arguments=arguments)


if __name__ == "__main__":
    sys.exit(main())  # type: ignore
