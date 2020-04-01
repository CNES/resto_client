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
from argparse import Namespace, RawDescriptionHelpFormatter
import argparse
from copy import deepcopy
from pathlib import Path
from typing import Optional, Dict, Any  # @UnusedImport @NoMove

from colorama import Fore, Style, colorama_text
from prettytable import PrettyTable

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.cli_utils import get_from_args
from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.cli.resto_server_persisted import RestoServerPersisted
from resto_client.entities.resto_criteria_definition import get_criteria_for_protocol
from resto_client.entities.resto_feature import KNOWN_FILES_TYPES
from resto_client.functions.aoi_utils import find_region_choice
from resto_client.settings.resto_client_config import resto_client_print
from resto_client.settings.servers_database import DB_SERVERS

from .parser_common import (credentials_options_parser, EPILOG_CREDENTIALS,
                            download_dir_option_parser, EPILOG_DOWNLOAD_DIR,
                            collection_option_parser, CliFunctionReturnType)
from .parser_settings import (REGION_ARGNAME, CRITERIA_ARGNAME, MAXRECORDS_ARGNAME,
                              PAGE_ARGNAME, DOWNLOAD_ARGNAME, JSON_ARGNAME)


def display_list_on_lines(list_to_display: list) -> str:
    """
    :returns: display one item of the list per line
    """
    final_display = str(list_to_display)
    return final_display


def get_table_help_criteria() -> str:
    """
    :returns: attributes to be displayed in the tabulated dump of all supported criteria
    """
    persisted_server_name = RestoServerPersisted.get_persisted_server_name()
    if persisted_server_name is None:
        protocol_name = None
        title_help = 'Following criteria are supported by all resto servers:'
    else:
        protocol_name = DB_SERVERS.get_server(persisted_server_name).resto_access.protocol
        msg = 'Current {} server supports the following criteria (defined in the Resto API):'
        title_help = msg.format(persisted_server_name)

    dict_to_print = get_criteria_for_protocol(protocol_name)

    criteria_table = PrettyTable()
    criteria_table.title = title_help
    criteria_table.field_names = ['Criteria Key', 'Info']
    criteria_table.align['Info'] = 'l'
    criteria_table.align['Criteria Key'] = 'l'
    for key, value in dict_to_print.items():
        if value['type'] == 'group':
            new_dict_to_print = deepcopy(value)
            del new_dict_to_print['type']
            for sub_key, sub_value in new_dict_to_print.items():
                if sub_value['help'] is not None:
                    criteria_table.add_row([sub_key, sub_value['help']])
        else:
            criteria_table.add_row([key, value['help']])
    print_help = criteria_table.get_string(sortby='Criteria Key')
    return print_help


def criteria_args_fitter(criteria: Optional[dict]=None,
                         maxrecords: Optional[int]=None,
                         page: Optional[int]=None) -> Dict[str, Any]:
    """
    CLI arguments adapter to criteria dictionary

    :param criteria: criteria arguments
    :param maxrecords: maxrecords criterion args
    :param page: page criterion args

    :returns: criteria dict which fit correctly the API
    :raises RestoClientUserError: if no value is given for a criterion key
    """
    criteria_dict: Dict[str, Any] = {}

    if criteria is not None:
        for criterion in criteria:
            criterion = criterion.split(':')
            # if multi-criteria case
            if criterion[0] in criteria_dict:
                # if it s the second input then transform to list
                if not isinstance(criteria_dict[criterion[0]], list):
                    criteria_dict[criterion[0]] = [criteria_dict[criterion[0]]]
                # add new criterion to list
                criteria_dict[criterion[0]].append(criterion[1])
            else:
                try:
                    criteria_dict[criterion[0]] = criterion[1]
                except IndexError:
                    msg_err = 'No value given for the following criterion : {}'.format(criterion[0])
                    raise RestoClientUserError(msg_err)

    if maxrecords is not None:
        criteria_dict['maxRecords'] = maxrecords

    if page is not None:
        criteria_dict['page'] = page

    return criteria_dict


def cli_search_collection(args: Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to search_by_criteria function

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    criteria_dict = criteria_args_fitter(get_from_args(CRITERIA_ARGNAME, args),
                                         get_from_args(MAXRECORDS_ARGNAME, args),
                                         get_from_args(PAGE_ARGNAME, args))
    criteria_dict.update({REGION_ARGNAME: get_from_args(REGION_ARGNAME, args)})
    client_params = RestoClientParameters.build_from_argparse(args)
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    features_collection = resto_server.search_by_criteria(criteria_dict)

    msg_no_result = Fore.MAGENTA + Style.BRIGHT + 'No result '
    with colorama_text():
        search_feature_id = None
        if len(features_collection.all_id) == 1:
            msg_head = Fore.BLUE + 'One result found with id : ' + Style.BRIGHT
            search_feature_id = features_collection.features[0].product_identifier
            resto_client_print(msg_head + search_feature_id)
        elif not features_collection.all_id:
            page_search = criteria_dict.get('page', 1)
            if page_search > 1:
                msg_search = msg_no_result + 'at page {}, try a lower page number'
                resto_client_print(msg_search.format(page_search))
            else:
                resto_client_print(msg_no_result + 'found with criteria : {}'.format(criteria_dict))
        else:
            search_feature_id = features_collection.all_id
            resto_client_print("\n".join(features_collection.all_id))
            msg_search = '{} results shown on a total of '
            msg_search += Style.BRIGHT + ' {} results ' + Style.NORMAL + 'beginning at index {}'
            resto_client_print(msg_search.format(len(features_collection.all_id),
                                                 features_collection.total_results,
                                                 features_collection.start_index))
        resto_client_print(Style.RESET_ALL)

    download_dir = Path(client_params.download_dir)
    record_json = get_from_args(JSON_ARGNAME, args)
    if record_json and resto_server.server_name is not None:
        json_path = resto_server.ensure_server_directory(download_dir)
        json_search_file = features_collection.write_json(json_path)
        resto_client_print('Search saved in {}'.format(json_search_file))

    download = get_from_args(DOWNLOAD_ARGNAME, args)
    if download and search_feature_id is not None:
        resto_server.download_features_file_from_ids(search_feature_id, download,
                                                     download_dir)
    return client_params, resto_server


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_search_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'search' subparser
    """
    epilog_total = EPILOG_CREDENTIALS + EPILOG_DOWNLOAD_DIR + get_table_help_criteria()
    parser_search = sub_parsers.add_parser('search',
                                           formatter_class=RawDescriptionHelpFormatter,
                                           help='search feature(s) in a collection.',
                                           description='Search feature(s) in a collection using '
                                           'selection criteria.',
                                           epilog=epilog_total,
                                           parents=[collection_option_parser(),
                                                    credentials_options_parser(),
                                                    download_dir_option_parser()])
    parser_search.add_argument('--criteria', dest=CRITERIA_ARGNAME, nargs='+',
                               help='search criteria (format --criteria=key:value)')

    region_choices = find_region_choice()
    parser_search.add_argument('--region', dest=REGION_ARGNAME, type=str.lower,
                               choices=region_choices,
                               help='add region criteria using .geojson, see set '
                               'region for more info')
    parser_search.add_argument('--maxrecords', dest=MAXRECORDS_ARGNAME, type=int,
                               help='maximum records to show')
    parser_search.add_argument('--page', dest=PAGE_ARGNAME, type=int,
                               help='the number of the page to display')
    parser_search.add_argument('--download', dest=DOWNLOAD_ARGNAME, nargs='?', default=False,
                               choices=KNOWN_FILES_TYPES,
                               const='product',
                               help='download files corresponding to found features, by default'
                               ' product will be downloaded')
    parser_search.add_argument('--save_json', action="store_true",
                               help="save search's response in a json")

    parser_search.set_defaults(func=cli_search_collection)
