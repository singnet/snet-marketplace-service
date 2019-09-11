import paypalrestsdk

from payments.settings import MODE, CLIENT_ACCESS_KEY, CLIENT_SECRET_KEY, PAYPAL_REST_PAYLOAD

payee_client_api = paypalrestsdk.Api({
  'mode': MODE,
  'client_id': CLIENT_ACCESS_KEY,
  'client_secret': CLIENT_SECRET_KEY}
)


def initiate_paypal_payment(amount):
    """TODO: Complete paypal initiation"""
    payment = paypalrestsdk.Payment(PAYPAL_REST_PAYLOAD, api=payee_client_api)
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
