#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

"""Unit tests to cover UserListService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import time
import unittest

from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class UserListServiceTestV201109(unittest.TestCase):

  """Unittest suite for UserListService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  user_list = None

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetUserListService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

  def testAddRemarketingUserList(self):
    """Test whether we can add a remarketing user list."""
    operations = [
        {
            'operator': 'ADD',
            'operand': {
                'xsi_type': 'RemarketingUserList',
                'name': 'Mars cruise customers #%s' % Utils.GetUniqueName(),
                'description': ('A list of mars cruise customers in the last ' +
                                'year.'),
                'membershipLifeSpan': '365',
                'conversionTypes': [
                    {
                        'name': ('Mars cruise customers #%s'
                                 % Utils.GetUniqueName())
                    }
                ]
            }
        }
    ]
    user_lists = self.__class__.service.Mutate(operations)
    self.__class__.user_list = user_lists[0]['value'][0]
    self.assert_(isinstance(user_lists, tuple))

  def testGetAllUserLists(self):
    """Test whether we can retrieve all user lists."""
    selector = {
        'fields': ['Id', 'Name', 'Status']
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(UserListServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
