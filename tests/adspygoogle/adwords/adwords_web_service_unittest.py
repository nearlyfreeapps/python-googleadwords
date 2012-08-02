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

"""Unit tests to cover GenericAdWordsService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import thread
import threading
import unittest

from adspygoogle.adwords.AdWordsErrors import AdWordsApiError
from adspygoogle.adwords.GenericAdWordsService import GenericAdWordsService
from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class AdWordsWebServiceTestV201109(unittest.TestCase):

  """Unittest suite for AdWordsWebService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  responses = []
  MAX_THREADS = 3

  def setUp(self):
    """Prepare unittest."""
    print self.id()

  def testCallRawMethod(self):
    """Test whether we can call an API method by posting SOAP XML message."""
    soap_message = Utils.ReadFile(os.path.join('data',
                                               'request_getallcampaigns.xml'))
    url = '/api/adwords/cm/v201109/CampaignService'
    http_proxy = None

    self.assert_(isinstance(client.CallRawMethod(soap_message, url,
                            self.__class__.SERVER, http_proxy), tuple))

  def testMultiThreads(self):
    """Test whether we can safely execute multiple threads."""
    all_threads = []
    for index in xrange(self.__class__.MAX_THREADS):
      t = TestThreadV201109()
      all_threads.append(t)
      t.start()

    for t in all_threads:
      t.join()

    self.assertEqual(len(self.responses), self.__class__.MAX_THREADS)


class TestThreadV201109(threading.Thread):

  """Creates TestThread.

  Responsible for defining an action for a single thread using v201109.
  """

  def run(self):
    """Represent thread's activity."""
    selector = {
        'fields': ['Id', 'Name', 'Status']
    }
    AdWordsWebServiceTestV201109.responses.append(
        client.GetCampaignService(AdWordsWebServiceTestV201109.SERVER,
            AdWordsWebServiceTestV201109.VERSION, HTTP_PROXY).Get(selector))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdWordsWebServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')

