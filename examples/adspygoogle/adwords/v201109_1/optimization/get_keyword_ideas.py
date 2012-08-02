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

"""This example retrieves keywords that are related to a given keyword.

Tags: TargetingIdeaService.get
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  targeting_idea_service = client.GetTargetingIdeaService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct selector object and retrieve related keywords.
  offset = 0
  keyword = 'space cruise'
  selector = {
      'searchParameters': [{
          'xsi_type': 'RelatedToKeywordSearchParameter',
          'keywords': [{
              'text': keyword,
              'matchType': 'EXACT'
          }]
      }],
      'ideaType': 'KEYWORD',
      'requestType': 'IDEAS',
      'requestedAttributeTypes': ['CRITERION',
                                  'CATEGORY_PRODUCTS_AND_SERVICES'],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = targeting_idea_service.Get(selector)[0]

    # Display results.
    if 'entries' in page:
      for result in page['entries']:
        result_attr1 = result['data'][0]['value']
        result_attr2 = result['data'][1]['value']
        print ('Keyword with \'%s\' text and \'%s\' match type is found.'
               % (result_attr1['value']['text'],
                  result_attr1['value']['matchType']))
        if 'value' in result_attr2:
          print ('  With Products and Services categories %s'
                 % result_attr2['value'])
      print
      print ('Total keywords found related to \'%s\': %s'
             % (keyword, page['totalNumEntries']))
    else:
      print 'No keywords found related to \'%s\'.' % keyword
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
