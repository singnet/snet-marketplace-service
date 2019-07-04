import glob
from os.path import dirname, basename, isfile, join
from snet_sdk import SnetSDK

from config.config import config
from stub import *
from proxy_channel_management_strategies.default import ProxyChannelManagementStrategy
from google.protobuf import json_format
from grpc_service_stub import mapping

class Client:
    def __init__(self, dapp_user_address):
        self.mapping = mapping
        config["dapp_user_address"] = dapp_user_address
        self.sdk = SnetSDK(config)

    def call_service(self, user_address, org_id, service_id, service_name, method, input):
        """ Method to invoke AI service for given org_id, service_id and user_address.
            Using python-sdk to call the
        """
        try:
            pb2 = self.mapping[org_id][service_id]['pb2']
            if service_name in getattr(pb2, "DESCRIPTOR").services_by_name.keys():
                pb2_grpc = self.mapping[org_id][service_id]['pb2_grpc']
                input_type = None
                output_type = None
                stub = service_name + "Stub"
                for rec in getattr(pb2, "_"+service_name.upper()).methods:
                    if rec.name==method:
                        input_type = rec.input_type.name
                        output_type = rec.output_type.fields
                service_client = self.sdk.create_service_client(
                    org_id, service_id, getattr(pb2_grpc, stub), payment_channel_management_strategy=ProxyChannelManagementStrategy)


                messageObj = json_format.Parse(input, getattr(pb2, input_type)())
                obj = service_client.service
                result = getattr(obj, method)(messageObj)
                return json_format.MessageToJson(result)
            else:
                raise Exception("Service %s is not supported under organization %s and service_id %s", service_name, org_id, service_id)
        except Exception as e:
            print(repr(e))
            raise e
