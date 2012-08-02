#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

"""This example adds an ad extension override to a given campaign. To get
campaigns, run get_campaigns.py.

Tags: GeoLocationService.get, AdExtensionOverrideService.mutate
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


ad_id = 'INSERT_AD_GROUP_AD_ID_HERE'
ad_extension_id = 'INSERT_AD_EXTENSION_ID_HERE'


def main(client, ad_id, ad_extension_id):
  # Initialize appropriate service.
  geo_location_service = client.GetGeoLocationService(
      'https://adwords-sandbox.google.com', 'v201109_1')
  ad_extension_override_service = client.GetAdExtensionOverrideService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct selector and get geo location info for a given address.
  selector = {
      'addresses': [
          {
              'streetAddress': '1600 Amphitheatre Parkway',
              'cityName': 'Mountain View',
              'provinceCode': 'US-CA',
              'provinceName': 'California',
              'postalCode': '94043',
              'countryCode': 'US'
          }
      ]
  }
  geo_location = geo_location_service.Get(selector)[0]

  # Construct operations and add ad extension override.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'adId': ad_id,
              'adExtension': {
                  'xsi_type': 'LocationExtension',
                  'id': ad_extension_id,
                  'address': geo_location['address'],
                  'geoPoint': geo_location['geoPoint'],
                  'encodedLocation': geo_location['encodedLocation'],
                  'source': 'ADWORDS_FRONTEND',
                  # Optional fields.
                  'companyName': 'ACME Inc.',
                  'phoneNumber': '(650) 253-0000'
                  # 'iconMediaId': '...',
                  # 'imageMediaId': '...'
              },
              # Optional fields.
              'overrideInfo': {
                  'LocationOverrideInfo': {
                      'radius': '5',
                      'radiusUnits': 'MILES'
                  }
              }
          }
      }
  ]
  ad_extensions = ad_extension_override_service.Mutate(operations)[0]

  # Display results.
  for ad_extension in ad_extensions['value']:
    print ('Ad extension override with id \'%s\' for ad with id \'%s\' was '
           'added.' % (ad_extension['adExtension']['id'], ad_extension['adId']))

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, ad_id, ad_extension_id)
