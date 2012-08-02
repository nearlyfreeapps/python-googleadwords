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

"""TThis example demonstrates how to handle partial failures. To get ad groups,
run get_ad_groups.py.

Tags: AdGroupCriterionService.mutate
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import re
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


ad_group_id = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Enable partial failure.
  client.partial_failure = True

  # Initialize appropriate service.
  ad_group_criterion_service = client.GetAdGroupCriterionService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct keyword ad group criteria objects.
  keywords = [
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'mars cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'inv\@lid cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'venus cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'b\(a\)d keyword cruise'
          }
      }
  ]

  # Construct operations and add ad group criteria.
  operations = []
  for keyword in keywords:
    operations.append(
        {
            'operator': 'ADD',
            'operand': keyword
        })
  result = ad_group_criterion_service.Mutate(operations)[0]

  # Display results.
  for criterion in result['value']:
    if criterion['AdGroupCriterion_Type'] == 'BiddableAdGroupCriterion':
      print ('Added keyword ad group criterion with ad group id \'%s\', '
             'criterion id \'%s\', text \'%s\', and match type \'%s\' was '
             'added.'
             % (criterion['adGroupId'], criterion['criterion']['id'],
                criterion['criterion']['text'],
                criterion['criterion']['matchType']))

  for error in result['partialFailureErrors']:
    index = re.findall('operations\[(.*)\]\.', error['fieldPath'])
    if index:
      print ('Keyword ad group criterion with ad group id \'%s\' and text '
             '\'%s\' triggered a failure for the following reason: \'%s\'.'
             % (keywords[int(index[0])]['adGroupId'],
                keywords[int(index[0])]['criterion']['text'],
                error['errorString']))
    else:
      print 'The following failure has occurred: \'%s\'.' % error['errorString']

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_group_id)
