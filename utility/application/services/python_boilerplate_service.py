from common.utils import create_text_file
from utility.constants import PYTHON_BOILERPLATE_TEMPLATE


def prepare_boilerplate_template(target_location, org_id, service_id, stub_name):
    for content in PYTHON_BOILERPLATE_TEMPLATE:
        context = prepare_data(PYTHON_BOILERPLATE_TEMPLATE[content]["content"], org_id, service_id, stub_name)
        create_text_file(
            target_path=f"{target_location}/{content}{PYTHON_BOILERPLATE_TEMPLATE[content]['extension']}",
            context=context
        )
    return target_location


def prepare_data(data, org_id, service_id, stub_name):
    replace_keys = {
        ("org_id_placeholder", org_id),
        ("service_id_placeholder", service_id),
        ("stub_placeholder", stub_name)
    }
    for key in replace_keys:
        data = data.replace(key[0], key[1])
    return data
