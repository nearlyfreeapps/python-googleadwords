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

"""Handy utility functions."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import codecs
import csv
import datetime
import htmlentitydefs
import re
import sys
import traceback
import urllib
from urlparse import urlparse
from urlparse import urlunparse

from adspygoogle.common.AuthToken import AuthToken
from adspygoogle.common.Buffer import Buffer
from adspygoogle.common.Errors import Error


_BASE_SOAP_TYPES = ['long', 'string', 'dateTime', 'float', 'int', 'boolean',
                    'base64Binary', 'double']


def ReadFile(f_path):
  """Load data from a given file.

  Args:
    f_path: str Absolute path to the file to read.

  Returns:
    str Data loaded from the file, None otherwise.
  """
  data = ''

  if f_path:
    fh = open(f_path, 'r')
    try:
      data = fh.read()
    finally:
      fh.close()
  return data


def GetDataFromCsvFile(loc):
  """Get data from CSV file, given its location.

  Args:
    loc: str Location of the CSV data file.

  Returns:
    list Data from CSV file.
  """
  rows = []
  try:
    data = urllib.urlopen(loc).read()
  except IOError, e:
    if str(e).find('[Errno url error] unknown url type: \'') > -1:
      data = ReadFile(loc)
    else:
      raise e
  for row in csv.reader(data.split('\n')):
    if row:
      rows.append(row)
  return rows[1:]


def GetDictFromCsvFile(loc):
  """Get data from CSV file as a dictionary, given its location.

  For each row, the first value will be used as a key mapped to the second value
  in the row.

  Args:
    loc: str Location of the CSV data file.

  Returns:
    dict Data from CSV file.
  """
  rows = {}
  try:
    data = urllib.urlopen(loc).read()
  except IOError, e:
    if str(e).find('[Errno url error] unknown url type: \'c\'') > -1:
      loc = 'file:///%s' % loc.replace('\\', '/').replace(':', '|')
      data = urllib.urlopen(loc).read()
    else:
      raise e
  for row in csv.reader(data.split('\n')):
    if row: rows[row[0]] = row[1]
  return rows


def PurgeLog(log):
  """Clear content of a given log file.

  If the file cannot be opened, Error is raised.

  Args:
    log: str Absolute path to a log file.
  """
  try:
    fh = open(log, 'w')
    try:
      fh.write('')
    finally:
      fh.close()
  except IOError, e:
    raise Error(e)


def GetErrorFromHtml(data):
  """Return error message from HTML page.

  Args:
    data: str HTML data.

  Returns:
    str Error message.
  """
  pattern = re.compile('\n')
  data = pattern.sub('', data)
  # Fetch error message.
  pattern = re.compile('<title>(.*)</title>|<TITLE>(.*)</TITLE>')
  msg = pattern.findall(data)
  if msg:
    for item in msg[0]:
      if item:
        msg = item
        # Cut unnecessary wording.
        pattern = re.compile('Error: |ERROR: ')
        msg = pattern.sub('', msg, count=1)
  else:
    pattern = re.compile('<body>(.*)</body>')
    msg = pattern.findall(data)
    if msg: msg = msg[0].rstrip('.')
  # Fetch detail for the error message
  pattern = re.compile(('<blockquote><H1>.*</H1>(.*)<p></blockquote>|'
                        '<H1>.*</H1>(.*)</BODY>'))
  msg_detail = pattern.findall(data)
  if isinstance(msg_detail, list) and msg_detail:
    for item in msg_detail[0]:
      if item: msg_detail = item
    msg_detail = msg_detail.strip('.')
    # Cut any HTML tags that appear in the message.
    pattern = re.compile('<.?H2>|<.?p>|<.?A.*>|<.?P.*>|<.?HR.*>')
    msg_detail = pattern.sub(' ', msg_detail).strip(' ')
    if msg_detail == msg: msg_detail = ''
  else:
    msg_detail = ''

  if msg:
    if not msg_detail: return '%s.' % msg
    return '%s. %s.' % (msg, msg_detail)
  else:
    # Check for non standard HTML content, with just the <body>.
    pattern = re.compile('<body>(.*)</body>')
    msg = pattern.findall(data)
    if msg: return msg[0]
  return ''


def IsHtml(data):
  """Return True if data is HTML, False otherwise.

  Args:
    data: str Data to check.

  Returns:
    bool True if data is HTML, False otherwise.
  """
  # Remove banners and XML header. Convert to lower case for easy search.
  data = ''.join(data.split('\n')).lower()
  pattern = re.compile('<html>.*?<body.*?>.*?</body>.*?</html>')
  if pattern.findall(data):
    return True
  else:
    return False


def DecodeNonASCIIText(text, encoding='utf-8'):
  """Decode a non-ASCII text into a unicode, using given encoding.

  A full list of supported encodings is available at
  http://docs.python.org/lib/standard-encodings.html. If unable to find given
  encoding, Error is raised.

  Args:
    text: str Text to encode.
    [optional]
    encoding: str Encoding format to use.

  Returns:
    tuple Decoded text with the text length, (text, len(text)).
  """
  if isinstance(text, unicode): return (text, len(text))

  dec_text = ''
  try:
    decoder = codecs.getdecoder(encoding)
    dec_text = decoder(text)
  except LookupError, e:
    msg = 'Unable to find \'%s\' encoding. %s.' % (encoding, e)
    raise Error(msg)
  except Exception, e:
    raise Error(e)
  return dec_text


def MakeTextXMLReady(text):
  """Convert given text into an XML ready text.

  XML ready text with all non-ASCII characters properly decoded.

  Args:
    text: str Text to convert.

  Returns:
    str Converted text.
  """
  dec_text = DecodeNonASCIIText(text)[0]
  items = []
  for char in dec_text:
    try:
      char = char.encode('ascii')
    except UnicodeEncodeError:
      # We have a non-ASCII character of type unicode. Convert it into an
      # XML-ready format.
      try:
        str(char)
        char.encode('utf-8')
      except UnicodeEncodeError:
        char = '%s;' % hex(ord(char)).replace('0x', '&#x')
    items.append(char)
  return ''.join(items)


def __ParseUrl(url):
  """Parse URL into components.

  Args:
    url: str URL to parse.

  Returns:
    tuple The components of the given URL.
  """
  return urlparse(url)


def GetSchemeFromUrl(url):
  """Return scheme portion of the URL.

  Args:
    url: str URL to parse.

  Returns:
    str The scheme portion of the URL.
  """
  return __ParseUrl(url)[0]


def GetNetLocFromUrl(url):
  """Return netloc portion of the URL.

  Args:
    url: str URL to parse.

  Returns:
    str Netloc portion of the URL.
  """
  return __ParseUrl(url)[1]


def GetPathFromUrl(url):
  """Return path portion of the URL.

  Args:
    url: str URL to parse.

  Returns:
    str Path portion of the URL.
  """
  return __ParseUrl(url)[2]


def GetServerFromUrl(url):
  """Return reconstructed scheme and netloc portion of the URL.

  Args:
    url: str URL to parse.

  Returns:
    str Scheme and netloc portion of given URL.
  """
  return urlunparse((GetSchemeFromUrl(url), GetNetLocFromUrl(url), '', '', '',
                     ''))


def GetAuthToken(email, password, service, lib_sig, proxy, login_token=None,
                 login_captcha=None):
  """Return an authentication token for Google Account.

  If an error occurs, AuthTokenError is raised.

  Args:
    email: str Google Account's login email.
    password: str Google Account's password.
    service: str Name of the Google service for which to authorize access.
    lib_sig: str Signature of the client library.
    proxy: str HTTP proxy to use.

  Returns:
    str Authentication token for Google Account.
  """
  return AuthToken(email, password, service, lib_sig, proxy, login_token,
                   login_captcha).GetAuthToken()


def GetCurrentFuncName():
  """Return current function/method name.

  Returns:
    str Current function/method name.
  """
  return sys._getframe(1).f_code.co_name


def UnLoadDictKeys(dct, keys_lst):
  """Return newly built dictionary with out the keys in keys_lst.

  Args:
    dct: dict Dictionary to unload keys from.
    keys_lst: list List of keys to unload from a dictionary.

  Returns:
    dict New dictionary with out given keys.
  """
  from adspygoogle.common import SanityCheck

  if not keys_lst: return dct
  SanityCheck.ValidateTypes(((dct, dict), (keys_lst, list)))

  new_dct = {}
  for key in dct:
    if key in keys_lst:
      continue
    new_dct[key] = dct[key]
  return new_dct


def CleanUpDict(dct):
  """Return newly built dictionary with out the keys that point to no values.

  Args:
    dct: dict Dictionary to clean up.

  Returns:
    dict New dictionary with out empty keys.
  """
  from adspygoogle.common import SanityCheck

  SanityCheck.ValidateTypes(((dct, dict),))

  new_dct = {}
  for key in dct:
    if dct[key]:
      new_dct[key] = dct[key]
  return new_dct


def BoolTypeConvert(bool_type, target=bool):
  """Convert bool to local bool and vice versa.

  Args:
    bool_type: bool or str a type to convert (i.e. True<=>'y', False<=>'n',
               'true'=>True, 'false'=>False).
    target: type (i.e. str or bool) for the return value, defaults to bool

  Returns:
    target boolean converted type.

  Raises:
    LookupError: Thrown when string value doesn't match one of: 1 y yes t true 0
                 n no f false
  """
  if isinstance(bool_type, target):
    return bool_type
  elif isinstance(bool_type, bool) and target == str:
    if bool_type:
      return 'y'
    else:
      return 'n'
  elif isinstance(bool_type, str):
    if bool_type.lower() in '1 y yes t true'.split():
      return target(True)
    elif bool_type.lower() in '0 n no f false'.split():
      return target(False)
    else:
      raise LookupError('unrecognized string boolean')
  else:
    return target(bool_type)


def LastStackTrace():
  """Fetch last stack traceback.

  Returns:
    str Last stack traceback.
  """
  # Temporarily redirect traceback from STDOUT into a buffer.
  trace_buf = Buffer()
  old_stdout = sys.stdout
  sys.stdout = trace_buf

  try:
    traceback.print_exc(file=sys.stdout)
  except AttributeError:
    # No exception for traceback exist.
    print ''

  # Restore STDOUT.
  sys.stdout = old_stdout
  return trace_buf.GetBufferAsStr().strip()


def HtmlUnescape(text):
  """Removes HTML or XML character references and entities from a text string.

  See http://effbot.org/zone/re-sub.htm#unescape-html.

  Args:
    text: str HTML (or XML) source text.

  Returns:
    str/unicode Plain text, as a Unicode string, if necessary.
  """

  def FixUp(m):
    """Helper function for HTML Unescaping."""
    text = m.group(0)
    if text[:2] == '&#':
        # character reference
      try:
        if text[:3] == '&#x':
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    return text  # leave as is
  return re.sub('&#?\w+;', FixUp, text)


def HtmlEscape(text):
  """Escapes characters in a given text string.

  See http://wiki.python.org/moin/EscapingHtml.

  Args:
    text: str Text to HTML escape.

  Returns:
    str HTML escaped string.
  """
  html_escape_table = {
      '&': '&amp;',
      '"': '&quot;',
      '\'': '&apos;',
      '>': '&gt;',
      '<': '&lt;'
  }
  return ''.join(html_escape_table.get(char, char) for char in text)


def CsvEscape(text):
  """Escapes data entry for consistency with CSV format.

  The CSV format rules:
    - Fields with embedded commas must be enclosed within double-quote
      characters.
    - Fields with embedded double-quote characters must be enclosed within
      double-quote characters, and each of the embedded double-quote characters
      must be represented by a pair of double-quote characters.
    - Fields with embedded line breaks must be enclosed within double-quote
      characters.
    - Fields with leading or trailing spaces must be enclosed within
      double-quote characters.

  Args:
    text: str Data entry.

  Returns:
    str CSV encoded data entry.
  """
  if not text: return ''
  if text.find('"') > -1: text = text.replace('"', '""')
  if (not text or text.find(',') > -1 or text.find('"') > -1 or
      text.find('\n') > -1 or text.find('\r') > -1 or text[0] == ' ' or
      text[-1] == ' '):
    text = '"%s"' % text
  return text


def GetUniqueName(max_len=None):
  """Returns a unique value consisting of parts from datetime.datetime.now().

  Args:
    max_len: int Maximum length for the unique name.

  Returns:
    str Unique name.
  """
  dt = datetime.datetime.now()
  name = '%s%s%s%s%s%s%s' % (dt.microsecond, dt.second, dt.minute, dt.hour,
                             dt.day, dt.month, dt.year)
  if max_len > len(name): max_len = len(name)
  return name[:max_len]


def GetDictFromMap(entries):
  """Gets a dictionary from an array of map entries.

  A map entry is any object that has a key and value fields.

  Args:
    entries: list List of map entries.

  Returns:
    dict Dictionary constructed from map entries.
  """
  dct = {}
  for entry in entries:
    dct[entry['key']] = entry['value']
  return dct


def IsBaseSoapType(xsi_type):
  """Checks to see if a type is in the xsd or soapenc namespaces.

  This function is based on the fact that the WSDL-parsing scripts remove all
  namespaces except xsd and soapenc.

  Args:
    xsi_type: str The xsi type of an object from a WSDL.

  Returns:
    bool Whether or not the given type is in the xsd or soapenc namespaces.
  """
  return xsi_type in _BASE_SOAP_TYPES
