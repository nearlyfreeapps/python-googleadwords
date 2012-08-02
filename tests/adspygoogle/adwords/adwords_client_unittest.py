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

"""Unit tests to cover AdWordsClient."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import StringIO
import sys
import unittest
import urllib2
sys.path.insert(0, os.path.join('..', '..', '..'))
from adspygoogle.adwords.AdWordsClient import AdWordsClient
from adspygoogle.common import Utils
from adspygoogle.common.Errors import ValidationError


DEFAULT_HEADERS = {
    'userAgent': 'Foo Bar',
    'developerToken': 'devtoken'
}


class AdWordsClientValidationTest(unittest.TestCase):

  """Tests the validation logic when instantiating AdWordsClient."""

  def setUp(self):
    """Monkey patch AuthToken retrieval."""

    def FakeGetAuthToken(a, b, c, d, e, f, g):
      return 'FooBar'
    self.__old_GetAuthToken = Utils.GetAuthToken
    Utils.GetAuthToken = FakeGetAuthToken

  def tearDown(self):
    Utils.GetAuthToken = self.__old_GetAuthToken

  def testEmailPassOnly(self):
    """Tests that specifying solely email & password works."""
    headers = DEFAULT_HEADERS.copy()
    headers['email'] = 'email@example.com'
    headers['password'] = 'password'
    client = AdWordsClient(headers=headers)
    self.assertEquals(client._headers['authToken'], 'FooBar')

  def testEmailPassOthersBlank(self):
    """Tests that email and password with other auth blank works."""
    headers = DEFAULT_HEADERS.copy()
    headers['email'] = 'email@example.com'
    headers['password'] = 'password'
    headers['authToken'] = ''
    headers['oauth_credentials'] = None
    client = AdWordsClient(headers=headers)
    self.assertEquals(client._headers['authToken'], 'FooBar')

  def testAuthTokenOnly(self):
    """Tests that specifying solely authtoken works."""
    headers = DEFAULT_HEADERS.copy()
    headers['authToken'] = 'MyToken'
    client = AdWordsClient(headers=headers)
    self.assertEquals(client._headers['authToken'], 'MyToken')

  def testAuthTokenOthersBlank(self):
    """Tests that authToken with other auth blank works."""
    headers = DEFAULT_HEADERS.copy()
    headers['authToken'] = 'MyToken'
    headers['email'] = ''
    headers['password'] = ''
    headers['oauth_credentials'] = None
    client = AdWordsClient(headers=headers)
    self.assertEquals(client._headers['authToken'], 'MyToken')

  def testOAuthCredentialsOnly(self):
    """Tests that specifying solely oauth_credentials works."""
    headers = DEFAULT_HEADERS.copy()
    headers['oauth_credentials'] = {
        'oauth_consumer_key': 'anonymous',
        'oauth_consumer_secret': 'anonymous'
    }
    client = AdWordsClient(headers=headers)
    self.assertTrue(client.oauth_credentials)

  def testOAuthCredentialsOthersBlank(self):
    """Tests that oauth_credentials with other auth blank works."""
    headers = DEFAULT_HEADERS.copy()
    headers['oauth_credentials'] = {
        'oauth_consumer_key': 'anonymous',
        'oauth_consumer_secret': 'anonymous'
    }
    headers['email'] = ''
    headers['password'] = ''
    headers['authToken'] = ''
    client = AdWordsClient(headers=headers)
    self.assertTrue(client.oauth_credentials)

  def testNonStrictThrowsValidationError(self):
    """Tests that even when using non-strict mode, we still raise a
    ValidationError when no auth credentials are provided."""
    headers = DEFAULT_HEADERS.copy()
    config = {'strict': 'n'}

    def Run():
      _ = AdWordsClient(headers=headers, config=config)
    self.assertRaises(ValidationError, Run)


class AdWordsClientCaptchaHandlingTest(unittest.TestCase):

  """Tests the captcha handling logic."""
  CAPTCHA_CHALLENGE = '''Url=http://www.google.com/login/captcha
Error=CaptchaRequired
CaptchaToken=DQAAAGgA...dkI1LK9
CaptchaUrl=Captcha?ctoken=HiteT4b0Bk5Xg18_AcVoP6-yFkHPibe7O9EqxeiI7lUSN'''
  SUCCESS = '''SID=DQAAAGgA...7Zg8CTN
LSID=DQAAAGsA...lk8BBbG
Auth=DQAAAGgA...dk3fA5N'''


  def setUp(self):
    """Monkey patch AuthToken retrieval."""

    def FakeUrlOpen(a, b):
      # If we don't see a captcha response, initiate challenge
      if b.find('logincaptcha') == -1:
        return StringIO.StringIO(self.__class__.CAPTCHA_CHALLENGE)
      else:
        return StringIO.StringIO(self.__class__.SUCCESS)
    self.__old_urlopen = urllib2.urlopen
    urllib2.urlopen = FakeUrlOpen

  def tearDown(self):
    urllib2.urlopen = self.__old_urlopen

  def testCaptchaHandling(self):
    headers = DEFAULT_HEADERS.copy()
    headers['email'] = 'email@example.com'
    headers['password'] = 'password'
    client = None
    try:
      client = AdWordsClient(headers=headers)
      self.fail('Expected a CaptchaError to be thrown')
    except ValidationError, e:
      client = AdWordsClient(headers=headers,
                             login_token=e.root_cause.captcha_token,
                             login_captcha='foo bar')
      self.assertEquals(client._headers['authToken'], 'DQAAAGgA...dk3fA5N')

def MakeTestSuite():
  """Set up test suite.

  Returns:
    TestSuite test suite.
  """
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(AdWordsClientValidationTest))
  suite.addTests(unittest.makeSuite(AdWordsClientCaptchaHandlingTest))
  return suite


if __name__ == '__main__':
  suites = [MakeTestSuite()]
  alltests = unittest.TestSuite(suites)
  unittest.main(defaultTest='alltests')
