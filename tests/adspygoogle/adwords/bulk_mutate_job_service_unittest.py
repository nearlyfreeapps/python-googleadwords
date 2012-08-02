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

"""Unit tests to cover BulkMutateJobService."""

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


class BulkMutateJobServiceTestV201109(unittest.TestCase):

  """Unittest suite for BulkMutateJobService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  campaign_id = '0'
  ad_group_id1 = '0'
  ad_group_id2 = '0'

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service:
      self.__class__.service = client.GetBulkMutateJobService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)

    if self.__class__.campaign_id == '0':
      operations = [
          {
              'operator': 'ADD',
              'operand': {
                  'name': 'Campaign #%s' % Utils.GetUniqueName(),
                  'status': 'PAUSED',
                  'biddingStrategy': {
                      'xsi_type': 'ManualCPC'
                  },
                  'endDate': date(date.today().year + 1,
                                  12, 31).strftime('%Y%m%d'),
                  'budget': {
                      'period': 'DAILY',
                      'amount': {
                          'microAmount': '1000000'
                      },
                      'deliveryMethod': 'STANDARD'
                  }
              }
          }
      ]
      service = client.GetCampaignService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      self.__class__.campaign_id = service.Mutate(
          operations)[0]['value'][0]['id']

    if (self.__class__.ad_group_id1 == '0' or
        self.__class__.ad_group_id2 == '0'):
      operations = [
          {
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'AdGroup',
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
          },
          {
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'AdGroup',
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
          }
      ]
      service = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      ad_groups = service.Mutate(operations)[0]['value']
      self.__class__.ad_group_id1 = ad_groups[0]['id']
      self.__class__.ad_group_id2 = ad_groups[1]['id']

  def testMultiplePartsMultipleStreams(self):
    """Test whether we can add ads and keywords using multiple part job with
    multiple streams."""
    ad_stream1_ops = []
    for _ in xrange(25):
      ad_stream1_ops.append(
          {
              'xsi_type': 'AdGroupAd',
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'AdGroupAd',
                  'adGroupId': self.__class__.ad_group_id1,
                  'ad': {
                      'xsi_type': 'TextAd',
                      'url': 'http://www.example.com',
                      'displayUrl': 'example.com',
                      'description1': 'Visit the Red Planet in style.',
                      'description2': 'Low-gravity fun for everyone!',
                      'headline': 'Luxury Cruise to Mars'

                  },
                  'status': 'ENABLED'
              }
          })
    ad_stream1 = {
        'scopingEntityId': {
            'type': 'CAMPAIGN_ID',
            'value': self.__class__.campaign_id,
        },
        'operations': ad_stream1_ops
    }

    ad_stream2_ops = []
    for _ in xrange(25):
      ad_stream2_ops.append(
          {
              'xsi_type': 'AdGroupAd',
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'AdGroupAd',
                  'adGroupId': self.__class__.ad_group_id2,
                  'ad': {
                      'xsi_type': 'TextAd',
                      'url': 'http://www.example.com',
                      'displayUrl': 'example.com',
                      'description1': 'Visit the Red Planet in style.',
                      'description2': 'Low-gravity fun for everyone!',
                      'headline': 'Luxury Cruise to Mars is here now!!!'

                  },
                  'status': 'ENABLED'
              }
          })
    ad_stream2 = {
        'scopingEntityId': {
            'type': 'CAMPAIGN_ID',
            'value': self.__class__.campaign_id,
        },
        'operations': ad_stream2_ops
    }
    part1 = {
        'partIndex': '0',
        'operationStreams': [ad_stream1, ad_stream2]
    }
    operation = {
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'BulkMutateJob',
            'request': part1,
            'numRequestParts': '2'
        }
    }
    job = self.__class__.service.Mutate(operation)
    self.assert_(isinstance(job, tuple))

    kw_stream1_ops = []
    for _ in xrange(25):
      kw_stream1_ops.append(
          {
              'xsi_type': 'AdGroupCriterion',
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'BiddableAdGroupCriterion',
                  'adGroupId': self.__class__.ad_group_id1,
                  'criterion': {
                      'xsi_type': 'Keyword',
                      'matchType': 'BROAD',
                      'text': 'mars cruise'
                  }
              }
          })
    kw_stream1 = {
        'scopingEntityId': {
            'type': 'CAMPAIGN_ID',
            'value': self.__class__.campaign_id,
        },
        'operations': kw_stream1_ops
    }

    kw_stream2_ops = []
    for _ in xrange(25):
      kw_stream2_ops.append(
          {
              'xsi_type': 'AdGroupCriterion',
              'operator': 'ADD',
              'operand': {
                  'xsi_type': 'BiddableAdGroupCriterion',
                  'adGroupId': self.__class__.ad_group_id2,
                  'criterion': {
                      'xsi_type': 'Keyword',
                      'matchType': 'BROAD',
                      'text': 'mars cruise'
                  }
              }
          })
    kw_stream2 = {
        'scopingEntityId': {
            'type': 'CAMPAIGN_ID',
            'value': self.__class__.campaign_id,
        },
        'operations': kw_stream2_ops
    }
    part2 = {
        'partIndex': '1',
        'operationStreams': [kw_stream1, kw_stream2]
    }
    operation = {
        'operator': 'SET',
        'operand': {
            'xsi_type': 'BulkMutateJob',
            'id': job[0]['id'],
            'request': part2
        }
    }
    job = self.__class__.service.Mutate(operation)
    self.assert_(isinstance(job, tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(BulkMutateJobServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
