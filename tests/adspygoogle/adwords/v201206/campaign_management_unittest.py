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

"""Unit tests to cover Campaign Management examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import time
import unittest

from examples.adspygoogle.adwords.v201206.campaign_management import add_experiment
from examples.adspygoogle.adwords.v201206.campaign_management import add_keywords_in_bulk
from examples.adspygoogle.adwords.v201206.campaign_management import add_location_extension
from examples.adspygoogle.adwords.v201206.campaign_management import add_location_extension_override
from examples.adspygoogle.adwords.v201206.campaign_management import get_all_disapproved_ads
from examples.adspygoogle.adwords.v201206.campaign_management import get_all_disapproved_ads_with_awql
from examples.adspygoogle.adwords.v201206.campaign_management import promote_experiment
from examples.adspygoogle.adwords.v201206.campaign_management import set_ad_parameters
from examples.adspygoogle.adwords.v201206.campaign_management import validate_text_ad
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201206
from tests.adspygoogle.adwords import TEST_VERSION_V201206
from tests.adspygoogle.adwords import util
from tests.adspygoogle.adwords import VERSION_V201206


class CampaignManagement(unittest.TestCase):

  """Unittest suite for Campaign Management code examples."""

  SERVER = SERVER_V201206
  VERSION = VERSION_V201206
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
      self.__class__.ad_id = util.CreateTestAd(client,
                                               self.__class__.ad_group_id)
      self.__class__.keyword_id = util.CreateTestKeyword(
          client, self.__class__.ad_group_id)

      self.__class__.extension_id = util.CreateTestLocationExtension(
          client, self.__class__.campaign_id)
      self.__class__.loaded = True

  def tearDown(self):
    client.validate_only = False

  def testAddExperiment(self):
    """Test whether we can add an experiment."""
    add_experiment.main(client, self.__class__.campaign_id,
                        self.__class__.ad_group_id)
    # Obtain the experiment ID so we can promote it later.
    self.__class__.experiment_id = util.GetExperimentIdForCampaign(
        client, self.__class__.campaign_id)

  def testAddKeywordsInBulk(self):
    """Test whether we can add keywords in bulk."""
    add_keywords_in_bulk.main(client, self.__class__.ad_group_id)

  def testAddLocationExtensionOverride(self):
    """Test whether we can add a location extension override."""
    add_location_extension_override.main(client, self.__class__.ad_id,
                                         self.__class__.extension_id)

  def testAddLocationExtension(self):
    """Test whether we can add a location extension."""
    add_location_extension.main(client, self.__class__.campaign_id)

  def testGetAllDisapprovedAds(self):
    """Test whether we can get all disapproved ads."""
    get_all_disapproved_ads.main(client, self.__class__.campaign_id)

  def testGetAllDisapprovedAdsWithAwql(self):
    """Test whether we can get all disapproved ads with AWQL."""
    get_all_disapproved_ads_with_awql.main(client, self.__class__.campaign_id)

  def testPromoteExperiment(self):
    """Test whether we can promote an experiment."""
    promote_experiment.main(client, self.__class__.experiment_id)

  def testSetAdParameters(self):
    """Test whether we can set ad parameters."""
    set_ad_parameters.main(client, self.__class__.ad_group_id,
                           self.__class__.keyword_id)

  def testValidateTextAd(self):
    """Test whether we can validate a text ad."""
    validate_text_ad.main(client, self.__class__.ad_group_id)


if __name__ == '__main__':
  if TEST_VERSION_V201206:
    unittest.main()
