import paypalrestsdk

my_api = paypalrestsdk.Api({"mode": "sandbox", "client_id": "", "client_secret": ""})
#
payment = paypalrestsdk.Payment(
    {
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/test/execute",
            "cancel_url": "http://localhost:3000/",
        },
        "transactions": [
            {
                "item_list": {
                    "items": [
                        {
                            "name": "item",
                            "sku": "item",
                            "price": "5.00",
                            "currency": "USD",
                            "quantity": 1,
                        }
                    ]
                },
                "amount": {"total": "5.00", "currency": "USD"},
                "description": "This is the payment transaction description.",
            }
        ],
    },
    api=my_api,
)


data = payment.create()

for link in payment.links:
    if link.rel == "approval_url":
        # Convert to str to avoid Google App Engine Unicode issue
        # https://github.com/paypal/rest-api-sdk-python/pull/58
        approval_url = str(link.href)
        print("Redirect for approval: %s" % (approval_url))

print(payment)

# payment = paypalrestsdk.Payment.find("PAYID-LVYRUYA12E852541G2761539",api=my_api)
#
# if payment.execute({"payer_id": "4LM6PXZ37RGL7"}):
#   print("Payment execute successfully")
# else:
#   print(payment.error) # Error Hash

# http://localhost:3000/payment/execute?paymentId=PAYID-LVYN3OA15W11958Y04269841&token=EC-9B015759WS7028732&PayerID=4LM6PXZ37RGL6
