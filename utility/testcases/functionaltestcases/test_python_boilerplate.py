import unittest

from utility.application.handlers.proto_stubs_handler import generate_grpc_python_stubs
from utility.config import NETWORKS, NETWORK_ID
from utility.application.services.python_boilerplate_service import prepare_data
from utility.constants import PYTHON_BOILERPLATE_TEMPLATE


class TestPythonBoilerplate(unittest.TestCase):
    def setUp(self):
        pass

    def test_boilerplate_content(self):
        for content in PYTHON_BOILERPLATE_TEMPLATE:
            context = prepare_data(PYTHON_BOILERPLATE_TEMPLATE[content]["content"], "test_org_id", "test_service_id",
                                   "test_stub_name")
            context = context.replace('\n', '')
            if content == "requirement":
                assert context == "snet.sdksnet-cli"
            if content == "readme":
                assert context == "Follow below instructions to setup dependencies :1.Create virtual environment   " \
                                                    "Once boilerplate is downloaded cd into the test_service_id-boilerplate folder and execute below commands   " \
                                                    "For unix/macOS:      -sudo apt-get install python3-venv      -sudo python3 -m venv venv      " \
                                                    "-source ./venv/bin/activate   For Windows:      " \
                                                    "-py -m pip install --user virtualenv      -py -m venv venv      " \
                                                    "-.\\venv\\Scripts\\activate2.Run following command to install dependencies   " \
                                                    "- pip install -r requirement.txt3.Replace appropriate values in config.py, service.py and run below command to invoke service   " \
                                                    "- python service.py"
            if content == "config":
                infura_link = NETWORKS[NETWORK_ID]["http_provider"]
                assert context == f'PRIVATE_KEY = "<your wallet\'s private key>"ETH_RPC_ENDPOINT = "{infura_link}/v3/<your infura key>"ORG_ID = "test_org_id"SERVICE_ID = "test_service_id"'
            if content == "service":
                assert context == 'from snet.sdk import SnetSDKimport configimport test_stub_name_pb2import test_stub_name_pb2_grpcdef invoke_service():   ' \
                                  'snet_config = {"private_key": config.PRIVATE_KEY, "eth_rpc_endpoint": config.ETH_RPC_ENDPOINT}   ' \
                                  'sdk = SnetSDK(config=snet_config)   service_client = sdk.create_service_client(      org_id=config.ORG_ID,      ' \
                                  'service_id=config.SERVICE_ID,      service_stub= test_stub_name_pb2_grpc.service_stub # replace service_stub   )   ' \
                                  'request = test_stub_name_pb2.input_method(arguments) # replace input_method and arguments   ' \
                                  'response = service_client.service.service_method(request) # replace service_method   ' \
                                  'print(f"service invoked successfully :: response :: {response}")invoke_service() ' \
                                  '# call invoke service method'