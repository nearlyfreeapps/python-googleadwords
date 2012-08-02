#!/usr/bin/python
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

"""This example gets all alerts for all clients of an MCC account. This example
assumes the email and password belong to an MCC.

Tags: AlertService.get
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  alert_service = client.GetAlertService(
      'https://adwords-sandbox.google.com', 'v201206')

  # Construct selector and get all alerts.
  offset = 0
  selector = {
      'query': {
          'clientSpec': 'ALL',
          'filterSpec': 'ALL',
          'types': ['ACCOUNT_BUDGET_BURN_RATE', 'ACCOUNT_BUDGET_ENDING',
                    'ACCOUNT_ON_TARGET', 'CAMPAIGN_ENDED', 'CAMPAIGN_ENDING',
                    'CREDIT_CARD_EXPIRING', 'DECLINED_PAYMENT',
                    'KEYWORD_BELOW_MIN_CPC', 'MANAGER_LINK_PENDING',
                    'MISSING_BANK_REFERENCE_NUMBER', 'PAYMENT_NOT_ENTERED',
                    'TV_ACCOUNT_BUDGET_ENDING', 'TV_ACCOUNT_ON_TARGET',
                    'TV_ZERO_DAILY_SPENDING_LIMIT', 'USER_INVITE_ACCEPTED',
                    'USER_INVITE_PENDING', 'ZERO_DAILY_SPENDING_LIMIT'],
          'severities': ['GREEN', 'YELLOW', 'RED'],
          'triggerTimeSpec': 'ALL_TIME'
      },
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = alert_service.Get(selector)[0]
    # Display results.
    if 'entries' in page:
      for alert in page['entries']:
        print ('Alert of type \'%s\' and severity \'%s\' for account \'%s\' was'
               ' found.' % (alert['alertType'], alert['alertSeverity'],
                            alert['clientCustomerId']))
    else:
      print 'No alerts were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))

if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))
  client.use_mcc = True
  main(client)
