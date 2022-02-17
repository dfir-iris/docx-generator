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
from logging import Logger

from docx_generator.adapters.uuid_adapter import is_a_valid_uuid
from docx_generator.exceptions.rendering_error import RenderingError


def recover_file_path_from_uuid(logger: Logger, label: str, base_path: str, file_uuid: str) -> str:
    if not is_a_valid_uuid(file_uuid):
        raise RenderingError(logger, '{}. File uuid is not a valid uuid: {}'.format(label, file_uuid))

    file_folder_path = os.path.join(base_path, file_uuid)
    if not os.path.isdir(file_folder_path):
        raise RenderingError(logger, '{}. Generator can not find file folder.'.format(label), '{}. Processed folder does not exist: {}'.format(label, file_folder_path))

    available_files = os.listdir(file_folder_path)

    if len(available_files) > 1:
        raise RenderingError(logger, '{}. Internal error during file processing'.format(label), '{}. Multiple files found in uuid folder. Uuid value: {}'.format(label, file_uuid))

    file_name = available_files[0]

    return os.path.abspath(os.path.join(file_folder_path, file_name))
