#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Unit tests for issues #16 and #25.

Unicode characters don't serialize/deserialize properly.
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from adspygoogle.adwords.AdWordsClient import AdWordsClient
from adspygoogle.common import Utils
from datetime import date


class Issue16(unittest.TestCase):

  """Unittests for Issue #16."""

  def testSendReceiveUnicode(self):
    """Tests if we can send/receive unicode characters."""
    client = AdWordsClient(path=os.path.join('..', '..', '..'))
    campaign_service = client.GetCampaignService(
      'https://adwords-sandbox.google.com', 'v201109')

    # Construct operations and add campaign.
    operations = [{
        'operator': 'ADD',
        'operand': {
            'name': 'межпланетных круиз #%s' % Utils.GetUniqueName(),
            'status': 'PAUSED',
            'biddingStrategy': {
                'xsi_type': 'ManualCPC'
            },
            'endDate': date(date.today().year + 1, 12, 31).strftime('%Y%m%d'),
            'budget': {
                'period': 'DAILY',
                'amount': {
                    'microAmount': '50000000'
                },
                'deliveryMethod': 'STANDARD'
            },
            'networkSetting': {
                'targetGoogleSearch': 'true',
                'targetSearchNetwork': 'true',
                'targetContentNetwork': 'false',
                'targetContentContextual': 'false',
                'targetPartnerSearchNetwork': 'false'
            }
        }
    }, {
        'operator': 'ADD',
        'operand': {
            'name': u'межпланетных круиз #%s' % Utils.GetUniqueName(),
            'status': 'PAUSED',
            'biddingStrategy': {
                'xsi_type': 'ManualCPC'
            },
            'endDate': date(date.today().year + 1, 12, 31).strftime('%Y%m%d'),
            'budget': {
                'period': 'DAILY',
                'amount': {
                    'microAmount': '50000000'
                },
                'deliveryMethod': 'STANDARD'
            },
            'networkSetting': {
                'targetGoogleSearch': 'true',
                'targetSearchNetwork': 'true',
                'targetContentNetwork': 'false',
                'targetContentContextual': 'false',
                'targetPartnerSearchNetwork': 'false'
            }
        }
    }]
    campaigns = campaign_service.Mutate(operations)[0]

    # Display results.
    for campaign in campaigns['value']:
      print ('Campaign with name \'%s\' and id \'%s\' was added.'
             % (campaign['name'], campaign['id']))


if __name__ == '__main__':
  unittest.main()
