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

"""Unit tests to cover Remarketing examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from examples.adspygoogle.adwords.v201206.remarketing import add_audience
from examples.adspygoogle.adwords.v201206.remarketing import add_conversion_tracker
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import SERVER_V201206
from tests.adspygoogle.adwords import TEST_VERSION_V201206
from tests.adspygoogle.adwords import VERSION_V201206


class Remarketing(unittest.TestCase):

  """Unittest suite for Remarketing code examples."""

  SERVER = SERVER_V201206
  VERSION = VERSION_V201206
  client.debug = False

  def setUp(self):
    """Prepare unittest."""
    client.use_mcc = False

  def testAddAudience(self):
    """Tests whether we can add an audience."""
    add_audience.main(client)

  def testAddConversionTracker(self):
    """Test whether we can add a conversion tracker."""
    add_conversion_tracker.main(client)


if __name__ == '__main__':
  if TEST_VERSION_V201206:
    unittest.main()
