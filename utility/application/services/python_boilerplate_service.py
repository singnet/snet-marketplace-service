import os
from common.utils import create_text_file
from utility.config import NETWORKS, NETWORK_ID


def prepare_boilerplate_content(org_id, service_id, stub_name):
    content = {
        "requirement": {
            "extension": ".txt",
            "content": "snet.sdk\nsnet-cli"
        },
        "readme": {
            "extension": ".txt",
            "content": "Follow below instructions to setup dependencies :\n"\
            "1.Create virtual environment\n"\
            f"   Once boilerplate is downloaded cd into the {service_id}-boilerplate folder and execute below commands\n"\
            f"   For unix/macOS:\n"\
            f"      -sudo apt-get install python3-venv\n"\
            f"      -sudo python3 -m venv venv\n"\
            f"      -source ./venv/bin/activate\n"\
            f"   For Windows:\n"\
            f"      -py -m pip install --user virtualenv\n"\
            f"      -py -m venv venv\n"\
            f"      -.\\venv\\Scripts\\activate\n"\
            "2.Run following command to install dependencies\n"\
            "   - pip install -r requirement.txt\n"\
            "3.Replace appropriate values in config.py, service.py and run below command to invoke service"\
            "   - python service.py"\
        },
        "config": {
            "extension": ".py",
            "content": 'PRIVATE_KEY = "<your wallet\'s private key>"\n' \
                       f'ETH_RPC_ENDPOINT = "{NETWORKS[NETWORK_ID]["http_provider"]}/v3/<your infura key>"\n'
                       f'ORG_ID = "{org_id}"\n' \
                       f'SERVICE_ID = "{service_id}"\n'
        },
        "service": {
            "extension": ".py",
            "content":
                'from snet.sdk import SnetSDK\n' \
                'import config\n' \
                f'import {stub_name}_pb2\n' \
                f'import {stub_name}_pb2_grpc\n\n' \
                'def invoke_service():\n' \
                '   snet_config = {"private_key": config.PRIVATE_KEY, "eth_rpc_endpoint": config.ETH_RPC_ENDPOINT}\n' \
                '   sdk = SnetSDK(config=snet_config)\n' \
                '   service_client = sdk.create_service_client(\n' \
                f'      org_id=config.ORG_ID,\n' \
                f'      service_id=config.SERVICE_ID,\n' \
                f'      service_stub= {stub_name}_pb2_grpc.service_stub # replace service_stub\n' \
                f'  )\n' \
                f'   request = {stub_name}_pb2.input_method(arguments) # replace input_method and arguments\n' \
                '   response = service_client.service.service_method(request) # replace service_method\n'
                '   print(f"service invoked successfully :: response :: {response}")\n\n\n'
                'invoke_service() # call invoke service method'
        }
    }
    return content


def prepare_boilerplate_template(target_location, stub_name, org_id, service_id):
    template_content = prepare_boilerplate_content(org_id=org_id, service_id=service_id, stub_name=stub_name)
    for content in template_content:
        create_text_file(
            target_path=f"{target_location}/{content}{template_content[content]['extension']}",
            context=template_content[content]["content"]
        )
    return target_location
