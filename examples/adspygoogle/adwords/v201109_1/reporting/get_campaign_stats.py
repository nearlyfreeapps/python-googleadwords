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

"""This example gets stats for all campaigns with an impression in the last
week. To add a campaign, run add_campaign.py.

Tags: CampaignService.get
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import datetime
import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  campaign_service = client.GetCampaignService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct selector and get all campaigns.
  offset = 0
  selector = {
      'fields': ['Id', 'Name', 'Impressions', 'Clicks', 'Cost', 'Ctr'],
      'predicates': [{
          'field': 'Impressions',
          'operator': 'GREATER_THAN',
          'values': ['0']
      }],
      'dateRange': {
          'min': (datetime.datetime.now() -
                  datetime.timedelta(7)).strftime('%Y%m%d'),
          'max': (datetime.datetime.now() -
                  datetime.timedelta(1)).strftime('%Y%m%d')
      },
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }

  more_pages = True
  while more_pages:
    page = campaign_service.Get(selector)[0]

    # Display results.
    if 'entries' in page:
      for campaign in page['entries']:
        print ('Campaign with id \'%s\' and name \'%s\' had the following '
               'stats during the last week.' % (campaign['id'],
                                                campaign['name']))
        print '  Impressions: %s' % campaign['campaignStats']['impressions']
        print '  Clicks: %s' % campaign['campaignStats']['clicks']
        cost = int(campaign['campaignStats']['cost']['microAmount']) / 1000000
        print '  Cost: %.02f' % cost
        ctr = float(campaign['campaignStats']['ctr']) * 100
        print '  CTR: %.02f %%' % ctr
    else:
      print 'No matching campaigns were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client)
