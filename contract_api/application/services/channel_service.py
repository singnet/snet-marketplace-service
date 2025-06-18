


class ChannelService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_util = Utils()
        self.blockchain_util = BlockChainUtil(provider_type="WS_PROVIDER", provider=NETWORKS[NETWORK_ID]["ws_provider"])

    # is used in handler
    def get_channels(self, user_address):
        last_block_no = self.blockchain_util.get_current_block_no()
        logger.info(f"got block number {last_block_no}")
        channel_details_query = "SELECT mc.channel_id, mc.sender, mc.recipient, mc.groupId as group_id, " \
                                "mc.balance_in_cogs, mc.pending, mc.nonce, mc.consumed_balance, mc.expiration, " \
                                "mc.signer, og.org_id, " \
                                "org.organization_name, IF(mc.expiration > %s, 'active','inactive') AS status, " \
                                "og.group_name, org.org_assets_url " \
                                "FROM mpe_channel AS mc JOIN org_group AS og ON mc.groupId = og.group_id " \
                                "JOIN organization AS org ON og.org_id = org.org_id WHERE mc.sender = %s "
        params = [last_block_no, user_address]
        channel_details = self.repo.execute(
            channel_details_query,
            params
        )
        self.obj_util.clean(channel_details)

        channel_details_response = {"wallet_address": user_address,
                                    "organizations": self._segregate_org_channel_details(channel_details)}

        return channel_details_response

    # is used in handler
    def update_consumed_balance(self, channel_id, signed_amount=None, org_id=None, service_id=None):
        mpe_repo = MPERepository(self.repo)
        channel = mpe_repo.get_mpe_channels(channel_id)
        if len(channel) != 0:
            channel = channel[0]
        else:
            raise Exception(f"Channel with id {channel_id} not found!")

        if signed_amount is None:
            signed_amount = self._get_channel_state_from_daemon(channel, org_id, service_id)
        mpe_repo.update_consumed_balance(channel_id, signed_amount)

        return {}

    def _segregate_org_channel_details(self, raw_channel_data):
        org_data = {}
        for channel_record in raw_channel_data:
            org_id = channel_record["org_id"]
            group_id = channel_record["group_id"]

            if org_id not in org_data:
                org_data[org_id] = {
                    "org_name": channel_record["organization_name"],
                    "org_id": org_id,
                    "hero_image": json.loads(channel_record["org_assets_url"]).get("hero_image", ""),
                    "groups": {}
                }
            if group_id not in org_data[org_id]["groups"]:
                org_data[org_id]["groups"][group_id] = {
                    "group_id": group_id,
                    "group_name": channel_record["group_name"],
                    "channels": []
                }

            channel = {
                "channel_id": channel_record["channel_id"],
                "recipient": channel_record["recipient"],
                'balance_in_cogs': channel_record['balance_in_cogs'],
                'consumed_balance': channel_record["consumed_balance"],
                'current_balance': str(decimal.Decimal(channel_record['balance_in_cogs']) - decimal.Decimal(
                    channel_record["consumed_balance"])),
                "pending": channel_record["pending"],
                "nonce": channel_record["nonce"],
                "expiration": channel_record["expiration"],
                "signer": channel_record["signer"],
                "status": channel_record["status"]
            }

            org_data[org_id]["groups"][group_id]["channels"].append(channel)

        for org_id in org_data:
            org_data[org_id]["groups"] = list(org_data[org_id]["groups"].values())

        return list(org_data.values())

    def _get_channel_state_from_daemon(self, channel, org_id, service_id):
        channel_id = channel["channel_id"]
        group_id = channel["groupId"]

        org_repo = ServiceRepository(self.repo)
        endpoint = org_repo.get_service_endpoints(org_id, service_id, group_id)
        if len(endpoint) != 0:
            endpoint = endpoint[0]
        else:
            raise Exception(f"Endpoint with org_id {org_id}, service_id {service_id} and group_id {group_id} not found!")
        endpoint = endpoint["endpoint"]

        signature, current_block_number = self._get_channel_state_signature(channel_id)
        if signature.startswith("0x"):
            signature = signature[2:]
        signed_amount = self._get_channel_state_via_grpc(endpoint, channel_id, signature, current_block_number)

        return signed_amount

    @staticmethod
    def _get_channel_state_signature(channel_id):
        body = {
            'channel_id': channel_id
        }

        payload = {
            "path": "/signer/state-service",
            "body": json.dumps(body),
            "httpMethod": "POST"
        }

        lambda_client = boto3.client('lambda', region_name = REGION_NAME)
        signature_response = lambda_client.invoke(
            FunctionName = SIGNER_SERVICE_ARN,
            InvocationType = 'RequestResponse',
            Payload = json.dumps(payload)
        )

        signature_response = json.loads(signature_response.get("Payload").read())
        if signature_response["statusCode"] != 200:
            raise Exception(f"Failed to create signature for {body}")
        signature_details = json.loads(signature_response["body"])["data"]
        return signature_details["signature"], signature_details["snet-current-block-number"]

    def _get_channel_state_via_grpc(self, endpoint, channel_id, signature, current_block_number):
        endpoint_object = urlparse(endpoint)
        if endpoint_object.port is None:
            channel_endpoint = endpoint_object.hostname
        else:
            channel_endpoint = f"{endpoint_object.hostname}:{endpoint_object.port}"

        if endpoint_object.scheme == "http":
            grpc_channel = grpc.insecure_channel(channel_endpoint)
        elif endpoint_object.scheme == "https":
            grpc_channel = grpc.secure_channel(channel_endpoint, grpc.ssl_channel_credentials(root_certificates = certificate))
        else:
            raise Exception(f"Invalid service endpoint {endpoint}")

        stub = state_service_pb2_grpc.PaymentChannelStateServiceStub(grpc_channel)
        request = state_service_pb2.ChannelStateRequest(
            channel_id = channel_id.to_bytes(4, "big"),
            signature = bytes.fromhex(signature),
            current_block = current_block_number
        )
        try:
            response = stub.GetChannelState(request)
        except Exception as e:
            logger.error(str(e))
            raise Exception(f"Failed to get channel state with id {channel_id} via grpc")

        return int.from_bytes(response.current_signed_amount, "big")