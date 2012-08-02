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

"""Validation functions."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

from adspygoogle.common import ETREE
from adspygoogle.common import PYXML
from adspygoogle.common import Utils
from adspygoogle.common.Errors import ValidationError
from adspygoogle.common.soappy import SoappyUtils


def ValidateRequiredHeaders(headers, required_headers):
  """Sanity check for required authentication elements.

  The required headers may contain several possible header combinations, only
  one of which must be satisfied to make successful API request. In order for
  any single combination to be satisfied, all of the headers it specifies must
  exist as keys within the headers dict and each entry must contain data.

  Args:
    headers: A dict containing authentication headers.
    required_headers: A tuple containing valid combinations of headers. Each
                      combination of headers is represented as a tuple of
                      strings. e.g. (('Name', 'Password'), ('Name', 'Token'))

  Raises:
    ValidationError: The given authentication headers are not sufficient to make
                     requests against this API.
  """
  is_valid = False
  for headers_set in required_headers:
    is_valid_set = True
    for key in headers_set:
      if key not in headers or not headers[key]: is_valid_set = False
    if is_valid_set:
      is_valid = True
      break

  if not is_valid:
    msg = ('Required authentication header is missing. Valid options for '
           'headers are %s.' % str(required_headers))
    raise ValidationError(msg)


def IsConfigUserInputValid(user_input, valid_el):
  """Determines if user input within configuration scripts is valid.

  Each time a choice is presented to the user, a set of allowed values specific
  to that interaction is passed into this function.

  Args:
    user_input: The string of user input.
    valid_el: A list of valid elements for the current interaction.

  Returns:
    bool True if user input is valid, False otherwise.
  """
  if not user_input: return False

  try:
    valid_el.index(str(user_input))
  except ValueError:
    return False
  return True


def ValidateConfigXmlParser(xml_parser):
  """Checks that the XML parser set in the configuration is a valid choice.

  Args:
    xml_parser: A string specifying which XML parser to use.

  Raises:
    ValidationError: The given XML parser is not supported by this library.
  """
  if (not isinstance(xml_parser, str) or
      not IsConfigUserInputValid(xml_parser, [PYXML, ETREE])):
    msg = ('Invalid input for %s \'%s\', expecting %s or %s of type <str>.'
           % (type(xml_parser), xml_parser, PYXML, ETREE))
    raise ValidationError(msg)


def ValidateTypes(vars_tpl):
  """Checks that each variable in a set of variables is the correct type.

  Args:
    vars_tpl: A tuple containing a set of variables to check.

  Raises:
    ValidationError: The given object was not one of the given accepted types.
  """
  for var, var_types in vars_tpl:
    if not isinstance(var_types, tuple):
      var_types = (var_types,)
    for var_type in var_types:
      if isinstance(var, var_type):
        return
    msg = ('The \'%s\' is of type %s, expecting one of %s.'
           % (var, type(var), var_types))
    raise ValidationError(msg)


def _SoappySanityCheckComplexType(soappy_service, obj, ns, xsi_type):
  """Validates a dict representing a complex type against its WSDL definition.

  Args:
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object containing the
                    descriptions of all WSDL-defined types.
    obj: A dict that should represent an instance of the given type.
    ns: string The namespace the given type belongs to.
    xsi_type: A string specifying the name of a complex type defined in the
              WSDL.

  Raises:
    ValidationError: The given object is not an acceptable representation of the
                     given WSDL-defined complex type.
  """
  ValidateTypes(((obj, dict),))
  obj_contained_type, type_key = SoappyUtils.GetExplicitType(obj, xsi_type, ns,
                                                             soappy_service)

  if obj_contained_type and not obj_contained_type == xsi_type:
    try:
      SoappyUtils.GetTypeFromSoappyService(obj_contained_type, ns,
                                           soappy_service)
    except KeyError:
      raise ValidationError('Object of class \'%s\' has an explicit type of '
                            '\'%s\', but this explicit type is not defined in '
                            'the WSDL.' % (xsi_type, obj_contained_type))
    if not SoappyUtils.IsASuperType(soappy_service, obj_contained_type, ns,
                                    xsi_type):
      raise ValidationError('Expecting type of \'%s\' but given type of class '
                            '\'%s\'.' % (xsi_type, obj_contained_type))
    xsi_type = obj_contained_type

  parameters = SoappyUtils.GenKeyOrderAttrs(soappy_service, ns, xsi_type)
  for key in obj:
    if obj[key] is None or key == type_key:
      continue
    found = False
    for parameter, param_type, max_occurs in [
        (param['name'], param['type'], param['maxOccurs']) for
        param in parameters]:
      if parameter == key:
        found = True
        if not max_occurs.isdigit() or int(max_occurs) > 1:
          # This parameter should be a list.
          if isinstance(obj[key], (list, tuple)):
            for item in obj[key]:
              SoappySanityCheck(soappy_service, item,
                                param_type.getTargetNamespace(),
                                param_type.getName())
          else:
            raise ValidationError('Field \'%s\' in complex type \'%s\' should '
                                  'be a list but value \'%s\' is a \'%s\' '
                                  'instead.'
                                  % (key, xsi_type, obj[key], type(obj[key])))
        else:
          SoappySanityCheck(soappy_service, obj[key],
                            param_type.getTargetNamespace(),
                            param_type.getName())
        break
    if not found:
      raise ValidationError('Field \'%s\' is not in type \'%s\'.'
                            % (key, xsi_type))


def _SoappySanityCheckSimpleType(obj, xsi_type):
  """Validates a string representing a simple type against its WSDL definition.

  Args:
    obj: String representing the given simple type.
    xsi_type: A string specifying the simple type name defined in the WSDL.

  Raises:
    ValidationError: The given object is not an acceptable representation of the
                     given WSDL-defined simple type.
  """
  try:
    ValidateTypes(((obj, (str, unicode)),))
  except ValidationError:
    raise ValidationError('Simple type \'%s\' should be a string but value '
                          '\'%s\' is a \'%s\' instead.' %
                          (xsi_type, obj, type(obj)))


def _SoappySanityCheckArray(soappy_service, obj, ns, type_name):
  """Validates a list representing an array type against its WSDL definition.

  Args:
    soappy_service: SOAPpy.WSDL.Proxy The SOAPpy service object containing the
                    descriptions of all WSDL-defined types.
    obj: Object to be validated. Depending on the WSDL-defined type this object
         represents, the data type will vary. It should always be either a
         dictionary, list, or string no matter what WSDL-defined type it is.
    ns: string The namespace the given type belongs to.
    type_name: A string specifying the type name defined in the WSDL.

  Raises:
    ValidationError if the given object is not a valid representation of the
    given list type.
  """
  try:
    ValidateTypes(((obj, list),))
  except ValidationError:
    raise ValidationError('Type \'%s\' should be a list but value '
                          '\'%s\' is a \'%s\' instead.' %
                          (type_name, obj, type(obj)))
  if Utils.IsBaseSoapType(type_name):
    for item in obj:
      if item is None: continue
      try:
        ValidateTypes(((item, (str, unicode)),))
      except ValidationError:
        raise ValidationError('The items in array \'%s\' must all be strings. '
                              'Value \'%s\' is of type \'%s\'.'
                              % (type_name, item, type(item)))
  else:
    for item in obj:
      if item is None: continue
      SoappySanityCheck(soappy_service, item, ns,
                        SoappyUtils.GetArrayItemTypeName(type_name, ns,
                                                         soappy_service))


def SoappySanityCheck(soappy_service, obj, ns, obj_type, max_occurs='1'):
  """Validates any given object against its WSDL definition.

  This method considers None and the empty string to be a valid representation
  of any type.

  Args:
    soappy_service: SOAPpy.WSDL.Proxy An object encapsulating a SOAP service.
    obj: Object to be validated. Depending on the WSDL-defined type this object
         represents, the data type will vary. It should always be either a
         dictionary, list, or string no matter what WSDL-defined type it is.
    ns: string The namespace the given type belongs to.
    obj_type: A string specifying the type name defined in the WSDL.
    max_occurs: string The maxOccurs attribute for this object.

  Raises:
    ValidationError: The given type has no definition in the WSDL or the given
                     object is not a valid representation of the type defined in
                     the WSDL.
  """
  if obj in (None, ''):
    return
  elif Utils.IsBaseSoapType(obj_type):
    try:
      ValidateTypes(((obj, (str, unicode)),))
    except ValidationError:
      raise ValidationError('Objects of type \'%s\' should be a string but '
                            'value \'%s\' is a \'%s\' instead.' %
                            (obj_type, obj, type(obj)))
  else:
    try:
      soap_type = soappy_service.wsdl.types[ns].types[obj_type].tag
      if soap_type == 'simpleType':
        _SoappySanityCheckSimpleType(obj, obj_type)
      elif soap_type == 'complexType':
        if (SoappyUtils.IsAnArrayType(obj_type, ns, soappy_service) or
            not max_occurs.isdigit() or int(max_occurs) > 1):
          _SoappySanityCheckArray(soappy_service, obj, ns, obj_type)
        else:
          _SoappySanityCheckComplexType(soappy_service, obj, ns, obj_type)
      else:
        raise ValidationError('Unrecognized type definition tag in WSDL: \'%s\''
                              % soap_type)
    except KeyError:
      raise ValidationError('This type is not defined in the WSDL: \'%s\''
                            % obj_type)
