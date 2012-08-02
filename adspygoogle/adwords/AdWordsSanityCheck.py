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

"""Validation functions."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

from adspygoogle.common.Errors import ValidationError

DEPRECATED_AFTER = {
    'ServicedAccountService': 'v201109_1',
    'CreateAccountService': 'v201109_1',
    'CampaignTargetService': 'v201109_1'
}


def ValidateServer(server, version):
  """Sanity check for API server.

  Args:
    server: str API server to access for this API call.
    version: str API version being used to access the server.

  Raises:
    ValidationError: if the given API server or version is not valid.
  """
  # Map of supported API servers and versions.
  prod = {'v201109': 'https://adwords.google.com',
          'v201109_1': 'https://adwords.google.com',
          'v201206': 'https://adwords.google.com'}
  sandbox = {'v201109': 'https://adwords-sandbox.google.com',
             'v201109_1': 'https://adwords-sandbox.google.com',
             'v201206': 'https://adwords-sandbox.google.com'}

  if server not in prod.values() and server not in sandbox.values():
    msg = ('Given API server, \'%s\', is not valid. Expecting one of %s.'
           % (server, sorted(prod.values() + sandbox.values())[1:]))
    raise ValidationError(msg)

  if version not in prod.keys() and version not in sandbox.keys():
    msg = ('Given API version, \'%s\', is not valid. Expecting one of %s.'
           % (version, sorted(set(prod.keys() + sandbox.keys()))))
    raise ValidationError(msg)

  if server != prod[version] and server != sandbox[version]:
    msg = ('Given API version, \'%s\', is not compatible with given server, '
           '\'%s\'.' % (version, server))
    raise ValidationError(msg)


def ValidateHeadersForServer(headers, server):
  """Check if provided headers match the ones expected on the provided server.

  The SOAP headers on Sandbox server are different from production.  See
  http://code.google.com/apis/adwords/docs/developer/adwords_api_sandbox.html.
  """
  fits_sandbox = False

  # The developerToken SOAP header in Sandbox has to be same as email SOAP
  # header with appended "++" and the currency code.
  if ('email' in headers and headers['email'] and
      headers['developerToken'].find('%s++' % headers['email'], 0,
                                     len(headers['email']) + 2) > -1):
    fits_sandbox = True
  elif ('authToken' in headers and headers['authToken'] and
        headers['developerToken'].find('++') ==
        len(headers['developerToken']) - 5):
    fits_sandbox = True
  else:
    fits_sandbox = False

  # Sandbox server is identifying by the "sandbox" part in the URL (e.g.,
  # https://sandbox.google.com or https://adwords-sandbox.google.com).
  if server.find('sandbox') > -1:
    if not fits_sandbox:
      msg = ('Invalid credentials for \'%s\', see http://code.google.com/apis/'
             'adwords/docs/developer/adwords_api_sandbox.html#requestheaders.'
             % server)
      raise ValidationError(msg)
  elif server.find('sandbox') < 0:
    if fits_sandbox:
      msg = ('Invalid credentials for \'%s\', see http://code.google.com/apis/'
             'adwords/docs/developer/index.html#adwords_api_intro_request.'
             % server)
      raise ValidationError(msg)


def ValidateService(service, version):
  """Checks if this service is available in the requested version.

  Args:
    service: str Service being requested.
    version: str Version being requested.
  """
  if service in DEPRECATED_AFTER and version > DEPRECATED_AFTER[service]:
    raise ValidationError('%s is not available in %s' % (service, version))
