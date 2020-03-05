import json
from enum import Enum

import boto3
from botocore.exceptions import ClientError

from common.logger import get_logger
from notification.config import EMAIL_FOR_SENDING_NOTIFICATION
logger = get_logger(__name__)

CHARSET = "UTF-8"
AWS_REGION = "us-east-1"


class NotificationType(Enum):
    SUPPORT = "support"


SENDERS = {NotificationType.SUPPORT.value: EMAIL_FOR_SENDING_NOTIFICATION}
BODY_HTMLS = {NotificationType.SUPPORT.value: """<html>
<head></head>
<body>
  <p>{}</p>
</body>
</html>
"""}
client = boto3.client('ses')


def send_email(recipient, subject, body_html, sender):
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        logger.info("Email sent! Message ID:"),
        logger.info(response['MessageId'])


def main(proxy_event, context):
    logger.info(proxy_event)
    if 'body' in proxy_event:
        try:
            event = json.loads(proxy_event['body'])
            recipient = event["recipient"]
            if recipient == '':
                print("No recipient")
            else:
                message = event["message"] if 'message' in event else ''
                subject = event["subject"] if 'subject' in event else 'Error occurred'
                notification_type = event["notification_type"] if 'notification_type' in event else ''
                body_html = BODY_HTMLS[notification_type].format(message)
                sender = SENDERS[notification_type]
                send_email(recipient, subject, body_html, sender)
        except Exception as e:
            logger.exception(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Received!')
    }
