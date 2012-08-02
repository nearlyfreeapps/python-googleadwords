#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

"""Script to fetch codes used throughout the AdWords API web services.

See http://code.google.com/apis/adwords/docs/developer/adwords_api_codes.html.
"""

__author__ = 'api.sgrinberg@gmail.com (Stan Grinberg)'

import os
import re
import sys
sys.path.insert(0, os.path.join('..', '..', '..'))
import urllib

from adspygoogle.common import Utils


URL = 'http://code.google.com/apis/adwords/docs/developer'
LOC = os.path.join('..', 'aw_api', 'data')
DATA_MAP = [
  {'csv': 'categories',
   'url': '/'.join([URL, 'adwords_api_categories.html']),
   're': ('<li><b>/(.*?)</b></li>|<li><span class="categorypath">(.*?)</span>'
          '<b>(.*?)</b></li>'),
   'cols': ['category', 'path']
  },
  {'csv': 'countries',
   'url': '/'.join([URL, 'adwords_api_countries.html']),
   're': '<tr><td>(.*?)</td><td>(.*?)</td></tr>',
   'cols': ['country', 'code']
  },
  {'csv': 'currencies',
   'url': '/'.join([URL, 'adwords_api_currency.html']),
   're': '<tr><td>(.*?)</td><td>(.*?)</td></tr>',
   'cols': ['code', 'currency']
  },
  {'csv': 'error_codes',
   'url': '/'.join([URL, 'adwords_api_error_codes.html']),
   're': ('<tr id=".*?" class="ShowHide"><td id=".*?"><code><span class="">'
          '(.*?)</span></code></td><td><span class=""> (.*?)</span></td></tr>'),
   'cols': ['code', 'message']
  },
  {'csv': 'languages',
   'url': '/'.join([URL, 'adwords_api_languages.html']),
   're': '<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>',
   'cols': ['name', 'target', 'display']
  },
  {'csv': 'timezones',
   'url': '/'.join([URL, 'adwords_api_timezones.html']),
   're': '<tr><td>(.*?)</td></tr>',
   'cols': ['timezone']
  },
  {'csv': 'us_cities',
   'url': '/'.join([URL, 'adwords_api_us_cities.html']),
   're': '<h2 id=".*?">(.*?)</h2><table.*?>(.*?)</table>',
   'cols': ['state', 'code']
  },
  {'csv': 'us_metros',
   'url': '/'.join([URL, 'adwords_api_us_metros.html']),
   're': '<table class="codes" summary="">.*?<h2>(.*?)</h2>(.*?)</table>',
   'cols': ['state', 'metro', 'code']
  },
  {'csv': 'world_cities',
   'url': '/'.join([URL, 'adwords_api_cities.html']),
   're': ('<h2 id=".*?">((?:\w+|\w+\s\w+))</h2><table class="codes" summary="" '
          'style="width: 100%"><tr>(.*?)(?:</ul></td>|)</tr></table>'),
   'cols': ['country', 'code']
  },
  {'csv': 'world_regions',
   'url': '/'.join([URL, 'adwords_api_regions.html']),
   're': ('<h2 id=".*?">((?:\w+|\w+\s\w+))</h2><table class="codes" '
          'summary="codes">(.*?)</table>'),
   'cols': ['country', 'code', 'region']
  }
]


if os.path.exists(os.path.abspath(LOC)):
  for f_name in os.listdir(os.path.abspath(LOC)):
    f_path = os.path.abspath(os.path.join(LOC, f_name))
    if f_name.split('.')[-1] == 'csv':
      os.unlink(f_path)
else:
  os.mkdir(os.path.abspath(LOC))

print 'Fetching codes ...'
for item in DATA_MAP:
  data = ''.join(urllib.urlopen(item['url']).read().split('\n'))

  # Remove weird unicode characters.
  for weird_char in ['\xa0', '\xc2']:
    if data.find(weird_char) > -1:
      data = data.replace(weird_char, '')

  pattern = re.compile(item['re'])
  groups = pattern.findall(data)
  lines = []
  for group in groups:
    if item['csv'] in ('categories',):
      group = [x for x in group if x != '']
      if len(group) == 1:
        category = ''.join(group)
        continue
      else:
        path = ''.join(group)
      lines.append('%s,%s'
                   % (Utils.CsvEscape(str(Utils.HtmlUnescape(category))),
                      Utils.CsvEscape(str(Utils.HtmlUnescape(path)))))
    elif item['csv'] in ('countries', 'currencies'):
      lines.append('%s,%s'
                   % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                      Utils.CsvEscape(str(Utils.HtmlUnescape(group[1])))))
    elif item['csv'] in ('error_codes',):
      pattern = re.compile('<.*?>')
      message = list(group)[1]
      message = pattern.sub('', message)
      lines.append('%s,%s'
                   % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                      Utils.CsvEscape(str(Utils.HtmlUnescape(message)))))
    elif item['csv'] in ('languages',):
      # Convert '-' into ''.
      new_group = []
      for sub_item in list(group):
        if sub_item == '-':
          new_group.append('')
        else:
          new_group.append(sub_item)
      lines.append('%s,%s,%s'
                   % (Utils.CsvEscape(str(Utils.HtmlUnescape(new_group[0]))),
                      Utils.CsvEscape(str(Utils.HtmlUnescape(new_group[1]))),
                      Utils.CsvEscape(str(Utils.HtmlUnescape(new_group[2])))))
    elif item['csv'] in ('timezones',):
      lines.append('%s' % str(Utils.HtmlUnescape(group)))
    elif item['csv'] in ('us_cities',):
      if group[0] != 'States':
        pattern = re.compile('<li>(.*?)</li>')
        sub_groups = pattern.findall(group[1])
        for sub_group in sub_groups:
          lines.append('%s,%s'
                       % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                          Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group)))))
    elif item['csv'] in ('us_metros',):
      pattern = re.compile('<tr><td>(.*?)</td><td>(.*?)</td></tr>')
      sub_groups = pattern.findall(group[1])
      for sub_group in sub_groups:
        lines.append('%s,%s,%s'
                     % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                        Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group[0]))),
                        Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group[1])))))
    elif item['csv'] in ('world_cities',):
      pattern = re.compile('<li>(.*?)</li>')
      sub_groups = pattern.findall(group[1])
      for sub_group in sub_groups:
        lines.append('%s,%s'
                     % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                        Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group)))))
    elif item['csv'] in ('world_regions',):
      pattern = re.compile('<tr><td>(.*?)</td><td>(.*?)</td></tr>')
      sub_groups = pattern.findall(group[1])
      for sub_group in sub_groups:
        lines.append('%s,%s,%s'
                     % (Utils.CsvEscape(str(Utils.HtmlUnescape(group[0]))),
                        Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group[0]))),
                        Utils.CsvEscape(str(Utils.HtmlUnescape(sub_group[1])))))

  print '  [+] %s.csv' % item['csv']
  fh = open('%s.csv' % os.path.abspath(os.path.join(LOC, item['csv'])), 'w')
  try:
    lines.insert(0, ','.join(item['cols']))
    for line in lines:
      fh.write('%s\n' % line)
  finally:
    fh.close()

print '... done.'
