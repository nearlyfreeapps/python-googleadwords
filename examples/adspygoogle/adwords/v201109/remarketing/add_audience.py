#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.
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

"""This example adds a remarketing user list (a.k.a. audience).

Tags: UserListService.mutate
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient
from adspygoogle.common import Utils


def main(client):
  # Initialize appropriate service.
  user_list_service = client.GetUserListService(
      'https://adwords-sandbox.google.com', 'v201109')
  conversion_tracker_service = client.GetConversionTrackerService(
      'https://adwords-sandbox.google.com', 'v201109')

  # Construct operations and add a user list.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'RemarketingUserList',
              'name': 'Mars cruise customers #%s' % Utils.GetUniqueName(),
              'description': 'A list of mars cruise customers in the last year',
              'membershipLifeSpan': '365',
              'conversionTypes': [
                  {
                      'name': ('Mars cruise customers #%s'
                               % Utils.GetUniqueName())
                  }
              ],
              # Optional field.
              'status': 'OPEN',
          }
      }
  ]
  result = user_list_service.Mutate(operations)[0]

  # Display results.
  if 'value' in result:
    conversion_ids = []
    for user_list in result['value']:
      if user_list['conversionTypes']:
        for conversion_type in user_list['conversionTypes']:
          conversion_ids.append(conversion_type['id'])

    selector = {
        'fields': ['Name', 'Status', 'Category'],
        'predicates': [{
            'field': 'Id',
            'operator': 'IN',
            'values': conversion_ids
        }],
        'ordering': [{
            'field': 'Name',
            'sortOrder': 'ASCENDING'
        }]
    }

    pages = conversion_tracker_service.Get(selector)[0]
    conversions_map = {}
    if pages['entries']:
      for conversion_tracker in pages['entries']:
        conversions_map[conversion_tracker['id']] = conversion_tracker

    for user_list in result['value']:
      print ('User list with name \'%s\' and id \'%s\' was added.'
             % (user_list['name'], user_list['id']))
      if user_list['conversionTypes']:
        for conversion_type in user_list['conversionTypes']:
          conversion_tracker = conversions_map[conversion_type['id']]
          print ('Conversion type code snippet associated to the list:\n%s\n'
                 % conversion_tracker['snippet'])
  else:
    print 'No user lists were added.'

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client)
