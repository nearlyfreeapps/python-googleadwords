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

"""Unit tests to cover TargetingIdeaService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import unittest
from datetime import date

from adspygoogle.adwords.AdWordsErrors import AdWordsRequestError
from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import VERSION_V201109
from tests.adspygoogle.adwords import client


class TargetingIdeaServiceTestV201109(unittest.TestCase):

  """Unittest suite for TargetingIdeaService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  TRIGGER_MSG = 'RequiredError.REQUIRED @ selector'
  client.debug = False
  service = None
  ad_group_id = '0'

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetTargetingIdeaService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if self.__class__.ad_group_id == '0':
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
                      'microAmount': '1000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      campaign_id = client.GetCampaignService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY).Mutate(
              operations)[0]['value'][0]['id']
      operations = [{
          'operator': 'ADD',
          'operand': {
              'campaignId': campaign_id,
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
      self.__class__.ad_group_id = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY).Mutate(
              operations)[0]['value'][0]['id']

  def testGetRelatedToUrlSearchParameter(self):
    """Test whether we can request related to url search parameter."""
    selector = {
        'searchParameters': [{
            'type': 'RelatedToUrlSearchParameter',
            'urls': ['http://finance.google.com'],
            'includeSubUrls': 'false'
        }],
        'ideaType': 'PLACEMENT',
        'requestType': 'IDEAS',
        'paging': {
            'startIndex': '0',
            'numberResults': '1'
        }
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))

  def testGetBulkKeywordIdeas(self):
    """Test whether we can request bulk keyword ideas."""
    selector = {
        'searchParameters': [
            {
                'type': 'RelatedToKeywordSearchParameter',
                'keywords': [
                    {
                        'text': 'presidential vote',
                        'matchType': 'EXACT'
                    }
                ]
            },
            {
                'type': 'RelatedToUrlSearchParameter',
                'urls': ['http://finance.google.com'],
                'includeSubUrls': 'false'
            }
        ],
        'ideaType': 'KEYWORD',
        'requestType': 'IDEAS',
        'paging': {
            'startIndex': '0',
            'numberResults': '1'
        }
    }
    self.assert_(isinstance(
        self.__class__.service.GetBulkKeywordIdeas(selector), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TargetingIdeaServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
