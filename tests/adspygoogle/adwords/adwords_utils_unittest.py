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

"""Unit tests to cover AdWordsUtils."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest

from adspygoogle.adwords import AdWordsUtils
from adspygoogle.adwords.AdWordsSoapBuffer import AdWordsSoapBuffer
from adspygoogle.common import Utils


class AdWordsUtilsTest(unittest.TestCase):

  """Unittest suite for AdWordsUtils."""

  TRIGGER_MSG = ('502 Server Error. The server encountered a temporary error'
                 ' and could not complete yourrequest. Please try again in 30 '
                 'seconds.')

  def setUp(self):
    """Prepare unittest."""
    print self.id()

  def testError502(self):
    """Test whether we can handle and report 502 errors."""
    # Temporarily redirect STDOUT into a buffer.
    buf = AdWordsSoapBuffer()
    sys.stdout = buf

    html_code = Utils.ReadFile(os.path.join('data', 'http_error_502.html'))
    print html_code

    # Restore STDOUT.
    sys.stdout = sys.__stdout__

    if not buf.IsHandshakeComplete():
      data = buf.GetBufferAsStr()
    else:
      data = ''

    self.assertEqual(Utils.GetErrorFromHtml(data), self.__class__.TRIGGER_MSG)

  def testDataFileCurrencies(self):
    """Test whether csv data file with currencies is valid."""
    cols = 2
    for item in AdWordsUtils.GetCurrencies():
      self.assertEqual(len(item), cols)

  def testDataFileErrorCodes(self):
    """Test whether csv data file with error codes is valid."""
    cols = 2
    for item in AdWordsUtils.GetErrorCodes():
      self.assertEqual(len(item), cols)

  def testDataFileTimezones(self):
    """Test whether csv data file with timezones is valid."""
    cols = 1
    for item in AdWordsUtils.GetTimezones():
      self.assertEqual(len(item), cols)


def makeTestSuite():
  """Set up test suite.

  Returns:
    TestSuite test suite.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdWordsUtilsTest))
  return suite


if __name__ == '__main__':
  suite = makeTestSuite()
  alltests = unittest.TestSuite([suite])
  unittest.main(defaultTest='alltests')
