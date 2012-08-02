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

"""This example illustrates how to retrieve all the campaign targets. To set
campaign targets, run add_campaign_targeting_criteria.py.

Tags: CampaignCriterionService.get
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import os
import sys
sys.path.insert(0, os.path.join('..', '..', '..', '..', '..'))

# Import appropriate classes from the client library.
from adspygoogle import AdWordsClient


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  campaign_criterion_service = client.GetCampaignCriterionService(
      'https://adwords-sandbox.google.com', 'v201109_1')

  # Construct selector and get all campaign targets.
  offset = 0
  selector = {
      'fields': ['CampaignId', 'Id', 'CriteriaType', 'PlatformName',
                 'LanguageName', 'LocationName', 'KeywordText'],
      'predicates': [{
          'field': 'CriteriaType',
          'operator': 'IN',
          'values': ['KEYWORD', 'LANGUAGE', 'LOCATION', 'PLATFORM']
      }],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = campaign_criterion_service.Get(selector)[0]

    # Display results.
    if 'entries' in page:
      for campaign_criterion in page['entries']:
        negative = ''
        if (campaign_criterion['CampaignCriterion_Type']
            == 'NegativeCampaignCriterion'):
          negative = 'Negative '
        criterion = campaign_criterion['criterion']
        criteria = (criterion.get('text') or criterion.get('platformName') or
                    criterion.get('name') or criterion.get('locationName'))
        print ('%sCampaign Criterion found for Campaign ID %s with type %s and '
               'criteria "%s".' % (negative, campaign_criterion['campaignId'],
                                   criterion['type'], criteria))
    else:
      print 'No campaign targets were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  print
  print ('Usage: %s units, %s operations' % (client.GetUnits(),
                                             client.GetOperations()))


if __name__ == '__main__':
  # Initialize client object.
  client = AdWordsClient(path=os.path.join('..', '..', '..', '..', '..'))

  main(client)
