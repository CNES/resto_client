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
import unittest

from resto_client.functions.utils import guess_extension_with_charset


class UTestUtils(unittest.TestCase):
    """
    Unit Tests of DownloadRequestBase
    """

    def test_n_guess_extension_with_charset(self) -> None:
        """
        Unit test of guess_extension_with_charset in nominal cases
        """
        dict_mime_extension = {'text/html': '.htm',
                               'image/jpeg': '.jpe',
                               'image/png': '.png',
                               'text/html; charset=UTF-8': '.htm'}
        for content_type, extension in dict_mime_extension.items():
            guessed_extension = guess_extension_with_charset(content_type)
            self.assertEqual(extension, guessed_extension)

    def test_d_guess_extension_with_charset(self) -> None:
        """
        Unit test of guess_extension_with_charset in degraded cases
        """
        guessed_extension = guess_extension_with_charset("coucou")
        self.assertEqual(guessed_extension, None)
