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

"""This example demonstrates how to handle two-factor authorization errors."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle.adwords import AUTH_TOKEN_SERVICE
from adspygoogle.adwords import LIB_SIG
from adspygoogle.common import Utils
from adspygoogle.common.Errors import AuthTokenError


login_email = '2steptester@gmail.com'
password = 'testaccount'


def main():
  try:
    Utils.GetAuthToken(login_email, password, AUTH_TOKEN_SERVICE, LIB_SIG, None)
  except AuthTokenError, e:
    if str(e).find('InvalidSecondFactor') != -1:
      print """The user has enabled two factor authentication in this
  account. Have the user generate an application-specific password to make
  calls against the AdWords API. See
  http://adwordsapi.blogspot.com/2011/02/authentication-changes-with-2-step.html
  for more details."""
    else:
      raise e


if __name__ == '__main__':
  main()
