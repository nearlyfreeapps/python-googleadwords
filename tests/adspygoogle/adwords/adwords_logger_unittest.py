#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Unit tests to cover Logger."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import logging
import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest

from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class LoggerTestV201109(unittest.TestCase):

  """Unittest suite for Logger using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  TMP_LOG = os.path.join('..', '..', '..', 'logs', 'logger_unittest.log')
  DEBUG_MSG1 = 'Message before call to an API method.'
  DEBUG_MSG2 = 'Message after call to an API method.'
  client.debug = False

  def setUp(self):
    """Prepare unittest."""
    print self.id()

  def testUpperStackLogging(self):
    """Tests whether we can define logger at client level and log before and
    after the API request is made."""
    logger = logging.getLogger('LoggerTest')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(self.__class__.TMP_LOG)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    # Clean up temporary log file.
    Utils.PurgeLog(self.__class__.TMP_LOG)

    logger.debug(self.__class__.DEBUG_MSG1)
    info_service = client.GetInfoService(
        self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
    selector = {
        'apiUsageType': 'TOTAL_USAGE_API_UNITS_PER_MONTH'
    }
    info_service.Get(selector)
    logger.debug(self.__class__.DEBUG_MSG2)

    data = Utils.ReadFile(self.__class__.TMP_LOG)
    self.assertEqual(data.find(self.__class__.DEBUG_MSG1), 0)
    self.assertEqual(data.find(self.__class__.DEBUG_MSG2),
                     len(self.__class__.DEBUG_MSG1) + 1)

    # Clean up and remove temporary log file.
    Utils.PurgeLog(self.__class__.TMP_LOG)
    os.remove(self.__class__.TMP_LOG)


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(LoggerTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
