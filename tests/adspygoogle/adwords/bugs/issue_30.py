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

"""Unit tests for issue #30.

Disabling RequestLog makes reportDownload fail.
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..'))
import unittest

from adspygoogle.adwords.AdWordsClient import AdWordsClient


class Issue30(unittest.TestCase):

  """Unittests for Issue #30."""

  def testDownloadReportWithRequestLogDisabled(self):
    """Tests if we can download a report with request logging disabled."""
    client = AdWordsClient(path=os.path.join('..', '..', '..'))
    client._config['request_log'] = 'n'  # pylint: disable=W0212
    report_downloader = client.GetReportDownloader(
        'https://adwords-sandbox.google.com', 'v201109')
    report = {
        'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
        'dateRangeType': 'LAST_7_DAYS',
        'reportType': 'CRITERIA_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                       'Criteria', 'Impressions', 'Clicks', 'Cost']
        },
        # Enable to get rows with zero impressions.
        'includeZeroImpressions': 'false'
    }

    report_downloader.DownloadReport(report)


if __name__ == '__main__':
  unittest.main()
