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

"""Unit tests to cover AdWordsErrors."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest

from adspygoogle.adwords.AdWordsClient import AdWordsClient
from adspygoogle.adwords.AdWordsSoapBuffer import AdWordsSoapBuffer
from adspygoogle.adwords.AdWordsErrors import AdWordsApiError
from adspygoogle.adwords.AdWordsErrors import AdWordsError
from adspygoogle.adwords.AdWordsErrors import AdWordsRequestError
from adspygoogle.common import Utils
from adspygoogle.common.Errors import ApiAsStrError
from adspygoogle.common.Errors import MalformedBufferError
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class AdWordsErrorsTest(unittest.TestCase):

  """Unittest suite for AdWordsErrors."""

  TRIGGER_MSG1 = 'The developer token is invalid.'
  TRIGGER_CODE1 = 42
  TRIGGER_STR = """faultcode: soapenv:Server.userException
faultstring: The developer token is invalid.

trigger: xxxxxx++USD
message: The developer token is invalid.
code: 42"""
  TRIGGER_MSG2 = 'An internal error has occurred.  Please retry your request.'
  TRIGGER_CODE2 = 0
  TRIGGER_MSG3 = 'Fault occurred while processing.'
  TRIGGER_MSG4 = 'One or more input elements failed validation.'
  TRIGGER_CODE4 = 122
  XML_RESPONSE_FAULT1 = Utils.ReadFile(
      os.path.join('data', 'response_fault_stacktrace.xml'))
  XML_RESPONSE_FAULT2 = Utils.ReadFile(
      os.path.join('data', 'response_fault.xml'))
  XML_RESPONSE_FAULT3 = Utils.ReadFile(
      os.path.join('data', 'response_fault_errors.xml'))

  def setUp(self):
    """Prepare unittest."""
    print self.id()

  def testApiAsStrError(self):
    """Tests whether we can catch an Errors.ApiAsStrError exception."""
    try:
      raise ApiAsStrError(self.__class__.TRIGGER_STR)
    except ApiAsStrError, e:
      self.assertEqual(str(e), self.__class__.TRIGGER_STR)

  def testStacktraceElement(self):
    """Tests whether we can handle a fault's stacktrace element."""
    try:
      buf = AdWordsSoapBuffer()
      buf.InjectXml(self.__class__.XML_RESPONSE_FAULT1)
      raise AdWordsApiError(buf.GetFaultAsDict())
    except AdWordsApiError, e:
      self.assertEqual(str(e), self.__class__.TRIGGER_MSG2)
      self.assertEqual(int(e.code), self.__class__.TRIGGER_CODE2)

  def testProcessingFault(self):
    """Tests whether we can handle a processing fault."""
    try:
      buf = AdWordsSoapBuffer()
      buf.InjectXml(self.__class__.XML_RESPONSE_FAULT2)
      raise AdWordsApiError(buf.GetFaultAsDict())
    except AdWordsApiError, e:
      self.assertEqual(str(e), self.__class__.TRIGGER_MSG3)

  def testErrorsFault(self):
    """Tests whether we can handle a fault with errors elements."""
    try:
      buf = AdWordsSoapBuffer()
      buf.InjectXml(self.__class__.XML_RESPONSE_FAULT3)
      raise AdWordsApiError(buf.GetFaultAsDict())
    except AdWordsApiError, e:
      self.assertEqual(str(e), self.__class__.TRIGGER_MSG4)
      self.assertEqual(int(e.code), self.__class__.TRIGGER_CODE4)

  def testMalformedBuffer(self):
    """Tests whether we can handle a malformed SOAP buffer."""
    buf = AdWordsSoapBuffer()
    buf.write('JUNK')
    self.assertRaises(MalformedBufferError, buf.GetCallResponseTime)


class AdWordsErrorsTestV201109(unittest.TestCase):

  """Unittest suite for AdWordsErrors using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  TRIGGER_TYPE1 = 'RequiredError'
  TRIGGER_MSG1 = 'operations[0].operand.biddingStrategy'
  client.debug = False

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    client.use_mcc = True

  def tearDown(self):
    """Finalize unittest."""
    client.use_mcc = False

  def testMissingBiddingStrategy(self):
    """Tests whether we can catch missing bidding strategy exception."""
    try:
      operations = [
          {
              'operator': 'ADD',
              'operand': {
                  'status': 'PAUSED',
                  'budget': {
                      'period': 'DAILY',
                      'amount': {
                          'microAmount': '1000000'
                      },
                      'deliveryMethod': 'STANDARD'
                  }
              }
          }
      ]
      client.GetCampaignService(self.__class__.SERVER, self.__class__.VERSION,
          HTTP_PROXY).Mutate(operations)
    except AdWordsRequestError, e:
      self.assertEqual(e.errors[0].type, self.__class__.TRIGGER_TYPE1)
      self.assertEqual(e.errors[0].fieldPath, self.__class__.TRIGGER_MSG1)


def makeTestSuite():
  """Set up test suite.

  Returns:
    TestSuite test suite.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdWordsErrorsTest))
  return suite


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdWordsErrorsTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  suites.append(makeTestSuite())
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
