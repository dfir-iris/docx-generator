#!/usr/bin/env python3
#
#  docx-generator Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS)
#  ir@cyberactionlab.net
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
from unittest import TestCase

from docx_generator.docx_generator import DocxGenerator
from docx_generator.exceptions.rendering_error import RenderingError


class TestDocxGenerator(TestCase):
    def setUp(self) -> None:
        # Create mock template file
        self._base_path = './template'
        self._result_path = 'result.docx'
        self._template_path = 'test_template.docx'

        self._subject = DocxGenerator()

    def tearDown(self) -> None:
        try:
            os.remove(os.path.join(self._base_path, self._result_path))
        except OSError:
            pass

    def test_generate_docx_should_not_fail(self):
        self._subject.generate_docx(self._base_path, self._template_path, {}, self._result_path)

    def test_generate_docx_should_create_docx_file(self):
        self._subject.generate_docx(self._base_path, self._template_path, {}, self._result_path)

        self.assertTrue(os.path.isfile(os.path.join(self._base_path, self._result_path)))

    def test_generate_docx_should_raise_error_if_base_path_does_not_exist(self):
        with self.assertRaises(RenderingError):
            self._subject.generate_docx('/invalid/', self._template_path, {}, self._result_path)

    def test_generate_docx_should_raise_error_if_template_path_does_not_exist(self):
        with self.assertRaises(RenderingError):
            self._subject.generate_docx(self._base_path, 'invalid.docx', {}, self._result_path)

    def test_generate_docx_should_raise_error_if_result_path_does_not_exist(self):
        with self.assertRaises(RenderingError):
            self._subject.generate_docx(self._base_path, self._template_path, {}, 'invalid/test.docx')
