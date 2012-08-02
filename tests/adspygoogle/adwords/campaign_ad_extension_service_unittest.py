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

"""Unit tests to cover CampaignAdExtensionService."""

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


class CampaignAdExtensionServiceTestV201109(unittest.TestCase):

  """Unittest suite for CampaignAdExtensionService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  campaign_id = '0'
  geo_location = None
  address = {
      'streetAddress': '1600 Amphitheatre Parkway',
      'cityName': 'Mountain View',
      'provinceCode': 'CA',
      'postalCode': '94043',
      'countryCode': 'US'
  }

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetCampaignAdExtensionService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if self.__class__.campaign_id == '0':
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

    if not self.__class__.geo_location:
      geo_location_service = client.GetGeoLocationService(
          self.__class__.SERVER, self.__class__.VERSION)
      selector = {
          'addresses': [self.__class__.address]
      }
      self.__class__.geo_location = \
          geo_location_service.Get(selector)[0]

  def testGetAdExtensionOverrides(self):
    """Test whether we can fetch existing ad extension overrides."""
    selector = {
        'fields': ['CampaignId', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': [self.__class__.campaign_id]
            },
            {
                'field': 'Status',
                'operator': 'EQUALS',
                'values': ['ACTIVE']
            }
        ]
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))

  def testAddAdExtensionOverride(self):
    """Test whether we can add ad extension override to a given campaign."""
    operations = [{
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'CampaignAdExtension',
            'campaignId': self.__class__.campaign_id,
            'adExtension': {
                'xsi_type': 'LocationExtension',
                'address': self.__class__.geo_location['address'],
                'geoPoint': self.__class__.geo_location['geoPoint'],
                'encodedLocation':
                    self.__class__.geo_location['encodedLocation'],
                'source': 'ADWORDS_FRONTEND'
            }
        }
    }]
    self.assert_(isinstance(self.__class__.service.Mutate(operations), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(CampaignAdExtensionServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
