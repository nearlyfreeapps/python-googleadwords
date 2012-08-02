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

"""This example gets all text ads for a given ad group. To add an ad, run
add_text_ads.py.

Tags: AdGroupAdService.get
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


PAGE_SIZE = 500
ad_group_id = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetAdGroupAdService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct selector and get all ads for a given ad group.
  offset = 0
  selector = {
      'fields': ['Id', 'AdGroupId', 'Status'],
      'predicates': [
          {
              'field': 'AdGroupId',
              'operator': 'EQUALS',
              'values': [ad_group_id]
          },
          {
              'field': 'AdType',
              'operator': 'EQUALS',
              'values': ['TEXT_AD']
          }
      ],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = ad_group_ad_service.Get(selector)[0]

    # Display results.
    if 'entries' in page:
      for ad in page['entries']:
        print ('Ad with id \'%s\', status \'%s\', and of type \'%s\' was found.'
               % (ad['ad']['id'], ad['status'], ad['ad']['Ad_Type']))
    else:
      print 'No ads were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_group_id)
