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

import os

from adspygoogle.adwords import LIB_HOME
from adspygoogle.common import Utils


def GetCurrencies():
  """Get a list of available currencies.

  Returns:
    list Available currencies.
  """
  return Utils.GetDataFromCsvFile(os.path.join(LIB_HOME, 'data',
                                               'currencies.csv'))


def GetErrorCodes():
  """Get a list of available error codes.

  Returns:
    list Available error codes.
  """
  return Utils.GetDataFromCsvFile(os.path.join(LIB_HOME, 'data',
                                               'error_codes.csv'))


def GetTimezones():
  """Get a list of available timezones.

  Returns:
    list Available timezones.
  """
  return Utils.GetDataFromCsvFile(os.path.join(LIB_HOME, 'data',
                                               'timezones.csv'))


def TransformJobOperationXsi(operation):
  """Ensures that the types in an JobOperation's inner Operations end correctly.

  This function ensures backwards compatibility with previous versions of the
  library which allowed you leave "Operation" off of an Operation's type. This
  is now considered deprecated style; always put a type's full name.

  Args:
    operation: dict The JobOperation object.
  """
  for item in operation['operand']['request']['operationStreams']:
    for sub_item in item['operations']:
      if ('xsi_type' in sub_item and
          not sub_item['xsi_type'].endswith('Operation')):
        sub_item['xsi_type'] = '%sOperation' % sub_item['xsi_type']
      elif 'type' in sub_item and not sub_item['type'].endswith('Operation'):
        sub_item['type'] = '%sOperation' % sub_item['type']


def TransformUserListRuleOperands(user_list):
  """Ensures that the key in the ruleOperands dicts is set correctly.

  This function ensures backwards compatibility with previous versions of the
  library which allowed you place a UserList or UserInterest directly into the
  ruleOperands field of a UserListLogicalRule instead of placing it inside of a
  LogicalUserListOperand object. This is now considered deprecated style; always
  put the LogicalUserListOperand object in the middle.

  Args:
    user_list: dict A UserList or UserInterest object.
  """
  if 'rules' in user_list:
    rules = []
    for item in user_list['rules']:
      if 'ruleOperands' in item:
        operands = []
        for sub_item in item['ruleOperands']:
          if 'xsi_type' in sub_item:
            operand = {}
            if sub_item['xsi_type'] in ('UserInterest',):
              TransformUserListRuleOperands(sub_item)
              operand['UserInterest'] = sub_item
            else:
              TransformUserListRuleOperands(sub_item)
              operand['UserList'] = sub_item
            operands.append(operand)
            item['ruleOperands'] = operands
      rules.append(item)
    user_list['rules'] = rules


def ExtractGroupNameFromUrl(url):
  """Takes an AdWords service's URL and extracts the group it belongs to.

  Args:
    url: string The URL of an AdWords service.

  Returns:
    string The group this AdWords service belongs to.
  """
  return url.split('/')[-2]
