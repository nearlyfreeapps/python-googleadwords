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

"""This example illustrates how to retrieve all languages and carriers available
for targeting.

Tags: ConstantDataService.getLanguageCriterion
Tags: ConstantDataService.getCarrierCriterion
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


def main(client):
  # Initialize appropriate service.
  constant_data_service = client.GetConstantDataService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Get all languages.
  languages = constant_data_service.GetLanguageCriterion()

  # Display results.
  for language in languages:
    print ('Language with name \'%s\' and ID \'%s\' was found.'
           % (language['name'], language['id']))

  # Get all carriers.
  carriers = constant_data_service.GetCarrierCriterion()

  # Display results.
  for carrier in carriers:
    print ('Carrier with name \'%s\', ID \'%s\', and country code \'%s\' was '
           'found.' % (carrier['name'], carrier['id'], carrier['countryCode']))

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client)
