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

"""Unit tests for issue #39.

Makes sure we can convert an integer clientCustomerId to string.
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from adspygoogle.adwords.AdWordsClient import AdWordsClient


class Issue39(unittest.TestCase):

  """Unittests for Issue #39."""

  def testIntegerClientCustomerId(self):
    """Tests if we can convert an integer clientCustomerId to string."""
    client = AdWordsClient({'authToken': 'abc', 'developerToken': 'abc',
                            'userAgent': 'foo', 'clientCustomerId': 123})
    campaign_service = client.GetCampaignService(
        'https://adwords-sandbox.google.com', 'v201206')
    campaign_service._SetHeaders()


if __name__ == '__main__':
  unittest.main()
