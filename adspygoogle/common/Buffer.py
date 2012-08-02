#!/usr/bin/python
#
# Copyright 2010 Google Inc.
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

"""Handler class for implementing a buffer."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'


class Buffer(object):

  """Implements a Buffer.

  Placeholder for temporarily storing data (i.e. sys.stdout, SOAP messages).
  """

  def __init__(self):
    """Inits Buffer."""
    self._buffer = ''

  def write(self, str_in):
    """Append given string to a buffer.

    Args:
      str_in: str String to append to a buffer.
    """
    self._buffer += str(str_in)

  def flush(self):
    pass

  def GetBufferAsStr(self):
    """Return buffer as string.

    Returns:
      str Buffer.
    """
    return str(self._buffer)
