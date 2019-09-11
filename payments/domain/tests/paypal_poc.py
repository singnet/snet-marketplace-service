import paypalrestsdk

from payments.settings import MODE, CLIENT_ACCESS_KEY, CLIENT_SECRET_KEY

my_api = paypalrestsdk.Api({
  'mode': MODE,
  'client_id': CLIENT_ACCESS_KEY,
  'client_secret': CLIENT_SECRET_KEY}
)
payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"},
    "redirect_urls": {
        "return_url": "http://localhost:3000/payment/test/execute",
        "cancel_url": "http://localhost:3000/"},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": "item",
                "sku": "item",
                "price": "5.00",
                "currency": "USD",
                "quantity": 1}]},
        "amount": {
            "total": "5.00",
            "currency": "USD"},
        "description": "This is the payment transaction description."}]}, api=my_api)


data = payment.create()

for link in payment.links:
    if link.rel == "approval_url":
        # Convert to str to avoid Google App Engine Unicode issue
        # https://github.com/paypal/rest-api-sdk-python/pull/58
        approval_url = str(link.href)
        print("Redirect for approval: %s" % (approval_url))

print(payment)

