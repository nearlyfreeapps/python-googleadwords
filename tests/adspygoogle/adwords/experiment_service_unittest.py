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

"""Unit tests to cover ExperimentService."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import datetime
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


class ExperimentServiceTestV201109(unittest.TestCase):

  """Unittest suite for ExperimentService using v201109."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  service = None
  ad_group_service = None
  campaign_id = '0'
  ad_group_id = '0'
  kw_id = '0'
  experiment = None

  def setUp(self):
    """Prepare unittest."""
    print self.id()
    if not self.__class__.service or not self.__class__.ad_group_service:
      self.__class__.service = client.GetExperimentService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      self.__class__.ad_group_service = client.GetAdGroupService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
      self.__class__.ad_group_criterion_service = \
          client.GetAdGroupCriterionService(self.__class__.SERVER,
                                            self.__class__.VERSION, HTTP_PROXY)

    if (self.__class__.campaign_id == '0' or
        self.__class__.ad_group_id == '0' or self.__class__.kw_id == '0'):
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
                      'microAmount': '10000000'
                  },
                  'deliveryMethod': 'STANDARD'
              }
          }
      }]
      self.__class__.campaign_id = campaign_service.Mutate(
          operations)[0]['value'][0]['id']
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
      self.__class__.ad_group_id = self.__class__.ad_group_service.Mutate(
          operations)[0]['value'][0]['id']
      criterion_service = client.GetAdGroupCriterionService(
          self.__class__.SERVER, self.__class__.VERSION, HTTP_PROXY)
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
      self.__class__.kw_id = criterion_service.Mutate(
          operations)[0]['value'][0]['criterion']['id']

  def testAddExperiment(self):
    """Test whether we can add an experiment."""
    today = datetime.datetime.now() + datetime.timedelta(hours=1)
    operations = [
        {
            'operator': 'ADD',
            'operand': {
                'campaignId': self.__class__.campaign_id,
                'name': 'Interplanetary Experiment #%s' % Utils.GetUniqueName(),
                'queryPercentage': '10',
                'startDateTime': today.strftime('%Y%m%d %H%M%S')
            }
        }
    ]
    experiments = self.__class__.service.Mutate(operations)
    self.__class__.experiment = experiments[0]['value'][0]
    self.assert_(isinstance(experiments, tuple))

    operations = [
        {
            'operator': 'SET',
            'operand': {
                'id': self.__class__.ad_group_id,
                'experimentData': {
                    'xsi_type': 'AdGroupExperimentData',
                    'experimentId': self.__class__.experiment['id'],
                    'experimentDeltaStatus': 'MODIFIED',
                    'experimentBidMultipliers': {
                        'xsi_type': 'ManualCPCAdGroupExperimentBidMultipliers',
                        'maxCpcMultiplier': {
                            'multiplier': '1.5'
                        }
                    }
                }
            }
        }
    ]
    self.assert_(isinstance(self.__class__.ad_group_service.Mutate(operations),
                            tuple))

    operations = [
        {
            'operator': 'ADD',
            'operand': {
                'xsi_type': 'BiddableAdGroupCriterion',
                'adGroupId': self.__class__.ad_group_id,
                'criterion': {
                    'xsi_type': 'Keyword',
                    'matchType': 'BROAD',
                    'text': 'mars cruise'
                },
                'experimentData': {
                    'xsi_type': 'BiddableAdGroupCriterionExperimentData',
                    'experimentId': self.__class__.experiment['id'],
                    'experimentDeltaStatus': 'EXPERIMENT_ONLY'
                }
            }
        }
    ]
    self.assert_(isinstance(
        self.__class__.ad_group_criterion_service.Mutate(operations), tuple))

  def testGetAllExperiments(self):
    """Test whether we can retrieve all experiments."""
    if self.__class__.experiment is None:
      self.testAddExperiment()
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [{
            'field': 'CampaignId',
            'operator': 'EQUALS',
            'values': [self.__class__.campaign_id]
        }]
    }
    self.assert_(isinstance(self.__class__.service.Get(selector), tuple))


def makeTestSuiteV201109():
  """Set up test suite using v201109.

  Returns:
    TestSuite test suite using v201109.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(ExperimentServiceTestV201109))
  return suite


if __name__ == '__main__':
  suites = []
  if TEST_VERSION_V201109:
    suites.append(makeTestSuiteV201109())
  if suites:
    alltests = unittest.TestSuite(suites)
    unittest.main(defaultTest='alltests')
