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

"""Utility functions for interacting with SOAPpy type objects."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'


def GetArrayItemTypeName(type_name, ns, soappy_service):
  """Returns the name of the SOAP type which the items in an array represent.

  Python arrays can represent two distinct kinds of SOAP objects: SOAP encoded
  arrays or complex type elements with a maxOccurs field greater than 1. In the
  first case, the type_name given represents the SOAP encoded array type and the
  type returned will be the content's type. In the second case, or any case
  where the type_name given is not a SOAP encoded array, the type_name given is
  the one that will be returned.

  Args:
    type_name: string The name of the WSDL-defined type of the array.
    ns: string The namespace this WSDL-defined type belongs to.
    soappy_service: SOAPpy.WSDL.proxy The SOAPpy service object which contains
                    the WSDL definitions.

  Returns:
    string The type name of the array's contents.
  """
  try:
    array_type = GetTypeFromSoappyService(type_name, ns, soappy_service)
    attr_contents = array_type.content.derivation.attr_content
    if attr_contents:
      raw_type_name = attr_contents[0].attributes[
          'http://schemas.xmlsoap.org/wsdl/']['arrayType']
      return raw_type_name[raw_type_name.find(':') + 1:-2]
    else:
      return type_name
  except KeyError:
    return type_name
  except AttributeError:
    return type_name


def IsASuperType(soappy_service, sub_type, ns, super_type):
  """Determines if one type is a supertype of another type.

  Any case where the sub_type cannot be traced through to super_type is
  considered to be false.

  Args:
    soappy_service: SOAPpy.WSDL.proxy The SOAPpy service object which contains
                    the WSDL definitions.
    sub_type: A string representing a type that may be extending super_type.
    ns: A string representing the namespace sub_type belongs to.
    super_type: A string representing a type that may be extended by sub_type.

  Returns:
    bool Whether super_type is really a supertype of sub_type.
  """
  if sub_type == super_type: return True

  try:
    if IsASubType(sub_type, ns, soappy_service):
      complex_type = GetTypeFromSoappyService(sub_type, ns, soappy_service)
      return IsASuperType(
          soappy_service,
          complex_type.content.derivation.attributes['base'].getName(), ns,
          super_type)
    else:
      return False
  except KeyError:
    # The given sub_type does not exist in the WSDL definitions.
    return False


def IsASubType(type_name, ns, soappy_service):
  """Determines if a WSDL-defined type is extending another WSDL-defined type.

  Args:
    type_name: string The name of the WSDL-defined type.
    ns: string The namespace this WSDL-defined type belongs to.
    soappy_service: SOAPpy.WSDL.proxy The SOAPpy service object which contains
                    the WSDL definitions.

  Returns:
    boolean Whether the given type is extending another type.
  """
  return hasattr(GetTypeFromSoappyService(
      type_name, ns, soappy_service).content, 'derivation')


def IsAnArrayType(type_name, ns, soappy_service):
  """Determines if a complex type represents a SOAP-encoded array.

  Args:
    type_name: string The name of the WSDL-defined type.
    ns: string The namespace this WSDL-defined type belongs to.
    soappy_service: SOAPpy.WSDL.proxy The SOAPpy service object which contains
                    the WSDL definitions.

  Returns:
    boolean Whether the given type represents an array.
  """
  if type_name == 'Array':
    return True
  try:
    wsdl_type_def = GetTypeFromSoappyService(type_name, ns, soappy_service)
    if hasattr(wsdl_type_def.content, 'derivation'):
      # This is an extension of another type.
      return IsAnArrayType(
          wsdl_type_def.content.derivation.attributes['base'].getName(),
          wsdl_type_def.content.derivation.attributes[
              'base'].getTargetNamespace(), soappy_service)
    else:
      return False
  except KeyError:
    return False


def GetTypeFromSoappyService(type_name, ns, soappy_service):
  """Digs in a SOAPpy service proxy and returns the object representing a type.

  Args:
    type_name: string The name of the WSDL-defined type to search for.
    ns: string The namespace the given WSDL-defined type belongs to.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    the information stored in the WSDL.

  Returns:
    mixed The object created by SOAPpy representing the given type. May be
    either a SOAPpy.wstools.XMLSchema.SimpleType or
    SOAPpy.wstools.XMLSchema.ComplexType object.
  """
  return soappy_service.wsdl.types[ns].types[type_name]


def GenKeyOrderAttrs(soappy_service, ns, type_name):
  """Generates the order and attributes of keys in a complex type.

  Args:
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    the information stored in the WSDL.
    ns: string The namespace the given WSDL-defined type belongs to.
    type_name: string The name of the WSDL-defined type to search for.

  Returns:
    list A list of dictionaries containing the attributes of keys within a
    complex type, in order.
  """
  complex_type = soappy_service.wsdl.types[ns].types[type_name]

  if IsASubType(type_name, ns, soappy_service):
    # This is an extension of another type.
    key_order = GenKeyOrderAttrs(
        soappy_service,
        complex_type.content.derivation.attributes['base'].getTargetNamespace(),
        complex_type.content.derivation.attributes['base'].getName())
    if hasattr(complex_type.content.derivation.content, 'content'):
      key_order.extend([element.attributes for element in
                        complex_type.content.derivation.content.content])
    return key_order
  else:
    # This is a base type.
    return [element.attributes for element in complex_type.content.content]


def PruneKeyOrder(key_order, soappy_struct_object):
  """Creates a new key order of only keys that the complex type used.

  Args:
    key_order: list A list of the keys these complex type contains, in order.
              These keys are not namespaced, whereas the ones in the given
              object may be.
    soappy_struct_object: SOAPpy.Types.structType The complex type packed into a
                          SOAPpy object. Already has within it all of the keys
                          it is going to use.

  Returns:
    list A new key order containing only the keys used in the given object.
    These keys may be namespaced; they appear as they are in the given object.
  """
  new_key_order = []
  key_to_namespaced_key = {}
  for namespaced_key in soappy_struct_object._data.keys():
    if ':' in namespaced_key:
      key_to_namespaced_key[namespaced_key[
          namespaced_key.find(':') + 1:]] = namespaced_key
    else:
      key_to_namespaced_key[namespaced_key] = namespaced_key
  for namespaced_attribute in dir(soappy_struct_object):
    if ':' in namespaced_attribute:
      key_to_namespaced_key[namespaced_attribute[
          namespaced_attribute.find(':') + 1:]] = namespaced_attribute
    else:
      key_to_namespaced_key[namespaced_attribute] = namespaced_attribute

  for key in key_order:
    if key in key_to_namespaced_key:
      new_key_order.append(key_to_namespaced_key[key])
  return new_key_order


def GetComplexFieldTypeByFieldName(key, type_name, ns, soappy_service):
  """Returns the type of a field within a complex type by its key name.

  Args:
    key: string The name of the field within the given complex type whose type
         is being looked up.
    type_name: string The name of the encapsulating complex type.
    ns: string The namespace the encapsulating compelx type belongs to.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object containing the
                    descriptions of these types.

  Returns:
    TypeDescriptionComponent The type of object stored in the field with the
    given name.

  Raises:
    TypeError: if the given key is not within the given complex type.
  """
  for param in GenKeyOrderAttrs(soappy_service, ns, type_name):
    if param['name'] == key:
      return param['type']
  raise TypeError('There is no field with the name %s in complex type %s.'
                  % (key, type_name))


def GetComplexFieldNamespaceByFieldName(field, type_name, ns, soappy_service):
  """Returns the namespace of the type which defines a field in a hierarchy.

  Args:
    field: string The name of the field within the given complex type whose
           namespace is being looked up.
    type_name: string The name of the encapsulating complex type.
    ns: string The namespace the encapsulating compelx type belongs to.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object containing the
                    descriptions of these types.

  Returns:
    string The URL of the namespace this field was defined within.

  Raises:
    TypeError: if the given field is not within the given complex type.
  """
  type_obj = soappy_service.wsdl.types[ns].types[type_name]

  if IsASubType(type_name, ns, soappy_service):
    if hasattr(type_obj.content.derivation.content, 'content'):
      for element in type_obj.content.derivation.content.content:
        if element.attributes['name'] == field: return ns
    try:
      return GetComplexFieldNamespaceByFieldName(
          field,
          type_obj.content.derivation.attributes['base'].getName(),
          type_obj.content.derivation.attributes['base'].getTargetNamespace(),
          soappy_service)
    except TypeError:
      raise TypeError('There is no field with the name %s in complex type %s.'
                      % (field, type_name))
  else:
    for element in type_obj.content.content:
      if element.attributes['name'] == field: return ns
    raise TypeError('There is no field with the name %s in complex type %s.'
                    % (field, type_name))


def GetExplicitType(obj, type_name, ns, soappy_service):
  """Returns the WSDL-defined type set within the given object, if one exists.

  Args:
    obj: dict The python representation of an object of the given type.
    type_name: string The name of the type the given object represents.
    ns: string The namespace the given type belongs to.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    the WSDL definitions.

  Returns:
    tuple(string, string) The name of the type explicitly set within the given
    object, followed by the key used to specify this type. If no type is set
    within the given object, returns the tuple (None, None).
  """
  for item in obj:
    if (item == 'xsi_type' or item == 'type' or item.find('.Type') > -1 or
        item.find('_Type') > -1):
      if item == 'type':
        if not _HasNativeType(type_name, ns, soappy_service):
          return (obj['type'], 'type')
      else:
        return (obj[item], item)
  return (None, None)


def _HasNativeType(type_name, ns, soappy_service):
  """Checks a given WSDL-defined type for a field named 'type'.

  Args:
    type_name: string The name of the type to search.
    ns: string The namespace the given type belongs to.
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object encapsulating
                    the WSDL definitions.

  Returns:
    bool Whether or not the given type has a field named 'type'.
  """
  params = GenKeyOrderAttrs(soappy_service, ns, type_name)
  for param in params:
    if param['name'] == 'type': return True
  return False
