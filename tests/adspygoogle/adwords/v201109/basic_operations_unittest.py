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

"""Unit tests to cover Basic Operations examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import time
import unittest

from examples.adspygoogle.adwords.v201109.basic_operations import add_ad_groups
from examples.adspygoogle.adwords.v201109.basic_operations import add_campaigns
from examples.adspygoogle.adwords.v201109.basic_operations import add_keywords
from examples.adspygoogle.adwords.v201109.basic_operations import add_text_ads
from examples.adspygoogle.adwords.v201109.basic_operations import delete_ad
from examples.adspygoogle.adwords.v201109.basic_operations import delete_ad_group
from examples.adspygoogle.adwords.v201109.basic_operations import delete_campaign
from examples.adspygoogle.adwords.v201109.basic_operations import delete_keyword
from examples.adspygoogle.adwords.v201109.basic_operations import get_ad_groups
from examples.adspygoogle.adwords.v201109.basic_operations import get_campaigns
from examples.adspygoogle.adwords.v201109.basic_operations import get_keywords
from examples.adspygoogle.adwords.v201109.basic_operations import get_text_ads
from examples.adspygoogle.adwords.v201109.basic_operations import pause_ad
from examples.adspygoogle.adwords.v201109.basic_operations import update_ad_group
from examples.adspygoogle.adwords.v201109.basic_operations import update_campaign
from examples.adspygoogle.adwords.v201109.basic_operations import update_keyword
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import SERVER_V201109
from tests.adspygoogle.adwords import TEST_VERSION_V201109
from tests.adspygoogle.adwords import util
from tests.adspygoogle.adwords import VERSION_V201109


class BasicOperations(unittest.TestCase):

  """Unittest suite for Account Management code examples."""

  SERVER = SERVER_V201109
  VERSION = VERSION_V201109
  client.debug = False
  loaded = False

  def setUp(self):
    """Prepare unittest."""
    time.sleep(1)
    client.use_mcc = False
    if not self.__class__.loaded:
      self.__class__.campaign_id = util.CreateTestCampaign(
          client)
      self.__class__.ad_group_id = util.CreateTestAdGroup(
          client, self.__class__.campaign_id)
      self.__class__.ad_id = util.CreateTestAd(client,
                                               self.__class__.ad_group_id)
      self.__class__.keyword_id = util.CreateTestKeyword(
          client, self.__class__.ad_group_id)
      self.__class__.loaded = True

  def testAddAdGroups(self):
    """Tests whether we can add ad groups."""
    add_ad_groups.main(client, self.__class__.campaign_id)

  def testAddCampaigns(self):
    """Tests whether we can add campaigns."""
    add_campaigns.main(client)

  def testAddKeywords(self):
    """Tests whether we can add keywords."""
    add_keywords.main(client, self.__class__.ad_group_id)

  def testAddTextAds(self):
    """Tests whether we can add text ads."""
    add_text_ads.main(client, self.__class__.ad_group_id)

  def testGetAdGroups(self):
    """Tests whether we can get ad groups."""
    get_ad_groups.main(client, self.__class__.campaign_id)

  def testGetCampaigns(self):
    """Tests whether we can get campaigns."""
    get_campaigns.main(client)

  def testGetKeywords(self):
    """Tests whether we can get keywords."""
    get_keywords.main(client)

  def testGetTextAds(self):
    """Tests whether we can get text ads."""
    get_text_ads.main(client, self.__class__.ad_group_id)

  def testUpdateAdGroup(self):
    """Tests whether we can update an ad group."""
    update_ad_group.main(client, self.__class__.ad_group_id)

  def testUpdateCampaign(self):
    """Tests whether we can update a campaign."""
    update_campaign.main(client, self.__class__.campaign_id)

  def testUpdateKeyword(self):
    """Tests whether we can update a keyword."""
    update_keyword.main(client, self.__class__.ad_group_id,
                        self.__class__.keyword_id)

  def testPauseAd(self):
    """Tests whether we can pause an ad."""
    pause_ad.main(client, self.__class__.ad_group_id,
                  self.__class__.ad_id)

  def testZDeleteAd(self):
    """Tests whether we can delete an ad."""
    delete_ad.main(client, self.__class__.ad_group_id,
                   self.__class__.ad_id)

  def testZDeleteKeyword(self):
    """Tests whether we can delete a keyword."""
    delete_keyword.main(client, self.__class__.ad_group_id,
                        self.__class__.keyword_id)

  def testZDeleteAdGroup(self):
    """Tests whether we can delete an ad group."""
    delete_ad_group.main(client, self.__class__.ad_group_id)

  def testZDeleteCampaign(self):
    """Tests whether we can delete a campaign."""
    delete_campaign.main(client, self.__class__.campaign_id)


if __name__ == '__main__':
  if TEST_VERSION_V201109:
    unittest.main()
