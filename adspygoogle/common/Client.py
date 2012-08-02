#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Interface for accessing all other services."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import pickle
import warnings

from adspygoogle.common import PYXML
from adspygoogle.common import SanityCheck
from adspygoogle.common import Utils
from adspygoogle.common.Errors import ValidationError


# The values in _DEFAULT_CONFIG will be used to populate a user's configuration
# if any of these keys was not provided.
_DEFAULT_CONFIG = {
    'proxy': None,
    'xml_parser': PYXML,
    'debug': 'n',
    'raw_debug': 'n',
    'xml_log': 'y',
    'request_log': 'y',
    'raw_response': 'n',
    'strict': 'y',
    'auth_token_epoch': 0,
    'auth_type': '',
    'pretty_xml': 'y',
    'compress': 'y',
    'access': '',
    'wrap_in_tuple': 'y'
}


class Client(object):

  """Provides entry point to all web services.

  Allows instantiation of all web services.
  """

  home = os.getcwd()
  auth_pkl = ''
  config_pkl = ''

  def __init__(self, headers=None, config=None, path=None):
    """Inits Client.

    Args:
      [optional]
      headers: dict Object with populated authentication credentials.
      config: dict Object with client configuration values.
      path: str Relative or absolute path to home directory (i.e. location of
            pickles and logs/).
    """
    self._headers = headers or {}
    self._config = config or self._SetMissingDefaultConfigValues()

  def _LoadAuthCredentials(self):
    """Load existing authentication credentials from auth.pkl.

    Returns:
      dict Dictionary object with populated authentication credentials.

    Raises:
      ValidationError: if authentication data is missing.
    """
    auth = {}
    if os.path.exists(self.__class__.auth_pkl):
      fh = open(self.__class__.auth_pkl, 'r')
      try:
        auth = pickle.load(fh)
      finally:
        fh.close()

    if not auth:
      msg = 'Authentication data is missing.'
      raise ValidationError(msg)
    return auth

  def _WriteUpdatedAuthValue(self, key, new_value):
    """Write updated authentication value for a key in auth.pkl.

    Args:
      key: str Key to update.
      new_value: str New value to update the key with.
    """
    auth = self._LoadAuthCredentials()
    auth[key] = new_value

    # Only write to an existing pickle.
    if os.path.exists(self.__class__.auth_pkl):
      fh = open(self.__class__.auth_pkl, 'w')
      try:
        pickle.dump(auth, fh)
      finally:
        fh.close()

  def _LoadConfigValues(self):
    """Load existing configuration values from config.pkl.

    Returns:
      dict Dictionary object with populated configuration values.
    """
    config = {}
    if os.path.exists(self.__class__.config_pkl):
      fh = open(self.__class__.config_pkl, 'r')
      try:
        config = pickle.load(fh)
      finally:
        fh.close()

    if not config:
      # Proceed to set default config values.
      pass
    return config

  def _SetMissingDefaultConfigValues(self, config=None):
    """Set default configuration values for missing elements in the config dict.

    Args:
      config: dict Object with client configuration values.

    Returns:
      dict Given config dictionary with default values added in.
    """
    if config is None: config = {}
    for key in _DEFAULT_CONFIG:
      if key not in config:
        config[key] = _DEFAULT_CONFIG[key]
    return config

  def GetAuthCredentials(self):
    """Return authentication credentials.

    Returns:
      dict Authentiaction credentials.
    """
    return self._headers

  def GetConfigValues(self):
    """Return configuration values.

    Returns:
      dict Configuration values.
    """
    return self._config

  def SetDebug(self, new_state):
    """Temporarily change debug mode for a given Client instance.

    Args:
      new_state: bool New state of the debug mode.
    """
    self._config['debug'] = Utils.BoolTypeConvert(new_state, str)

  def __GetDebug(self):
    """Return current state of the debug mode.

    Returns:
      bool State of the debug mode.
    """
    return self._config['debug']

  def __SetDebug(self, new_state):
    """Temporarily change debug mode for a given Client instance.

    Args:
      new_state: bool New state of the debug mode.
    """
    self._config['debug'] = Utils.BoolTypeConvert(new_state, str)

  debug = property(__GetDebug, __SetDebug)

  def __GetRawDebug(self):
    """Return current state of the raw debug mode.

    Returns:
      bool State of the debug mode.
    """
    return self._config['raw_debug']

  def __SetRawDebug(self, new_state):
    """Temporarily change raw debug mode for a given Client instance.

    Args:
      new_state: bool New state of the raw debug mode.
    """
    self._config['raw_debug'] = Utils.BoolTypeConvert(new_state, str)

  raw_debug = property(__GetRawDebug, __SetRawDebug)

  def __GetUseStrict(self):
    """Return current state of the strictness mode.

    Returns:
      str State of the strictness mode.
    """
    return self._config['strict']

  def __SetUseStrict(self, new_state):
    """Temporarily change strictness mode for a given Client instance.

    Args:
      new_state: bool New state of the strictness mode.
    """
    self._config['strict'] = Utils.BoolTypeConvert(new_state, str)

  strict = property(__GetUseStrict, __SetUseStrict)

  def __GetXmlParser(self):
    """Return current state of the xml parser in use.

    Returns:
      bool State of the xml parser in use.
    """
    return self._config['xml_parser']

  def __SetXmlParser(self, new_state):
    """Temporarily change xml parser in use for a given Client instance.

    Args:
      new_state: bool New state of the xml parser to use.
    """
    SanityCheck.ValidateConfigXmlParser(new_state)
    self._config['xml_parser'] = new_state

  xml_parser = property(__GetXmlParser, __SetXmlParser)

  def CallRawMethod(self, soap_message, url, http_proxy):
    """Call API method directly, using raw SOAP message.

    For API calls performed with this method, outgoing data is not run through
    library's validation logic.

    Args:
      soap_message: str SOAP XML message.
      url: str URL of the API service for the method to call.
      http_proxy: str HTTP proxy to use for this API call.

    Returns:
      tuple Response from the API method (SOAP XML response message).
    """
    pass

  def RequestOAuthToken(self, server, callbackurl=None, applicationname=None):
    """Obtains an OAuth Request Token from Google.

    Args:
      server: str The API server that requests will be made to.
      callbackurl: str Optional callback url.
      applicationname: str Optional name of the application to display on the
                       authorization redirect page.
    """
    scope = self._GetOAuthScope(server)
    self.oauth_credentials = self.oauth_handler.GetRequestToken(
        self.oauth_credentials, scope, applicationname=applicationname,
        callbackurl=callbackurl)

  def GetOAuthAuthorizationUrl(self):
    """Gets the OAuth authorization URL for the OAuth token.

    Returns:
      str The URL that will allow the user to authorize the token.
    """
    return self.oauth_handler.GetAuthorizationUrl(self.oauth_credentials)

  def _GetOAuthScope(self, server):
    """Gets the OAuth scope for this user.

    Must be overridden by implementors.

    Args:
      server: str The API server that requests will be made to.
    Returns:
      str The scope to use when requesting an OAuth token.
    """
    raise NotImplementedError

  def UpgradeOAuthToken(self, verifier):
    """Upgrades the authorized OAuth token.

    Args:
      verifier: str The verifier string returning from authorizing the token.
    """
    self.oauth_credentials = self.oauth_handler.GetAccessToken(
        self.oauth_credentials, verifier)

  def __SetOAuthCredentials(self, credentials):
    """Sets the OAuth credentials into the config.

    Args:
      credentials: dict OAuth credentials.
    """
    self._headers['oauth_credentials'] = credentials

  def __GetOAuthCredentials(self):
    """Retrieves the OAuth credentials from the config.

    Returns:
      dict The OAuth credentials.
    """
    return self._headers['oauth_credentials']

  oauth_credentials = property(__GetOAuthCredentials, __SetOAuthCredentials)

  def __SetOAuth2Credentials(self, credentials):
    """Sets the OAuth2 credentials into the config.

    Args:
      credentials: object OAuth2 credentials.
    """
    self._headers['oauth2credentials'] = credentials

  def __GetOAuth2Credentials(self):
    """Retrieves the OAuth2 credentials from the config.

    Returns:
      object The OAuth2 credentials.
    """
    return self._headers['oauth2credentials']

  oauth2credentials = property(__GetOAuth2Credentials, __SetOAuth2Credentials)

  def __SetOAuthHandler(self, oauth_handler):
    """Sets the config to use the specified OAuth Handler.

    Args:
      oauth_handler: OAuthHandler The OAuthHandler to use for OAuth.
    """
    self._config['oauth_handler'] = oauth_handler

  def __GetOAuthHandler(self):
    """Returns the currently set OAuthHandler.

    Returns:
      OAuthHandler The OAuthHandler to use for OAuth.
    """
    return self._config['oauth_handler']

  oauth_handler = property(__GetOAuthHandler, __SetOAuthHandler)

  def __SetUsingOAuth(self, is_using):
    """Deprecated - set oauth_credentials field instead.

    Args:
      is_using: boolean Whether the client is using OAuth or not.
    """
    warnings.warn('Set a value in the oauth_credentials field to enable OAuth.',
                  DeprecationWarning, stacklevel=2)

  def __GetUsingOAuth(self):
    """Deprecated - test field oauth_credentials instead.

    Returns:
      boolean Whether this client is using OAuth or not
    """
    warnings.warn('Evaluate the oauth_credentials field for truth instead.',
                  DeprecationWarning, stacklevel=2)
    return self._headers.get('oauth_credentials')

  use_oauth = property(__GetUsingOAuth, __SetUsingOAuth)

  def __SetCaCertsFile(self, ca_certs_file):
    """Sets the certificates file to use for validating SSL certificates.

    WARNING: Using this feature will monkey-patch a new HTTPS class into
    httplib. Be aware that any other part of your application that uses httplib,
    directly or indirectly, will be affected by its use.

    Args:
      ca_certs_file: string Path to a file storing trusted certificates. If this
                     variable cleared (as in, set to None or something that
                     evaluates to False), the original httplib.HTTPS class will
                     be put back in place and certificate validation will cease.
    """
    try:
      from https import Https
      if not ca_certs_file: ca_certs_file = None
      Https.MonkeyPatchHttplib(ca_certs_file)
    except ImportError:
      warnings.warn('Your Python installation does not support SSL certificate'
                    ' validation!')

  def __GetCaCertsFile(self):
    """Retrieves the current trusted certificates source file path."""
    try:
      from https import Https
      return Https.GetCurrentCertsFile()
    except ImportError:
      warnings.warn('Your Python installation does not support SSL certificate'
                    ' validation!')

  ca_certs = property(__GetCaCertsFile, __SetCaCertsFile)

  def __SetUsingCompression(self, is_using):
    """Sets the config to use HTTP message compression.

    Args:
      is_using: boolean Whether the client is using HTTP compression or not.
    """
    self._config['compress'] = is_using

  def __GetUsingCompression(self):
    """Returns if the client is currently set to use HTTP compression.

    Returns:
      boolean Whether this client is using HTTP comrpession or not
    """
    return self._config['compress']

  compress = property(__GetUsingCompression, __SetUsingCompression)
