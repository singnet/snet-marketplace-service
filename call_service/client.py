import glob
from os.path import dirname, basename, isfile, join
from snet_sdk import SnetSDK

from config.config import config
from stub import *


class Client:
    def __init__(self, dapp_user_address):
        self.mapping = {'snet': {'example-service': {'stub': example_service_pb2_grpc.CalculatorStub}}}
        config["dapp_user_address"] = dapp_user_address        
        self.sdk = SnetSDK(config)

    def call_service(self, user_address, org_id, service_id, method, input):
        """ Method to invoke AI service for given org_id, service_id and user_address.
            Using python-sdk to call the
        """
        try:
            service_client = self.sdk.create_service_client(org_id, service_id,
                                                            self.mapping[org_id][service_id]['stub'],
                                                            payment_channel_management_strategy=ProxyChannelManagementStrategy)

            obj = service_client.service

            result = getattr(obj, method)(input)
            return result
        except Exception as e:
            print(repr(e))
            raise e
