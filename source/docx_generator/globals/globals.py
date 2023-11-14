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
from typing import Dict

from docxtpl import DocxTemplate, RichText
from jinja2 import Environment

from docx_generator.globals.document_globals import DocumentGlobals
from docx_generator.globals.picture_globals import PictureGlobals
from docx_generator.globals.rich_text_globals import RichTextGlobals


class Globals(object):
    def __init__(self, base_path: str, output_path: str, image_directory_path: str, template: DocxTemplate, style_mapper: Dict[str, str], jinja2_environment: Environment):
        self._base_path = base_path
        self._output_path = output_path
        self._image_directory_path = image_directory_path
        self._template = template
        self._style_mapper = style_mapper
        self._jinja2_environment = jinja2_environment

        self._logger = logging.getLogger(__name__)

    def _hyperlink(self, caption: str, url: str, style_name: str = None) -> RichText:
        """
        Returns A RichText Hyperlink

        :param caption: str
        :param url: str

        :return: RichText
        """

        rt = RichText()
        rt.add(caption, url_id=self._template.build_url_id(url), style=style_name)

        self._logger.debug('Adding hyperlink: {} - {}'.format(caption, url))

        return rt

    def set_available_globals(self) -> None:
        """
        Sets custom globals to Jinja2 environment.

        :return: None
        """

        picture_globals = PictureGlobals(self._template, self._base_path, self._image_directory_path)
        document_globals = DocumentGlobals(self._template, self._base_path)
        rich_text_globals = RichTextGlobals(self._template, self._base_path, self._output_path, self._image_directory_path, self._style_mapper)

        self._jinja2_environment.globals['addPicture'] = picture_globals.add_picture
        self._jinja2_environment.globals['addPictureFromUuid'] = picture_globals.add_picture_from_uuid
        self._jinja2_environment.globals['addSubDocument'] = document_globals.add_sub_document
        self._jinja2_environment.globals['addSubDocumentFromUuid'] = document_globals.add_sub_document_from_uuid
        self._jinja2_environment.globals['addHyperlink'] = self._hyperlink
        self._jinja2_environment.globals['addRichtext'] = rich_text_globals.richtext_to_docx
