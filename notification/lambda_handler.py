import json
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

import boto3
import requests
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


def send_email_with_attachment(recipient: str, subject: str, body_html: str, sender: str, attachment_urls: list):
    logger.info(f"Receipent={recipient}, subject={subject}, body={body_html}, sender={sender}, "
                f"attachment_urls={attachment_urls}")
    attachment_filepaths = list()
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # Set message body
        body = MIMEText(body_html, "html")
        msg.attach(body)

        for attachment_url in attachment_urls:
            logger.info(f"Downloading the file from url={attachment_url}")
            filename = os.path.basename(attachment_url)
            try:
                response = requests.get(attachment_url)
                filepath = f"/tmp/{filename}"
                open(filepath, "wb").write(response.content)
                attachment_filepaths.append(filepath)
                logger.info(f"Download completed for the file from url={attachment_url}")
            except Exception as e:
                logger.error(f"Unable to download the file from the url={attachment_url} and error={e}")

        logger.info(f"Attachment file path={attachment_filepaths}")
        for attachment_filepath in attachment_filepaths:
            with open(attachment_filepath, "rb") as attachment:
                filename = os.path.basename(attachment_filepath)
                part = MIMEApplication(attachment.read())
                part.add_header("Content-Disposition",
                                "attachment",
                                filename=filename)
            msg.attach(part)

        # Convert message to string and send
        response = client.send_raw_email(
            Source=sender,
            Destinations=list(recipient.split(",")),
            RawMessage={"Data": msg.as_string()}
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
                attachment_urls = event["attachment_urls"] if 'attachment_urls' in event else []
                subject = event["subject"] if 'subject' in event else 'Error occurred'
                notification_type = event["notification_type"] if 'notification_type' in event else ''
                body_html = BODY_HTMLS[notification_type].format(message)
                sender = SENDERS[notification_type]
                send_email_with_attachment(recipient, subject, body_html, sender, attachment_urls=attachment_urls)
        except Exception as e:
            logger.exception(e)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Access-Control-Allow-Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps('Received!')
    }
