#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Script to run all existing bug unit tests."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import glob
import inspect
import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from adspygoogle.adwords import LIB_SIG
from adspygoogle.common.Logger import Logger


LOG_NAME = 'adwords_api_lib'
LOGGER = Logger(LIB_SIG, os.path.join('..', '..', '..', 'logs'))


suite = unittest.TestSuite()
tests = [test[:-3] for test in glob.glob('issue_*.py')]
for test in tests:
  module = __import__(test)
  for name, obj in inspect.getmembers(module):
    if inspect.isclass(obj):
      suite.addTest(unittest.makeSuite(obj))


if __name__ == '__main__':
  LOGGER.Log(LOG_NAME, 'Start all unit tests.', log_level=Logger.DEBUG)
  unittest.TextTestRunner(verbosity=1).run(suite)
  LOGGER.Log(LOG_NAME, 'End all unit tests.', log_level=Logger.DEBUG)
