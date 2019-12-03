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
from typing import Type, Optional, Dict, Tuple, Sequence, Any  # @NoMove @UnusedImport

from shapely.errors import WKTReadingError

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.functions.aoi_utils import search_file_from_key, geojson_zone_to_bbox
from resto_client.generic.basic_types import (SquareInterval, DateYMD, GeometryWKT, AscOrDesc,
                                              Polarisation)

CriteriaDictType = Dict[str, Sequence[Any]]
COMMON_CRITERIA_KEYS: CriteriaDictType
COMMON_CRITERIA_KEYS = {'box': (str, {'def': 'Accept a Geometry object'}), 'identifier': (str,),
                        'lang': (str,),
                        'parentIdentifier': (str,), 'q': (str,),

                        'platform': ('list', str), 'instrument': ('list', str),
                        'processingLevel': ('list', str), 'productType': ('list', str),
                        'sensorMode': ('list', str), 'organisationName': ('list', str),

                        'index': (int,), 'maxRecords': (int,), 'orbitNumber': (int,),
                        'page': (int,),

                        'geometry': (GeometryWKT,),

                        'startDate': (DateYMD,), 'completionDate': (DateYMD,),
                        'updated': (DateYMD,),

                        'resolution': (SquareInterval,), 'cloudCover': (SquareInterval,),
                        'snowCover': (SquareInterval,), 'cultivatedCover': (SquareInterval,),
                        'desertCover': (SquareInterval,), 'floodedCover': (SquareInterval,),
                        'forestCover': (SquareInterval,), 'herbaceousCover': (SquareInterval,),
                        'iceCover': (SquareInterval,), 'urbanCover': (SquareInterval,),
                        'waterCover': (SquareInterval,),

                        'geomPoint': ('group', {'lat': float, 'lon': float}),
                        'geomSurface': ('group', {'lat': float, 'lon': float, 'radius': float}),

                        'region': ('region',)
                        }

DOTCLOUD_KEYS: CriteriaDictType
DOTCLOUD_KEYS = {'identifiers': (str,), 'producerProductId': (str,), 'location': (str,),
                 'metadataVisibility': (str,),

                 'productMode': ('list', str), 'license': ('list', str),
                 'dotcloudType': ('list', str), 'dotcloudSubType': ('list', str),

                 'publishedFrom': (DateYMD,), 'publishedTo': (DateYMD,),
                 'updatedFrom': (DateYMD,), 'updatedTo': (DateYMD,),

                 'incidenceAngle': (SquareInterval,),

                 'onlyDownloadableProduct': (bool,)
                 }

PEPS_VERSION_KEYS: CriteriaDictType
PEPS_VERSION_KEYS = {'latitudeBand': (str,), 'mgrsGSquare': (str,), 'realtime': (str,),
                     's2TakeId': (str,), 'isNrt': (str,), 'location': (str,),
                     'resolution': (str,),  # resolution overwritten but not working on peps

                     'relativeOrbitNumber': (int,),

                     'orbitDirection': (AscOrDesc,),
                     'polarisation': (Polarisation,),

                     'publishedBegin': (DateYMD,), 'publishedEnd': (DateYMD,),
                     }

THEIA_VERSION_KEYS: CriteriaDictType
THEIA_VERSION_KEYS = {'location': (str,), 'locationVECTOR': (str,), 'locationRASTER': (str,),
                      'typeOSO': (str,), 'OSOsite': (str,), 'OSOcountry': (str,),
                      'country': (str,), 'name': (str,), 'state': (str,),
                      'zonegeo': (str,),

                      'relativeOrbitNumber': (int,), 'year': (int,),
                      'nbColInterpolationErrorMax': (int,),
                      'percentSaturatedPixelsMax': (int,), 'percentNoDataPixelsMax': (int,),
                      'percentGroundUsefulPixels': (int,), 'percentUsefulPixelsMin': (int,),
                      }

CREODIAS_VERSION_KEYS: CriteriaDictType
CREODIAS_VERSION_KEYS = {'bands': (str,), 'cycle': (str,), 'missionTakeId': (str,),
                         'productIdentifier': (str,), 'product_id': (str,), 'phase': (str,),
                         'swath': (str,), 'sortParam': (str,), 'status': (str,),
                         'row': (str,), 'path': (str,), 'version': (str,), 'name': (str,),

                         'dataset': (int,),

                         'sortOrder': (AscOrDesc,),

                         'publishedAfter': (DateYMD,), 'publishedBefore': (DateYMD,),
                         }

SPECIFIC_CRITERIA_KEYS: Dict[str, CriteriaDictType]
SPECIFIC_CRITERIA_KEYS = {'dotcloud': DOTCLOUD_KEYS,
                          'peps_version': PEPS_VERSION_KEYS,
                          'theia_version': THEIA_VERSION_KEYS,
                          'creodias_version': CREODIAS_VERSION_KEYS
                          }


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


class RestoCriteria(dict):
    """
    A class to hold criteria in a dictionary which can be read and written by the API.
    """

    def __init__(self, resto_protocol: str, **kwargs: str) -> None:
        """
        Constructor

        :param resto_protocol : associated resto service protocol
        :param dict kwargs : dictonary in keyword=value form
        :raises IndexError: if no service protocol given
        :raises RestoClientUserError: if a criterion is not in criteria key list
        """
        self.criteria_keys: CriteriaDictType = {}
        self.criteria_keys.update(COMMON_CRITERIA_KEYS)

        if resto_protocol not in SPECIFIC_CRITERIA_KEYS:
            msg = 'specific criteria type of "{}" protocol not supported by resto_client'
            raise RestoClientUserError(msg.format(resto_protocol))
        self.criteria_keys.update(SPECIFIC_CRITERIA_KEYS[resto_protocol])

        super(RestoCriteria, self).__init__()
        self.update(kwargs)

    def __setitem__(self, key: str, value: object) -> None:
        """
        overidden setitem to test criterion before recording in dict

        :param value: value to store as criterion
        :param key: name of the criterion
        :raises RestoClientUserError: when a criterion has a wrong type
        :raises RestoClientDesignError: when a group type criteria entry does not provide a dict.
        """
        if key not in self.criteria_keys:
            # Search for the same criterion without case sensitive and rewrite it
            for key_to_test in self.criteria_keys:
                if key.lower() == key_to_test.lower():
                    key = key_to_test
                    break
            # if not found raise criterion error
            else:
                msg = 'Criterion {} not supported by this resto server'.format(key)
                msg += ', choose from the following list: {}'.format(self.criteria_keys)
                raise RestoClientUserError(msg)

        auth_key_type = self.criteria_keys[key][0]

        # if key is has direct recording type (no list or group)
        if isinstance(auth_key_type, type):
            test_criterion(key, value, auth_key_type)
            super(RestoCriteria, self).__setitem__(key, value)
            self._manage_geometry()
        elif auth_key_type == 'list':
            auth_key_type = self.criteria_keys[key][1]
            # if can be list but is single
            if not isinstance(value, list):
                test_criterion(key, value, auth_key_type)
                super(RestoCriteria, self).__setitem__(key, value)
            # if it is realy a list of criteria
            else:
                for value_item in value:
                    test_criterion(key, value_item, auth_key_type)
                    new_key = '{}[{}]'.format(key, value.index(value_item))
                    super(RestoCriteria, self).__setitem__(new_key, value_item)
        elif auth_key_type == 'group':
            if not isinstance(value, dict):
                raise RestoClientDesignError('group key_type must be followed by a dict')
            for criterion, value_item in value.items():
                # Test the key in group item
                try:
                    auth_key_type = self.criteria_keys[key][1][criterion]
                except KeyError:
                    msg = 'Criterion {} in {} not supported by this resto server'
                    raise RestoClientUserError(msg.format(criterion, key))

                test_criterion(criterion, value_item, auth_key_type)
                super(RestoCriteria, self).__setitem__(criterion, value_item)
        elif auth_key_type == 'region':
            if isinstance(value, (str, type(None))):
                self._manage_geometry(region=value)
            else:
                raise RestoClientDesignError('region must be a str or None')

    def update(self, criteria: dict) -> None:
        """
        Update the Criteria dict with new criteria and test them

        :param criteria : dict of criteria
        """
        for key, value in criteria.items():
            self[key] = value

    def _manage_geometry(self, region: Optional[str]=None) -> None:
        """
        Add the region file criteria if not already given and no id given

        :param region: name of the geojson file
        """
        # if an id is given do not look at geometry
        if 'identifiers' in self or 'identifier' in self:
            if 'geometry' in self:
                del self['geometry']
        # else if geometry already given we won't overwrite it
        elif 'geometry' not in self and region is not None:
            geojson_file = search_file_from_key(region)
            shape_bbox = geojson_zone_to_bbox(geojson_file)
            geometry_criteria = str(shape_bbox)
            self['geometry'] = geometry_criteria
