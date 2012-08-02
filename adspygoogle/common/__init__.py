#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Settings and configurations for the client library."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import sys

VERSION = '3.0.8'

MIN_PY_VERSION = '2.4.4'
PYXML_NAME = 'PyXML'
ETREE_NAME = 'ElementTree'
MIN_PYXML_VERSION = '0.8.3'
MIN_ETREE_VERSION = '1.2.6'
PYXML = '1'
ETREE = '2'
COMMON_LIB_SIG = 'Common-Python/%s' % VERSION
PYTHON_VERSION = 'Python/%d.%d' % (sys.version_info[0], sys.version_info[1])


def GenerateLibSig(short_name, version):
  """Generates a library signature suitable for a UserAgent field.

  Args:
    short_name: str The short, product-specific name of the library.
    version: str The product-specific version of the library.
  Returns:
    str Library signature suitable to append to user-supplied user-agent value.
  """
  return ' (%s/%s, %s, %s)' % (short_name, version, COMMON_LIB_SIG,
                               PYTHON_VERSION)
