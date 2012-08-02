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

"""Handler functions for outgoing and incoming messages."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import types

from adspygoogle import SOAPpy
from adspygoogle.common import Utils
from adspygoogle.common.soappy import SoappyUtils


def UnpackResponseAsDict(response):
  """Unpack (recursively) SOAP data holder into a Python dict object.

  Args:
    response: instance SOAP data holder object.

  Returns:
    dict Unpacked SOAP data holder.
  """
  if (isinstance(response, types.InstanceType) and
      response.__dict__['_type'] == 'struct'):
    if not response.__dict__.keys(): return (response.__dict__,)
    dct = {}
    for key in response.__dict__:
      if key[0] == '_': continue
      value = response.__dict__.get(key)
      if key.find('.') > -1: key = key.replace('.', '_')
      data = UnpackResponseAsDict(value)
      dct[str(key)] = data
    return dct
  elif (isinstance(response, list) or
        (isinstance(response, types.InstanceType) and
         isinstance(response.__dict__['_type'], tuple)) or
        isinstance(response, SOAPpy.Types.typedArrayType)):
    lst = []
    for item in response:
      if item is None: continue
      lst.append(UnpackResponseAsDict(item))
    return lst
  elif isinstance(response, tuple) and len(response) == 6:
    return '%04d-%02d-%02dT%02d:%02d:%02d' % response
  else:
    if (isinstance(response, int) or isinstance(response, long) or
        isinstance(response, float)):
      return str(response)
    return response


def WrapInTuple(response):
  """Wraps the response in a tuple to support legacy behavior.

  Dictionaries and strings are placed in a tuple, while lists are unpacked into
  the tuple. None will not be wrapped in a tuple at all.

  Args:
    response: mixed The response from the API to wrap in a tuple. Could be a
              string, list, or dictionary depending on the operation.

  Returns:
    tuple: The given response wrapped in a tuple. Will be None if the input was
           None.
  """
  if response is None: return response
  if not isinstance(response, (list, tuple)): response = [response]
  return tuple(response)


def PackForSoappy(obj, xmlns, type_name, soappy_service, wrap_lists,
                  prefix_function):
  """Packs a given object into SOAPpy.Type objects for transport.

  Args:
    obj: mixed The python object to pack for SOAPpy transport. May be a string,
         list, or dictionary depending on what it represents.
    xmlns: string The namespace that the given object's type belongs to.
    type_name: string The name of the SOAP type this object represents.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    this service/WSDL.
    wrap_lists: boolean Whether or not to wrap lists in an additional layer.
    prefix_function: callable Takes in an xml namespace and returns the prefix
                     to use to represent it.

  Returns:
    mixed The given object ready for SOAPpy transport. Depending on the input,
    this will be either a list, a SOAPpy.Types.structType, or a
    SOAPpy.Types.untypedType.
  """
  if isinstance(obj, dict):
    return _PackDictForSoappy(obj, xmlns, type_name, soappy_service, wrap_lists,
                              prefix_function)
  elif isinstance(obj, (list, tuple)):
    return _PackListForSoappy(obj, xmlns, type_name, soappy_service, wrap_lists,
                              prefix_function)
  elif isinstance(obj, str):
    return SOAPpy.Types.untypedType(Utils.HtmlEscape(obj).decode('utf-8'))
  elif isinstance(obj, unicode):
    return SOAPpy.Types.untypedType(Utils.HtmlEscape(obj))
  elif isinstance(obj, SOAPpy.Types.anyType) or obj is None:
    return obj
  else:
    return SOAPpy.Types.untypedType(obj)


def _PackDictForSoappy(obj, xmlns, type_name, soappy_service, wrap_lists,
                       prefix_function):
  """Packs a dictionary into a SOAPpy.Types.structType object for transport.

  Args:
    obj: dict The python object to pack for SOAPpy transport.
    xmlns: string The namespace that the given object's type belongs to.
    type_name: string The name of the SOAP type this object represents.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    this service/WSDL.
    wrap_lists: boolean Whether or not to wrap lists in an additional layer.
    prefix_function: callable Takes in an xml namespace and returns the prefix
                     to use to represent it.

  Returns:
    SOAPpy.Types.structType The given dictionary ready for SOAPpy transport.
  """
  packed_data = {}
  obj_contained_type, type_key = SoappyUtils.GetExplicitType(
      obj, type_name, xmlns, soappy_service)
  if obj_contained_type:
    type_name = obj_contained_type

  for key in obj:
    if key == type_key or not obj[key]:
      continue
    ns_prefix = prefix_function(SoappyUtils.GetComplexFieldNamespaceByFieldName(
        key, type_name, xmlns, soappy_service))
    key_type = SoappyUtils.GetComplexFieldTypeByFieldName(
        key, type_name, xmlns, soappy_service)
    packed_data[ns_prefix + key] = PackForSoappy(
        obj[key], key_type.getTargetNamespace(), key_type.getName(),
        soappy_service, wrap_lists, prefix_function)

  attrs = {(SOAPpy.NS.XSI3, 'type'): prefix_function(xmlns) + type_name}
  packed_object = SOAPpy.Types.structType(packed_data, typed=0, attrs=attrs)
  packed_object._typename = type_name
  packed_object._keyord = SoappyUtils.PruneKeyOrder(
      [param['name'] for param in SoappyUtils.GenKeyOrderAttrs(
          soappy_service, xmlns, type_name)], packed_object)
  return packed_object


def _PackListForSoappy(obj, xmlns, type_name, soappy_service, wrap_lists,
                       prefix_function, item_element_name='item'):
  """Packs an array input into a form ready for SOAPpy transport.

  Args:
    obj: list The python object to pack for SOAPpy transport.
    xmlns: string The namespace that the given object's type belongs to.
    type_name: string The name of the SOAP type this object represents.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    this service/WSDL.
    wrap_lists: boolean Whether or not to wrap lists in an additional layer.
    prefix_function: callable Takes in an xml namespace and returns the prefix
                     to use to represent it.
    [optional]
    item_element_name: string The XML element name to wrap items of the list in.
                       Only used if wrap_lists is set to True. Defaults to
                       'item'.

  Returns:
    mixed The given object ready for SOAPpy transport. If wrap_lists is set to
    False, this will return a list. If wrap_lists is set to True, this will
    return a SOAPpy.Types.structType.
  """
  if wrap_lists:
    new_list = SOAPpy.Types.structType(typed=0)
    for item in obj:
      item_type = SoappyUtils.GetArrayItemTypeName(type_name, xmlns,
                                                   soappy_service)
      new_list._addItem(item_element_name, PackForSoappy(
          item, xmlns, item_type, soappy_service, wrap_lists,
          prefix_function))
    return new_list
  else:
    new_list = []
    for item in obj:
      item_type = SoappyUtils.GetArrayItemTypeName(type_name, xmlns,
                                                   soappy_service)
      new_list.append(PackForSoappy(item, xmlns, item_type, soappy_service,
                                    wrap_lists, prefix_function))
    return new_list


def RestoreListTypeWithSoappy(response, service, operation_return_types):
  """Restores list types within given response which were overwritten by SOAPpy.

  Args:
    response: mixed A string, list, or dict of response data.
    service: SOAPpy.WSDL.Proxy A SOAPpy service object encapsulating the WSDL
             definitions.
    operation_return_types: list Data types this operation returns, in
                            order.

  Returns:
    String, list, or dict: The given response with nested items corrected if
    necessary. Should always be the same data type as the input response.
  """
  if not operation_return_types:
    # If the method doesn't return anything, return None. SOAPpy returns {}.
    return None
  if len(operation_return_types) > 1:
    new_response = []
    for i in len(response):
      new_response.append(RestoreListTypeWithSoappy(response[i], service,
                                                    operation_return_types[i]))
    return new_response

  return_ns, return_type_name, return_max_occurs = operation_return_types[0]

  if not return_max_occurs.isdigit() or int(return_max_occurs) > 1:
    if not response:
      return []
    elif not isinstance(response, list):
      return [_RestoreListTypesForResponse(
          response, return_type_name, return_ns, service)]
    else:
      return _RestoreListTypesForResponse(
          response, return_type_name, return_ns, service)
  else:
    return _RestoreListTypesForResponse(
        response, return_type_name, return_ns, service)


def _RestoreListTypesForResponse(response, type_name, ns, service):
  """Restores list types for an individual response object.

  Args:
    response: mixed An individual object returned by the webservice. May be a
              dictionary, list, or string depending on what it represents.
    type_name: string The type name defined in the WSDL.
    ns: string The namespace the given type belongs to.
    service: SOAPpy.WSDL.Proxy An object encapsulating a SOAP service.

  Returns:
    obj The response in its proper format. May be a dictionary, list, or string
    depending on what was input. Not guaranteed to output the same data type
    that was input - may output a list instead.
  """
  if isinstance(response, dict):
    if not response: return response
    for key in response:
      if key.endswith("_Type"): type_name = response[key]
    parameters = SoappyUtils.GenKeyOrderAttrs(service, ns, type_name)
    for param, param_type, param_max_occurs in [
        (param['name'], param['type'], param['maxOccurs'])
        for param in parameters]:
      if not param in response:
        continue
      value = response[param]
      if ((SoappyUtils.IsAnArrayType(
          param_type.getName(), param_type.getTargetNamespace(), service) or
           (not param_max_occurs.isdigit() or int(param_max_occurs) > 1)) and
          not isinstance(response[param], list)):
        value = [value]
      response[param] = _RestoreListTypesForResponse(
          value, param_type.getName(), param_type.getTargetNamespace(), service)
    return response
  elif isinstance(response, list):
    return [_RestoreListTypesForResponse(item, SoappyUtils.GetArrayItemTypeName(
        type_name, ns, service), ns, service) for item in response if item]
  else:
    return response
