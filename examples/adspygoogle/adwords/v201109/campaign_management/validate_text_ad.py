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

"""This example shows how to use validateOnly SOAP header.

Tags: CampaignService.mutate
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient
from adspygoogle.adwords.AdWordsErrors import AdWordsRequestError


ad_group_id = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service with validate only flag enabled.
  client.validate_only = True
  ad_group_ad_service = client.GetAdGroupAdService(
      'https://adwords-sandbox.google.com', 'v201109')

  # Construct operations to add a text ad.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'xsi_type': 'AdGroupAd',
          'adGroupId': ad_group_id,
          'ad': {
              'xsi_type': 'TextAd',
              'url': 'http://www.example.com',
              'displayUrl': 'example.com',
              'description1': 'Visit the Red Planet in style.',
              'description2': 'Low-gravity fun for everyone!',
              'headline': 'Luxury Cruise to Mars'
          }
      }
  }]
  ad_group_ad_service.Mutate(operations)
  # No error means the request is valid.

  # Now let's check an invalid ad using a very long line to trigger an error.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'xsi_type': 'AdGroupAd',
          'adGroupId': ad_group_id,
          'ad': {
              'xsi_type': 'TextAd',
              'url': 'http://www.example.com',
              'displayUrl': 'example.com',
              'description1': 'Visit the Red Planet in style.',
              'description2': 'Low-gravity fun for all astronauts in orbit',
              'headline': 'Luxury Cruise to Mars'
          }
      }
  }]
  try:
    ad_group_ad_service.Mutate(operations)
  except AdWordsRequestError, e:
    print 'Validation correctly failed with \'%s\'.' % str(e)

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_group_id)
