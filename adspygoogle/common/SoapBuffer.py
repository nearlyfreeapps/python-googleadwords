#!/usr/bin/python
#
# Copyright 2010 Google Inc.
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

"""Handler class for implementing a SOAP buffer."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import re
import sys

from adspygoogle.common import ETREE
from adspygoogle.common import ETREE_NAME
from adspygoogle.common import MIN_ETREE_VERSION
from adspygoogle.common import MIN_PY_VERSION
from adspygoogle.common import MIN_PYXML_VERSION
from adspygoogle.common import PYXML
from adspygoogle.common import PYXML_NAME
from adspygoogle.common import Utils
from adspygoogle.common.Buffer import Buffer
from adspygoogle.common.Errors import InvalidInputError
from adspygoogle.common.Errors import MalformedBufferError
from adspygoogle.common.Errors import MissingPackageError

# Is this running on Google's App Engine?
try:
  import google.appengine
  from _xmlplus.parsers.expat import ExpatError
except:
  from xml.parsers.expat import ExpatError

# Check if PyXML is installed.
try:
  # Is this running on Google's App Engine?
  try:
    import google.appengine
    import _xmlplus
  except:
    try:
      import _xmlplus
    except:
      import xml as _xmlplus
  from xml.dom import minidom
  # Test whether xml.version_info exists.
  version = _xmlplus.__dict__.get('version_info')
  PYXML_LIB = True
except (ImportError, AttributeError):
  # An anti-anti-hack/workaround for users of python2.5 (and up) to convince
  # Python not to ignore PyXML. We really do want to use _xmlplus here, even
  # though it is 'too old'.
  if ((list(map(eval, MIN_PY_VERSION.split('.'))) <
       list(sys.version_info)[0:3])):
    # The change to the environment variables is only active during the life of
    # a process.
    import os
    os.environ['PY_USE_XMLPLUS'] = 'YES'
    PYXML_LIB = True
  else:
    PYXML_LIB = False
else:
  if (not version or
      list(version) < (list(map(eval, MIN_PYXML_VERSION.split('.'))))):
    PYXML_LIB = False

# Check if cElementTree or ElementTree is installed ...
try:
  # ... as a third party.
  import cElementTree as etree
  ETREE_LIB = True
  ETREE_NAME = etree.__name__
  ETREE_VERSION = etree.VERSION
except (ImportError, AttributeError):
  try:
    # ... natively.
    import xml.etree.cElementTree as etree
    ETREE_LIB = True
    ETREE_NAME = etree.__name__
    ETREE_VERSION = etree.VERSION
  except (ImportError, AttributeError):
    try:
      # ... as a third party.
      import elementtree.ElementTree as etree
      ETREE_LIB = True
      ETREE_NAME = etree.__name__
      ETREE_VERSION = etree.VERSION
    except (ImportError, AttributeError):
      try:
        # ... natively.
        import xml.etree.ElementTree as etree
        ETREE_LIB = True
        ETREE_NAME = etree.__name__
        ETREE_VERSION = etree.VERSION
      except (ImportError, AttributeError):
        ETREE_LIB = False

if not PYXML_LIB and not ETREE_LIB:
  msg = ('PyXML v%s or ElementTree v%s or newer is required.'
         % (MIN_PYXML_VERSION, MIN_ETREE_VERSION))
  raise MissingPackageError(msg)


class SoapBuffer(Buffer):

  """Implements a SoapBuffer.

  Catches and parses outgoing and incoming SOAP XML messages.
  """

  def __init__(self, xml_parser=None, pretty_xml=False):
    """Inits SoapBuffer.

    Args:
      xml_parser: str XML parser to use.
      pretty_xml: bool Indicator for whether to prettify XML.
    """
    super(SoapBuffer, self).__init__()

    self._buffer = ''
    self.__dump = {}
    self.__xml_parser = xml_parser
    # Pick a default XML parser, if none was set.
    if not self.__xml_parser:
      for parser, status in [(PYXML, PYXML_LIB), (ETREE, ETREE_LIB)]:
        if status: self.__xml_parser = parser
    # Validate current state of the chosen XML parser.
    if self.__xml_parser == PYXML and not PYXML_LIB:
      msg = 'PyXML v%s or newer is required.' % MIN_PYXML_VERSION
      raise MissingPackageError(msg)
    elif self.__xml_parser == ETREE and not ETREE_LIB:
      msg = 'ElementTree v%s or newer is required.' % MIN_ETREE_VERSION
      raise MissingPackageError(msg)
    elif self.__xml_parser != PYXML and self.__xml_parser != ETREE:
      msg = ('Invalid input for XML parser, expecting one of %s.'
             % sorted(set(PYXML + ETREE)))
      raise InvalidInputError(msg)
    # Set XML parser signature.
    if self.__xml_parser == PYXML:
      self.__xml_parser_sig = '%s v%s' % (PYXML_NAME, MIN_PYXML_VERSION)
    elif self.__xml_parser == ETREE:
      self.__xml_parser_sig = '%s v%s' % (ETREE_NAME, ETREE_VERSION)
    self.__pretty_xml = pretty_xml

  def write(self, str_in):
    """Append given string to a buffer.

    Args:
      str_in: str String to append to a buffer.
    """
    super(SoapBuffer, self).write(str_in)

  def flush(self):
    super(SoapBuffer, self).flush()

  def GetBufferAsStr(self):
    """Return buffer as string.

    Returns:
      str Content of buffer.
    """
    return super(SoapBuffer, self).GetBufferAsStr()

  def IsHandshakeComplete(self):
    """Return state of the handshake.

    A successful handshake occurs when a SOAP request is sent and a SOAP
    response is recieved.

    Returns:
      bool True if successful handshake, False otherwise.
    """
    if (self.GetHeadersOut() and self.GetSoapOut() and self.GetHeadersIn() and
        self.GetSoapIn() and not Utils.IsHtml(self.GetSoapIn())):
      return True
    return False

  def __GetBufferAsDict(self):
    """Parse HTTP headers and SOAP data.

    Returns:
      dict Request's HTTP headers and SOAP data.
    """
    tags = (('Outgoing HTTP headers', 'dumpHeadersOut'),
            ('Outgoing SOAP', 'dumpSoapOut'),
            ('Incoming HTTP headers', 'dumpHeadersIn'),
            ('Incoming SOAP', 'dumpSoapIn'))
    # The HTTP and SOAP messages were delivered via SOAPpy or httplib.HTTPS.
    xml_dumps = self.GetBufferAsStr().split('*' * 72)
    for xml_part in xml_dumps:
      xml_part = xml_part.lstrip('\n').rstrip('\n')
      for name, tag in tags:
        if xml_part.find(name) > -1:
          # Insert XML parser signature into the SOAP header.
          trigger = xml_part[xml_part.lower().find('content-type'):
                             xml_part.lower().find('content-type')+12]
          if trigger and tag == 'dumpHeadersOut':
            xml_part = xml_part.replace(
                trigger,
                'XML-parser: %s\n%s' % (self.__xml_parser_sig, trigger))
          if self.__pretty_xml:
            doc = []
            banner = ''
            for line in xml_part.split('\n'):
              if line.rfind('SOAP %s' % ('*' * 46)) > -1:
                banner = line
                continue
              doc.append(line)
            if banner:
              xml_part = '%s\n%s' % (banner,
                                     self.__PrettyPrintXml('\n'.join(doc), 1))
          self.__dump[tag] = (xml_part + '\n' + '*' * 72)
          break
    return self.__dump

  def __GetDumpValue(self, dump_type):
    """Return dump value given its type.

    Args:
      dump_type: str Type of the dump.

    Returns:
      str Value of the dump.
    """
    dump_value = None
    try:
      if dump_type in self.__dump:
        dump_value = self.__dump[dump_type]
      else:
        dump_value = self.__GetBufferAsDict()[dump_type]
    except KeyError:
      dump_value = ''
    return dump_value

  def GetHeadersOut(self):
    """Return outgoing headers dump.

    Returns:
      str Outgoing headers dump.
    """
    return self.__GetDumpValue('dumpHeadersOut')

  def GetSoapOut(self):
    """Return SOAP out dump.

    Returns:
      str Outgoing SOAP dump.
    """
    dump_value = self.__GetDumpValue('dumpSoapOut')

    # Mask out sensitive data, if present.
    dump_value = dump_value.replace('><', '>\n<')
    for mask in ['password', 'Password', 'authToken', 'ns1:authToken']:
      pattern = re.compile('>.*?</%s>' % mask)
      dump_value = pattern.sub('>xxxxxx</%s>' % mask, dump_value)
    return dump_value

  def GetHeadersIn(self):
    """Return incoming headers dump.

    Returns:
      str Incoming headers dump.
    """
    return self.__GetDumpValue('dumpHeadersIn')

  def GetSoapIn(self):
    """Return incoming SOAP dump.

    Returns:
      str Incoming SOAP dump.
    """
    return self.__GetDumpValue('dumpSoapIn')

  def GetRawSoapIn(self):
    """Return raw incoming SOAP dump with out banners and not prettified.

    Returns:
      str Raw incoming SOAP dump.
    """
    doc = ''.join(self.GetSoapIn().split('\n')[1:-1])
    return self.__PrettyPrintXml(doc, -1)

  def _GetXmlOut(self):
    """Remove banners from outgoing SOAP XML and contstruct XML object.

    Returns:
      Document/Element object generated from string, representing XML message.
    """
    # Remove banners.
    xml_dump = self.GetSoapOut().lstrip('\n').rstrip('\n')
    xml_parts = xml_dump.split('\n')

    # While multiple threads are used, SoapBuffer gets too greedy and tries to
    # capture all traffic that goes to sys.stdout. The parts that we don't need
    # should be redirected back to sys.stdout.
    banner = '%s Outgoing SOAP %s' % ('*' * 3, '*' * 54)
    begin = 1
    for index in range(len(xml_parts)):
      if xml_parts[index] == banner:
        begin = index + 1
        break
    non_xml = '\n'.join(xml_parts[:begin-1])
    # Send data we don't need back to sys.stdout.
    if non_xml: print non_xml

    xml_dump = '\n'.join(xml_parts[begin:len(xml_parts)-1])

    try:
      if self.__xml_parser == PYXML:
        xml_obj = minidom.parseString(xml_dump)
      elif self.__xml_parser == ETREE:
        xml_obj = etree.fromstring(xml_dump)
    except (ExpatError, SyntaxError), e:
      msg = 'Unable to parse SOAP buffer for outgoing messages. %s' % e
      raise MalformedBufferError(msg)
    return xml_obj

  def _GetXmlIn(self):
    """Remove banners from incoming SOAP XML and construct XML object.

    Returns:
      Document/Element object generated from string, representing XML message.
    """
    # Remove banners.
    xml_dump = self.GetSoapIn().lstrip('\n').rstrip('\n')
    xml_parts = xml_dump.split('\n')
    xml_dump = '\n'.join(xml_parts[1:len(xml_parts)-1])

    try:
      if self.__xml_parser == PYXML:
        xml_obj = minidom.parseString(xml_dump)
      elif self.__xml_parser == ETREE:
        xml_obj = etree.fromstring(xml_dump)
    except (ExpatError, SyntaxError), e:
      msg = 'Unable to parse SOAP buffer for incoming messages. %s' % e
      raise MalformedBufferError(msg)
    return xml_obj

  def __RemoveElemAttr(self, elem):
    """Remove element's attribute, if any.

    Args:
      elem: str XML element with or without an attribute.

    Returns:
      str XML element without attribute.
    """
    pattern = re.compile('({.*?})')
    return re.sub(pattern, '', elem)

  def __GetXmlNameByName(self, xml_obj, name):
    """Get XML object name from a given tag name.

    Args:
      xml_obj: Document/Element object.
      name: str Tag name to look up.

    Returns:
      str XML object name, or None if tag name is not found in the XML object.
    """
    value = None
    if self.__xml_parser == PYXML:
      for node in xml_obj.getElementsByTagName(name):
        if len(node.childNodes) == 1:
          value = node.childNodes[0].nodeName
        else:
          value = node.childNodes[1].nodeName
    elif self.__xml_parser == ETREE:
      root = xml_obj
      etags = etags = name.split('/')
      for etag in etags:
        for item in root.getchildren():
          if item.tag.find(etag) > -1 or etag == '*':
            root = item
            if etag == etags[-1]:
              value = self.__RemoveElemAttr(root.tag)
    return value

  def _GetXmlValueByName(self, xml_obj, name, get_all=False):
    """Get XML object value from a given tag name.

    Args:
      xml_obj: Document/Element object.
      name: str Tag name whose value to look up.
      get_all: bool Whether to return all values that were found or just one.

    Returns:
      str XML object value, list if more than one value is found and if
      explicitly requested, or None if name is not found in the XML object.
    """
    values = []
    if self.__xml_parser == PYXML:
      for node in xml_obj.getElementsByTagName(name):
        if node.childNodes: values.append(node.childNodes[0].nodeValue)
    elif self.__xml_parser == ETREE:
      root = xml_obj
      etags = name.split('/')
      for etag in etags:
        for item in root.getchildren():
          if item.tag.find(etag) > -1:
            root = item
            if etag == etags[-1]:
              values.append(root.text)
    if get_all and values:
      return values
    elif values:
      return values[0]
    return None

  def IsSoap(self):
    """Whether buffer contains SOAP message(s) or not.

    Returns:
      bool True if message is a SOAP, False otherwise.
    """
    data = self.GetBufferAsStr()
    if not data:
      return False
    try:
      if self.__xml_parser == PYXML:
        if (self.GetCallResponseTime() is None and
            not self._GetXmlIn().getElementsByTagName('soapenv:Body') and
            not self._GetXmlIn().getElementsByTagName('soap:Body')):
          return False
      elif self.__xml_parser == ETREE:
        if self.__GetXmlNameByName(self._GetXmlIn(), 'Body') is None:
          return False
    except Exception:
      # Data contains malformed XML message.
      return False
    return True

  def GetServiceName(self):
    """Get name of the API service that was called.

    Note: the way service is determined depends on the particular order of
    elements in the caller stack. For example:

    XxxService.Get() ->
      WebService.__ManageSoap() ->
        SoapBuffer.GetServiceName()

    Returns:
      str Name of the API service that was called.
    """
    return sys._getframe(3).f_locals['self'].__class__.__name__

  def GetCallName(self):
    """Get name of the API method that was called.

    Returns:
      str Name of the API method that was called.
    """
    if self.__xml_parser == PYXML:
      # Remove "nsX:" if exists.
      pattern = re.compile('ns.*?:')
      value = pattern.sub('', self.__GetXmlNameByName(self._GetXmlOut(),
                                                      'SOAP-ENV:Body'))
    elif self.__xml_parser == ETREE:
      value = self.__GetXmlNameByName(self._GetXmlOut(), 'Body/*')
    return value

  def GetFaultAsDictWhenOtherFails(self):
    ''' Since this is an ETREE, we have to parse through the whole thing '''
    xml_obj = xml_obj = self._GetXmlIn()
    fault_node = xml_obj.getchildren()[-1].getchildren()[0]

    fault_code_elem = None
    fault_string_elem = None
    detail_elem = None
    fault_code = ''
    fault_string = ''

    for child in fault_node.getchildren():
      if child.tag == 'faultcode':
        fault_code_elem = child
      elif child.tag == 'faultstring':
        fault_string_elem = child
      elif child.tag == 'detail':
        detail_elem = child

    detail = {'errors': []}

    if fault_code_elem is not None:
      fault_code = fault_code_elem.text
    if fault_string_elem is not None:
      fault_string = fault_string_elem.text
    if detail_elem is not None:
      detail_elem = detail_elem.getchildren()[0]
      for child in detail_elem.getchildren():
        if child.tag.endswith('message'):
          detail['message'] = child.text
        elif child.tag.endswith('errors'):
          error_dict = dict()
          for c in child.getchildren():
            if c.tag.endswith('ApiError.Type'):
              error_dict['type'] = c.text
            elif c.tag.endswith('fieldPath'):
              error_dict['fieldPath'] = c.text
            elif c.tag.endswith('reason'):
              error_dict['reason'] = c.text
            elif c.tag.endswith('trigger'):
              error_dict['trigger']  = c.text
            elif c.tag.endswith('limit'):
              error_dict['limit']  = c.text
            elif c.tag.endswith('isExemptable'):
              error_dict['isExemptable']  = c.text
            elif c.tag.endswith('externalPolicyName'):
              error_dict['externalPolicyName']  = c.text
            elif c.tag.endswith('externalPolicyDescription'):
              error_dict['externalPolicyDescription']  = c.text
            elif c.tag.endswith('externalPolicyUrl'):
              error_dict['externalPolicyUrl']  = c.text
            elif c.tag.endswith('violatingParts'):
              vp_dict = dict()
              for c2 in c.getchildren():
                if c2.tag.endswith('ApiError.Type'):
                  vp_dict['type'] = c2.text
                elif c2.tag.endswith('index'):
                  vp_dict['index'] = c2.text
                elif c2.tag.endswith('length'):
                  vp_dict['length'] = c2.text
              error_dict['violatingParts']  = vp_dict
            elif c.tag.endswith('key'):
              key_dict = dict()
              for c2 in c.getchildren():
                if c2.tag.endswith('ApiError.Type'):
                  key_dict['type'] = c2.text
                elif c2.tag.endswith('policyName'):
                  key_dict['policyName'] = c2.text
                elif c2.tag.endswith('violatingText'):
                  key_dict['violatingText'] = c2.text
              error_dict['key'] = key_dict
          detail['errors'].append(error_dict)

    return {'faultcode': fault_code, 'faultstring': fault_string,
            'detail': detail}

  def GetFaultAsDict(self, obj=None):
    """Recursively parse SOAP fault and load all elements into a dictionary.

    Args:
      [optional]
      obj: instance SOAP fault object holder.

    Returns:
      dict Dictionary object with all fault elements.
    """
    if not obj:
      elems = ['soapenv:Fault', 'soap:Fault']
      for elem in elems:
        xml_obj = self._GetXmlIn()
        if self.__xml_parser == PYXML:
          try:
            obj = xml_obj.getElementsByTagName(elem)[0]
          except:
            envelope = xml_obj.childNodes[0]
            body = None
            for element in envelope.childNodes:
              if element.nodeName.lower().find('body') > -1:
                body = element.childNodes[0]
                if len(element.childNodes) > 1: body = element.childNodes[1]
            obj = body
        elif self.__xml_parser == ETREE:
          obj = xml_obj.getchildren()[len(
              xml_obj.getchildren())-1].getchildren()[0]

    dct = {}
    nodes = {PYXML: ['childNodes', 'localName', 'childNodes[0].nodeValue'],
             ETREE: ['getchildren()', 'tag', 'text']}
    # Step through the Document or Element (depending on which XML parser is
    # used) and construct a dictionary representation of the fault.
    for item in eval('obj.%s' % nodes[self.__xml_parser][0]):
      if ((self.__xml_parser == PYXML and item.hasChildNodes()) or
          self.__xml_parser == ETREE):
        tag = self.__RemoveElemAttr(eval('item.%s'
                                         % nodes[self.__xml_parser][1]))
        # Rename type elements that have a dot in them: ApiError.Type => type.
        if tag.find('.') > -1: tag = tag.split('.')[1].lower()
        value = eval('item.%s' % nodes[self.__xml_parser][2])
        if value is not None:
          if not value.rstrip():
            tmp_dct = self.GetFaultAsDict(item)
            if tag in dct:
              if isinstance(dct[tag], list):
                tmp_dct = [elem for elem in dct[tag] + [tmp_dct]]
              else:
                tmp_dct = [dct[tag], tmp_dct]
            if tag == 'ApiExceptionFault' or tag == 'fault': return tmp_dct
            if tag == 'errors' and isinstance(tmp_dct, dict):
              tmp_dct = [tmp_dct]
            dct[tag] = tmp_dct
          else:
            dct[tag] = value.rstrip()
        else:
          dct[tag] = value
    return dct

  def GetFaultAsStr(self, dct={}):
    """Format SOAP fault to make it human readable.

    Returns:
      str String with all fault elements.
    """
    if not dct:
      try:
        dct = self.GetFaultAsDict()
      except Exception:
        return ''

    items = []
    for key in dct:
      if isinstance(dct[key], list):
        for item in dct[key]:
          items.append('\n\n%s\n' % key)
          items.append(self.GetFaultAsStr(item))
      elif isinstance(dct[key], dict):
        items.append('\n%s: {\n%s\n}' % (key, self.GetFaultAsStr(dct[key])))
      else:
        items.append('\n%s: %s' % (key, dct[key]))
    return ''.join(items).strip()

  def InjectXml(self, xml_in):
    """Hook into the SoapBuffer to test local SOAP XML.

    Prepares dump dict with a given input.

    Args:
      xml_in: str SOAP XML request, response, or both.
    """
    # Prepare string for use with regular expression.
    xml_in = xml_in.replace('\n', '%newline%')

    try:
      pattern = re.compile('(<SOAP-ENV:Envelope:Envelope.*</SOAP-ENV:Envelope>|'
                           '<ns0:Envelope.*RequestHeader.*?</.*?:Envelope>)')
      req = pattern.findall(xml_in)
      pattern = re.compile('(<soap.*?:Envelope.*</soap.*?:Envelope>|'
                           '<ns0:Envelope.*ResponseHeader.*?</.*?:Envelope>)')
      res = pattern.findall(xml_in)

      # Do we have a SOAP XML request?
      if req:
        # Rebuild original formatting of the string and dump it.
        req = req[0].replace('%newline%', '\n')
        self.__dump['dumpSoapOut'] = (
            '%s Outgoing SOAP %s\n'
            '<?xml version="1.0" encoding="UTF-8"?>\n%s\n'
            '%s' % ('*' * 3, '*' * 54, req, '*' * 72))

      # Do we have a SOAP XML response?
      if res:
        # Rebuild original formatting of the string and dump it.
        res = res[0].replace('%newline%', '\n')
        self.__dump['dumpSoapIn'] = (
            '%s Incoming SOAP %s\n'
            '<?xml version="1.0" encoding="UTF-8"?>\n%s\n'
            '%s' % ('*' * 3, '*' * 54, res.lstrip('\n'), '*' * 72))
    except Exception:
      msg = 'Invalid input, expecting SOAP XML request, response, or both.'
      raise InvalidInputError(msg)

  def __Indent(self, elem, level=0):
    """Add whitespace to the tree, to get its pretty-printed version.

    See, http://effbot.org/zone/element-lib.htm#prettyprint.
    """
    i = "\n" + level*" "
    if len(elem):
      if not elem.text or not elem.text.strip():
        elem.text = i + " "
      if not elem.tail or not elem.tail.strip():
        elem.tail = i
      for elem in elem:
        self.__Indent(elem, level+1)
      if not elem.tail or not elem.tail.strip():
        elem.tail = i
    else:
      if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

  def __PrettyPrintXml(self, doc, level=0):
    """Return a pretty-printed version of the XML document.

    Args:
      doc: str XML document.
      level: int Level of prettiness, defaults to 0. If -1, remove prettiness.

    Returns:
      str Pretty-printed version of the XML document.
    """
    # Make sure we have a valid doc to work with.
    if Utils.IsHtml(doc):
      return doc

    try:
      if self.__xml_parser == PYXML:
        dom = minidom.parseString(doc)
        pretty_doc = dom.toprettyxml(indent=' ', encoding='UTF-8')
      elif self.__xml_parser == ETREE:
        tree = etree.fromstring(doc)
        self.__Indent(tree)
        pretty_doc = etree.tostring(tree, 'UTF-8')
    except (ExpatError, SyntaxError):
      # If there was a problem with loading XML message into a DOM, return
      # original XML message.
      return doc

    # Adjust prettiness of data values in the XML document.
    #
    # Before:  <operations>
    #            0
    #          </operations>
    #
    # After:   <operations>0</operations>
    pattern = re.compile('\n\s+\n')
    pretty_doc = pattern.sub('\n', pretty_doc)
    groups = re.findall('>(\n\s+(.*?)\n\s+)</', pretty_doc, re.M)
    for old, new in groups:
      if old and new and (new.find('<') > -1 or new.find('>') > -1):
        continue
      pretty_doc = pretty_doc.replace(old, new)

    if level == -1:
      pattern = re.compile('>\s+<')
      pretty_doc = pattern.sub('><', pretty_doc)
    return pretty_doc.strip('\n')
