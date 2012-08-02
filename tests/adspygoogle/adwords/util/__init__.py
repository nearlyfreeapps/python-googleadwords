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

"""Helper functions to create objects to run tests with."""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

from adspygoogle.common import Utils
from tests.adspygoogle.adwords import HTTP_PROXY
from tests.adspygoogle.adwords import SERVER_V201206 as SERVER
from tests.adspygoogle.adwords import VERSION_V201206 as VERSION


def CreateTestCampaign(client):
  """Creates a CPC campaign to run tests with.

  Args:
    client: AdWordsClient client to obtain services from.

  Returns:
    int CampaignId
  """
  campaign_service = client.GetCampaignService(SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'name': 'Campaign #%s' % Utils.GetUniqueName(),
          'status': 'PAUSED',
          'biddingStrategy': {
              'type': 'ManualCPC'
          },
          'budget': {
              'period': 'DAILY',
              'amount': {
                  'microAmount': '10000000'
              },
              'deliveryMethod': 'STANDARD'
          },
          'settings': [
              {
                  'xsi_type': 'KeywordMatchSetting',
                  'optIn': 'false'
              }
          ]
      }
  }]
  return campaign_service.Mutate(
      operations)[0]['value'][0]['id']


def CreateTestRTBCampaign(client):
  """Creates a CPM campaign to run tests with.

  Args:
    client: AdWordsClient client to obtain services from.

  Returns:
    int CampaignId
  """
  campaign_service = client.GetCampaignService(SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'name': 'Campaign #%s' % Utils.GetUniqueName(),
          'status': 'PAUSED',
          'biddingStrategy': {
              'type': 'ManualCPM'
          },
          'budget': {
              'period': 'DAILY',
              'amount': {
                  'microAmount': '10000000'
              },
              'deliveryMethod': 'STANDARD'
          },
          'settings': [{
              'xsi_type': 'RealTimeBiddingSetting',
              'optIn': 'true'
          }, {
              'xsi_type': 'KeywordMatchSetting',
              'optIn': 'false'
          }]
      }
  }]
  return campaign_service.Mutate(
      operations)[0]['value'][0]['id']


def CreateTestAdGroup(client, campaign_id):
  """Creates a CPC AdGroup to run tests with.

  Args:
    client: AdWordsClient client to obtain services from.
    campaign_id: int ID of a CPC Campaign.

  Returns:
    int AdGroupId
  """
  ad_group_service = client.GetAdGroupService(SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign_id,
          'name': 'AdGroup #%s' % Utils.GetUniqueName(),
          'status': 'ENABLED',
          'bids': {
              'type': 'ManualCPCAdGroupBids',
              'keywordMaxCpc': {
                  'amount': {
                      'microAmount': '1000000'
                  }
              }
          }
      }
  }]
  ad_groups = ad_group_service.Mutate(operations)[0]['value']
  return ad_groups[0]['id']


def CreateTestCPMAdGroup(client, campaign_id):
  """Creates a CPM AdGroup to run tests with.

  Args:
    client: AdWordsClient client to obtain services from.
    campaign_id: int ID of a CPM Campaign.

  Returns:
    int AdGroupId
  """
  ad_group_service = client.GetAdGroupService(SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign_id,
          'name': 'AdGroup #%s' % Utils.GetUniqueName(),
          'status': 'ENABLED',
          'bids': {
              'type': 'ManualCPMAdGroupBids',
              'maxCpm': {
                  'amount': {
                      'microAmount': '1000000'
                  }
              }
          }
      }
  }]
  ad_groups = ad_group_service.Mutate(operations)[0]['value']
  return ad_groups[0]['id']


def CreateTestAd(client, ad_group_id):
  """Creates an Ad for running tests with.

  Args:
    client: AdWordsClient client to obtain services from.
    ad_group_id: int ID of the AdGroup the Ad should belong to.

  Returns:
    int AdGroupAdId
  """
  ad_group_ad_service = client.GetAdGroupAdService(SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'type': 'AdGroupAd',
          'adGroupId': ad_group_id,
          'ad': {
              'type': 'TextAd',
              'url': 'http://www.example.com',
              'displayUrl': 'example.com',
              'description1': 'Visit the Red Planet in style.',
              'description2': 'Low-gravity fun for everyone!',
              'headline': 'Luxury Cruise to Mars'
          },
          'status': 'ENABLED',
      }
  }]
  ads = ad_group_ad_service.Mutate(operations)
  return ads[0]['value'][0]['ad']['id']


def CreateTestKeyword(client, ad_group_id):
  """Creates a Keyword for running tests with.

  Args:
    client: AdWordsClient client to obtain services from.
    ad_group_id: int ID of the AdGroup the Ad should belong to.

  Returns:
    int: KeywordId
  """
  ad_group_criterion_service = client.GetAdGroupCriterionService(
      SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'mars cruise'
          }
      }
  }]
  criteria = ad_group_criterion_service.Mutate(operations)
  return criteria[0]['value'][0]['criterion']['id']


def CreateTestPlacement(client, ad_group_id):
  """Creates a Placement for running tests with.

  Args:
    client: AdWordsClient client to obtain services from.
    ad_group_id: int ID of the AdGroup the Ad should belong to.

  Returns:
    int: KeywordId
  """
  ad_group_criterion_service = client.GetAdGroupCriterionService(
      SERVER, VERSION, HTTP_PROXY)
  operations = [{
      'operator': 'ADD',
      'operand': {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Placement',
              'url': 'http://mars.google.com'
          },
      }
  }]
  criteria = ad_group_criterion_service.Mutate(operations)
  return criteria[0]['value'][0]['criterion']['id']


def CreateTestLocationExtension(client, campaign_id):
  """Creates a Location Extension for testing.

  Args:
    client: AdWordsClient client to obtain services from.
    campaign_id: int ID of a CPC Campaign.

  Returns:
    int Location Extension ID
  """
  geo_location_service = client.GetGeoLocationService(
      SERVER, VERSION,HTTP_PROXY)
  campaign_ad_extension_service = client.GetCampaignAdExtensionService(
      SERVER, VERSION, HTTP_PROXY)
  selector = {
      'addresses': [
          {
              'streetAddress': '1600 Amphitheatre Parkway',
              'cityName': 'Mountain View',
              'provinceCode': 'US-CA',
              'provinceName': 'California',
              'postalCode': '94043',
              'countryCode': 'US'
          }
      ]
  }
  geo_locations = geo_location_service.Get(selector)
  # Construct operations and add campaign ad extension.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'CampaignAdExtension',
              'campaignId': campaign_id,
              'adExtension': {
                  'xsi_type': 'LocationExtension',
                  'address': geo_locations[0]['address'],
                  'geoPoint': geo_locations[0]['geoPoint'],
                  'encodedLocation': geo_locations[0]['encodedLocation'],
                  'source': 'ADWORDS_FRONTEND'
              }
          }
      }
  ]
  ad_extensions = campaign_ad_extension_service.Mutate(operations)[0]
  ad_extension = ad_extensions['value'][0]
  return ad_extension['adExtension']['id']


def GetExperimentIdForCampaign(client, campaign_id):
  """Retreives the ID of an ACTIVE experiment for the specified campaign.

  Args:
    client: AdWordsClient client to obtain services from.
    campaign_id: int ID of a CPC Campaign.

  Returns:
    int Experiment ID
  """
  selector = {
      'fields': ['Id'],
      'predicates': [{
          'field': 'CampaignId',
          'operator': 'EQUALS',
          'values': [campaign_id]
      }, {
          'field': 'Status',
          'operator': 'EQUALS',
          'values': ['ACTIVE']
      }]
  }
  experiment_service = client.GetExperimentService(SERVER, VERSION, HTTP_PROXY)
  page = experiment_service.get(selector)[0]
  return page['entries'][0]['id']
