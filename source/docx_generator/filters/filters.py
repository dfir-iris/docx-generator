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
from datetime import datetime
import mistletoe
from jinja2 import Environment
from markupsafe import Markup

from docx_generator.adapters.docx.style_adapter import RenderStylesCollection
from docx_generator.adapters.mistletoe.DocxRenderer import DocxRenderer


class Filters(object):
    def __init__(self, renderer: DocxRenderer, styles: RenderStylesCollection, jinja2_environment: Environment):
        self._renderer = renderer
        self._styles = styles

        self._jinja2_environment = jinja2_environment

        self._logger = logging.getLogger(__name__)

    def _timestamp_to_human_date_filter(self, timestamp: str, time_format: str = '%d/%m/%Y') -> str:
        """
        Converts timestamps into human readable dates

        :param timestamp: int
            Time in milliseconds
        :param time_format: str, optional
            Datetime format used by the 'datetime.strftime' method
            (Default value is '%d/%m/%Y')

        :return: str
            Formatted date
        """
        try:
            processed_timestamp = int(timestamp)
        except ValueError:
            self._logger.warning('Cannot convert timestamp to human date. {} is not a valid timestamp'.format(timestamp))
            processed_timestamp = 0

        return_value = datetime.fromtimestamp(processed_timestamp / 1000).strftime(time_format)

        self._logger.info('Adding timestamp: {}'.format(return_value))
        return return_value

    def _markdown_to_docx(self, markdown: str, style_name: str = 'default') -> Markup:
        """
        Convert Markdown string into Docx XML

        :param markdown: string
            Markdown string to be converted to Docx
        :param style_name: str
            Name of the style described in the template.
            (Default value is 'default')

        :return:
            XML to be added to the .docx file
        """
        self._renderer.set_style(self._styles.get_style(style_name))
        return_value = mistletoe.markdown(markdown + "\r\n", self._renderer)
        for warn in self._renderer.warnings:
            self._logger.info(warn)

        self._logger.info('Adding Markdown after processing ... {} characters.'.format(len(return_value)))
        return Markup(return_value)

    def set_available_filters(self) -> None:
        """
        Sets custom filters to Jinja2 environment

        :return: None
        """

        self._jinja2_environment.filters['timestampToDate'] = self._timestamp_to_human_date_filter
        self._jinja2_environment.filters['markdown'] = self._markdown_to_docx
