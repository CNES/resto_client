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
from typing import (Optional, Any)  # @NoMove @UnusedImport


from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.entities.resto_criteria_definition import (test_criterion,
                                                             get_criteria_for_protocol)
from resto_client.functions.aoi_utils import search_file_from_key, geojson_zone_to_bbox


class RestoCriteria(dict):
    """
    A class to hold criteria in a dictionary which can be read and written by the API.
    """

    def __init__(self, resto_protocol: Optional[str], **kwargs: str) -> None:
        """
        Constructor

        :param resto_protocol : name of the resto protocol or None for common criteria.
        :param dict kwargs : dictionary in keyword=value form
        """
        self.supported_criteria = get_criteria_for_protocol(resto_protocol)

        super(RestoCriteria, self).__init__()
        self.update(kwargs)

    def __setitem__(self, key: str, value: object) -> None:
        """
        overidden setitem to test criterion before recording in dict

        :param value: value to store as criterion
        :param key: name of the criterion
        :raises RestoClientUserError: when a criterion is not supported on the server
        :raises RestoClientDesignError: when a group type criteria entry does not provide a dict.
        """
        key = self._retrieve_criterion(key)

        auth_key_type = self.supported_criteria[key]['type']

        # if key is has direct recording type (no list or group)
        if isinstance(auth_key_type, type):
            test_criterion(key, value, auth_key_type)
            super(RestoCriteria, self).__setitem__(key, value)
            self._manage_geometry()
        elif auth_key_type == 'list':
            auth_key_type = self.supported_criteria[key]['sub_type']
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
                    auth_key_type = self.supported_criteria[key][criterion]["type"]
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

    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Update this dictionary such that __setitem__ is called
        """
        criteria_dict = dict(*args, **kwargs)
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

        for key, value in criteria_dict.items():
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

    def _retrieve_criterion(self, key: str) -> str:
        """
        Case unsensitive search of the criterion and return its case sensitive name.

        :param key: key to test
        :raises RestoClientUserError: when key is unknown
        :returns: key suitable for the current server
        """
        if key not in self.supported_criteria:
            for key_to_test in self.supported_criteria:
                if key.lower() == key_to_test.lower():
                    return key_to_test
            # if not found raise criterion error
            msg = 'Criterion {} not supported by this resto server'.format(key)
            msg += ', choose from the following list: '
            msg += '{}'.format(list(self.supported_criteria.keys()))
            raise RestoClientUserError(msg)
        return key
