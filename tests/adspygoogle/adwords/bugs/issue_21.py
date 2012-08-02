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

"""Unit tests for issue #21.

validateOnly header was not being lower-cased.  Increased XML validation in
v201109 meant this field was ignored when sent as True/False.
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from adspygoogle.adwords.AdWordsClient import AdWordsClient


class Issue21(unittest.TestCase):

  """Unittests for Issue #21."""

  def testNewAdWordsClient(self):
    """Tests if the constructor handlers interpreting the header value."""
    self.assertDefaultConstructor('y', 'true')
    self.assertDefaultConstructor('true', 'true')
    self.assertDefaultConstructor('1', 'true')
    self.assertDefaultConstructor('True', 'true')
    self.assertDefaultConstructor('n', 'false')
    self.assertDefaultConstructor('false', 'false')
    self.assertDefaultConstructor('0', 'false')
    self.assertDefaultConstructor('False', 'false')

  def testSetters(self):
    """Tests if the setters also handle properly interpreting the value."""
    self.assertSetter('y', 'true')
    self.assertSetter('true', 'true')
    self.assertSetter('1', 'true')
    self.assertSetter('True', 'true')
    self.assertSetter('n', 'false')
    self.assertSetter('false', 'false')
    self.assertSetter('0', 'false')
    self.assertSetter('False', 'false')

  def assertSetter(self, value, expected):
    """Constructs an AdWordsClient and sets value using setters..

    Tests that the provided value is parsed to the expected value in the setter
    methods method.

    Args:
      value: multiple Value to test.
      expected: multiple Expected value.
    """
    client = AdWordsClient(headers={
        'authToken': '...',
        'clientCustomerId': '1234567890',
        'userAgent': 'GoogleTest',
        'developerToken': 'johndoe@example.com++USD'
    })
    client.partial_failure = value
    client.validate_only = value
    self.assertEquals(client.partial_failure, expected)

  def assertDefaultConstructor(self, value, expected):
    """Constructs an AdWordsClient using value in headers.

    Tests that the provided value is parsed to the expected value in the
    __init__ method.

    Args:
      value: multiple Value to test.
      expected: multiple Expected value.
    """
    client = AdWordsClient(headers={
        'authToken': '...',
        'clientCustomerId': '1234567890',
        'userAgent': 'GoogleTest',
        'developerToken': 'johndoe@example.com++USD',
        'validateOnly': value,
        'partialFailure': value
    })
    self.assertEquals(client.partial_failure, expected)
    self.assertEquals(client.validate_only, expected)


if __name__ == '__main__':
  unittest.main()
