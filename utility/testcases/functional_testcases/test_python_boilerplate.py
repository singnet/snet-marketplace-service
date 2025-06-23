import unittest

from utility.application.services.stubs_generator_service import StubsGeneratorService
from utility.settings import settings
from utility.constants import PYTHON_BOILERPLATE_TEMPLATE


class TestPythonBoilerplate(unittest.TestCase):

    def test_boilerplate_content(self):
        for content_file in PYTHON_BOILERPLATE_TEMPLATE:
            context = StubsGeneratorService._prepare_data(PYTHON_BOILERPLATE_TEMPLATE[content_file]["content"],
                                                          "test_org_id", "test_service_id")
            context = context.replace('\n', '')
            if content_file == "requirement":
                assert context == "snet-sdk"
            if content_file == "readme":
                assert context == "Follow below instructions to setup dependencies :1.Create virtual environment   " \
                                                    "Once boilerplate is downloaded cd into the test_service_id-boilerplate folder and execute below commands   " \
                                                    "For unix/macOS:      -sudo apt-get install python3-venv      -sudo python3 -m venv venv      " \
                                                    "-source ./venv/bin/activate   For Windows:      " \
                                                    "-py -m pip install --user virtualenv      -py -m venv venv      " \
                                                    "-.\\venv\\Scripts\\activate2.Run following command to install dependencies   " \
                                                    "- pip install -r requirement.txt3.Replace appropriate values in config.py, service.py and run below command to invoke service   " \
                                                    "- python service.py"
            if content_file == "config":
                assert context == f'PRIVATE_KEY = "<your wallet\'s private key>"ETH_RPC_ENDPOINT = "https://{settings.network.networks[settings.network.id].name}.infura.io/v3/<your infura key>"ORG_ID = "test_org_id"SERVICE_ID = "test_service_id"'
            if content_file == "service":
                expected_context = """
from snet import sdk
import config

def main():
    sdk_config = sdk.config.Config(private_key = config.PRIVATE_KEY, 
                               eth_rpc_endpoint = config.ETH_RPC_ENDPOINT)

    snet_sdk = sdk.SnetSDK(sdk_config)
    service_client = snet_sdk.create_service_client(org_id=config.ORG_ID,
                                                    service_id=config.SERVICE_ID)

    arguments = {...} # insert method arguments here
    try:
        response = service_client.call_rpc("<METHOD_NAME>", "<MESSAGE_NAME>", **arguments) # replace METHOD_NAME and MESSAGE_NAME
        print(f"Service invoked successfully :: response :: {response}")
    except Exception as e:
        print(f"Exception when invoking a service :: {e}")


if __name__ == "__main__":
    main()
""".replace('\n', '')
                assert context == expected_context