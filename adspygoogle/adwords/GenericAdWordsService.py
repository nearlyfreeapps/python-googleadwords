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

"""Generic proxy to access any AdWords web service."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import time

from adspygoogle import SOAPpy
from adspygoogle.adwords import AdWordsUtils
from adspygoogle.adwords import AUTH_TOKEN_EXPIRE
from adspygoogle.adwords import AUTH_TOKEN_SERVICE
from adspygoogle.adwords import LIB_SIG
from adspygoogle.adwords import LIB_URL
from adspygoogle.adwords.AdWordsErrors import AdWordsApiError
from adspygoogle.adwords.AdWordsErrors import AdWordsError
from adspygoogle.adwords.AdWordsErrors import ERRORS
from adspygoogle.adwords.AdWordsSoapBuffer import AdWordsSoapBuffer
from adspygoogle.common import Utils
from adspygoogle.common.Errors import Error
from adspygoogle.common.Errors import ValidationError
from adspygoogle.common.GenericApiService import GenericApiService
from adspygoogle.common.GenericApiService import MethodInfoKeys


class GenericAdWordsService(GenericApiService):

  """Wrapper for any AdWords web service."""

  # The _POSSIBLE_ADWORDS_REQUEST_HEADERS are both the SOAP element names and
  # the self._headers dictionary keys for all elements that may be in an AdWords
  # header.
  _POSSIBLE_ADWORDS_REQUEST_HEADERS = (
      'authToken', 'developerToken', 'userAgent', 'clientCustomerId',
      'validateOnly', 'partialFailure')
  # The _OAUTH_IGNORE_HEADERS are the header elements that should not be
  # included when the client is using OAuth.
  _OAUTH_IGNORE_HEADERS = ('authToken')
  # The _WRAP_LISTS constant indicates that AdWords services do not need to wrap
  # lists in an extra layer of XML element tags.
  _WRAP_LISTS = False
  # The _BUFFER_CLASS is the subclass of SoapBuffer that should be used to track
  # all SOAP interactions
  _BUFFER_CLASS = AdWordsSoapBuffer
  # List of fields we should convert to string.
  _STR_CONVERT = ['clientCustomerId']

  def __init__(self, headers, config, op_config, lock, logger, service_name):
    """Inits GenericAdWordsService.

    Args:
      headers: dict Dictionary object with populated authentication
               credentials.
      config: dict Dictionary object with populated configuration values.
      op_config: dict Dictionary object with additional configuration values for
                 this operation.
      lock: thread.lock Thread lock to use to synchronize requests.
      logger: Logger Instance of Logger to use for logging.
      service_name: string The name of this service.
    """
    group = op_config['group']
    if service_name == 'BulkMutateJobService': group = 'job'
    service_url = [op_config['server'], 'api/adwords', group,
                   op_config['version'], service_name]
    if config['access']:
      service_url.insert(len(service_url) - 1, config['access'])
    service_url = '/'.join(service_url)
    namespace = '/'.join(['https://adwords.google.com/api/adwords',
                          op_config['group'], op_config['version']])
    namespace_extractor = _DetermineNamespacePrefix

    super(GenericAdWordsService, self).__init__(
        headers, config, op_config, lock, logger, service_name, service_url,
        GenericAdWordsService._WRAP_LISTS, GenericAdWordsService._BUFFER_CLASS,
        namespace, namespace_extractor)

    # AdWords-specific changes to the SOAPpy.WSDL.Proxy
    methodattrs = {}
    for namespace in self._soappyservice.wsdl.types.keys():
      group_name = AdWordsUtils.ExtractGroupNameFromUrl(namespace)
      methodattrs['xmlns:' + group_name] = namespace
    methodattrs['xmlns'] = self._namespace
    self._soappyservice.soapproxy.methodattrs = methodattrs

  def _SetHeaders(self):
    """Sets the SOAP headers for this service's requests."""
    now = time.time()
    if ((('authToken' not in self._headers and
          'auth_token_epoch' not in self._config) or
         int(now - self._config['auth_token_epoch']) >= AUTH_TOKEN_EXPIRE) and
        not (self._headers.get('oauth_credentials') or
             self._headers.get('oauth2credentials'))):
      if ('email' not in self._headers or not self._headers['email'] or
          'password' not in self._headers or not self._headers['password']):
        raise ValidationError('Required authentication headers, \'email\' and '
                              '\'password\', are missing. Unable to regenerate '
                              'authentication token.')
      self._headers['authToken'] = Utils.GetAuthToken(
          self._headers['email'], self._headers['password'], AUTH_TOKEN_SERVICE,
          LIB_SIG, self._config['proxy'])
      self._config['auth_token_epoch'] = time.time()

    # Apply headers to the SOAPpy service.
    header_attrs = {
        'xmlns': self._namespace,
        'xmlns:cm': ('https://adwords.google.com/api/adwords/cm/' +
                     self._op_config['version'])
    }
    soap_headers = SOAPpy.Types.headerType(attrs=header_attrs)
    request_header_data = {}
    for key in GenericAdWordsService._POSSIBLE_ADWORDS_REQUEST_HEADERS:
      if (key in GenericAdWordsService._OAUTH_IGNORE_HEADERS
          and (self._headers.get('oauth_credentials') or
               self._headers.get('oauth2credentials'))):
        continue
      if key in self._headers and self._headers[key]:
        value = self._headers[key]
        if key in GenericAdWordsService._STR_CONVERT:
          value = str(value)
        request_header_data['cm:' + key] = SOAPpy.Types.stringType(
            value)
    request_header = SOAPpy.Types.structType(
        data=request_header_data, name='RequestHeader', typed=0)
    soap_headers.RequestHeader = request_header
    self._soappyservice.soapproxy.header = soap_headers

  def _GetMethodInfo(self, method_name):
    """Pulls all of the relevant data about a method from a SOAPpy service.

    The return dictionary has two keys, MethodInfoKeys.INPUTS and
    MethodInfoKeys.OUTPUTS. Each of these keys has a list value. These lists
    contain a dictionary of information on the input/output parameter list, in
    order.

    Args:
      method_name: string The name of the method to pull information for.
    Returns:
      dict A dictionary containing information about a SOAP method.
    """
    rval = {}
    rval[MethodInfoKeys.INPUTS] = []
    for i in range(len(self._soappyservice.wsdl.types[
        self._namespace].elements[method_name].content.content.content)):
      param_attributes = self._soappyservice.wsdl.types[
          self._namespace].elements[method_name].content.content.content[
              i].attributes
      inparam = {
          MethodInfoKeys.ELEMENT_NAME: param_attributes['name'],
          MethodInfoKeys.NS: param_attributes['type'].getTargetNamespace(),
          MethodInfoKeys.TYPE: param_attributes['type'].getName(),
          MethodInfoKeys.MAX_OCCURS: param_attributes['maxOccurs']
      }
      rval[MethodInfoKeys.INPUTS].append(inparam)

    rval[MethodInfoKeys.OUTPUTS] = []
    for i in range(len(self._soappyservice.wsdl.types[
        self._namespace].elements[
            method_name + 'Response'].content.content.content)):
      param_attributes = self._soappyservice.wsdl.types[
          self._namespace].elements[
              method_name + 'Response'].content.content.content[i].attributes
      outparam = {
          MethodInfoKeys.ELEMENT_NAME: param_attributes['name'],
          MethodInfoKeys.NS: param_attributes['type'].getTargetNamespace(),
          MethodInfoKeys.TYPE: param_attributes['type'].getName(),
          MethodInfoKeys.MAX_OCCURS: param_attributes['maxOccurs']
      }
      rval[MethodInfoKeys.OUTPUTS].append(outparam)
    return rval

  def _TakeActionOnSoapCall(self, method_name, args):
    """Gives the service a chance to take product-specific action on raw inputs.

    AdWords will support legacy xsi_typing for the BulkMutateJobService.

    Args:
      method_name: string The name of the SOAP operation being called.
      args: tuple The arguments passed into the SOAP operation.

    Returns:
      tuple The method arguments, possibly modified.
    """
    if (self._service_name == 'BulkMutateJobService' and
        method_name.lower() == 'mutate'):
      AdWordsUtils.TransformJobOperationXsi(args[0])
    elif (self._service_name == 'UserListService' and
          method_name.lower() == 'mutate'):
      if isinstance(args[0], (list, tuple)):
        for operation in args[0]:
          if isinstance(operation, dict) and 'operand' in operation:
            AdWordsUtils.TransformUserListRuleOperands(operation['operand'])
    return args

  def _HandleLogsAndErrors(self, buf, start_time, stop_time, error=None):
    """Manage SOAP XML message.

    Args:
      buf: SoapBuffer SOAP buffer.
      start_time: str Time before service call was invoked.
      stop_time: str Time after service call was invoked.
      [optional]
      error: dict Error, if any.
    """
    if error is None:
      error = {}
    try:
      # Update the number of units and operations consumed by API call.
      if buf.GetCallUnits() and buf.GetCallOperations():
        self._config['units'][0] += int(buf.GetCallUnits())
        self._config['operations'][0] += int(buf.GetCallOperations())
        self._config['last_units'][0] = int(buf.GetCallUnits())
        self._config['last_operations'][0] = int(buf.GetCallOperations())

      handlers = self.__GetLogHandlers(buf)
      fault = super(GenericAdWordsService, self)._ManageSoap(
          buf, handlers, LIB_URL, start_time, stop_time, error)
      if fault:
        # Raise a specific error, subclass of AdWordsApiError.
        if 'detail' in fault and fault['detail']:
          if 'code' in fault['detail']:
            code = int(fault['detail']['code'])
            if code in ERRORS: raise ERRORS[code](fault)
          elif 'errors' in fault['detail']:
            error_type = fault['detail']['errors'][0]['type']
            if error_type in ERRORS: raise ERRORS[str(error_type)](fault)

        if isinstance(fault, str):
          raise AdWordsError(fault)
        elif isinstance(fault, dict):
          raise AdWordsApiError(fault)
    except AdWordsApiError, e:
      raise e
    except AdWordsError, e:
      raise e
    except Error, e:
      if error: e = error
      raise Error(e)

  def __GetLogHandlers(self, buf):
    """Gets a list of log handlers for the AdWords library.

    Args:
      buf: SoapBuffer SOAP buffer from which calls are retrieved for logging.

    Returns:
      list Log handlers for the AdWords library.
    """
    return [
        {
            'tag': 'xml_log',
            'name': 'soap_xml',
            'data': ''
        },
        {
            'tag': 'request_log',
            'name': 'request_info',
            'data': str('host=%s service=%s method=%s operator=%s '
                        'responseTime=%s operations=%s units=%s requestId=%s'
                        % (Utils.GetNetLocFromUrl(self._service_url),
                           self._service_name, buf.GetCallName(),
                           buf.GetOperatorName(), buf.GetCallResponseTime(),
                           buf.GetCallOperations(), buf.GetCallUnits(),
                           buf.GetCallRequestId()))
        },
        {
            'tag': '',
            'name': 'adwords_api_lib',
            'data': ''
        }
    ]


def _DetermineNamespacePrefix(url):
  """Returns the SOAP prefix to use for definitions within the given namespace.

  Args:
    url: string The URL of the namespace.

  Returns:
    string The SOAP namespace prefix to use for the given namespace.
  """
  return AdWordsUtils.ExtractGroupNameFromUrl(url) + ':'
