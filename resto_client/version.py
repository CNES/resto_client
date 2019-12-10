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


Define version informations for the package.

This definition is made in a module separate from <package>.__init__.py, in order to avoid
systematic version computation, even when no access to __version__ or __updated__ is needed.

Those needing access to these symbols shall import this module on their own.
"""
__version__ = "v0.2.0"
__updated__ = "10.12.2019"
