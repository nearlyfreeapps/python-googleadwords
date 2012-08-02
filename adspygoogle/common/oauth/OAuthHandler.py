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

"""Creates custom handler for OAuth messiness."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import urllib
import urlparse


class OAuthHandler(object):
  """Defines a base, abstract class that handles the messiness of OAuth."""

  DEFAULT_CALLBACK_URL = 'oob'

  REQUEST_ENDPOINT = 'https://www.google.com/accounts/OAuthGetRequestToken'
  AUTHORIZE_ENDPOINT = 'https://www.google.com/accounts/OAuthAuthorizeToken'
  ACCESS_ENDPOINT = 'https://www.google.com/accounts/OAuthGetAccessToken'

  def GetRequestToken(self, credentials, scope, server=None, callbackurl=None,
                      applicationname=None):
    """Gets a request token.

    Must be overridden by implementors.

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
    raise NotImplementedError

  def GetAuthorizationUrl(self, credentials, server=None):
    """Gets the authorization URL for a request token.

    Args:
      credentials: dict The credentials, including the token.
      server: str Optional OAuth server to generate the URL for.
    Returns:
      str An authorization URL to redirect users to.
    """
    endpoint = self.GetAuthorizeEndpoint(server, None)
    params = {
        'oauth_token': credentials['oauth_token']
    }
    return self.AddParamsToUrl(endpoint, params)

  def GetAccessToken(self, credentials, verifier, server=None):
    """Gets the access token for an authorized request token.

    Must be overridden by implementors.

    Args:
      credentials: dict The credentials, including the consumer key, consumer
                   secret, token, and token secret.
      verifier: str The OAuth verifier code returned with the callback.
      server: str Optional OAuth server to make the request against.
    Returns:
      str The credentials, including the consumer key, consumer secret, token,
          and token secret.
    """
    raise NotImplementedError

  def GetSignedRequestParameters(self, credentials, url):
    """Gets the signed OAuth parameters required to make a request for the URL.

    Must be overridden by implementors.

    Args:
      credentials: dict The credentials, including the consumer key, consumer
                        secret, token, and token secret.
      url: str The URL the request will be made against.
    Returns:
      dict An array of OAuth parameter names to values.
    """
    raise NotImplementedError

  def FormatParametersForUrl(self, params):
    """Formats OAuth parameters for use in a URL.

    For example: param1=value1&param2=value2.

    Args:
      params: dict The OAuth parameters.
    Returns:
      str The parameters formatted for use in a URL.
    """
    return urllib.urlencode(params)

  def FormatParametersForHeader(self, params):
    """Formats OAuth parameters for use in an HTTP header.

    For example: param1="value1", param2="value2"

    Args:
      params: dict The OAuth parameters.
    Returns:
      str The parameters formatted for use in an HTTP header.
    """
    return ', '.join('%s="%s"' %
                     (key, urllib.quote_plus(value))
                     for key, value in params.items())

  def GetRequestEndpoint(self, server=None, params=None):
    """Gets the request endpoint using the given server and parameters.

    Args:
      server: str Optional OAuth server to use for the endpoint.
      params: dict Optional params to include in the endpoint.
    Returns:
      str The request endpoint.
    """
    return self.GetEndpoint(self.__class__.REQUEST_ENDPOINT, server, params)

  def GetAuthorizeEndpoint(self, server=None, params=None):
    """Gets the authorization endpoint using the given server and parameters.

    Args:
      server: str Optional OAuth server to use for the endpoint.
      params: dict Optional params to include in the endpoint.
    Returns:
      str The authorization endpoint.
    """
    return self.GetEndpoint(self.__class__.AUTHORIZE_ENDPOINT, server, params)

  def GetAccessEndpoint(self, server=None, params=None):
    """Gets the access endpoint using the given server and parameters.

    Args:
      server: str Optional OAuth server to use for the endpoint.
      params: dict Optional params to include in the endpoint.
    Returns:
      str The access endpoint.
    """
    return self.GetEndpoint(self.__class__.ACCESS_ENDPOINT, server, params)

  def GetEndpoint(self, endpoint, server=None, params=None):
    """Gets an endpoint using the given server and parameters.

    Args:
      endpoint: str The base endpoint URL to use.
      server: str Optional OAuth server to use for the endpoint.
      params: dict Optional params to include in the endpoint.
    Returns:
      str The endpoint.
    """
    endpoint = self.AddParamsToUrl(endpoint, params)
    if server:
      endpoint = self.ReplaceServerInUrl(endpoint, server)
    return endpoint

  def ReplaceServerInUrl(self, url, server):
    """Replaces the protocol and server portion of a URL with another.

    Args:
      url: str The full URL.
      server: str The protocol and server to replace with.
    Returns:
      str The URL with the protocol and server replaced.
    """
    _, _, path, params, query, fragment = urlparse.urlparse(url)
    newscheme, newhost, _, _, _, _ = urlparse.urlparse(server)
    return urlparse.urlunparse((newscheme, newhost, path, params, query,
                                fragment))

  def AddParamsToUrl(self, url, params):
    """Adds parameters to a URL.

    Args:
      url: str The URL.
      params: dict The parameters to add.
    Returns:
      str The new URL with the parameters added.
    """
    if not params: return url
    paramstring = self.FormatParametersForUrl(params)
    scheme, host, path, curparams, query, fragment = urlparse.urlparse(url)
    if query:
      query = query + '&' + paramstring
    else:
      query = paramstring
    return urlparse.urlunparse((scheme, host, path, curparams, query, fragment))

