#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Utility functions to create a fake WSDL to house an XSD."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import re
import urllib

from adspygoogle import SOAPpy
from adspygoogle.SOAPpy import wstools


WSDL_TEMPLATE = ('<?xml version="1.0" encoding="UTF-8"?>'
                 '<wsdl:definitions xmlns:tns="https://example.com/fake"'
                 ' xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"'
                 ' xmlns:wsdlsoap="http://schemas.xmlsoap.org/wsdl/soap/"'
                 ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
                 ' targetNamespace="https://example.com/fake">'
                 '<wsdl:types>%s</wsdl:types>'
                 '</wsdl:definitions>')


class FakeWsdlProxy(SOAPpy.WSDL.Proxy):

  """Class that pretends to be a SOAPpy.WSDL.Proxy for XSD defined objects."""

  def __init__(self, wsdl):
    self.wsdl = wsdl


def ElementToComplexType(xsd):
  """Replaces the first <element> tag with the complexType inside of it.

  The complexType tag will use the name attribute from the removed element tag.

  Args:
    xsd: str XSD string contents.

  Returns:
    str: Modified XSD.
  """
  xsd = re.sub(r'<(\w+:)?element name="(\w+)">\s*<(\w+:)?complexType>',
               '<\\3complexType name="\\2">',
               xsd)
  xsd = re.sub(r'(\s+)?</(\w+:)?element>', '', xsd)
  xsd = re.sub(r'<\?xml.*?>', '', xsd)
  return xsd


def CreateWsdlFromXsdUrl(xsd_url):
  """Creates a fake WSDL object we can use with our SOAPpy xml logic.

  Args:
    xsd_url: str URL the XSD can be located at.

  Returns:
    FakeWsdlProxy: A Fake WSDL proxy.
  """
  wsdl = DownloadAndWrapXsdInWsdl(xsd_url)
  reader = wstools.WSDLTools.WSDLReader()
  parsed_wsdl = reader.loadFromString(wsdl)
  return FakeWsdlProxy(parsed_wsdl)


def DownloadAndWrapXsdInWsdl(url):
  """Creates a fake WSDL text from XSD text.

  Args:
    url: str URL the XSD can be located at.

  Returns:
    str: WSDL wrapping the provided XSD.
  """
  xsd = urllib.urlopen(url).read()
  return WSDL_TEMPLATE % ElementToComplexType(xsd)
