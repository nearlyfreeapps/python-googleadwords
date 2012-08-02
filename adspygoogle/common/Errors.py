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


class Error(Exception):

  """Implements Error.

  Responsible for handling error.
  """

  def __init__(self, msg):
    Exception.__init__(self, msg)
    self.msg = msg

  def __str__(self):
    return str(self.msg)

  def __call__(self):
    return (self.msg,)


class DetailError(object):

  """Implements DetailError.

  Responsible for handling detailed ApiException error.
  """

  def __init__(self):
    pass

  def __call__(self):
    pass


class ApiAsStrError(Error):

  """Implements ApiAsStrError.

  Responsible for handling API exceptions that come in a form of a string.
  """

  def __init__(self, msg):
    Error.__init__(self, msg)

  def __call__(self):
    return (self.code, Error.__str__(self))


class InvalidInputError(Error):

  """Implements InvalidInputError.

  Responsible for handling invalid local input error.
  """

  pass


class ValidationError(Error):

  """Implements ValidationError.

  Responsible for handling validation error that is caught locally by the
  client library.
  """

  def __init__(self, msg, root_cause=None):
    Error.__init__(self, msg)
    self.root_cause = root_cause


class ApiVersionNotSupportedError(Error):

  """Implements ApiVersionNotSupportedError.

  Responsible for handling error due to unsupported version of API.
  """

  pass


class MissingPackageError(Error):

  """Implements MissingPackageError.

  Responsible for handling missing package error.
  """

  pass


class MalformedBufferError(Error):

  """Implements MalformedBufferError.

  Responsible for handling malformaed SOAP buffer error.
  """

  pass


class AuthTokenError(Error):

  """Implements AuthTokenError.

  Responsible for handling auth token error.
  """

  pass


class CaptchaError(AuthTokenError):

  """Implements CaptchaError which encapsulates a CAPTCHA challenge."""

  def __init__(self, captcha_token, captcha_url):
    AuthTokenError.__init__(self, 'Captcha challenge, token \'%s\', url \'%s\'.'
                            % (captcha_token, captcha_url))
    self.captcha_token = captcha_token
    self.captcha_url = captcha_url
