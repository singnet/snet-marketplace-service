import json
import boto3
from botocore.exceptions import ClientError
from string import Template

from common.logger import get_logger

logger = get_logger(__name__)

EMAIL_SENDER_EMAIL = "<tech-support@singularitynet.io>"
EMAIL_BODY_TEXT = "Hello"
EMAIL_BODY_HTML = """<html>
<head></head>
<body>
  <h1>SNET Error Notification</h1>
  <br>Error:$message</br>
  <br>Details:$details</br>
</body>
</html>
"""


def send_email(recipient, subject, context):
    client = boto3.client('ses')
    try:
        src = Template(EMAIL_BODY_HTML)
        body = src.substitute(context)
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=EMAIL_SENDER_EMAIL,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


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
                details = event["details"] if 'details' in event else ''
                component = event["component"] if 'component' in event else ''
                component_id = event["component_id"] if 'component_id' in event else ''
                subject = 'Error occurred'
                if 'daemon' == component:
                    subject = 'Error detected by the Daemon ' + component_id
                send_email(recipient, subject, event)
        except Exception as e:
            logger.exception(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Received!')
    }
