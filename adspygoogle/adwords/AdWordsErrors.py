#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Classes for handling errors."""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

from adspygoogle.adwords import ERROR_TYPES
from adspygoogle.common.Errors import DetailError
from adspygoogle.common.Errors import Error


class AdWordsError(Error):

  """Implements AdWordsError.

  Responsible for handling error.
  """
  pass


class AdWordsDetailError(DetailError):

  """Implements AdWordsDetailError.

  Responsible for handling detailed ApiException error.
  """

  def __init__(self, **error):
    DetailError.__init__(self)
    self.__error = error
    for key in self.__error:
      self.__dict__.__setitem__(key, self.__error[key])

  def __call__(self):
    return (self.__error,)


class AdWordsApiError(AdWordsError):

  """Implements AdWordsApiError.

  Responsible for handling API exception.
  """

  def __init__(self, fault):
    (self.__fault, self.fault_code, self.fault_string) = (fault, '', '')
    if 'faultcode' in fault: self.fault_code = fault['faultcode']
    if 'faultstring' in fault: self.fault_string = fault['faultstring']

    (self.code, error_msg, self.trigger, self.errors) = (-1, '', '', [])
    if 'detail' in fault and fault['detail']:
      if 'code' in fault['detail']: self.code = int(fault['detail']['code'])
      if 'trigger' in fault['detail']: self.trigger = fault['detail']['trigger']
      if 'message' in fault['detail']: error_msg = fault['detail']['message']
    if not error_msg: error_msg = self.fault_string

    errors = [None]
    if 'detail' in fault and fault['detail'] and 'errors' in fault['detail']:
      errors = fault['detail']['errors']
    elif 'detail' not in fault or not fault['detail']:
      errors[0] = {}
    else:
      errors[0] = fault['detail']
    if isinstance(errors, list):
      for error in errors:
        # Keys need to be of type str not unicode.
        error_dct = dict([(str(key), value) for key, value in error.items()])
        self.errors.append(AdWordsDetailError(**error_dct))
    else:
      # Keys need to be of type str not unicode.
      error_dct = dict([(str(key), value) for key, value in errors.items()])
      self.errors.append(AdWordsDetailError(**error_dct))
    AdWordsError.__init__(self, error_msg)

  def __call__(self):
    return (self.__fault,)


class AdWordsRequestError(AdWordsApiError):

  """Implements AdWordsRequestError.

  Responsible for handling request error."""

  pass


class AdWordsGoogleInternalError(AdWordsApiError):

  """Implements AdWordsGoogleInternalError.

  Responsible for handling Google internal error.
  """

  pass


class AdWordsAuthenticationError(AdWordsApiError):

  """Implements AdWordsAuthenticationError.

  Responsible for handling authentication error.
  """

  pass


class AdWordsAccountError(AdWordsApiError):

  """Implements AdWordsAccountError.

  Responsible for handling account error.
  """

  pass


class AdWordsWebpageError(AdWordsApiError):

  """Implements AdWordsWebpageError.

  Responsible for handling webpage error.
  """

  pass


class AdWordsBillingError(AdWordsApiError):

  """Implements AdWordsBillingError.

  Responsible for handling billing error.
  """

  pass


# Map error codes and types to their corresponding classes.
ERRORS = {}
ERROR_CODES = [x for x in xrange(0, 208)]
for index in ERROR_CODES+ERROR_TYPES:
  if (((index >= 1 and index <= 10) or (index >= 12 and index <= 17) or
       (index >= 19 and index <= 42) or (index >= 43 and index <= 49) or
       index == 51 or index == 54 or (index >= 57 and index <= 59) or
       (index >= 61 and index <= 63) or (index >= 70 and index <= 83) or
       (index >= 87 and index <= 94) or index == 96 or index == 97 or
       index == 99 or index == 112 or index == 115 or index == 116 or
       (index >= 120 and index <= 125) or index == 127 or index == 128 or
       index == 131 or index == 133 or index == 134 or index == 137 or
       index == 138 or (index >= 140 and index <= 142) or
       (index >= 144 and index <= 147) or index == 149 or index == 153 or
       (index >= 156 and index <= 158) or (index >= 170 and index <= 174) or
       index == 176 or index == 177 or index == 186 or index == 188 or
       index == 190 or index == 206 or index == 207) or
      (index in ('AdError', 'AdExtensionError', 'AdExtensionOverrideError',
                 'AdGroupAdError', 'AdGroupCriterionError',
                 'AdGroupServiceError', 'AdParamError', 'AdParamPolicyError',
                 'AlertError', 'ApiError', 'ApiUsageError', 'AudioError',
                 'BidLandscapeServiceError', 'BiddingError',
                 'BiddingTransitionError', 'BudgetError', 'BulkMutateJobError',
                 'CampaignAdExtensionError',
                 'CampaignCriterionError', 'CampaignError',
                 'CollectionSizeError', 'ConversionTrackingError',
                 'CriterionError', 'CriterionPolicyError', 'CurrencyCodeError',
                 'CustomerSyncError', 'DataError', 'DateError', 'DistinctError',
                 'ExperimentServiceError', 'GeoLocationError', 'IdError',
                 'ImageError', 'JobError', 'MatchesRegexError', 'MediaError',
                 'NewEntityCreationError', 'NotEmptyError', 'NullError',
                 'OperatorError', 'OpportunityError', 'PagingError',
                 'PolicyViolationError', 'RangeError', 'ReadOnlyError',
                 'RegionCodeError', 'RejectedError', 'ReportDefinitionError',
                 'RequestError', 'RequiredError', 'SelectorError',
                 'ServicedAccountError', 'SettingError', 'SizeLimitError',
                 'StatsQueryError', 'StringLengthError', 'TargetError',
                 'TargetingIdeaError', 'TrafficEstimatorError', 'UserListError',
                 'VideoError'))):
    ERRORS[index] = AdWordsRequestError
  elif ((index == 0 or index == 18 or index == 55 or index == 60 or
         index == 95 or index == 98 or index == 117 or index == 143 or
         index == 155) or
        (index in ('InternalApiError', 'DatabaseError', 'QuotaCheckError',
                   'QuotaError', 'QuotaExceededError', 'RateExceededError'))):
    ERRORS[index] = AdWordsGoogleInternalError
  elif (((index >= 84 and index <= 86) or index == 111 or index == 119 or
         index == 129 or index == 139 or (index >= 162 and index <= 165) or
         index == 183 or index == 189) or
        (index in ('ClientTermsError', 'NotWhitelistedError'))):
    ERRORS[index] = AdWordsAccountError
  elif (index >= 100 and index <= 105):
    ERRORS[index] = AdWordsWebpageError
  elif (index == 50 or index == 52 or index == 53 or index == 106 or
         index == 107 or index == 109 or index == 110 or index == 114 or
         index == 118 or index == 130 or index == 132) or (index in ()):
    ERRORS[index] = AdWordsBillingError
  elif ((index == 166 or index == 184) or
        ('AuthenticationError', 'AuthorizationError')):
    ERRORS[index] = AdWordsAuthenticationError
