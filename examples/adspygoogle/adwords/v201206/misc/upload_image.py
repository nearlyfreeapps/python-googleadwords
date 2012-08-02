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

"""This example uploads an image. To get images, run get_all_images.py.

Tags: MediaService.upload
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import base64
import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient
from adspygoogle.common import Utils


image_filename = 'INSERT_IMAGE_PATH_HERE'


def main(client, image_filename):
  # Initialize appropriate service.
  media_service = client.GetMediaService(
      'https://adwords-sandbox.google.com', 'v201206')

  image_data = Utils.ReadFile(image_filename)
  image_data = base64.encodestring(image_data)

  # Construct media and upload image.
  media = [{
      'xsi_type': 'Image',
      'data': image_data,
      'type': 'IMAGE'
  }]
  media = media_service.Upload(media)[0]

  # Display results.
  if media:
    dimensions = Utils.GetDictFromMap(media['dimensions'])
    print ('Image with id \'%s\', dimensions \'%sx%s\', and MimeType \'%s\' was'
           ' uploaded.' % (media['mediaId'], dimensions['FULL']['height'],
                           dimensions['FULL']['width'], media['mimeType']))
  else:
    print 'No images were uploaded.'

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, image_filename)
