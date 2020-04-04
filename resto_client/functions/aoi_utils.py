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
from typing import Any, List  # @UnusedImport @NoMove

import json

from pathlib import Path
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from resto_client.base_exceptions import RestoClientUserError


HERE = Path(__file__).parent
PATH_AOI = HERE.parent / 'zones'


class LowerList(list):
    """
     Class representing a less restrictive list
    """

    def __contains__(self, other: object) -> bool:
        """
        other is in my class if this lower is in it

        :param other: object whose str representation is to be tested for being in the list.
        :returns: boolean response of : is the other.lower in self ?
        """
        return super(LowerList, self).__contains__(str(other).lower())


def list_all_geojson() -> List[str]:
    """
    List all geojson file in the proper path for aoi

    :returns: list of file in lower_case
    """
    list_file = [f.name for f in PATH_AOI.iterdir() if f.suffix == '.geojson']
    # prepare test by lower all name
    list_file = [element.lower() for element in list_file]
    return list_file


def search_file_from_key(key: str) -> Path:
    """
    Translate a key to this proper geojson file

    :param  key: the geojson file
    :returns: geojson file associated
    """
    if not key.endswith('.geojson'):
        key += '.geojson'
    return PATH_AOI / key


def find_region_choice() -> LowerList:
    """
    Cut all .geojson extension in the list geojson file

    :returns: the list of region choices file without .geojson extension
    """
    list_to_cut = list_all_geojson()
    cut_list = [f[0:-8] for f in list_to_cut if f.endswith('.geojson')]
    return LowerList(cut_list)


def geojson_zone_to_bbox(geojson_path: Path) -> BaseGeometry:
    """
    Translate a geojson file to a bbox geometry

    :param geojson_path: the path to the geojson file
    :returns: the bbox geometry of the kml
    """
    # will contain all shape of the geojson
    shapes = geojson_to_shape(geojson_path)
    # translate it for resto into bbox bounds
    return shapes_to_bbox(shapes)


def find_sensitive_file(geojson_path: Path) -> Path:
    """
    Find the proper file name if the given has not a good sensitive case

    :param geojson_path: the geojson file path
    :returns: correct path with case taking into account
    :raises RestoClientUserError: when the region file is not found.
    """
    file_name = geojson_path.name
    directory = geojson_path.parent
    for name_in_dir in directory.iterdir():
        if file_name.lower() == str(name_in_dir.name).lower():
            improved_path = directory / name_in_dir
            return improved_path
    raise RestoClientUserError('No region file found with name {}'.format(geojson_path))


def geojson_to_shape(geojson_file: Path) -> List[BaseGeometry]:
    """
    Translate a geojson file to a shape of shapely

    :param geojson_file: the path of the geojson file
    :returns: list of shape
    """
    if not geojson_file.exists():
        geojson_file = find_sensitive_file(geojson_file)

    with open(geojson_file, 'r') as file:
        data = json.load(file)

    shapes = []
    for feature in data['features']:
        shapes.append(shape(feature['geometry']))

    return shapes


def shapes_to_bbox(shapes: List[BaseGeometry]) -> BaseGeometry:
    """
    Translate shapes to a bbox envelope

    :param shapes: list of shapely shape
    :returns: bbox of the shapes, rectangular boundaries
    """
    # convert to a single shape, union of all
    union_mono_shape = unary_union(shapes)
    # returns the smallest rectangular polygon
    convex_envelope = union_mono_shape.convex_hull

    return convex_envelope
