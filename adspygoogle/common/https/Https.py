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

"""HTTPS connection classes that can be monkey-patched into httplib."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import httplib
import re
import socket
import ssl

from adspygoogle.common.Errors import Error


_old_https = None
_ca_certs_file = None


def MonkeyPatchHttplib(ca_cert):
  """Overrides the httplib.HTTPS class with the local _SslAwareHttps class.

  Args:
    ca_cert: string Path to a file containing trusted certificates. If None,
             certificate validation will cease and the original httplib.HTTPS
             class will be restored.
  """
  global _old_https
  global _ca_certs_file
  if ca_cert is None:
    if _old_https is not None:
      httplib.HTTPS = _old_https
  else:
    if _old_https is None:
      _old_https = httplib.HTTPS
      httplib.HTTPS = _SslAwareHttps
  _ca_certs_file = ca_cert


def GetCurrentCertsFile():
  """Getter method for the current trusted certificates source file."""
  return _ca_certs_file


class _SslAwareHttps(httplib.HTTPS):
  """Overridden HTTPS class which can handle SSL certificate verification."""

  def __init__(self, host='', port=None, key_file=None, cert_file=None,
               strict=None, ca_cert=None):
    if port == 0: port = None
    self._setup(_SslAwareHttpsConnection(
        host, port, key_file, cert_file, strict, ca_cert))


class _SslAwareHttpsConnection(httplib.HTTPSConnection):
  """Overridden connection which can handle SSL certificate verification."""

  def __init__(self, host, port=None, key_file=None, cert_file=None,
               strict=None, ca_certs=None):
    httplib.HTTPSConnection.__init__(self, host, port, key_file, cert_file,
                                     strict)

    if ca_certs is None: ca_certs = _ca_certs_file
    self.ca_certs = ca_certs
    if self.ca_certs:
      self.cert_reqs = ssl.CERT_REQUIRED
    else:
      self.cert_reqs = ssl.CERT_NONE

  def connect(self):
    """Creates a socket and validates SSL certificates."""
    sock = socket.create_connection((self.host, self.port))
    try:
      self.sock = ssl.wrap_socket(sock, keyfile=self.key_file,
                                  certfile=self.cert_file,
                                  cert_reqs=self.cert_reqs,
                                  ca_certs=self.ca_certs)
    except ssl.SSLError, e:
      raise Error('Error validating SSL certificate for "' + self.host +
                  '": ' + str(e))

    if self.cert_reqs == ssl.CERT_REQUIRED:
      self._VerifyHostName(self.host, self.sock.getpeercert())

  def _VerifyHostName(self, hostname, certificate):
    """Checks the host name used against the host's SSL certificate.

    Args:
      hostname: string The name of the host this socket is connecting to.
      certificate: dictionary The SSL certificate returned by this host.

    Raises:
      Error: if the host name used for this connection is not listed as one of
      the names in the SSL certificate returned by this host.
    """
    if 'subjectAltName' in certificate:
      names = [name for (name_type, name) in certificate['subjectAltName']
               if name_type.lower() == 'dns']
    else:
      names = [value for ((key, value),) in certificate['subject']
               if key.lower() == 'commonname']

    for name in names:
      if re.match(name.replace('.', '\.').replace('*', '[^.]*'), hostname,
                  re.I) is not None:
        return

    raise Error('Host name "' + self.host + '" does not match any name listed '
                'in its SSL certificate!')
