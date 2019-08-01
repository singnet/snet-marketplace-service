import base64
import json
import os
import time
import ipfsapi
import web3.eth
import sys
import web3.utils.events
from web3 import Web3

from common.constant import IPFS_URL, NETWORKS, MPE_EVTS, REG_EVTS, REG_CNTRCT_PATH, MPE_CNTRCT_PATH, REG_ADDR_PATH
from common.constant import MPE_ADDR_PATH
from common.error import ErrorHandler
from parse_events.handle_contracts_db import HandleContractsDB
from common.utils import Utils


class HandleContracts:
    def __init__(self, net_id):
        self.net_id = net_id
        self.mpe_cntrct = None
        self.mpe_cntrct_addr = None
        self.reg_cntrct = None
        self.reg_cntrct_addr = None
        self.err_obj = ErrorHandler()
        self.db_obj = HandleContractsDB(err_obj=self.err_obj, net_id=net_id)
        self.util_obj = Utils()

    def _init_w3(self):
        try:
            self.web3_pvdr = NETWORKS[self.net_id]['ws_provider']
            self.w3 = Web3(web3.providers.WebsocketProvider(self.web3_pvdr))
        except KeyError as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            raise KeyError(self.err_obj.get_err_msg(err_cd=1001), repr(e))
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            raise Exception(self.err_obj.get_err_msg(err_cd=1002), repr(e))

    def _loadContract(self, path):
        with open(path) as f:
            contract = json.load(f)
        return contract

    def _rd_cntrct_addr(self, path, key):
        contract = self._loadContract(path)
        return Web3.toChecksumAddress(contract[str(self.net_id)][key])

    def _contrct_inst(self, contrct, addr):
        return self.w3.eth.contract(abi=contrct, address=addr)

    def _read_ipfs_node(self, ipfs_hash):
        ipfs_conn = ipfsapi.connect(
            host=IPFS_URL['url'], port=IPFS_URL['port'])
        ipfs_data = ipfs_conn.cat(ipfs_hash)
        return json.loads(ipfs_data.decode('utf8'))

    def _hex_to_str(self, hex_str):
        return Web3.toText(hex_str).rstrip("\u0000")

    def _process_organization_event(self, org_id, org_data):
        print('_process_organization_event::org_data: ', org_data)
        org_metadata_uri = self._hex_to_str(org_data[2])[7:]
        ipfs_data = self._read_ipfs_node(org_metadata_uri)
        self.db_obj.process_org_data(org_id=org_id, org_data=org_data, ipfs_data=ipfs_data)

    def _process_srvc_evts(self, srvc_data, inst_cntrct):
        print('process_srvc_evts::srvc_data: ', srvc_data)
        org_id = self._hex_to_str(srvc_data['orgId'])
        service_id = self._hex_to_str(srvc_data['serviceId'])
        metadata_uri = self._hex_to_str(srvc_data['metadataURI'])[7:]
        ipfs_data = self._read_ipfs_node(metadata_uri)
        tags_data = self._fetch_tags(
            inst_cntrct=inst_cntrct, org_id_hex=srvc_data['orgId'], srvc_id_hex=srvc_data['serviceId'])
        self.db_obj.process_srvc_data(org_id=org_id, service_id=service_id, ipfs_hash=metadata_uri,
                                      ipfs_data=ipfs_data, tags_data=tags_data)

    def _fetch_tags(self, inst_cntrct, org_id_hex, srvc_id_hex):
        tags_data = inst_cntrct.functions.getServiceRegistrationById(
            org_id_hex, srvc_id_hex).call()
        return tags_data

    def __handle_events(self, evt_data):
        print('_handle_events::evt_data: ', evt_data['event'], 'start')
        event = evt_data['event']

        if event in MPE_EVTS:
            self.mpe_cntrct = self._loadContract(
                MPE_CNTRCT_PATH) if self.mpe_cntrct == None else self.mpe_cntrct
            self.mpe_cntrct_addr = self._rd_cntrct_addr(MPE_ADDR_PATH,
                                                        'address') if self.mpe_cntrct_addr == None else self.mpe_cntrct_addr

            inst_cntrct = self._contrct_inst(
                contrct=self.mpe_cntrct, addr=self.mpe_cntrct_addr)
            if event == 'ChannelOpen':
                self.db_obj.create_channel(evt_data['returnValues'])
            elif event in MPE_EVTS:
                channel_id = int(evt_data['returnValues']['channelId'])
                channel_data = inst_cntrct.functions.channels(
                    channel_id).call()
                group_id = base64.b64encode(channel_data[4]).decode('utf8')
                self.db_obj.update_channel(
                    channel_id=channel_id, group_id=group_id, channel_data=channel_data)
        elif event in REG_EVTS:
            self.reg_cntrct = self._loadContract(
                REG_CNTRCT_PATH) if self.reg_cntrct == None else self.reg_cntrct
            self.reg_cntrct_addr = self._rd_cntrct_addr(REG_ADDR_PATH,
                                                        'address') if self.reg_cntrct_addr == None else self.reg_cntrct_addr
            inst_cntrct = self._contrct_inst(
                contrct=self.reg_cntrct, addr=self.reg_cntrct_addr)
            reg_data = evt_data['returnValues']
            org_id_hex = reg_data['orgId']
            org_id = self._hex_to_str(org_id_hex)
            print('org_id: ', org_id)
            if event in ['OrganizationCreated', 'OrganizationModified']:
                org_data = inst_cntrct.functions.getOrganizationById(
                    org_id_hex).call()
                print('__handle_events::org_data: ', org_data)
                self._process_organization_event(org_id=org_id, org_data=org_data)
            elif event == 'OrganizationDeleted':
                self.db_obj.del_org(org_id)
            elif event in ['ServiceCreated', 'ServiceMetadataModified']:
                self._process_srvc_evts(
                    srvc_data=reg_data, inst_cntrct=inst_cntrct)
            elif event == 'ServiceTagsModified':
                srvc_id_hex = reg_data['serviceId']
                srvc_id = self._hex_to_str(srvc_id_hex)
                self.db_obj.update_tags(org_id=org_id, service_id=srvc_id, tags_data=self._fetch_tags(
                    inst_cntrct=inst_cntrct, org_id_hex=org_id_hex, srvc_id_hex=srvc_id_hex))
            elif event == 'ServiceDeleted':
                self.db_obj.del_srvc(
                    org_id=org_id, service_id=self._hex_to_str(reg_data['serviceId']))
        print('_handle_events::evt_data: ', evt_data['event'], 'end')
        return True

    def _process_events(self, evts_data, type):
        for evt_data in evts_data:
            try:
                print('process_events::row_id: ',
                      evt_data['row_id'], '|', type, '|', evt_data['block_no'])
                handled = self.__handle_events(
                    json.loads(evt_data['json_str']))
                if handled:
                    self.db_obj.updt_raw_evts(
                        evt_data['row_id'], type, err_cd=0, err_msg='')
            except Exception as e:
                err_msg = self.err_obj.log_err_msg(
                    err=e, fn_nme='_process_events')
                self.util_obj.report_slack(type=1, slack_msg=err_msg)
                print('writing error for row_id: ', evt_data['row_id'])
                self.db_obj.updt_raw_evts(
                    evt_data['row_id'], type, err_cd=1, err_msg=err_msg)

    def handle_contract(self):
        try:
            self._init_w3()
            self._process_events(self.db_obj.read_registry_events(), 'REG')
            self._process_events(self.db_obj.read_mpe_events(), 'MPE')
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            self.err_obj.log_err_msg(err=e, fn_nme='handle_contract')
        finally:
            if self.db_obj.repo.connection is not None:
                self.db_obj.repo.connection.close()


if __name__ == '__main__':
    net_id = int(sys.argv[1])
    os.environ["NETWORK_ID"] = str(net_id)
    obj = HandleContracts(net_id=net_id)
    obj.util_obj.report_slack(
        type=0, slack_msg="start of the parse_events service")
    while True:
        obj.handle_contract()
        time.sleep(20)
        obj = HandleContracts(net_id=net_id)
