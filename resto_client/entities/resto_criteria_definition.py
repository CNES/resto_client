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
from typing import Type, Dict, Optional  # @NoMove

from shapely.errors import WKTReadingError

from resto_client.base_exceptions import RestoClientUserError
from resto_client.generic.basic_types import (SquareInterval, DateYMD, GeometryWKT, AscOrDesc,
                                              Polarisation, DateYMDInterval)


CriteriaDictType = Dict[str, dict]
COVER_TEXT = ' expressed as a percentage and using brackets. e.g. [n1,n2[ '
INTERVAL_TXT = '{} of the time slice of {}. Format should follow RFC-3339'
LATLON_TXT = 'expressed in decimal degrees (EPSG:4326) - must be used with'
COMMON_CRITERIA_KEYS: CriteriaDictType
COMMON_CRITERIA_KEYS = {'box': {'type': str, 'help':
                                "Defined by 'west, south, east, north' meridians and parallels"
                                " in that order, in decimal degrees (EPSG:4326)"},
                        'identifier': {'type': str, 'help':
                                       'Valid ID or UUID according to RFC 4122'},
                        'lang': {'type': str, 'help':
                                 'Two letters language code according to ISO 639-1'},
                        'parentIdentifier': {'type': str, 'help': 'deprecated'},
                        'q': {'type': str, 'help': 'Free text search / Keywords'},

                        'platform': {'type': 'list', 'sub_type': str, 'help':
                                     'Acquisition platform'},
                        'instrument': {'type': 'list', 'sub_type': str, 'help':
                                       'Satellite Instrument'},
                        'processingLevel': {'type': 'list', 'sub_type': str, 'help':
                                            'e.g. L1A, ORTHO'},
                        'productType': {'type': 'list', 'sub_type': str, 'help':
                                        'e.g. changes, landuse, etc'},
                        'sensorMode': {'type': 'list', 'sub_type': str, 'help':
                                       'Acquisition mode of the instrument'},
                        'organisationName': {'type': 'list', 'sub_type': str, 'help':
                                             'e.g. CNES'},

                        'index': {'type': int, 'help': 'Results page will begin at this index'},
                        'maxRecords': {'type': int, 'help':
                                       'Number of results returned per page (default 50)'},
                        'orbitNumber': {'type': int, 'help': 'Orbit Number (for satellite)'},
                        'page': {'type': int, 'help': 'Number of the page to display'},

                        'geometry': {'type': GeometryWKT, 'help':
                                     "Defined in Well Known Text standard (WKT) with "
                                     "coordinates in decimal degrees (EPSG:4326)"},

                        'startDate': {'type': DateYMD, 'help':
                                      INTERVAL_TXT.format('Beginning', 'the search query')},
                        'completionDate': {'type': DateYMD, 'help':
                                           INTERVAL_TXT.format('End', 'the search query')},

                        'updated': {'type': DateYMDInterval, 'help':
                                    'Time slice of last update of the data updatedFrom:updatedTo'},

                        'resolution': {'type': SquareInterval, 'help':
                                       "Spatial resolution expressed in meter and using brackets."
                                       " e.g.  [n1,n2["},
                        'cloudCover': {'type': SquareInterval, 'help':
                                       'Cloud cover' + COVER_TEXT},
                        'snowCover': {'type': SquareInterval, 'help':
                                      'Snow cover' + COVER_TEXT},
                        'cultivatedCover': {'type': SquareInterval, 'help':
                                            'Cultivated area' + COVER_TEXT},
                        'desertCover': {'type': SquareInterval, 'help':
                                        'Desert area' + COVER_TEXT},
                        'floodedCover': {'type': SquareInterval, 'help':
                                         'Flooded area' + COVER_TEXT},
                        'forestCover': {'type': SquareInterval, 'help': 'Forest area' + COVER_TEXT},
                        'herbaceousCover': {'type': SquareInterval, 'help':
                                            'Herbaceous area' + COVER_TEXT},
                        'iceCover': {'type': SquareInterval, 'help': 'Ice area' + COVER_TEXT},
                        'urbanCover': {'type': SquareInterval, 'help': 'Urban area' + COVER_TEXT},
                        'waterCover': {'type': SquareInterval, 'help': 'Water area' + COVER_TEXT},

                        'geomPoint': {'type': 'group',
                                      'lat': {'type': float,
                                              'help': 'Latitude ' + LATLON_TXT + ' lon'},
                                      'lon': {'type': float,
                                              'help': 'Longitude ' + LATLON_TXT + ' lat'}
                                      },
                        'geomSurface': {'type': 'group',
                                        'lat': {'type': float, 'help': None},
                                        'lon': {'type': float, 'help': None},
                                        'radius': {'type': float, 'help':
                                                   "Expressed in meter - "
                                                   "should be used with lon and lat"}
                                        },

                        'region': {'type': 'region', 'help':
                                   'Shortname of .shp file from zones folder'},
                        }

DOTCLOUD_KEYS: CriteriaDictType
DOTCLOUD_KEYS = {
    'identifiers': {'type': str, 'help': 'Accept multiple identifiers i1,i2,etc.'},
    'producerProductId': {'type': str, 'help': 'Producer product identifier'},
    'location': {'type': str, 'help': 'Location string e.g. Paris, France'},
    'metadataVisibility': {'type': str, 'help': 'Hiden access of product'},

    'productMode': {'type': 'list', 'sub_type': str, 'help': 'Product production mode'},
    'license': {'type': 'list', 'sub_type': str, 'help':
                'Identifier of applied license'},
    'dotcloudType': {'type': 'list', 'sub_type': str, 'help':
                     'Dotcloud Product Type e.g. eo_image'},
    'dotcloudSubType': {'type': 'list', 'sub_type': str, 'help':
                        'Dotcloud Product Sub-type e.g. optical'},

    'publishedFrom': {'type': DateYMD, 'help':
                      INTERVAL_TXT.format('Beginning', "the product's publication")},
    'publishedTo': {'type': DateYMD, 'help':
                    INTERVAL_TXT.format('End', "the product's publication")},
    'updatedFrom': {'type': DateYMD, 'help':
                    INTERVAL_TXT.format('Beginning', "the product's update")},
    'updatedTo': {'type': DateYMD, 'help':
                  INTERVAL_TXT.format('End', "the product's update")},

    'incidenceAngle': {'type': SquareInterval, 'help':
                       'Satellite incidence angle [n1,n2['},

    'onlyDownloadableProduct': {'type': bool, 'help':
                                "True or False : show only downlodable products for "
                                "the current account"},
}

PEPS_VERSION_KEYS: CriteriaDictType
PEPS_VERSION_KEYS = {'latitudeBand': {'type': str, 'help': ''},
                     'mgrsGSquare': {'type': str, 'help': ''},
                     'realtime': {'type': str, 'help': ''},
                     's2TakeId': {'type': str, 'help': ''},
                     'isNrt': {'type': str, 'help': ''},
                     'location': {'type': str, 'help': 'Location string e.g. Paris, France'},
                     # resolution overwritten but not available on peps
                     'resolution': {'type': str, 'help': 'not available on peps'},

                     'relativeOrbitNumber': {'type': int, 'help': 'Should be an integer'},

                     'orbitDirection': {'type': AscOrDesc, 'help': 'ascending or descending'},
                     'polarisation': {'type': Polarisation, 'help':
                                      "For Radar : 'HH', 'VV', 'HH HV' or 'VV VH'"},

                     'publishedBegin': {'type': DateYMD, 'help':
                                        INTERVAL_TXT.format('Beginning',
                                                            "the product's publication")},
                     'publishedEnd': {'type': DateYMD, 'help':
                                      INTERVAL_TXT.format('End', "the product's publication")},
                     }

THEIA_VERSION_KEYS: CriteriaDictType
THEIA_VERSION_KEYS = {'location': {'type': str, 'help': 'Location string e.g. Paris, France'},
                      'locationVECTOR': {'type': str, 'help': ''},
                      'locationRASTER': {'type': str, 'help': ''},
                      'typeOSO': {'type': str, 'help': ''},
                      'OSOsite': {'type': str, 'help': ''},
                      'OSOcountry': {'type': str, 'help': ''},
                      'country': {'type': str, 'help': ''},
                      'name': {'type': str, 'help': ''},
                      'state': {'type': str, 'help': ''},
                      'tileId': {'type': str, 'help': "e.g. T31TCJ"},
                      'zonegeo': {'type': str, 'help': ''},

                      'relativeOrbitNumber': {'type': int, 'help': ''},
                      'year': {'type': int, 'help': ''},
                      'nbColInterpolationErrorMax': {'type': int, 'help': ''},
                      'percentSaturatedPixelsMax': {'type': int, 'help': ''},
                      'percentNoDataPixelsMax': {'type': int, 'help': ''},
                      'percentGroundUsefulPixels': {'type': int, 'help': ''},
                      'percentUsefulPixelsMin': {'type': int, 'help': ''},
                      }

CREODIAS_VERSION_KEYS: CriteriaDictType
CREODIAS_VERSION_KEYS = {'bands': {'type': str, 'help': ''},
                         'cycle': {'type': str, 'help': ''},
                         'missionTakeId': {'type': str, 'help': ''},
                         'productIdentifier': {'type': str, 'help': ''},
                         'product_id': {'type': str, 'help': ''},
                         'phase': {'type': str, 'help': ''},
                         'swath': {'type': str, 'help': ''},
                         'sortParam': {'type': str, 'help': ''},
                         'status': {'type': str, 'help': ''},
                         'row': {'type': str, 'help': ''},
                         'path': {'type': str, 'help': ''},
                         'version': {'type': str, 'help': ''},
                         'name': {'type': str, 'help': ''},

                         'dataset': {'type': int, 'help': ''},

                         'sortOrder': {'type': AscOrDesc, 'help': 'ascending or descending'},

                         'publishedAfter': {'type': DateYMD, 'help':
                                            INTERVAL_TXT.format('Beginning',
                                                                "the product's publication")},
                         'publishedBefore': {'type': DateYMD, 'help':
                                             INTERVAL_TXT.format('End',
                                                                 "the product's publication")},
                         }

SPECIFIC_CRITERIA_KEYS: Dict[str, CriteriaDictType]
SPECIFIC_CRITERIA_KEYS = {'dotcloud': DOTCLOUD_KEYS,
                          'peps_version': PEPS_VERSION_KEYS,
                          'theia_version': THEIA_VERSION_KEYS,
                          'creodias_version': CREODIAS_VERSION_KEYS
                          }


def get_criteria_for_protocol(protocol_name: Optional[str]) -> CriteriaDictType:
    """

    :param protocol_name: the protocol name or None if only common criteria are requested.
    :returns: the criteria definition associated to a resto protocol, or the common criteria only
              if the resto protocol name is None.
    """
    protocol_criteria: CriteriaDictType = {}
    protocol_criteria.update(COMMON_CRITERIA_KEYS)

    if protocol_name is not None:
        protocol_criteria.update(SPECIFIC_CRITERIA_KEYS[protocol_name])
    return protocol_criteria


def test_criterion(key: str, value: object, auth_key_type: Type) -> None:
    """
    A function to test criterion and return the value to store if acceptable

    :param value: value to store as criterion
    :param auth_key_type: authorized type for the associated key
    :param key: name of the criterion
    :raises RestoClientUserError: when a criterion has a wrong type
    """
    try:
        str_value = str(value)
        auth_key_type(str_value)
    except (ValueError, WKTReadingError):
        msg = 'Criterion {} has an unexpected type : {}, expected : {}'
        raise RestoClientUserError(msg.format(key, type(value).__name__, auth_key_type.__name__))
