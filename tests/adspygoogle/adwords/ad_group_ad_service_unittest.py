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

"""Unit tests to cover AdGroupAdService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import base64
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


class AdGroupAdServiceTestV201109(unittest.TestCase):

  """Unittest suite for AdGroupAdService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  IMAGE_DATA = Utils.ReadFile(os.path.join('data', 'image.jpg'))
  MOBILE_IMAGE_DATA = Utils.ReadFile(os.path.join('data', 'image_192x53.jpg'))
  IMAGE_DATA = base64.encodestring(IMAGE_DATA)
  MOBILE_IMAGE_DATA = base64.encodestring(MOBILE_IMAGE_DATA)
  client.debug = False
  service = None
  campaign_id = '0'
  ad_group_id = '0'
  ad = None

  def setUp(self):
    """Prepare unittest."""
    if not self.__class__.service:
      self.__class__.service = client.GetAdGroupAdService(
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

  def testAddTextAd(self):
    """Test whether we can add a text ad."""
    operations = [{
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'AdGroupAd',
            'adGroupId': self.__class__.ad_group_id,
            'ad': {
                'xsi_type': 'TextAd',
                'url': 'http://www.example.com',
                'displayUrl': 'example.com',
                'description1': 'Visit the Red Planet in style.',
                'description2': 'Low-gravity fun for everyone!',
                'headline': 'Luxury Cruise to Mars'
            },
            'status': 'ENABLED',
        }
    }]
    ads = self.__class__.service.Mutate(operations)
    self.__class__.ad = ads[0]['value'][0]
    self.assert_(isinstance(ads, tuple))

  def testGetAllAdsFromCampaign(self):
    """Test whether we can fetch all ads from given campaign."""
    selector = {
        'fields': ['AdGroupId', 'Status'],
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
  suite.addTests(unittest.makeSuite(AdGroupAdServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
