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

import logging
import os
import re

from docx import Document
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, Subdoc

from docx_generator.adapters.file_adapter import recover_file_path_from_uuid
from docx_generator.exceptions.rendering_error import RenderingError


class DocumentGlobals(object):
    def __init__(self, template: DocxTemplate, base_path: str):
        self._template = template
        self._base_path = base_path

        self._logger = logging.getLogger(__name__)

    def _process_sub_document(self, sub_document_path) -> Subdoc:
        subdoc = self._template.new_subdoc()
        composer = Composer(subdoc)

        document_to_merge = Document(sub_document_path)

        composer.append(document_to_merge)

        return subdoc

    def add_sub_document(self, sub_document_path: str) -> Subdoc:
        """
        Adds sub document to main document from local path

        :param sub_document_path: str
            Full path to sub document .docx file

        :return: docxtpl.Subdoc
        """
        incorrect_path_pattern = r'\.\.'

        if len(re.findall(incorrect_path_pattern, sub_document_path)) > 0:
            raise RenderingError(self._logger, 'Invalid filename provided')

        if not os.path.isfile(sub_document_path):
            raise RenderingError(self._logger, 'The path provided is not a correct file')

        try:
            sub_document = self._process_sub_document(sub_document_path)

            self._logger.info('Adding Sub Document: {}'.format(sub_document_path))
            return sub_document
        except Exception as e:
            self._logger.info(e)

    def add_sub_document_from_uuid(self, uuid: str) -> Subdoc:
        """
        Adds sub document to main document from FTP

        :param uuid: str
            uuid of sub document .docx file on the FTP

        :return: docxtpl.Subdoc
        """
        sub_document_file_path = recover_file_path_from_uuid(self._logger, 'Sub Document', self._base_path, uuid)

        return self.add_sub_document(sub_document_file_path)
