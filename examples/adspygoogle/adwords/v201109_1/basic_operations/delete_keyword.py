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

"""This example deletes an ad group criterion using the 'REMOVE' operator. To
get ad group criteria, run get_keywords.py.

Tags: AdGroupCriterionService.mutate
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


ad_group_id = 'INSERT_AD_GROUP_ID_HERE'
criterion_id = 'INSERT_CRITERION_ID_HERE'


def main(client, ad_group_id, criterion_id):
  # Initialize appropriate service.
  ad_group_criterion_service = client.GetAdGroupCriterionService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct operations and delete ad group criteria.
  operations = [
      {
          'operator': 'REMOVE',
          'operand': {
              'xsi_type': 'BiddableAdGroupCriterion',
              'adGroupId': ad_group_id,
              'criterion': {
                  'id': criterion_id
              }
          }
      }
  ]
  result = ad_group_criterion_service.Mutate(operations)[0]

  # Display results.
  for criterion in result['value']:
    print ('Ad group criterion with ad group id \'%s\', criterion id \'%s\', '
           'and type \'%s\' was deleted.'
           % (criterion['adGroupId'], criterion['criterion']['id'],
              criterion['criterion']['Criterion_Type']))

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_group_id, criterion_id)
