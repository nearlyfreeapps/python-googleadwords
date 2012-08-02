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

"""Creates a default OAuth handler."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import urllib
import urlparse
import oauth2 as oauth
from OAuthHandler import OAuthHandler


class PythonOAuth2OAuthHandler(OAuthHandler):
  """An OAuth handler that uses python-oauth2.

  Library included from: https://github.com/simplegeo/python-oauth2.
  """

  def GetRequestToken(self, credentials, scope, server=None, callbackurl=None,
                      applicationname=None):
    """Gets a request token.

    Args:
      credentials: dict The credentials, including the consumer key and consumer
                   secret.
      scope: str The scope of the application to authorize.
      server: str Optional OAuth server to make the request against.
      callbackurl: str Optional callback url.
      applicationname: str Optional name of the application to display on the
                       authorization redirect page.
    Returns:
      dict The credentials, including the consumer key, consumer secret, token
           and token secret.
    """
    consumer = oauth.Consumer(credentials['oauth_consumer_key'],
                              credentials['oauth_consumer_secret'])
    signature_method = oauth.SignatureMethod_HMAC_SHA1()

    params = {
        'scope': scope,
        'oauth_version': '1.0a'
    }
    if applicationname: params['xoauth_displayname'] = applicationname
    if callbackurl:
      params['oauth_callback'] = callbackurl
    else:
      params['oauth_callback'] = self.DEFAULT_CALLBACK_URL
    endpoint = self.GetRequestEndpoint(server)

    request = oauth.Request.from_consumer_and_token(consumer, None, 'GET',
                                                    endpoint, params)
    request.sign_request(signature_method, consumer, None)

    token = self.GetTokenFromUrl(request.to_url())
    credentials['oauth_token'] = token.key
    credentials['oauth_token_secret'] = token.secret
    return credentials

  def GetAccessToken(self, credentials, verifier, server=None):
    """Gets the access token for an authorized request token.

    Args:
      credentials: dict The credentials, including the consumer key, consumer
                   secret, token, and token secret.
      verifier: str The OAuth verifier code returned with the callback.
      server: str Optional OAuth server to make the request against.
    Returns:
      str The credentials, including the consumer key, consumer secret, token,
          and token secret.
    """
    consumer = oauth.Consumer(credentials['oauth_consumer_key'],
                              credentials['oauth_consumer_secret'])
    token = oauth.Token(credentials['oauth_token'],
                        credentials['oauth_token_secret'])
    signature_method = oauth.SignatureMethod_HMAC_SHA1()

    if verifier:
      params = {
          'oauth_verifier': verifier,
          'oauth_version': '1.0a'
      }
    else:
      params = None
    endpoint = self.GetAccessEndpoint(server)

    request = oauth.Request.from_consumer_and_token(consumer, token, 'GET',
                                                    endpoint, params)
    request.sign_request(signature_method, consumer, token)

    token = self.GetTokenFromUrl(request.to_url())
    credentials['oauth_token'] = token.key
    credentials['oauth_token_secret'] = token.secret
    return credentials

  def GetSignedRequestParameters(self, credentials, url):
    """Gets the signed OAuth parameters required to make a request for the URL.

    Args:
      credentials: dict The credentials, including the consumer key, consumer
                        secret, token, and token secret.
      url: str The URL the request will be made against.
    Returns:
      dict An array of OAuth parameter names to values.
    """
    consumer = oauth.Consumer(credentials['oauth_consumer_key'],
                              credentials['oauth_consumer_secret'])
    token = oauth.Token(credentials['oauth_token'],
                        credentials['oauth_token_secret'])
    signature_method = oauth.SignatureMethod_HMAC_SHA1()

    params = {
        'oauth_version': '1.0a'
    }

    request = oauth.Request.from_consumer_and_token(consumer, token, 'POST',
                                                    url, params)
    request.sign_request(signature_method, consumer, token)
    return dict(request)

  def GetTokenFromUrl(self, url):
    """Makes and HTTP request to the given URL and extracts the OAuth token.

    Args:
      url: str The URL to make the request to.
    Returns:
      Token The returned token.
    """
    response = urllib.urlopen(url).read()
    return self.GetTokenFromQueryString(response)

  def GetTokenFromQueryString(self, querystring):
    """Parses a query string and extracts the OAuth token.

    Args:
      querystring: str The query string.
    Returns:
      Token The returned token.
    """
    values = urlparse.parse_qs(querystring)
    return oauth.Token(values['oauth_token'][0],
                       values['oauth_token_secret'][0])
