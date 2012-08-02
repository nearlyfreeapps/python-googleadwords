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

"""Generic service wrapper to access any API."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import httplib
import sys
import time
import threading

from adspygoogle import SOAPpy
from adspygoogle.common import MessageHandler
from adspygoogle.common import SanityCheck
from adspygoogle.common import Utils
from adspygoogle.common.Errors import AuthTokenError
from adspygoogle.common.Errors import Error
from adspygoogle.common.Errors import ValidationError
from adspygoogle.common.Logger import Logger
from adspygoogle.SOAPpy.wstools.WSDLTools import WSDLError

sys_stdout_monkey_lock = threading.Lock()

class GenericApiService(object):

  """Generic wrapper around a SOAPpy proxy.

  GenericApiService is an abstract class and should not be instantiated
  directly. Classes which implement this class are required to provide the
  following methods:

  _SetHeaders
  _GetMethodInfo
  _HandleLogsAndErrors

  The following methods are intended to be overridden as necessary, but provide
  functioning default implementations:

  _TakeActionOnSoapCall
  _TakeActionOnPackedArgs
  """

  def __init__(self, headers, config, op_config, lock, logger, service_name,
               service_url, wrap_lists, buffer_class, namespace,
               namespace_extractor):
    """Inits GenericApiService.

    Args:
      headers: dict Dictionary object with populated authentication
               credentials.
      config: dict Dictionary object with populated configuration values.
      op_config: dict Dictionary object with additional configuration values for
                 this operation.
      lock: mixed Thread lock to use to synchronize requests. May be a
            thread.lock or a threading.RLock
      logger: Logger Instance of Logger to use for logging.
      service_name: string The name of this service.
      service_url: string The URL pointing to this web service.
      wrap_lists: boolean Whether this service needs to wrap lists in an
                  additional layer of XML element tags.
      buffer_class: class The SoapBuffer subclass to use as a buffer.
      namespace: string The namespace this service uses by default.
      namespace_extractor: function A function which takes a URL and returns the
                           namespace prefix to use to represent it.

    Raises:
      Error: The WSDL for this service could not be found. Will also be raised
      if GenericApiService is initialized directly rather than by a subclass.
    """
    if self.__class__ == GenericApiService:
      raise Error('GenericApiService cannot be instantiated directly.')

    self._headers = headers
    self._config = config
    self._op_config = op_config
    self._lock = lock
    self._logger = logger
    self._service_name = service_name
    self._service_url = service_url
    self._wrap_lists = wrap_lists
    self._buffer_class = buffer_class
    self._namespace = namespace
    self._namespace_extractor = namespace_extractor
    self._method_proxies = {}

    wsdl_url = service_url + '?wsdl'
    try:
      self._soappyservice = SOAPpy.WSDL.Proxy(
          wsdl_url, noroot=1, http_proxy=self._op_config['http_proxy'])
    except WSDLError:
      raise Error('Unable to locate WSDL at path \'%s\'' % wsdl_url)
    else:
      for method_key in self._soappyservice.methods:
        self._soappyservice.methods[method_key].location = service_url

      self._soappyservice.soapproxy.config.typed = 0
      self._soappyservice.soapproxy.config.namespaceStyle = '2001'
      self._soappyservice.soapproxy.config.returnFaultInfo = 1
      self._soappyservice.soapproxy.config.dumpHeadersIn = 1
      self._soappyservice.soapproxy.config.dumpHeadersOut = 1
      self._soappyservice.soapproxy.config.dumpSOAPIn = 1
      self._soappyservice.soapproxy.config.dumpSOAPOut = 1

  def __getattr__(self, name):
    """Takes an attribute name and tries to create a SOAP call proxy around it.

    Args:
      name: string The name of the attribute to fetch. This should be the name
            of an operation/method in the SOAP service this object represents.

    Returns:
      function A function wrapping an invocation to the given operation
      (actually a function) in the SOAP service this object contains.

    Raises:
      AttributeError: if the given attribute name cannot be found in this
      object's SOAP service. Most likely, the given name was not a WSDL-defined
      SOAP operation in this service.
    """
    if name not in self._method_proxies:
      self._method_proxies[name] = self._CreateMethod(name)
    return self._method_proxies[name]

  def __dir__(self):
    """Overrides default dir() behavior; prints the service's public methods."""
    dir_list = ['CallRawMethod']
    dir_list.extend(self._soappyservice.methods.keys())
    return dir_list

  def _SetHeaders(self):
    """Sets the SOAP headers for this service's requests.

    Must be overridden by an extending class.
    """
    raise NotImplementedError

  def _GetMethodInfo(self, method_name):
    """Pulls all of the relevant data about a method from a SOAPpy service.

    Must be overridden by an extending class.

    The return dictionary has two keys, MethodInfoKeys.INPUTS and
    MethodInfoKeys.OUTPUTS. Each of these keys has a list value. These lists
    contain a dictionary of information on the input/output parameter list, in
    order.

    Args:
      method_name: string The name of the method to pull information for.

    Returns:
      dict A dictionary containing information about a SOAP method.
    """
    raise NotImplementedError

  def _HandleLogsAndErrors(self, buf, start_time, stop_time, error=None):
    """Manage SOAP XML message.

    Must be overridden by an extending class.

    Args:
      buf: SoapBuffer SOAP buffer.
      start_time: str Time before service call was invoked.
      stop_time: str Time after service call was invoked.
      [optional]
      error: dict Error, if any.
    """
    raise NotImplementedError

  def _TakeActionOnSoapCall(self, method_name, args):
    """Gives the service a chance to take product-specific action on raw inputs.

    If a product needs to take the opportunity to modify the inputs, then its
    extending service class must override this method.

    Args:
      method_name: string The name of the SOAP operation being called.
      args: tuple The arguments passed into the SOAP operation.

    Returns:
      tuple The method arguments, possibly modified.
    """
    return args

  def _TakeActionOnPackedArgs(self, method_name, ksoap_args):
    """Allows a service to take product-specific action on packed arguments.

    If a product needs to take the opportunity to modify the packed inputs, then
    its extending service class must override this method.

    Args:
      method_name: string The name of the SOAP operation being called.
      ksoap_args: dictionary The keyword arguments packed for the SOAP
                  operation.

    Returns:
      dictionary The packed keyword arguments, possibly modified.
    """
    return ksoap_args

  def _ReadyOAuth(self):
    """If OAuth is on, sets the transport handler to add OAuth HTTP header."""
    if (self._config.get('oauth_handler') and
        self._headers.get('oauth_credentials')):
      signedrequestparams = self._config[
          'oauth_handler'].GetSignedRequestParameters(
              self._headers['oauth_credentials'], str(self._service_url))
      self._soappyservice.soapproxy.transport.additional_headers[
          'Authorization'] = (
              'OAuth ' +
              self._config['oauth_handler'].FormatParametersForHeader(
                  signedrequestparams))
    elif self._headers.get('oauth2credentials'):
      self._headers['oauth2credentials'].apply(
          self._soappyservice.soapproxy.transport.additional_headers)
    else:
      if ('Authorization' in
          self._soappyservice.soapproxy.transport.additional_headers):
        del self._soappyservice.soapproxy.transport.additional_headers[
            'Authorization']

  def _ReadyCompression(self):
    """Sets whether the HTTP transport layer should use compression."""
    compress = Utils.BoolTypeConvert(self._config['compress'])
    self._soappyservice.soapproxy.config.send_compressed = compress
    self._soappyservice.soapproxy.config.accept_compressed = compress

  def _CreateMethod(self, method_name):
    """Create a method wrapping an invocation to the SOAP service."""
    try:
      soap_service_method = getattr(self._soappyservice, method_name)
    except AttributeError:
      method_name = method_name[0].lower() + method_name[1:]
      soap_service_method = getattr(self._soappyservice, method_name)

    def CallMethod(*args):
      """Perform a SOAP call."""
      try:
        self._lock.acquire()
        self._SetHeaders()
        self._ReadyOAuth()
        self._ReadyCompression()

        args = self._TakeActionOnSoapCall(method_name, args)
        method_info = self._GetMethodInfo(method_name)
        method_attrs_holder = None
        if not method_info[MethodInfoKeys.INPUTS]:
          # Don't put any namespaces other than this service's namespace on
          # calls with no input params.
          method_attrs_holder = self._soappyservice.soapproxy.methodattrs
          self._soappyservice.soapproxy.methodattrs = {
              'xmlns': self._namespace
          }

        if len(args) != len(method_info[MethodInfoKeys.INPUTS]):
          raise TypeError(''.join([
              method_name + '() takes exactly ',
              str(len(self._soappyservice.methods[method_name].inparams)),
              ' argument(s). (', str(len(args)), ' given)']))

        ksoap_args = {}
        for i in range(len(method_info[MethodInfoKeys.INPUTS])):
          if Utils.BoolTypeConvert(self._config['strict']):
            SanityCheck.SoappySanityCheck(
                self._soappyservice, args[i],
                method_info[MethodInfoKeys.INPUTS][i][MethodInfoKeys.NS],
                method_info[MethodInfoKeys.INPUTS][i][MethodInfoKeys.TYPE],
                method_info[MethodInfoKeys.INPUTS][i][
                    MethodInfoKeys.MAX_OCCURS])

          element_name = str(method_info[MethodInfoKeys.INPUTS][i][
              MethodInfoKeys.ELEMENT_NAME])

          ksoap_args[element_name] = MessageHandler.PackForSoappy(
              args[i],
              method_info[MethodInfoKeys.INPUTS][i][MethodInfoKeys.NS],
              method_info[MethodInfoKeys.INPUTS][i][MethodInfoKeys.TYPE],
              self._soappyservice,
              self._wrap_lists,
              self._namespace_extractor)

        ksoap_args = self._TakeActionOnPackedArgs(method_name, ksoap_args)

        buf = self._buffer_class(
            xml_parser=self._config['xml_parser'],
            pretty_xml=Utils.BoolTypeConvert(self._config['pretty_xml']))
        sys_stdout_monkey_lock.acquire()
        try:
            old_stdout = sys.stdout
            sys.stdout = buf

            error = {}
            response = None
            start_time = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
              response = MessageHandler.UnpackResponseAsDict(
                  soap_service_method(**ksoap_args))
            except Exception, e:
              error['data'] = e
            stop_time = time.strftime('%Y-%m-%d %H:%M:%S')
            # Restore stdout
            sys.stdout = old_stdout
        finally:
            sys_stdout_monkey_lock.release()

        if isinstance(response, Error):
          error = response

        if not Utils.BoolTypeConvert(self._config['raw_debug']):
          self._HandleLogsAndErrors(buf, start_time, stop_time, error)

        # When debugging mode is ON, fetch last traceback.
        if Utils.BoolTypeConvert(self._config['debug']):
          if Utils.LastStackTrace() and Utils.LastStackTrace() != 'None':
            error['trace'] = Utils.LastStackTrace()

        # Catch local errors prior to going down to the SOAP layer, which may
        # not exist for this error instance.
        if 'data' in error and not buf.IsHandshakeComplete():
          # Check if buffer contains non-XML data, most likely an HTML page.
          # This happens in the case of 502 errors (and similar). Otherwise,
          # this is a local error and API request was never made.
          html_error = Utils.GetErrorFromHtml(buf.GetBufferAsStr())
          if html_error:
            msg = html_error
          else:
            msg = str(error['data'])
            if Utils.BoolTypeConvert(self._config['debug']):
              msg += '\n%s' % error['trace']

          # When debugging mode is ON, store the raw content of the buffer.
          if Utils.BoolTypeConvert(self._config['debug']):
            error['raw_data'] = buf.GetBufferAsStr()

          # Catch errors from AuthToken and ValidationError levels, raised
          # during try/except above.
          if isinstance(error['data'], AuthTokenError):
            raise AuthTokenError(msg)
          elif isinstance(error['data'], ValidationError):
            raise ValidationError(error['data'])
          if 'raw_data' in error:
            msg = '%s [RAW DATA: %s]' % (msg, error['raw_data'])
          return Error(msg)

        if Utils.BoolTypeConvert(self._config['raw_response']):
          response = buf.GetRawSoapIn()
        elif error:
          response = error
        else:
          output_types = [(out_param[MethodInfoKeys.NS],
                           out_param[MethodInfoKeys.TYPE],
                           out_param[MethodInfoKeys.MAX_OCCURS]) for out_param
                          in method_info[MethodInfoKeys.OUTPUTS]]
          response = MessageHandler.RestoreListTypeWithSoappy(
              response, self._soappyservice, output_types)

        if Utils.BoolTypeConvert(self._config['wrap_in_tuple']):
          response = MessageHandler.WrapInTuple(response)

        # Restore method_attrs if they were over-ridden
        if method_attrs_holder:
          self._soappyservice.soapproxy.methodattrs = method_attrs_holder

        return response
      finally:
        self._lock.release()

    return CallMethod

  def _ManageSoap(self, buf, log_handlers, lib_url, start_time, stop_time,
                  error=None):
    """Manage SOAP XML message.

    Args:
      buf: SoapBuffer SOAP buffer.
      log_handlers: list Log handlers.
      lib_url: str URL of the project's home.
      start_time: str Time before service call was invoked.
      stop_time: str Time after service call was invoked.
      [optional]
      error: dict Error, if any.

    Returns:
      mixed Any fault that occurred with this SOAP operation. The data type may
      be a string or dictionary depending on what went wrong. If there were no
      faults with this operation, None is returned.
    """
    if error is None:
      error = {}

    # Load trace errors, if any.
    if error and 'trace' in error:
      error_msg = error['trace']
    else:
      error_msg = ''

    # Check if response was successful or not.
    if error and 'data' in error:
      is_fault = True
    else:
      is_fault = False

    # Forward SOAP XML, errors, and other debugging data to console, external
    # file, both, or ignore. Each handler supports the following elements,
    #   tag: Config value for this handler. If left empty, will never write
    #        data to file.
    #   target: Target/destination represented by this handler (i.e. FILE,
    #           CONSOLE, etc.). Initially, it should be set to Logger.NONE.
    #   name: Name of the log file to use.
    #   data: Data to write.
    for handler in log_handlers:
      if handler['tag'] == 'xml_log':
        handler['target'] = Logger.NONE
        handler['data'] += ('StartTime: %s\n%s\n%s\n%s\n%s\nEndTime: %s'
                            % (start_time, buf.GetHeadersOut(),
                               buf.GetSoapOut(), buf.GetHeadersIn(),
                               buf.GetSoapIn(), stop_time))
      elif handler['tag'] == 'request_log':
        handler['target'] = Logger.NONE
        handler['data'] += ' isFault=%s' % is_fault
      elif not handler['tag']:
        handler['target'] = Logger.NONE
        handler['data'] += 'DEBUG: %s' % error_msg
    for handler in log_handlers:
      if (handler['tag'] and
          Utils.BoolTypeConvert(self._config[handler['tag']])):
        handler['target'] = Logger.FILE
      # If debugging is On, raise handler's target two levels,
      #   NONE -> CONSOLE
      #   FILE -> FILE_AND_CONSOLE.
      if Utils.BoolTypeConvert(self._config['debug']):
        handler['target'] += 2

      if (handler['target'] != Logger.NONE and handler['data'] and
          handler['data'] != 'None' and handler['data'] != 'DEBUG: '):
        self._logger.Log(handler['name'], handler['data'],
                         log_level=Logger.DEBUG, log_handler=handler['target'])

    # If raw response is requested, no need to validate and throw appropriate
    # error. Up to the end user to handle successful or failed request.
    if Utils.BoolTypeConvert(self._config['raw_response']): return

    # Report SOAP fault.
    if is_fault:
      try:
        fault = buf.GetFaultAsDict()
        if 'detail' in fault and fault['detail'] is None:
           fault = buf.GetFaultAsDictWhenOtherFails()
        if not fault: msg = error['data']
      except Exception:
        fault = None
        # An error is not a SOAP fault, but check if some other error.
        if error_msg:
          msg = error_msg
        else:
          msg = ('Unable to parse incoming SOAP XML. Please, file '
                 'a bug at %s/issues/list.' % lib_url)
      if not fault and msg: return msg
      return fault
    return None

  def CallRawMethod(self, soap_message):
    """Makes an API call by POSTing a raw SOAP XML message to the server.

    Args:
      soap_message: str SOAP XML message.

    Returns:
      tuple Raw XML response from the API method.

    Raises:
      Error: if the SOAP call is not successful. Most likely this is the result
      of the server sending back an HTTP error, such as a 502.
    """

    self._lock.acquire()
    try:
      buf = self._buffer_class(
          xml_parser=self._config['xml_parser'],
          pretty_xml=Utils.BoolTypeConvert(self._config['pretty_xml']))

      http_header = {
          'post': self._service_url,
          'host': Utils.GetNetLocFromUrl(self._op_config['server']),
          'user_agent': '%s; CallRawMethod' % self.__class__.__name__,
          'content_type': 'text/xml; charset=\"UTF-8\"',
          'content_length': '%d' % len(soap_message),
          'soap_action': ''
      }

      # Add OAuth header if OAuth is enabled.
      if (self._config.get('oauth_handler') and
          self._headers.get('oauth_credentials')):
        signedrequestparams = self._config[
            'oauth_handler'].GetSignedRequestParameters(
                self._headers['oauth_credentials'], self._service_url)
        http_header['authorization'] = (
            'OAuth ' + self._config['oauth_handler'].FormatParametersForHeader(
                signedrequestparams))

      self._start_time = time.strftime('%Y-%m-%d %H:%M:%S')
      buf.write('%s Outgoing HTTP headers %s\nPOST %s\nHost: %s\nUser-Agent: '
                '%s\nContent-type: %s\nContent-length: %s\nSOAPAction: %s\n' %
                ('*'*3, '*'*46, http_header['post'], http_header['host'],
                 http_header['user_agent'], http_header['content_type'],
                 http_header['content_length'], http_header['soap_action']))
      if (self._config.get('oauth_handler') and
          self._headers.get('oauth_credentials') or
          self._headers.get('oauth2credentials')):
        buf.write('Authorization: ' + http_header['authorization'] + '\n')
      buf.write('%s\n%s Outgoing SOAP %s\n%s\n%s\n' %
                ('*'*72, '*'*3, '*'*54, soap_message, '*'*72))

      if self._op_config['http_proxy']:
        real_address = self._op_config['http_proxy']
      else:
        real_address = http_header['host']

      # Construct header and send SOAP message.
      web_service = httplib.HTTPS(real_address)
      web_service.putrequest('POST', http_header['post'])
      web_service.putheader('Host', http_header['host'])
      web_service.putheader('User-Agent', http_header['user_agent'])
      web_service.putheader('Content-type', http_header['content_type'])
      web_service.putheader('Content-length', http_header['content_length'])
      web_service.putheader('SOAPAction', http_header['soap_action'])
      if (self._config.get('oauth_handler') and
          self._headers.get('oauth_credentials') or
          self._headers.get('oauth2credentials')):
        web_service.putheader('Authorization', http_header['authorization'])
      web_service.endheaders()
      web_service.send(soap_message)

      # Get response.
      status_code, status_message, header = web_service.getreply()
      response = web_service.getfile().read()

      header = str(header).replace('\r', '')
      buf.write(('%s Incoming HTTP headers %s\n%s %s\n%s\n%s\n%s Incoming SOAP'
                 ' %s\n%s\n%s\n' % ('*'*3, '*'*46, status_code, status_message,
                                    header, '*'*72, '*'*3, '*'*54, response,
                                    '*'*72)))
      self._stop_time = time.strftime('%Y-%m-%d %H:%M:%S')

      # Catch local errors prior to going down to the SOAP layer, which may not
      # exist for this error instance.
      if not buf.IsHandshakeComplete() or not buf.IsSoap():
        # The buffer contains non-XML data, most likely an HTML page. This
        # happens in the case of 502 errors.
        html_error = Utils.GetErrorFromHtml(buf.GetBufferAsStr())
        if html_error:
          msg = html_error
        else:
          msg = 'Unknown error.'
        raise Error(msg)

      self._HandleLogsAndErrors(buf, self._start_time, self._stop_time)
    finally:
      self._lock.release()
    if self._config['wrap_in_tuple']:
      response = MessageHandler.WrapInTuple(response)
    return response


class MethodInfoKeys(object):
  """Static constants holder; keys used to pass method information around."""

  INPUTS = 'inputs'
  ELEMENT_NAME = 'elemname'
  NS = 'ns'
  TYPE = 'type'
  OUTPUTS = 'outputs'
  MAX_OCCURS = 'maxOccurs'
