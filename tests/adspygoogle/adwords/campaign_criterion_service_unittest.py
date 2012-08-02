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

"""Unit tests to cover CampaignCriterionService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

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


class CampaignCriterionServiceTestV201109(unittest.TestCase):

  """Unittest suite for CampaignCriterionService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  campaign_id = '0'
  kw = None

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetCampaignCriterionService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if (self.__class__.campaign_id == '0'):
      campaign_service = client.GetCampaignService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'name': 'Campaign #%s' % Utils.GetUniqueName(),
              'status': 'PAUSED',
              'biddingStrategy': {
                  'xsi_type': 'ManualCPC'
              },
              'budget': {
                  'period': 'DAILY',
                  'amount': {
                      'microAmount': '1000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      self.__class__.campaign_id = \
          campaign_service.Mutate(operations)[0]['value'][0]['id']

  def testAddCriterionKeyword(self):
    """Test whether we can add an ad group criterion keyword."""
    operations = [{
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'NegativeCampaignCriterion',
            'campaignId': self.__class__.campaign_id,
            'criterion': {
                'xsi_type': 'Keyword',
                'matchType': 'BROAD',
                'text': 'mars cruise'
            }
        }
    }]
    criteria = self.__class__.service.Mutate(operations)
    self.__class__.kw = criteria[0]['value'][0]
    self.assert_(isinstance(criteria, tuple))

  def testGetAllCriteriaCampaignLevel(self):
    """Test whether we can fetch criteria at campaign level."""
    selector = {
        'fields': ['CampaignId'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': [self.__class__.campaign_id]
            }
        ]
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(CampaignCriterionServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
