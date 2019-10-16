import json
import boto3
from botocore.exceptions import ClientError


from common.logger import get_logger

logger = get_logger(__name__)



SENDER = "Tech Support <tech-support@singularitynet.io>"
CHARSET = "UTF-8"
AWS_REGION = "us-east-1"

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Header message</h1>
  <p>Custom message {}</p>
</body>
</html>
"""

def send_email(recipient, subject, message):
    client = boto3.client('ses')
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
                        'Data': BODY_HTML.format(message),
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
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
                subject = event["subject"] if 'subject' in event else 'Error occurred'
                send_email(recipient, subject, message)
        except Exception as e:
            logger.exception(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Received!')
    }
