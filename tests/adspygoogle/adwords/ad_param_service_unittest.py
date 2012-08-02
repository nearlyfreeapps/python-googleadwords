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

"""Unit tests to cover AdParamService."""

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


class AdParamServiceTestV201109(unittest.TestCase):

  """Unittest suite for AdParamService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  ad_group_id = '0'
  text_ad_id = '0'
  criterion_id = '0'
  has_param = False

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetAdParamService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if (self.__class__.ad_group_id == '0' or self.__class__.text_ad_id == '0' or
        self.__class__.criterion_id == '0'):
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
      campaign_id = campaign_service.Mutate(operations)[0]['value'][0]['id']
      ad_group_service = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'campaignId': campaign_id,
              'name': 'AdGroup #%s' % Utils.GetUniqueName(),
              'status': 'ENABLED',
              'bids': {
                  'xsi_type': 'ManualCPCAdGroupBids',
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
      ad_group_ad_service = client.GetAdGroupAdService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdGroupAd',
              'adGroupId': self.__class__.ad_group_id,
              'ad': {
                  'xsi_type': 'TextAd',
                  'url': 'http://www.example.com',
                  'displayUrl': 'example.com',
                  'description1': 'Good deals, only {param2:} left',
                  'description2': 'Low prices under {param1:}!',
                  'headline': 'MacBook Pro Sale'
              },
              'status': 'ENABLED'
          }
      }]
      self.__class__.text_ad_id = ad_group_ad_service.Mutate(
          operations)[0]['value'][0]['ad']['id']
      ad_group_criterion_service = client.GetAdGroupCriterionService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      operations = [{
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'BiddableAdGroupCriterion',
              'adGroupId': self.__class__.ad_group_id,
              'criterion': {
                  'xsi_type': 'Keyword',
                  'matchType': 'BROAD',
                  'text': 'macbook pro'
              }
          }
      }]
      self.__class__.criterion_id = ad_group_criterion_service.Mutate(
          operations)[0]['value'][0]['criterion']['id']

  def testGetAdParam(self):
    """Test whether we can fetch an existing ad param for a given ad group."""
    if not self.__class__.has_param:
      self.testCreateAdParam()
    selector = {
        'fields': ['AdGroupId', 'CriterionId', 'InsertionText', 'ParamIndex'],
        'predicates': [{
            'field': 'AdGroupId',
            'operator': 'EQUALS',
            'values': [self.__class__.ad_group_id]
        },
        {
            'field': 'CriterionId',
            'operator': 'EQUALS',
            'values': [self.__class__.criterion_id]
        }]
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))

  def testCreateAdParam(self):
    """Test whether we can create a new ad param."""
    operations = [
        {
            'operator': 'SET',
            'operand': {
                'adGroupId': self.__class__.ad_group_id,
                'criterionId': self.__class__.criterion_id,
                'insertionText': '$1,699',
                'paramIndex': '1'
            }
        },
        {
            'operator': 'SET',
            'operand': {
                'adGroupId': self.__class__.ad_group_id,
                'criterionId': self.__class__.criterion_id,
                'insertionText': '139',
                'paramIndex': '2'
            }
        }
    ]
    self.assert_(isinstance(self.__class__.service.Mutate(operations), tuple))
    self.__class__.has_param = True


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdParamServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
