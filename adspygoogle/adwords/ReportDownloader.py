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

"""Utility functions for working with reports."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import gzip
import re
import StringIO
import time
import urllib
import urllib2

from adspygoogle import SOAPpy
from adspygoogle.adwords import AUTH_TOKEN_EXPIRE
from adspygoogle.adwords import AUTH_TOKEN_SERVICE
from adspygoogle.adwords import LIB_SIG
from adspygoogle.adwords.AdWordsErrors import AdWordsError
from adspygoogle.adwords.util import XsdToWsdl
from adspygoogle.common import MessageHandler
from adspygoogle.common import SanityCheck
from adspygoogle.common import Utils
from adspygoogle.common.Errors import ValidationError
from adspygoogle.common.Logger import Logger


SERVICE_NAME = 'ReportDefinitionService'
DOWNLOAD_URL_BASE = '/api/adwords/reportdownload'
REPORT_ID='?__rd=%s'
VERSIONED='/%s'
OLD_ERROR_REGEX = r'^!!!([-\d]+)\|\|\|([-\d]+)\|\|\|(.*)\?\?\?'
ATTRIBUTES_REGEX = r'( )?[\w:-]+="[\w:\[\]-]+"'
BUF_SIZE = 4096


class ReportDownloader(object):

  """Utility class that downloads reports."""

  def __init__(self, headers, config, op_config, logger):
    """Inits ReportDownloader.

    Args:
      headers: dict Dictionary object with populated authentication
               credentials.
      config: dict Dictionary object with populated configuration values.
      op_config: dict Dictionary object with additional configuration values for
                 this operation.
    """
    self._headers = headers
    self._config = config
    self._op_config = op_config
    self._message_handler = MessageHandler
    namespace_suffix = '/'.join(('/api/adwords', op_config['group'],
                                 self._op_config['version']))
    self._namespace = 'https://adwords.google.com' + namespace_suffix
    xsd_url = '%s%s%s/reportDefinition.xsd' % (op_config['server'],
                                               '/api/adwords/reportdownload/',
                                               self._op_config['version'])
    self._soappyservice = XsdToWsdl.CreateWsdlFromXsdUrl(xsd_url)
    self._logger = logger

  def DownloadReport(self, report_definition_or_id, return_micros=False,
                     file_path=None, fileobj=None):
    """Downloads a report by object or id.

    Args:
      report_definition_or_id: dict or str Report or reportDefinitionId.
      return_micros: bool Whether to return currency in micros (optional).
      file_path: str File path to download to (optional).
      fileobj: file An already-open file-like object that supports write()
               (optional).

    Returns:
      str Report data if file_path and fileobj are None, None if fileobj is
          not None and file_path otherwise.
    """
    if not fileobj and file_path:
      fileobj = open(file_path, 'w+')

    if isinstance(report_definition_or_id, dict):
      return self.__DownloadAdHocReport(report_definition_or_id, return_micros,
                                        fileobj) or file_path
    else:
      return self.__DownloadReportById(report_definition_or_id, return_micros,
                                       fileobj) or file_path

  def DownloadReportWithAwql(self, report_query, download_format,
                             return_micros=False, file_path=None, fileobj=None):
    """Downloads a report with AWQL.

    Args:
      report_query: str AWQL for the report.
      download_format: str Download format. E.g. CSV, TSV, XML.
      return_micros: bool Whether to return currency in micros (optional).
      file_path: str File path to download to (optional).
      fileobj: file An already-open file-like object that supports write()
               (optional).

    Returns:
      str Report data if file_path and fileobj are None, None if fileobj is
          not None and file_path otherwise.
    """
    if not fileobj and file_path:
      fileobj = open(file_path, 'w+')

    return self.__DownloadAdHocReportWithAwql(report_query,
                                              download_format,
                                              return_micros,
                                              fileobj) or file_path

  def __DownloadAdHocReport(self, report_definition, return_micros=False,
                            fileobj=None):
    """Downloads an AdHoc report.

    Args:
      report_definition: dict Report to download.
      return_micros: bool Whether to return currency in micros (optional).
      fileobj: file File to write to (optional).

    Returns:
      str Report data if no fileobj, otherwise None.
    """
    report_xml = self.__GetReportXml(report_definition)
    query_params = {'__rdxml': report_xml}

    payload = urllib.urlencode(query_params)
    return self.__DownloadReport(payload, return_micros, fileobj)

  def __DownloadAdHocReportWithAwql(self,
                                    report_query,
                                    download_format,
                                    return_micros=False,
                                    fileobj=None):
    """Downloads an AdHoc report with AWQL.

    Args:
      report_query: str AWQL to download a report for.
      download_format: str Format of the report download.
      return_micros: bool Whether to return currency in micros (optional).
      fileobj: file File to write to (optional).

    Returns:
      str Report data if no fileobj, otherwise None.
    """
    query_params = {
        '__fmt': download_format,
        '__rdquery': report_query
    }

    payload = urllib.urlencode(query_params)
    return self.__DownloadReport(payload, return_micros, fileobj)

  def __DownloadReport(self, report_payload, return_micros=False, fileobj=None):
    """Downloads an AdHoc report for the specified payload.

    Args:
      report_payload: str Report payload to POST to the server.
      return_micros: bool Whether to return currency in micros (optional).
      fileobj: file File to write to (optional).

    Returns:
      str Report data if no fileobj, otherwise None.
    """
    url = self.__GenerateUrl()
    self.__ReloadAuthToken()
    headers = self.__GenerateHeaders(return_micros, url)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Content-Length'] = str(len(report_payload))
    return self.__MakeRequest(url, headers, fileobj, payload=report_payload)

  def __GetReportXml(self, report):
    """Transforms the report object into xml.

    Args:
      report: dict ReportDefinition object to turn to xml.

    Returns:
      str ReportDefinition XML.
    """
    SanityCheck.SoappySanityCheck(self._soappyservice, report, self._namespace,
                                  u'reportDefinition')

    packed = self._message_handler.PackForSoappy(report, self._namespace,
                                                 'reportDefinition',
                                                 self._soappyservice, False,
                                                 lambda x: '')

    # Use a SOAPBuilder
    builder = SOAPpy.SOAPBuilder(kw={'reportDefinition': packed}, envelope=0,
                                 noroot=1)

    # Fixes list serialization.
    builder.config.typed = False

    # Hack, need to remove top element and body wrapper.
    builder._xml_top = ''
    builder.body = 0

    # Build the XML.
    report_xml = builder.build()

    # Removes xsi:types.
    report_xml = self.__RemoveAttributes(report_xml)
    return report_xml

  def __RemoveAttributes(self, report_xml):
    """Removes all attributes from tags.

    Args:
      report_xml: str xml to remove attributes from.

    Returns:
      str Report xml with attributes removed.
    """
    return re.sub(ATTRIBUTES_REGEX, '', report_xml).strip()

  def __DownloadReportById(self, report_definition_id, return_micros=False,
                           fileobj=None):
    """Download report and return raw data.

    Args:
      report_definition_id: str Id of the report definition to download.
      return_micros: bool Whether to return currency in micros.
      fileobj: str Path to download file to.

    Returns:
      str Report data if no fileobj, otherwise None.
    """
    self.__ReloadAuthToken()
    url = self.__GenerateUrl(report_definition_id)
    headers = self.__GenerateHeaders(return_micros, url)
    return self.__MakeRequest(url, headers, fileobj)

  def __GenerateUrl(self, report_definition_id=None):
    """Generates the URL to get a report from.

    Args:
      report_definition_id: int ID of the report to download.

    Returns:
      str url to request
    """
    url = [DOWNLOAD_URL_BASE]
    url.append(VERSIONED % self._op_config['version'])
    if report_definition_id:
      url.append(REPORT_ID % report_definition_id)
    return ''.join(url)

  def __GenerateHeaders(self, return_micros, url):
    """Generates the headers to use for the report download.

    Args:
      return_micros: bool whether or not to use micros for money.
      url: str URL the report will be downloaded from, needed if OAuth is
           enabled.

    Returns:
      dict Dictionary containing all the headers for the request
    """
    headers = {}
    if 'clientCustomerId' in self._headers:
      headers['clientCustomerId'] = self._headers['clientCustomerId']

    # Handle OAuth (if enabled) and ClientLogin
    if self._headers.get('oauth_credentials'):
      signedrequestparams = (self._config['oauth_handler']
          .GetSignedRequestParameters(self._headers['oauth_credentials'],
                                      self._op_config['server'] + url))
      headers['Authorization'] = ('OAuth ' +
          self._config['oauth_handler']
          .FormatParametersForHeader(signedrequestparams))
    elif self._headers.get('oauth2credentials'):
      self._headers['oauth2credentials'].apply(headers)
    else:
      headers['Authorization'] = ('GoogleLogin %s' %
          urllib.urlencode({'auth':
                            self._headers['authToken'].strip()}))

    headers['returnMoneyInMicros'] = str(return_micros).lower()
    headers['developerToken'] = self._headers['developerToken']
    headers['User-Agent'] = self._headers['userAgent']
    if Utils.BoolTypeConvert(self._config['compress']):
      headers['Accept-Encoding'] = 'gzip'
      headers['User-Agent'] += ',gzip'
      headers['Content-Encoding'] = 'gzip'
    return headers

  def __MakeRequest(self, url, headers=None, fileobj=None, payload=None):
    """Performs an HTTPS request and slightly processes the response.

    If fileobj is provided, saves the body to file instead of including it
    in the return value.

    Args:
      url: str Resource for the request line.
      headers: dict Headers to send along with the request.
      fileobj: file File to save to (optional).
      payload: str Xml to POST (optional).

    Returns:
      str Report data as a string if fileobj=None, otherwise None
    """
    headers = headers or {}
    request_url = self._op_config['server'] + url

    orig_payload = payload

    if Utils.BoolTypeConvert(self._config['compress']):
      buffer = StringIO.StringIO()
      gzip_file = gzip.GzipFile(mode='wb', fileobj=buffer)
      gzip_file.write(payload)
      gzip_file.close()
      payload = buffer.getvalue()
      headers['Content-Length'] = str(len(payload))

    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    request = urllib2.Request(request_url, payload, headers)
    try:
      try:
        response = urllib2.urlopen(request)
        response_code = response.code
        response_headers = response.info().headers
        if response.info().get('Content-Encoding') == 'gzip':
          response = gzip.GzipFile(fileobj=StringIO.StringIO(response.read()),
                                   mode='rb')
        if fileobj:
          self.__DumpToFile(response, fileobj)
          return None
        else:
          return response.read()
      except urllib2.HTTPError, e:
        response = e
        response_code = response.code
        response_headers = response.info().headers
        if response.info().get('Content-Encoding') == 'gzip':
          response = gzip.GzipFile(fileobj=StringIO.StringIO(response.read()),
                                   mode='rb')
        error = response.read()
        match = re.search(OLD_ERROR_REGEX, error)
        if match:
          error = match.group(3)
        raise AdWordsError('%s %s' % (str(e), error))
    finally:
      end_time = time.strftime('%Y-%m-%d %H:%M:%S')
      xml_log_data = self.__CreateXmlLogData(start_time, end_time, request_url,
                                             headers, orig_payload,
                                             response_code, response_headers)
      self.__LogRequest(xml_log_data)

  def __ReloadAuthToken(self):
    """Ensures we have a valid auth_token in our headers."""
    # Load/set authentication token. If authentication token has expired,
    # regenerate it.
    now = time.time()
    # Do not need an AuthToken if OAuth is enabled.
    if (self._headers.get('oauth_credentials') or
        self._headers.get('oauth2credentials')): return
    if (('authToken' not in self._headers and
         'auth_token_epoch' not in self._config) or
        int(now - self._config['auth_token_epoch']) >= AUTH_TOKEN_EXPIRE):
      if ('email' not in self._headers or
          not self._headers['email'] or
          'password' not in self._headers or
          not self._headers['password']):
        msg = ('Required authentication headers, \'email\' and \'password\', '
               'are missing. Unable to regenerate authentication token.')
        raise ValidationError(msg)
      self._headers['authToken'] = Utils.GetAuthToken(
          self._headers['email'], self._headers['password'],
          AUTH_TOKEN_SERVICE, LIB_SIG, self._config['proxy'])
      self._config['auth_token_epoch'] = time.time()

  def __DumpToFile(self, response, fileobj):
    """Reads from response.read() and writes to fileobj.

     Args:
      response: file Some object that supports read().
      fileobj: file Some object that supports write()

     Returns:
      number Number of bytes written.
    """
    byteswritten = 0
    while True:
      buf = response.read(BUF_SIZE)
      if buf:
        fileobj.write(buf)
        byteswritten += len(buf)
      else:
        break
    return byteswritten

  def __LogRequest(self, xml_log_data):
    """Logs the Report Download request.

    Args:
      xml_log_data: str Data to log for this request.
    """
    log_handlers = self.__GetLogHandlers()
    for handler in log_handlers:
      handler['target'] = Logger.NONE
      if handler['tag'] == 'xml_log':
        handler['data'] += xml_log_data
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

  def __GetLogHandlers(self):
    """Gets a list of log handlers for the AdWords library.

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
            'data': ('host=%s operation=%s'
                     % (self._op_config['server'], 'ReportDownload'))
        }
    ]

  def __CreateXmlLogData(self, start_time, end_time, request_url,
                         request_headers, payload, response_code,
                         response_headers):
    """Transforms arguments into a string to log.

    Args:
      start_time: str Formatted start time.
      end_time: str Formatted end time.
      request_url: str URL POSTed to.
      request_headers: dict Request headers sent with request.
      payload: str Payload (http request body).
      response_code: int Response code from remote server.
      response_headers: list List of string headers received.

    Returns:
      str Data to log.
    """
    # Errors will have a response code, otherwise it should have been success.
    response_code = response_code or 200
    return ('StartTime: %s\n%s\n%s\n\n%s\n\n%s\n%s\nEndTime: %s'
            % (start_time, 'POST: %s' % request_url,
               self.__SerializeRequestHeaders(request_headers), payload,
               'HTTP %s' % response_code,
               self.__SerializeResponseHeaders(response_headers), end_time))

  def __SerializeRequestHeaders(self, request_headers):
    """Serializes the request headers into a string for logging.

    Returns each key->value pair as "key: value" with newlines separating them.

    Args:
      request_headers: dict Dictionary of headers to serialize.

    Returns:
      str Serialized request headers.
    """
    return '\n'.join(['%s: %s' % (key, request_headers[key])
                      for key in request_headers])

  def __SerializeResponseHeaders(self, response_headers):
    """Serializes the response headers.

    Headers are already formatted, this joins them into a single string.

    Args:
      response_headers: list List of string headers received.

    Returns:
      str Serialized response headers.
    """
    return (''.join(response_headers)).strip()
