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


import argparse
import unittest
import xmlrunner
import sys

sys.path.append('source/')

parser = argparse.ArgumentParser()
parser.add_argument('test_type', choices=['unit', 'component'], help='the type of test to run')
arguments = parser.parse_args()

test_type = arguments.test_type

loader = unittest.TestLoader()
tests = loader.discover('test/' + test_type, top_level_dir='test')
testRunner = xmlrunner.XMLTestRunner(output='results/reports/test')
testRunner.run(tests)

