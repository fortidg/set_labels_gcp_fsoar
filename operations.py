""" Copyright start
  Copyright (C) 2008 - 2022 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import os
import json
import sys
import google.cloud.compute_v1 as compute
import google.api_core.retry as retry
from google.api_core.exceptions import NotFound
from google.oauth2 import service_account
from connectors.core.connector import get_logger, ConnectorError
from connectors.cyops_utilities.builtins import download_file_from_cyops

logger = get_logger('google-cloud-compute')


class GoogleCloudCompute(object):

    def __init__(self, config):
        self.client_details = dict()
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        try:
            cert_file_iri = config.get('auth_file').get('@id')
            filename = download_file_from_cyops(cert_file_iri).get('cyops_file_path')
            file_data = os.path.join('/tmp/', filename)
            self.credentials = service_account.Credentials.from_service_account_file(file_data, scopes=scopes)
            self.p_id = self.credentials.project_id
        except Exception as err:
            logger.exception("{0}".format(str(err)))
            raise ConnectorError("{0}".format(str(err)))

    def create_clients(self):
        try:
            image_client = compute.ImagesClient(credentials=self.credentials)
            ins_client = compute.InstancesClient(credentials=self.credentials)
            zo_client = compute.ZoneOperationsClient(credentials=self.credentials)
            mt_client = compute.MachineTypesClient(credentials=self.credentials)
            nw_client = compute.NetworksClient(credentials=self.credentials)
            add_client = compute.AddressesClient(credentials=self.credentials)
            go_client = compute.GlobalOperationsClient(credentials=self.credentials)
            ro_client = compute.RegionOperationsClient(credentials=self.credentials)
            ga_client = compute.GlobalAddressesClient(credentials=self.credentials)
            disks_client = compute.DisksClient(credentials=self.credentials)
            dt_client = compute.DiskTypesClient(credentials=self.credentials)
            ig_client = compute.InstanceGroupsClient(credentials=self.credentials)
            reg_client = compute.RegionsClient(credentials=self.credentials)
            zone_client = compute.ZonesClient(credentials=self.credentials)
            f_client = compute.FirewallsClient(credentials=self.credentials)
            snap_client = compute.SnapshotsClient(credentials=self.credentials)
            proj_client = compute.ProjectsClient(credentials=self.credentials)
            self.client_details['images_client'] = image_client
            self.client_details['instances_client'] = ins_client
            self.client_details['zone_operations_client'] = zo_client
            self.client_details['machine_types_client'] = mt_client
            self.client_details['networks_client'] = nw_client
            self.client_details['addresses_client'] = add_client
            self.client_details['global_operations_client'] = go_client
            self.client_details['region_operations_client'] = ro_client
            self.client_details['global_addresses_client'] = ga_client
            self.client_details['disks_client'] = disks_client
            self.client_details['disk_types_client'] = dt_client
            self.client_details['instance_groups_client'] = ig_client
            self.client_details['regions_client'] = reg_client
            self.client_details['zones_client'] = zone_client
            self.client_details['firewalls_client'] = f_client
            self.client_details['snapshots_client'] = snap_client
            self.client_details['projects_client'] = proj_client
        except Exception as e:
            logger.exception(
                'Failed to get clients. Please check the service account json contents for authentication.')
            raise ConnectorError('Error: {0}'.format(e))

    def make_client_call(self, client_types, health_check=False):
        clients = dict()
        if not self.client_details:
            logger.info("Creating different clients.")
            self.create_clients()
        if health_check and not self.client_details:
            logger.error("Failed to create clients. Make sure the provided credentials are correct.")
            raise ConnectorError("Connector is not available. Health check failed.")
        for typ in client_types:
            clients[typ] = self.client_details[typ]
        return clients
    @retry.Retry()

    def set_labels(self, params):
        zone = params.get('zone')
        instance_name = params.get('instance_name')
        client_types = ['instances_client']
        clients = self.make_client_call(client_types)
        ins_client = clients[client_types[0]]
        request = compute.ListInstancesRequest(
            project=self.p_id, zone=zone)
        instances = ins_client.list(request=request)
        data_res = []
        for instance in instances:
            if instance.name == instance_name:
                data_res_item = {
                    'name': instance.name,
                    'zone': instance.zone,
                    'labels': instance.labels,
                    'label_fingerprint': instance.label_fingerprint
                }
                data_res.append(data_res_item)
                # Add a label to the instance
                zone = params.get('zone')
                project = self.p_id
                labels = {params.get('new_key'): params.get('new_value')}
                instance_name = params.get('instance_name')
                fingerprint = data_res_item['label_fingerprint']
                request = compute.SetLabelsInstanceRequest(
                    project=project,
                    zone=zone,
                    instance=instance_name,
                    instances_set_labels_request_resource=compute.InstancesSetLabelsRequest(
                        labels=labels,
                        label_fingerprint=fingerprint
                    )
                )
                ins_client.set_labels(request=request)
        return data_res
    
    
            
            

def _run_operation(config, params):
    compute_obj = GoogleCloudCompute(config)
    command = getattr(GoogleCloudCompute, params['operation'])
    response = command(compute_obj, params)
    return response


def _check_health(config):
    compute_obj = GoogleCloudCompute(config)
    logger.info('Checking Health check.')
    return compute_obj.make_client_call(['instances_client'], True)

