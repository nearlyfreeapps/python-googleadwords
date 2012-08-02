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

"""This example downloads a criteria performance report. To get report fields,
run get_report_fields.py.

Tags: ReportDefinitionService.mutate
Api: AdWordsOnly
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


# Specify where to download the file here.
path = '/tmp/report_download.csv'


def main(client, path):
  # Initialize appropriate service.
  report_downloader = client.GetReportDownloader(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Create report definition.
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

  file_path = report_downloader.DownloadReport(report, file_path=path)

  print 'Report was downloaded to \'%s\'.' % file_path


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client, path)
