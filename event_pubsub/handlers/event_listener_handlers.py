import sys

sys.path.append('/opt')
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification
from common.exception_handler import exception_handler
from event_pubsub.config import NETWORK_ID, SLACK_HOOK
from event_pubsub.listeners.event_listeners import MPEEventListener, RFAIEventListener, RegistryEventListener, \
    TokenStakeEventListener, AirdropEventListener, OccamAirdropEventListener, ConverterAGIXEventListener, \
    ConverterNTXEventListener, ConverterRJVEventListener

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def registry_event_listener_handler(event, context):
    RegistryEventListener().listen_and_publish_registry_events()


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def mpe_event_listener_handler(event, context):
    MPEEventListener().listen_and_publish_mpe_events()


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def rfai_event_listener_handler(event, context):
    RFAIEventListener().listen_and_publish_rfai_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def token_stake_event_listener_handler(event, context):
    TokenStakeEventListener().listen_and_publish_token_stake_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def airdrop_event_listener_handler(event, context):
    AirdropEventListener().listen_and_publish_airdrop_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def occam_airdrop_event_listener_handler(event, context):
    OccamAirdropEventListener().listen_and_publish_occam_airdrop_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def converter_agix_event_listener_handler(event, context):
    ConverterAGIXEventListener().listen_and_publish_converter_agix_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def converter_ntx_event_listener_handler(event, context):
    ConverterNTXEventListener().listen_and_publish_converter_ntx_events()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def converter_rjv_event_listener_handler(event, context):
    ConverterRJVEventListener().listen_and_publish_converter_rjv_events()
