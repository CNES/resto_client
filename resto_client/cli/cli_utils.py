# -*- coding: utf-8 -*-
"""
.. admonition:: License

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
from typing import Optional, Any


def get_from_args(arg_name: str, args: Optional[argparse.Namespace] = None) -> Optional[Any]:
    """
    Returns the content of an argument in an argparse Namespace, or None if the argument is not
    found or the Namespace is None.

    :param arg_name: name of an argument to retrieve in the Namespace
    :param args: CLI arguments as parsed by argparse
    :returns: the content of the selected argument or None if not found.
    """
    if args is None:
        return None
    return getattr(args, arg_name) if hasattr(args, arg_name) else None
