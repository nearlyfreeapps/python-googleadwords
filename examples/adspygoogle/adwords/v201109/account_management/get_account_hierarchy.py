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

"""This example gets the account hierarchy under the current account.

Tags: ServicedAccountService.get
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


def DisplayAccountTree(account, link, accounts, links, depth=0):
  """Displays an account tree.

  Args:
    account: dict The account to display.
    link: dict The link used to reach this account.
    accounts: dict Map from customerId to account.
    links: dict Map from customerId to child links.
    depth: int Depth of the current account in the tree.
  """
  prefix = '-' * depth * 2
  link_text = ''
  descriptive_name = ''
  if link:
    link_text = ' (%s)' % link['typeOfLink']
    if len(link['descriptiveName']) > 0:
      descriptive_name = ' (%s)' % link['descriptiveName']
  print '%s%s%s, %s%s' % (prefix, account['login'], descriptive_name,
                          account['customerId'], link_text)
  if account['customerId'] in links:
    for child_link in links[account['customerId']]:
      child_account = accounts[child_link['clientId']['id']]
      DisplayAccountTree(child_account, child_link, accounts, links, depth + 1)


def main(client):
  # Initialize appropriate service.
  serviced_account_service = client.GetServicedAccountService(
      'https://adwords-sandbox.google.com', 'v201109')

  # Construct selector to get all accounts.
  selector = {
      'enablePaging': 'false'
  }
  # Get serviced account graph.
  graph = serviced_account_service.Get(selector)[0]
  if 'accounts' in graph and len(graph['accounts']):
    # Create map from customerId to parent and child links.
    child_links = {}
    parent_links = {}
    if 'links' in graph:
      for link in graph['links']:
        if link['managerId']['id'] not in child_links:
          child_links[link['managerId']['id']] = []
        child_links[link['managerId']['id']].append(link)
        if link['clientId']['id'] not in parent_links:
          parent_links[link['clientId']['id']] = []
        parent_links[link['clientId']['id']].append(link)
    # Create map from customerID to account and find root account.
    accounts = {}
    root_account = None
    for account in graph['accounts']:
      accounts[account['customerId']] = account
      if account['customerId'] not in parent_links:
        root_account = account
    # Display account tree.
    if not root_account and len(child_links) > 0:
      # Sandbox doesn't handle parent links properly, so use a fake account.
      root_account = {'customerId': child_links.items()[0][0], 'login': 'Root'}
    if root_account:
      print 'Login, CustomerId (Status)'
      DisplayAccountTree(root_account, None, accounts, child_links, 0)
    else:
      print 'Unable to determine a root account'
  else:
    print 'No serviced accounts were found'

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))
  client.use_mcc = True

  main(client)
