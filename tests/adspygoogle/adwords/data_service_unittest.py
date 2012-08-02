#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

"""Unit tests to cover DataService."""

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
from adspygoogle.common import Utils


class DataServiceTestV201109(unittest.TestCase):

  """Unittest suite for DataService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  campaign_id = '0'
  ad_group_id = '0'
  criterion_id = '0'

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetDataService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
    if self.__class__.campaign_id == '0' or self.__class__.ad_group_id == '0':
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
              'budget': {
                  'period': 'DAILY',
                  'amount': {
                      'microAmount': '1000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      self.__class__.campaign_id = campaign_service.Mutate(
          operations)[0]['value'][0]['id']
      ad_group_service = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'campaignId': self.__class__.campaign_id,
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
      self.__class__.ad_group_id = ad_group_service.Mutate(
          operations)[0]['value'][0]['id']
      operations = [{
          'operator': 'ADD',
          'operand': {
              'type': 'BiddableAdGroupCriterion',
              'adGroupId': self.__class__.ad_group_id,
              'criterion': {
                  'xsi_type': 'Keyword',
                  'matchType': 'BROAD',
                  'text': 'mars cruise'
              }
          }
      }]
      ad_group_criterion_service = client.GetAdGroupCriterionService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      criteria = ad_group_criterion_service.Mutate(operations)
      self.__class__.criterion_id = criteria[0]['value'][0]['criterion']['id']

  def testGetAdGroupBidLandscape(self):
    """Test whether we can retrieve AdGroupBidLandscape."""
    selector = {
        'fields': ['CampaignId', 'AdGroupId', 'StartDate', 'EndDate',
                   'LandscapeType'],
        'predicates': [
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [self.__class__.ad_group_id]
            }
        ]
    }
    self.assert_(isinstance(self.__class__.service
                            .GetAdGroupBidLandscape(selector), tuple))

  def testGetCriterionBidLandscape(self):
    """Test whether we can retrieve CriterionBidLandscape."""
    selector = {
        'fields': ['CampaignId', 'AdGroupId', 'StartDate', 'EndDate',
                   'CriterionId'],
        'predicates': [
            {
                'field': 'CriterionId',
                'operator': 'EQUALS',
                'values': [self.__class__.criterion_id]
            }
        ]
    }
    self.assert_(isinstance(self.__class__.service
                            .GetCriterionBidLandscape(selector), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(DataServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
