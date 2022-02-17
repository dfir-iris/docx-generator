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

from setuptools import setup
from setuptools import find_packages

project_description = {}
with open('Project.conf') as configuration:
    for line in configuration:
        line = line.strip()
        if line == '':
            continue
        key, value = line.split('=', 1)
        project_description[key] = value

setup(name=project_description['NAME'],
      version=project_description['VERSION'],
      package_dir={'': 'source'},
      packages=find_packages('source'),
      author=project_description['AUTHOR'],
      author_email=project_description['EMAIL'],
      url=project_description['URL'],
      install_requires=project_description['DEPENDENCIES'].split(' ')
      )
