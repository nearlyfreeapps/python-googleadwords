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

"""Module that can be used to enforce SSL certificate verification.

Using this module will monkey-patch a new HTTPS class into httplib. Be aware
that any other part of your application that uses httplib, directly or
indirectly, will be affected by its use.
"""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'
