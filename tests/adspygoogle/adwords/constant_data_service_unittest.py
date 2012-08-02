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

"""Unit tests to cover ConstantDataService."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest

from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class ConstantDataServiceTestV201109(unittest.TestCase):

  """Unittest suite for ConstantDataService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    client.use_mcc = True
    if not self.__class__.service:
      self.__class__.service = client.GetConstantDataService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

  def tearDown(self):
    """Finalize unittest."""
    client.use_mcc = False

  def testGetCarrierCriterion(self):
    """Test whether we can get all CarrierCriterion."""
    carrier_criteria = self.__class__.service.GetCarrierCriterion()
    for carrier_criterion in carrier_criteria:
      self.assertTrue(bool(carrier_criterion['id']))
      self.assertTrue(bool(carrier_criterion['name']))
      self.assertTrue(bool(carrier_criterion['countryCode']))

  def testGetLanguageCriterion(self):
    """Test whether we can get all LanguageCriterion."""
    language_criteria = self.__class__.service.GetLanguageCriterion()
    for language_criterion in language_criteria:
      self.assertTrue(bool(language_criterion['id']))
      self.assertTrue(bool(language_criterion['code']))
      self.assertTrue(bool(language_criterion['name']))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(ConstantDataServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
