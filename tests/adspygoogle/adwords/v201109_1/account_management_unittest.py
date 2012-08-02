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

"""Unit tests to cover Account Management examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from examples.adspygoogle.adwords.v201109_1.account_management import create_account
from examples.adspygoogle.adwords.v201109_1.account_management import get_account_alerts
from examples.adspygoogle.adwords.v201109_1.account_management import get_account_changes
from examples.adspygoogle.adwords.v201109_1.account_management import get_account_hierarchy
from examples.adspygoogle.adwords.v201109_1.account_management import get_client_customer_id
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import SERVER_V201109_1
from tests.adspygoogle.adwords import TEST_VERSION_V201109_1
from tests.adspygoogle.adwords import VERSION_V201109_1


# Currently, creating accounts is broken in sandbox, so we disable that test.
CREATE_ACCOUNT = False


class AccountManagement(unittest.TestCase):

  """Unittest suite for Account Management code examples."""

  SERVER = SERVER_V201109_1
  VERSION = VERSION_V201109_1
  client.debug = False

  def setUp(self):
    """Prepare unittest."""
    client.use_mcc = False

  def testCreateAccount(self):
    """Tests whether we can create an account."""
    client.use_mcc = True
    if CREATE_ACCOUNT:
      create_account.main(client)

  def testGetAccountAlerts(self):
    """Test whether we can get account alerts."""
    get_account_alerts.main(client)

  def testGetAccountChanges(self):
    """Test whether we can get account changes."""
    get_account_changes.main(client)

  def testGetAccountHierarchy(self):
    """Test whether we can get account hierarchy."""
    client.use_mcc = True
    get_account_hierarchy.main(client)

  def testGetClientCustomerId(self):
    """Test whether we can get a clientCustomerId."""
    client.use_mcc = True
    client_email = 'client_1+%s' % client._headers['email']
    get_client_customer_id.main(client, client_email)


if __name__ == '__main__':
  if TEST_VERSION_V201109_1:
    unittest.main()
