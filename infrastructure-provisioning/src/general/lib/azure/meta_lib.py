# *****************************************************************************
#
# Copyright (c) 2016, EPAM SYSTEMS INC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ******************************************************************************

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage import CloudStorageAccount
from azure.storage.blob.models import ContentSettings, PublicAccess
import azure.common.exceptions as AzureExceptions
import logging
import traceback
import sys, time
import os


class AzureMeta:
    def __init__(self):
        if os.environ['conf_resource'] == 'ssn':
            os.environ['AZURE_AUTH_LOCATION'] = '/root/azure_auth.json'
            self.compute_client = get_client_from_auth_file(ComputeManagementClient)
            self.resource_client = get_client_from_auth_file(ResourceManagementClient)
            self.network_client = get_client_from_auth_file(NetworkManagementClient)

    def get_resource_group(self, resource_group_name):
        try:
            result = self.resource_client.resource_groups.get(resource_group_name)
            return result
        except AzureExceptions.CloudError as err:
            if err.status_code == 404:
                return ''
        except Exception as err:
            logging.info(
                "Unable to get Resource Group: " + str(err) + "\n Traceback: " + traceback.print_exc(file=sys.stdout))
            append_result(str({"error": "Unable to get Resource Group",
                               "error_message": str(err) + "\n Traceback: " + traceback.print_exc(
                                   file=sys.stdout)}))
            traceback.print_exc(file=sys.stdout)

    def get_vpc(self, resource_group_name, vpc_name):
        try:
            result = self.network_client.virtual_networks.get(resource_group_name, vpc_name)
            return result
        except AzureExceptions.CloudError as err:
            if err.status_code == 404:
                return ''
        except Exception as err:
            logging.info(
                "Unable to get Virtual Network: " + str(err) + "\n Traceback: " + traceback.print_exc(file=sys.stdout))
            append_result(str({"error": "Unable to get Virtual Network",
                               "error_message": str(err) + "\n Traceback: " + traceback.print_exc(
                                   file=sys.stdout)}))
            traceback.print_exc(file=sys.stdout)

    def get_subnet(self, resource_group_name, vpc_name, subnet_name):
        try:
            result = self.network_client.subnets.get(resource_group_name, vpc_name, subnet_name)
            return result
        except AzureExceptions.CloudError as err:
            if err.status_code == 404:
                return ''
        except Exception as err:
            logging.info(
                "Unable to get Subnet: " + str(err) + "\n Traceback: " + traceback.print_exc(file=sys.stdout))
            append_result(str({"error": "Unable to get Subnet",
                               "error_message": str(err) + "\n Traceback: " + traceback.print_exc(
                                   file=sys.stdout)}))
            traceback.print_exc(file=sys.stdout)

    def list_subnets(self, resource_group_name, vpc_name):
        try:
            result = self.network_client.subnets.list(resource_group_name, vpc_name)
            return result
        except AzureExceptions.CloudError as err:
            if err.status_code == 404:
                return ''
        except Exception as err:
            logging.info(
                "Unable to get list of Subnets: " + str(err) + "\n Traceback: " + traceback.print_exc(file=sys.stdout))
            append_result(str({"error": "Unable to get list of Subnets",
                               "error_message": str(err) + "\n Traceback: " + traceback.print_exc(
                                   file=sys.stdout)}))
            traceback.print_exc(file=sys.stdout)