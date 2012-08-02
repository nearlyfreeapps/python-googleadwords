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

"""This example updates status for a given ad. To get ads, run
get_text_ads.py.

Tags: AdGroupAdService.mutate
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


ad_group_id = 'INSERT_AD_GROUP_ID_HERE'
ad_id = 'INSERT_AD_ID_HERE'


def main(client, ad_group_id, ad_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetAdGroupAdService(
      'https://adwords-sandbox.google.com', 'v201109')

  # Construct operations and update an ad.
  operations = [{
      'operator': 'SET',
      'operand': {
          'adGroupId': ad_group_id,
          'ad': {
              'id': ad_id,
          },
          'status': 'PAUSED'
      }
  }]
  ads = ad_group_ad_service.Mutate(operations)[0]

  # Display results.
  for ad in ads['value']:
    print 'Ad with id \'%s\' was updated.'% ad['ad']['id']

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_group_id, ad_id)
