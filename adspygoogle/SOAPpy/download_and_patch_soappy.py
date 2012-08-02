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

"""Downloads and patches SOAPpy into the current directory."""

__author__ = 'api.jdilallo@gmail.com (Joseph DiLallo)'

import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib


# The DOWNLOAD_URL is the location where SOAPpy can be downloaded from.
DOWNLOAD_URL = ('http://sourceforge.net/projects/pywebsvcs/files/SOAP.py/'
                '0.12.0_rc1/SOAPpy-0.12.0.tar.gz/'
                'download?use_mirror=superb-dca2')
REMOVE_FILES = ['GSIServer.py']


def main():
  download_filename, _ = urllib.urlretrieve(DOWNLOAD_URL)
  tar_out_dir = tempfile.mkdtemp()
  downloaded_tar = tarfile.open(download_filename)
  downloaded_tar.extractall(tar_out_dir)

  for filename in os.listdir(os.path.join(tar_out_dir, 'SOAPpy-0.12.0',
                                          'SOAPpy')):
    abs_filename = os.path.join(tar_out_dir, 'SOAPpy-0.12.0', 'SOAPpy',
                                filename)
    if os.path.isdir(abs_filename):
      # If the destination exists (i.e. wstools), first remove it.
      if os.path.exists(os.path.join(os.curdir, filename)):
        shutil.rmtree(os.path.join(os.curdir, filename))
      shutil.copytree(abs_filename, os.path.join(os.curdir, filename))
    else:
      shutil.copy(abs_filename, os.curdir)

  code = subprocess.call(['patch', '-p0'],
                         stdin=open(os.path.join(os.curdir, 'SOAPpy.patch')))
  shutil.rmtree(tar_out_dir)
  for path in REMOVE_FILES:
    os.remove(path)
  if not code: print 'Success! SOAPpy-0.12.0 has been downloaded and patched.'


if __name__ == '__main__':
  main()
