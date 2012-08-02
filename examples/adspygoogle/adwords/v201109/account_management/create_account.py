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

"""This example illustrates how to create an account.

Note by default this account will only be accessible via parent MCC.

Tags: CreateAccountService.mutate
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


def main(client):
  # Initialize appropriate service.
  create_account_service = client.GetCreateAccountService(
      'https://adwords-sandbox.google.com', 'v201109')

  today = datetime.today().strftime('%Y%m%d %H:%M:%S')
  # Construct operations and add campaign.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'currencyCode': 'EUR',
          'dateTimeZone': 'Europe/London',
      },
      'descriptiveName': ('Account created with CreateAccountService on %s'
                          % today)
  }]

  # Create the account. It is possible to create multiple accounts with one
  # request by sending an array of operations.
  accounts = create_account_service.Mutate(operations)

  # Display results.
  for account in accounts:
    print ('Account with customer ID \'%s\' was successfully created.'
           % account['customerId'])

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))

if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  # An Account must be created under an MCC.
  client.use_mcc = True
  main(client)
