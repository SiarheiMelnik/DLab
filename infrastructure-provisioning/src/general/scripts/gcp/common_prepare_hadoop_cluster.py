#!/usr/bin/python

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

import json
import time
from fabric.api import *
from dlab.fab import *
from dlab.meta_lib import *
from dlab.actions_lib import *
import sys
import os
import uuid
import logging
from Crypto.PublicKey import RSA


if __name__ == "__main__":
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO,
                        filename=local_log_filepath)
    try:
        os.environ['exploratory_name']
    except:
        os.environ['exploratory_name'] = ''
    if os.path.exists('/response/.dataproc_creating_' + os.environ['exploratory_name']):
        time.sleep(30)

    # edge_status = GCPMeta().get_instance_status(os.environ['conf_service_base_name'] + "-" +
    #                                             os.environ['edge_user_name'] + '-edge')
    # if edge_status != 'RUNNING':
    #     logging.info('ERROR: Edge node is unavailable! Aborting...')
    #     print 'ERROR: Edge node is unavailable! Aborting...'
    #     ssn_hostname = GCPMeta().get_private_ip_address(os.environ['conf_service_base_name'] + '-ssn')
    #     put_resource_status('edge', 'Unavailable', os.environ['ssn_dlab_path'], os.environ['conf_os_user'], ssn_hostname)
    #     append_result("Edge node is unavailable")
    #     sys.exit(1)

    print 'Generating infrastructure names and tags'
    dataproc_conf = dict()
    dataproc_conf['uuid'] = str(uuid.uuid4())[:5]
    try:
        dataproc_conf['exploratory_name'] = os.environ['exploratory_name']
    except:
        dataproc_conf['exploratory_name'] = ''
    try:
        dataproc_conf['computational_name'] = os.environ['computational_name']
    except:
        dataproc_conf['computational_name'] = ''
    dataproc_conf['service_base_name'] = os.environ['conf_service_base_name']
    dataproc_conf['key_name'] = os.environ['conf_key_name']
    dataproc_conf['key_path'] = os.environ['conf_key_dir'] + os.environ['conf_key_name'] + '.pem'
    dataproc_conf['region'] = os.environ['gcp_region']
    dataproc_conf['zone'] = os.environ['gcp_zone']
    dataproc_conf['subnet'] = os.environ['gcp_subnet_name']
    dataproc_conf['cluster_name'] = dataproc_conf['service_base_name'] + '-' + os.environ['edge_user_name'] + '-dp-' + dataproc_conf['exploratory_name'] + '-' + dataproc_conf['computational_name'] + '-' + dataproc_conf['uuid']
    dataproc_conf['cluster_tag'] = dataproc_conf['service_base_name'] + '-' + os.environ['edge_user_name'] + '-dp'
    dataproc_conf['bucket_name'] = (dataproc_conf['service_base_name'] + '-ssn-bucket').lower().replace('_', '-')
    dataproc_conf['release_label'] = os.environ['dataproc_version']
    dataproc_conf['cluster_label'] = {os.environ['notebook_instance_name']: "not-configured"}

    print "Will create exploratory environment with edge node as access point as following: " + \
          json.dumps(dataproc_conf, sort_keys=True, indent=4, separators=(',', ': '))
    logging.info(json.dumps(dataproc_conf))

    local("echo Waiting for changes to propagate; sleep 10")

    dataproc_cluster = json.loads(open('/root/templates/dataproc_cluster.json').read().decode('utf-8-sig'))
    dataproc_cluster['projectId'] = os.environ['gcp_project_id']
    dataproc_cluster['clusterName'] = dataproc_conf['cluster_name']
    dataproc_cluster['labels'] = dataproc_conf['cluster_label']
    dataproc_cluster['config']['gceClusterConfig']['zoneUri'] = dataproc_conf['zone']
    dataproc_cluster['config']['gceClusterConfig']['subnetworkUri'] = dataproc_conf['subnet']
    dataproc_cluster['config']['masterConfig']['machineTypeUri'] = os.environ['dataproc_master_instance_type']
    dataproc_cluster['config']['workerConfig']['machineTypeUri'] = os.environ['dataproc_slave_instance_type']
    dataproc_cluster['config']['workerConfig']['numInstances'] = int(os.environ['dataproc_instance_count']) - 1
    dataproc_cluster['config']['softwareConfig']['imageVersion'] = dataproc_conf['release_label']
    ssh_user = os.environ['conf_os_user']
    ssh_user_pubkey = open(os.environ['conf_key_dir'] + os.environ['edge_user_name'] + '.pub').read()
    key = RSA.importKey(open(dataproc_conf['key_path'], 'rb').read())
    ssh_admin_pubkey = key.publickey().exportKey("OpenSSH")
    dataproc_cluster['config']['gceClusterConfig']['metadata']['ssh-keys'] = '{0}:{1}\n{0}:{2}'.format(ssh_user, ssh_user_pubkey, ssh_admin_pubkey)
    dataproc_cluster['config']['gceClusterConfig']['tags'][0] = dataproc_conf['cluster_tag']

    try:
        logging.info('[Creating Dataproc Cluster]')
        print '[Creating Dataproc Cluster]'
        params = "--region {0} --bucket {1} --params '{2}'".format(dataproc_conf['region'], dataproc_conf['bucket_name'], json.dumps(dataproc_cluster))

        try:
            local("~/scripts/{}.py {}".format('dataproc_create', params))
        except:
            traceback.print_exc()
            raise Exception

        keyfile_name = "/root/keys/{}.pem".format(dataproc_conf['key_name'])
        # local('rm /response/.dataproc_creating_' + os.environ['exploratory_name'])
    except Exception as err:
        append_result("Failed to create Dataproc Cluster.", str(err))
        # local('rm /response/.dataproc_creating_' + os.environ['exploratory_name'])
        sys.exit(1)

    try:
        logging.info('[SUMMARY]')
        print '[SUMMARY]'
        print "Service base name: " + dataproc_conf['service_base_name']
        print "Cluster name: " + dataproc_conf['cluster_name']
        print "Key name: " + dataproc_conf['key_name']
        print "Region: " + dataproc_conf['region']
        print "Zone: " + dataproc_conf['zone']
        print "Subnet: " + dataproc_conf['subnet']
        print "Dataproc version: " + dataproc_conf['release_label']
        print "Dataproc master node shape: " + os.environ['dataproc_master_instance_type']
        print "Dataproc slave node shape: " + os.environ['dataproc_slave_instance_type']
        print "Instance count: " + os.environ['dataproc_instance_count']
        # print "Notebook IP address: " + dataproc_conf['notebook_ip']
        print "Bucket name: " + dataproc_conf['bucket_name']
        with open("/root/result.json", 'w') as result:
            res = {"hostname": dataproc_conf['cluster_name'],
                   "key_name": dataproc_conf['key_name'],
                   "user_own_bucket_name": dataproc_conf['bucket_name'],
                   "Action": "Create new Dataproc cluster"}
            print json.dumps(res)
            result.write(json.dumps(res))
    except:
        print "Failed writing results."
        sys.exit(1)

    sys.exit(0)