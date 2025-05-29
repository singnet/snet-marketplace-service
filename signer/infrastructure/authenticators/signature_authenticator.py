from web3.auto import w3

from signer.infrastructure.authenticators.daemon_authenticator import DaemonAuthenticator
from signer.settings import settings


def extract_public_key(message_data, signature):
    public_key = w3.eth.account.recover_message(message_data, signature=signature)
    return public_key


def verify_public_key(public_keys, derived_public_key):
    if public_keys is None:
        return False
    for public_key in public_keys:
        if public_key == derived_public_key:
            return True
    return False


def generatePolicy(principalId, effect, methodArn):
    authResponse = {}
    authResponse['principalId'] = principalId

    if effect and methodArn:
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'FirstStatement',
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        }

        authResponse['policyDocument'] = policyDocument

    return authResponse


def main(event, context):
    # default is Deamon authenticator, in future we will introduce new authentications
    print(event)
    authenticator = None
    if 'x-authtype' in event:
        pass
    else:
        authenticator = DaemonAuthenticator(event, settings.network.networks, settings.network.id)

    try:
        message = authenticator.get_signature_message()
        signature = authenticator.get_signature()
        public_keys = authenticator.get_public_keys()
        principal = authenticator.get_principal()
        derived_public_key = extract_public_key(message, signature)
        print("Derived public key is %s", derived_public_key)
        verified = (
            verify_public_key(public_keys, derived_public_key) and authenticator.verify_current_block_number()
        )
        if verified:
            print(f"verified sign auth for {principal}")
            return generatePolicy(principal, 'Allow', event['methodArn'])
        print(f"verified failed sign auth for {principal}")
        return generatePolicy(principal, 'Deny', event['methodArn'])
    except Exception as e:
        print(e)
        return generatePolicy('exception', 'Deny', event['methodArn'])
