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

"""Unit tests to cover AuthToken."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))

import StringIO
import unittest
import urllib
import urlparse

from adspygoogle.common import AuthToken
from adspygoogle.common.Errors import AuthTokenError
from adspygoogle.common.Errors import CaptchaError


OLD_URLLIB_URLOPEN = urllib.urlopen


class AuthTokenTest(unittest.TestCase):

  """Tests for the adspygoogle.common.AuthToken module."""

  def tearDown(self):
    urllib.urlopen = OLD_URLLIB_URLOPEN

  def CreateFakeUrlopen(self, expected_url, expected_data, response_to_return,
                        error=None):
    """Creates a mock of the urllib.urlopen function.

    Args:
      expected_url: str The expected URL handed to urllib.urlopen.
      expected_data: dict The expected values in the query string handed to
                    urllib.urlopen.
      response_to_return: file A file-like object which is the response returned
                          from our mock of urllib.urlopen
      error: Error An error that should be raised instead of completing
             successfully. If an error is provided, it will override any
             response_to_return provided.

    Returns:
      function A mock of the urllib.urlopen function.
    """

    def FakeUrlopen(url, data):
      """Mock of the urllib.urlopen function."""
      self.assertEqual(url, expected_url)
      data = urlparse.parse_qs(data)
      self.assertEquals(len(data.keys()), len(expected_data))

      for data_key in data:
        self.assertEquals(len(data[data_key]), 1)
        self.assertTrue(data_key in expected_data)
        self.assertEquals(data[data_key][0], expected_data[data_key])

      if error: raise error
      return response_to_return
    return FakeUrlopen

  def testAuthToken_noCaptcha(self):
    """Tests generating a standard auth token."""
    fake_sid = '1a2b3c45'
    fake_lsid = '2b3c4e56'
    fake_auth = '3c4d5e67'
    fake_client_login_response = StringIO.StringIO(
        ''.join(['SID=', fake_sid, '\nLSID=', fake_lsid, '\nAuth=', fake_auth]))

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    token = AuthToken.AuthToken(email, password, service, lib_sig, proxy)

    self.assertEqual(token.GetAuthToken(), fake_auth)
    self.assertEqual(token.GetSidToken(), fake_sid)
    self.assertEqual(token.GetLsidToken(), fake_lsid)

  def testAuthToken_answerCaptcha(self):
    """Tests answering a captcha challenge."""
    fake_sid = '1a2b3c45'
    fake_lsid = '2b3c4e56'
    fake_auth = '3c4d5e67'
    fake_client_login_response = StringIO.StringIO(
        ''.join(['SID=', fake_sid, '\nLSID=', fake_lsid, '\nAuth=', fake_auth]))

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None
    login_token = 'loginTOKEN'
    login_captcha = 'loginCAPTcha'

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE',
        'logintoken': login_token,
        'logincaptcha': login_captcha
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    token = AuthToken.AuthToken(email, password, service, lib_sig, proxy,
                                login_token, login_captcha)

    self.assertEqual(token.GetAuthToken(), fake_auth)
    self.assertEqual(token.GetSidToken(), fake_sid)
    self.assertEqual(token.GetLsidToken(), fake_lsid)

  def testAuthToken_returnCaptcha(self):
    """Tests receiving a captcha challenge."""
    captcha_token = 'captCHA gonna getCHA'
    captcha_url = '15762tgyhwb'

    fake_client_login_response = StringIO.StringIO(
        ''.join(['CaptchaToken=', captcha_token, '\nCaptchaUrl=', captcha_url,
                 '\nError=CaptchaRequired']))

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    try:
      AuthToken.AuthToken(email, password, service, lib_sig, proxy)
      self.fail('Exception should have been thrown.')
    except CaptchaError, e:
      self.assertEqual(e.captcha_token, captcha_token)
      self.assertEqual(e.captcha_url, 'http://www.google.com/accounts/' +
                       captcha_url)

  def testAuthToken_returnError(self):
    """Tests receiving a generic failure."""
    error_msg = 'Fail'

    fake_client_login_response = StringIO.StringIO('Error=%s' % error_msg)

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    try:
      AuthToken.AuthToken(email, password, service, lib_sig, proxy)
      self.fail('Exception should have been thrown.')
    except AuthTokenError, e:
      self.assertEqual(e.msg, error_msg)

  def testAuthToken_returnErrorWithInfo(self):
    """Tests receiving a generic failure with additional information."""
    error_msg = 'Fail'
    info = 'It failed because I said so'

    fake_client_login_response = StringIO.StringIO(
        ''.join(['Error=', error_msg, '\nInfo=', info]))

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    try:
      AuthToken.AuthToken(email, password, service, lib_sig, proxy)
      self.fail('Exception should have been thrown.')
    except AuthTokenError, e:
      self.assertEqual(e.msg, error_msg + ' Additional Info: ' + info)

  def testAuthToken_returnUnExpectedError(self):
    """Tests receiving an unexpected failure."""
    error_msg = 'Fail'

    fake_client_login_response = StringIO.StringIO('Other=%s' % error_msg)

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(expected_url, expected_data,
                                            fake_client_login_response)

    try:
      AuthToken.AuthToken(email, password, service, lib_sig, proxy)
      self.fail('Exception should have been thrown.')
    except AuthTokenError, e:
      self.assertEqual(e.msg, 'Unexpected response: {\'Other\': \'Fail\'}')

  def testAuthToken_IOError(self):
    """Tests receiving an IOError from urlopen."""
    error_msg = 'You have been IOd'

    email = 'api.jdilallo@gmail.com'
    password = 'fake_password'
    service = 'adwords'
    lib_sig = 'AwApi-Python-15.3.0 (Python 2.6)'
    proxy = None

    expected_url = 'https://www.google.com/accounts/ClientLogin'
    expected_error = IOError(error_msg)
    expected_data = {
        'Email': email,
        'Passwd': password,
        'service': service,
        'source': 'Google-%s' % lib_sig,
        'accountType': 'GOOGLE'
    }

    urllib.urlopen = self.CreateFakeUrlopen(
        expected_url, expected_data, None, error=expected_error)

    try:
      AuthToken.AuthToken(email, password, service, lib_sig, proxy)
      self.fail('Exception should have been thrown.')
    except AuthTokenError, e:
      self.assertEqual(e.msg, expected_error)


if __name__ == '__main__':
  unittest.main()
