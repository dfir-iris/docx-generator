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
from typing import Dict

from docxtpl import DocxTemplate
from jinja2 import Environment

from docx_generator.adapters.docx.style_adapter import RenderStylesCollection, get_document_render_styles
from docx_generator.adapters.mistletoe.DocxRenderer import DocxRenderer
from docx_generator.exceptions.rendering_error import RenderingError
from docx_generator.filters.filters import Filters
from docx_generator.globals.globals import Globals


def _sanitize_path(path: str) -> str:
    sanitized_path = path.strip('./').strip(',').strip(' ')
    return os.path.normpath(sanitized_path)


class DocxGenerator(object):
    def __init__(self, logger_mode: str = 'INFO', max_recursive_render_depth: int = 5):
        logging.basicConfig(
            format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
            level=getattr(logging, logger_mode, logging.INFO)
        )

        self._logger = logging.getLogger(__name__)

        self._max_recursive_render_depth = max_recursive_render_depth

    def _process_template_path(self, base_path: str, template_path: str) -> str:
        template_path = _sanitize_path(template_path)
        full_template_path = os.path.join(base_path, template_path)
        if not os.path.isfile(full_template_path):
            raise RenderingError(self._logger, 'Generator can not find template.', 'Generator can not find template: {}'.format(full_template_path))
        else:
            self._logger.info('Template located: {}'.format(full_template_path))

        return full_template_path

    def _process_output_path(self, base_path: str, output_path: str) -> str:
        output_path = _sanitize_path(output_path)
        full_output_path = os.path.join(base_path, output_path)
        full_output_dir = os.path.dirname(full_output_path)
        if not os.path.isdir(full_output_dir):
            raise RenderingError(self._logger, 'Generator can not find output directory.', 'Generator can not find output directory to create {}'.format(full_output_path))
        else:
            self._logger.info('Output directory located: {}'.format(full_output_path))
        return full_output_path

    def _set_jinja2_custom_environment(self, base_path: str, template: DocxTemplate, jinja2_environment: Environment, renderer: DocxRenderer, template_styles: RenderStylesCollection) -> None:
        jinja2_custom_filters = Filters(renderer, template_styles, jinja2_environment)
        jinja2_custom_globals = Globals(base_path, template, jinja2_environment)

        jinja2_custom_filters.set_available_filters()
        jinja2_custom_globals.set_available_globals()

    def _recursive_rendering(self, base_path: str, template_path: str, data: Dict, output_path: str, render_level: int):
        render_level += 1
        self._logger.info('Start rendering for level {}'.format(render_level))

        loaded_template = DocxTemplate(template_path)
        template_styles = get_document_render_styles(template_path)

        docx_renderer = DocxRenderer(loaded_template)

        jinja_custom_environment = Environment()

        self._set_jinja2_custom_environment(base_path, loaded_template, jinja_custom_environment, docx_renderer, template_styles)

        try:
            loaded_template.render(data, jinja_env=jinja_custom_environment, autoescape=True)
        except Exception as e:
            error_message = '{} ({})'.format(str(e), os.path.basename(template_path))
            raise RenderingError(self._logger, error_message)

        is_variable_found = False
        variable_regex = "{{.+}}|{%.+%}"

        for paragraph in loaded_template.paragraphs:
            if re.search(variable_regex, paragraph.text) is not None:
                is_variable_found = True
                break

        for table in loaded_template.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if re.search(variable_regex, paragraph.text) is not None:
                            is_variable_found = True
                            break

        loaded_template.save(output_path)
        self._logger.info('Document generated for level {}'.format(render_level))

        if is_variable_found and render_level <= self._max_recursive_render_depth:
            self._logger.info('Variable found in generated document. Restarting rendering process ...')
            self._recursive_rendering('', output_path, data, output_path, render_level)

        if render_level > self._max_recursive_render_depth:
            self._logger.info('Rendering depth level exceeded, leaving render loop')

        self._logger.info('Rendering process completed !')

    """
        template_path and absolute_path must be relative to base_path
    """
    def generate_docx(self, base_path: str, template_path: str, data: Dict, output_path: str):
        processed_base_path = os.path.abspath(base_path)
        full_template_path = self._process_template_path(processed_base_path, template_path)
        full_output_path = self._process_output_path(processed_base_path, output_path)

        self._logger.info('Starting new report generation. Base path: {}. Template path: {}. Output path'.format(processed_base_path, full_template_path, full_output_path))
        self._recursive_rendering(processed_base_path, full_template_path, data, full_output_path, 0)
