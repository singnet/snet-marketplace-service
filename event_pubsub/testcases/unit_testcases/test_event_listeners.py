import unittest
import unittest
from unittest.mock import patch, Mock
from datetime import datetime

from event_pubsub.listeners.event_listeners import EventListener, RegistryEventListener, AirdropEventListener, \
    OccamAirdropEventListener, ConverterAGIXEventListener, ConverterNTXEventListener


class TestBlockchainEventSubscriber(unittest.TestCase):
    def setUp(self):
        pass

    @patch('event_pubsub.event_repository.EventRepository.read_registry_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event')
    def test_event_publisher_success(self, mock_push_event, mock_read_registry_event):
        mock_read_registry_event.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'ServiceCreated',
                                                  'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'freecall\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                                                  'processed': 0,
                                                  'transactionHash': "b'~\\xb5\\x0c\\x93\\xe7y\\xc1\\x9d\\xf2I\\xef3\\xc6H\\x16\\xbd\\xab \\xa4\\xb5\\r\\xaau5eb\\x82B\\xe0\\x1c\\xf7\\xdd'",
                                                  'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                  'row_updated': '2019-10-31 09:44:00',
                                                  'row_created': '2019-10-31 09:44:00'}]
        mock_push_event.return_value = {"statusCode": 200}

        error_map, success_list = RegistryEventListener().listen_and_publish_registry_events()
        assert success_list == [526]

    @patch('event_pubsub.event_repository.EventRepository.read_registry_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event', side_effect=Exception('Test Error'))
    def test_event_publisher_failure(self, mock_lambda_handler, mock_read_registry_event):
        mock_read_registry_event.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'ServiceCreated',
                                                  'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'freecall\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                                                  'processed': 0,
                                                  'transactionHash': "b'~\\xb5\\x0c\\x93\\xe7y\\xc1\\x9d\\xf2I\\xef3\\xc6H\\x16\\xbd\\xab \\xa4\\xb5\\r\\xaau5eb\\x82B\\xe0\\x1c\\xf7\\xdd'",
                                                  'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                  'row_updated': '2019-10-31 09:44:00',
                                                  'row_created': '2019-10-31 09:44:00'}]

        mock_lambda_handler.return_value = {"statusCode": 500}

        error_map, success_list = RegistryEventListener().listen_and_publish_registry_events()
        assert error_map == {526: {'error_code': 500, 'error_message': 'for listener arn:aws got error Test Error'}}

    @patch('event_pubsub.event_repository.EventRepository.read_airdrop_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event')
    def test_airdrop_event_publisher_success(self, mock_push_event, mock_read_airdrop_event):
        now = datetime.utcnow()
        mock_read_airdrop_event.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'Claim',
                                                 'json_str': "{'authorizer': '0xD93209FDC420e8298bDFA3dBe340F366Faf1E7bc', 'claimer': '0x35d603B1433C9fFf79B61c905b07822684834542', 'amount': 0, 'airDropId': 1, 'airDropWindowId': 1}",
                                                 'processed': 0,
                                                 'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45a",
                                                 'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                 'row_updated': now,
                                                 'row_created': now}]
        mock_push_event.return_value = {"statusCode": 200}

        error_map, success_list = AirdropEventListener().listen_and_publish_airdrop_events()
        assert success_list == [526]

    @patch('event_pubsub.event_repository.EventRepository.read_converter_agix_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event')
    def test_converter_agix_event_publisher_success(self, mock_push_event, mock_read_converter_agix_events):
        now = datetime.utcnow()
        mock_read_converter_agix_events.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'ConversionOut',
                                                         'json_str': "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}",
                                                         'processed': 0,
                                                         'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45a",
                                                         'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                         'row_updated': now,
                                                         'row_created': now},
                                                        {'row_id': 527, 'block_no': 6247993, 'event': 'ConversionIn',
                                                         'json_str': "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}",
                                                         'processed': 0,
                                                         'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45b",
                                                         'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                         'row_updated': now,
                                                         'row_created': now}
                                                        ]
        mock_push_event.return_value = {"statusCode": 200}

        error_map, success_list = ConverterAGIXEventListener().listen_and_publish_converter_agix_events()
        assert success_list == [526, 527]

    @patch('event_pubsub.event_repository.EventRepository.read_converter_ntx_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event')
    def test_converter_ntx_event_publisher_success(self, mock_push_event, mock_read_converter_ntx_events):
        now = datetime.utcnow()
        mock_read_converter_ntx_events.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'ConversionOut',
                                                        'json_str': "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}",
                                                        'processed': 0,
                                                        'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45a",
                                                        'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                        'row_updated': now,
                                                        'row_created': now},
                                                       {'row_id': 527, 'block_no': 6247993, 'event': 'ConversionIn',
                                                        'json_str': "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}",
                                                        'processed': 0,
                                                        'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45b",
                                                        'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                        'row_updated': now,
                                                        'row_created': now}
                                                       ]
        mock_push_event.return_value = {"statusCode": 200}

        error_map, success_list = ConverterNTXEventListener().listen_and_publish_converter_ntx_events()
        assert success_list == [526, 527]

    @patch('event_pubsub.event_repository.EventRepository.read_airdrop_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event', side_effect=Exception('Test Error'))
    def test_airdrop_event_publisher_failure(self, mock_lambda_handler, mock_read_airdrop_event):
        now = datetime.utcnow()
        mock_read_airdrop_event.return_value = [{'row_id': 526, 'block_no': 6247992, 'event': 'Claim',
                                                 'json_str': "{'authorizer': '0xD93209FDC420e8298bDFA3dBe340F366Faf1E7bc', 'claimer': '0x35d603B1433C9fFf79B61c905b07822684834542', 'amount': 0, 'airDropId': 1, 'airDropWindowId': 1}",
                                                 'processed': 0,
                                                 'transactionHash': "0x62a730ef8a537d09ee9064da3f57ad3ff3027399c91daa531e41a6c4e10af45a",
                                                 'logIndex': '43', 'error_code': 200, 'error_msg': '',
                                                 'row_updated': now,
                                                 'row_created': now}]

        mock_lambda_handler.return_value = {"statusCode": 500}

        error_map, success_list = AirdropEventListener().listen_and_publish_airdrop_events()
        assert error_map == {526: {'error_code': 500, 'error_message': 'for listener arn:aws got error Test Error'}}

    @patch('event_pubsub.event_repository.EventRepository.read_occam_airdrop_events')
    @patch('event_pubsub.listeners.listener_handlers.LambdaArnHandler.push_event', side_effect=Exception('Test Error'))
    def test_airdrop_event_publisher_failure(self, mock_lambda_handler, mock_read_occam_airdrop_event):
        now = datetime.utcnow()
        mock_read_occam_airdrop_event.return_value = [{'row_id': 1, 'block_no': 11624692, 'event': 'Claim',
                                                       'json_str': "{'authorizer': '0xD93209FDC420e8298bDFA3dBe340F366Faf1E7bc', 'claimer': '0x176133a958449C28930970989dB5fFFbEdd9F447', 'amount': 1000, 'airDropId': 2, 'airDropWindowId': 4}",
                                                       'processed': 0,
                                                       'transactionHash': "0x805bec29d6f72eea170a748e4bc14e21bfce9f50c229db7ba006bccfafbded34",
                                                       'logIndex': '2', 'error_code': 0, 'error_msg': '',
                                                       'row_updated': now,
                                                       'row_created': now}]

        mock_lambda_handler.return_value = {"statusCode": 500}

        error_map, success_list = OccamAirdropEventListener().listen_and_publish_occam_airdrop_events()
        assert error_map == {1: {'error_code': 500, 'error_message': 'for listener arn:aws got error Test Error'}}
