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
from typing import Optional, Dict, Union, Any  # @UnusedImport @NoMove

from colorama import Fore, Style, colorama_text
from prettytable import PrettyTable

from resto_client.base_exceptions import RestoClientUserError
from resto_client.services.resto_server import RestoServer
from resto_client.cli.cli_utils import get_from_args
from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.cli.resto_server_persisted import (RestoClientNoPersistedServer,
                                                     RestoServerPersisted)
from resto_client.functions.aoi_utils import find_region_choice
from resto_client.functions.collections_functions import search_current_collection
from resto_client.functions.resto_criteria import RestoCriteria

from .parser_common import (EPILOG_CREDENTIALS, CliFunctionReturnType, credentials_options_parser,
                            collection_option_parser, download_dir_option_parser)
from .parser_settings import (REGION_ARGNAME, CRITERIA_ARGNAME, MAXRECORDS_ARGNAME,
                              PAGE_ARGNAME, DOWNLOAD_ARGNAME)


def get_table_help_criteria() -> str:
    """
    :returns: attributes to be displayed in the tabulated dump of all supported criteria
    :raises RestoClientUserError: when the resto service is not initialized
    """
    # FIXME: this approach implies a server instanciation which is useless
    resto_server: Union[RestoServerPersisted, RestoServer]
    try:
        resto_server = RestoServerPersisted.build_from_argparse()
    except RestoClientNoPersistedServer:
        resto_server = RestoServer()
    resto_criteria = RestoCriteria(resto_server.resto_service)
    title_help = 'Current {} server supports the following criteria (defined in the Resto API):'
    title_help = title_help.format(resto_server.server_name)
    dict_to_print = resto_criteria.criteria_keys

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
    :raises RestoClientUserError: if no latitude and longitude present when required
    :raises RestoClientUserError: if radius without latitude and longitude
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

    if 'lat' in criteria_dict or 'lon' in criteria_dict:
        try:
            criteria_dict['geomPoint'] = {'lat': criteria_dict['lat'],
                                          'lon': criteria_dict['lon']}
            del criteria_dict['lat']
            del criteria_dict['lon']
        except KeyError:
            raise RestoClientUserError('lat AND lon must be present simultaneously')

    if 'radius' in criteria_dict:
        if 'geomPoint' not in criteria_dict:
            raise RestoClientUserError('With radius, latitude AND longitude must be present')
        criteria_dict['geomSurface'] = {'radius': criteria_dict['radius']}
        criteria_dict['geomSurface'].update(criteria_dict['geomPoint'])
        del criteria_dict['geomPoint']
        del criteria_dict['radius']

    return criteria_dict


def cli_search_collection(args: Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to search_current_collection function

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    criteria_dict = criteria_args_fitter(get_from_args(CRITERIA_ARGNAME, args),
                                         get_from_args(MAXRECORDS_ARGNAME, args),
                                         get_from_args(PAGE_ARGNAME, args))
    criteria_dict.update({'region': get_from_args(REGION_ARGNAME, args)})
    client_params = RestoClientParameters.build_from_argparse(args)
    resto_server = RestoServerPersisted.build_from_argparse(args)
    features_collection = search_current_collection(resto_server, criteria_dict)

    msg_no_result = Fore.MAGENTA + Style.BRIGHT + 'No result '
    with colorama_text():
        search_feature_id = None
        if len(features_collection.all_id) == 1:
            msg_head = Fore.BLUE + 'One result found with id : ' + Style.BRIGHT
            search_feature_id = features_collection.features[0].product_identifier
            print(msg_head + search_feature_id)
        elif not features_collection.all_id:
            page_search = criteria_dict.get('page', 1)
            if page_search > 1:
                msg_search = msg_no_result + 'at page {}, try a lower page number'
                print(msg_search.format(page_search))
            else:
                print(msg_no_result + 'found with criteria : {}'.format(criteria_dict))
        else:
            search_feature_id = features_collection.all_id
            print(features_collection.all_id)
            msg_search = '{} results shown on a total of '
            msg_search += Style.BRIGHT + ' {} results ' + Style.NORMAL + 'beginning at index {}'
            print(msg_search.format(len(features_collection.all_id),
                                    features_collection.total_results,
                                    features_collection.start_index))
        print(Style.RESET_ALL)

    download = get_from_args(DOWNLOAD_ARGNAME, args)
    if download and search_feature_id is not None:
        resto_server.download_features_file_from_ids(search_feature_id, download,
                                                     Path(client_params.download_dir))
    return client_params, resto_server


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_search_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'search' subparser
    """
    epilog_total = EPILOG_CREDENTIALS + get_table_help_criteria()
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
                               choices=['product', 'quicklook', 'annexes', 'thumbnail'],
                               const='product',
                               help='download files corresponding to found features, by default'
                               ' product will be downloaded')

    parser_search.set_defaults(func=cli_search_collection)
