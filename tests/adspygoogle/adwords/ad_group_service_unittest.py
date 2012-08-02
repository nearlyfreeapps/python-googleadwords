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

"""Unit tests to cover AdGroupService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest
from datetime import date

from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class AdGroupServiceTestV201109(unittest.TestCase):

  """Unittest suite for AdGroupService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  client.raw_debug = False
  service = None
  cpc_campaign_id = '0'
  cpm_campaign_id = '0'
  ad_group = None

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if self.__class__.cpc_campaign_id == '0':
      campaign_service = client.GetCampaignService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'name': 'Campaign #%s' % Utils.GetUniqueName(),
              'status': 'PAUSED',
              'biddingStrategy': {
                  'type': 'ManualCPC'
              },
              'endDate': date(date.today().year + 1, 12, 31).strftime('%Y%m%d'),
              'budget': {
                  'period': 'DAILY',
                  'amount': {
                      'microAmount': '2000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      self.__class__.cpc_campaign_id = campaign_service.Mutate(
          operations)[0]['value'][0]['id']
    if self.__class__.cpm_campaign_id == '0':
      campaign_service = client.GetCampaignService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'name': 'Campaign #%s' % Utils.GetUniqueName(),
              'status': 'PAUSED',
              'biddingStrategy': {
                  'type': 'ManualCPM'
              },
              'endDate': date(date.today().year + 1, 12, 31).strftime('%Y%m%d'),
              'budget': {
                  'period': 'DAILY',
                  'amount': {
                      'microAmount': '2000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      self.__class__.cpm_campaign_id = campaign_service.Mutate(
          operations)[0]['value'][0]['id']

  def testAddAdGroupKeyword(self):
    """Test whether we can add an ad group for keywords."""
    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': self.__class__.cpc_campaign_id,
            'name': 'AdGroup #%s' % Utils.GetUniqueName(),
            'status': 'ENABLED',
            'bids': {
                'type': 'ManualCPCAdGroupBids',
                'keywordMaxCpc': {
                    'amount': {
                        'microAmount': '1000000'
                    }
                }
            }
        }
    }]
    ad_groups = self.__class__.service.Mutate(operations)
    self.__class__.ad_group = ad_groups[0]['value'][0]
    self.assert_(isinstance(ad_groups, tuple))

  def testGetAdGroup(self):
    """Test whether we can fetch an existing ad group."""
    if self.__class__.ad_group is None:
      self.testAddAdGroupKeyword()
    selector = {
        'fields': ['Id', 'Name'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': [self.__class__.cpc_campaign_id]
            },
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [self.__class__.ad_group['id']]
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
  suite.addTests(unittest.makeSuite(AdGroupServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
