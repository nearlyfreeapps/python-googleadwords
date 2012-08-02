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

"""Unit tests to cover Buffer."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))

import unittest

from adspygoogle.common.Buffer import Buffer


class BufferTest(unittest.TestCase):

  """Tests for the adspygoogle.common.Buffer module."""

  def testBuffer(self):
    """Tests the full functionality of the tiny Buffer class."""
    my_buffer = Buffer()
    self.assertEqual(my_buffer.GetBufferAsStr(), '')

    line_1 = '12345'
    my_buffer.write(line_1)
    self.assertEqual(my_buffer.GetBufferAsStr(), line_1)

    line_2 = 'abcde'
    my_buffer.write(line_2)
    self.assertEqual(my_buffer.GetBufferAsStr(), ''.join([line_1, line_2]))

    my_buffer.flush()
    self.assertEqual(my_buffer.GetBufferAsStr(), ''.join([line_1, line_2]))


if __name__ == '__main__':
  unittest.main()
