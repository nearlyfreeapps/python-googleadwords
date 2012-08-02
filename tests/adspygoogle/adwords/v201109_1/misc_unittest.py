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

"""Unit tests to cover Misc examples."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import time
import unittest

from examples.adspygoogle.adwords.v201109_1.misc import get_all_images_and_videos
from examples.adspygoogle.adwords.v201109_1.misc import upload_image
from tests.adspygoogle.adwords import client
from tests.adspygoogle.adwords import SERVER_V201109_1
from tests.adspygoogle.adwords import TEST_VERSION_V201109_1
from tests.adspygoogle.adwords import VERSION_V201109_1


class Misc(unittest.TestCase):

  """Unittest suite for Misc code examples."""

  SERVER = SERVER_V201109_1
  VERSION = VERSION_V201109_1
  client.debug = False
  loaded = False

  def setUp(self):
    """Prepare unittest."""
    time.sleep(1)
    client.use_mcc = False

  def tearDown(self):
    """Reset partial failure."""
    client.partial_failure = False

  def testGetAllImagesAndVideo(self):
    """Tests whether we can get all images and video."""
    get_all_images_and_videos.main(client)

  def testUploadImage(self):
    """Test whether we can upload an image."""
    upload_image.main(client, os.path.join('..', 'data', 'image.jpg'))


if __name__ == '__main__':
  if TEST_VERSION_V201109_1:
    unittest.main()
