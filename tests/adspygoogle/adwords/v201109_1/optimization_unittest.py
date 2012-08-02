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

"""Unit tests to cover Optimization examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import time
import unittest

from examples.adspygoogle.adwords.v201109_1.optimization import estimate_keyword_traffic
from examples.adspygoogle.adwords.v201109_1.optimization import get_keyword_bid_simulations
from examples.adspygoogle.adwords.v201109_1.optimization import get_keyword_ideas
from examples.adspygoogle.adwords.v201109_1.optimization import get_placement_ideas
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import SERVER_V201109_1
from tests.adspygoogle.adwords import TEST_VERSION_V201109_1
from tests.adspygoogle.adwords import util
from tests.adspygoogle.adwords import VERSION_V201109_1


class Optimization(unittest.TestCase):

  """Unittest suite for Optimization code examples."""

  SERVER = SERVER_V201109_1
  VERSION = VERSION_V201109_1
  client.debug = False
  loaded = False

  def setUp(self):
    """Prepare unittest."""
    time.sleep(3)
    client.use_mcc = False
    if not self.__class__.loaded:
      self.__class__.campaign_id = util.CreateTestCampaign(client)
      self.__class__.ad_group_id = util.CreateTestAdGroup(
          client, self.__class__.campaign_id)
      self.__class__.keyword_id = util.CreateTestKeyword(
          client, self.__class__.ad_group_id)
      self.__class__.loaded = True

  def testEstimateKeywordTraffic(self):
    """Test whether we can estimate keyword traffic."""
    estimate_keyword_traffic.main(client)

  def testGetKeywordBidSimulations(self):
    """Test whether we can get keyword bid simulations."""
    get_keyword_bid_simulations.main(client, self.__class__.ad_group_id,
                                     self.__class__.keyword_id)

  def testGetKeywordIdeas(self):
    """Test whether we can get keyword ideas."""
    get_keyword_ideas.main(client)

  def testGetPlacementIdeas(self):
    """Test whether we can get placement ideas."""
    get_placement_ideas.main(client)


if __name__ == '__main__':
  if TEST_VERSION_V201109_1:
    unittest.main()
