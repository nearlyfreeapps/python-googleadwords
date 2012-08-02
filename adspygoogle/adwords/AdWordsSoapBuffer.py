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

from adspygoogle.common import ETREE
from adspygoogle.common import PYXML
from adspygoogle.common.SoapBuffer import SoapBuffer

class AdWordsSoapBuffer(SoapBuffer):

  """Implements a AdWordsSoapBuffer.

  Catches and parses outgoing and incoming SOAP XML messages for AdWords API
  requests.
  """

  def __init__(self, xml_parser=None, pretty_xml=False):
    """Inits AdWordsSoapBuffer.

    Args:
      xml_parser: str XML parser to use.
      pretty_xml: bool Indicator for whether to prettify XML.
    """
    super(AdWordsSoapBuffer, self).__init__(xml_parser, pretty_xml)
    self.__xml_parser = xml_parser

  def __GetXmlOut(self):
    """Remove banners from outgoing SOAP XML and contstruct XML object.

    Returns:
      Document/Element Object generated from string, representing XML message.
    """
    return super(AdWordsSoapBuffer, self)._GetXmlOut()

  def __GetXmlIn(self):
    """Remove banners from incoming SOAP XML and construct XML object.

    Returns:
      Document/Element Object generated from string, representing XML message.
    """
    return super(AdWordsSoapBuffer, self)._GetXmlIn()

  def __GetXmlValueByName(self, xml_obj, names, get_all=False):
    """Get XML object value from a given tag name.

    Args:
      xml_obj: Document/Element object.
      names: list List of tag names whose value to look up.
      get_all: bool Whether to return all values that were found or just one.

    Returns:
      str XML object value, list if more than one value is found and if
      explicitly requested, or None if name is not found in the XML object.
    """
    response = None
    for name in names:
      response = super(AdWordsSoapBuffer, self)._GetXmlValueByName(
          xml_obj, name, get_all)
      if response: break
    return response

  def GetCallResponseTime(self):
    """Get value for responseTime header.

    Returns:
      str responseTime header value.
    """
    return self.__GetXmlValueByName(self._GetXmlIn(),
        ['responseTime', 'Header/ResponseHeader/responseTime',
         'ns2:responseTime'])

  def GetCallRequestId(self):
    """Get value for requestId header.

    Returns:
      str requestId header value.
    """
    return self.__GetXmlValueByName(self._GetXmlIn(),
        ['requestId', 'Header/ResponseHeader/requestId', 'ns2:requestId'])

  def GetOperatorName(self):
    """Get name of the operator that was used in the API call.

    Returns:
      dict Dictionary consisting of the name of the operator mapped to the
           number of times that operator was used in the API request.
    """
    if self.__xml_parser == PYXML:
      values = self.__GetXmlValueByName(self.__GetXmlOut(),
                                        ['ns1:operator', 'operator'],
                                        True)
    elif self.__xml_parser == ETREE:
      values = self.__GetXmlValueByName(self.__GetXmlOut(),
                                        ['Body/mutate/operations/operator'],
                                        True)
    # If no operator found, returns None. Otherwise, the format
    # is {'ADD': 1, 'SET': 2}.
    operator = {}
    if not values or (values and self.GetCallName() == 'get'):
      operator = None
    else:
      for value in values:
        if value in operator:
          operator[str(value)] += 1
        else:
          operator[str(value)] = 1
    return operator

  def GetCallOperations(self):
    """Get value for operations header.

    Returns:
      str Operations header value.
    """
    return self.__GetXmlValueByName(self.__GetXmlIn(),
        ['operations', 'Header/ResponseHeader/operations', 'ns2:operations'])

  def GetCallUnits(self):
    """Get value for units header.

    Returns:
      str Units header value.
    """
    return self.__GetXmlValueByName(self.__GetXmlIn(),
        ['units', 'Header/ResponseHeader/units', 'ns2:units'])
