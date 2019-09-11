import paypalrestsdk
from payments.settings import MODE, CLIENT_ACCESS_KEY, CLIENT_SECRET_KEY

my_api = paypalrestsdk.Api({
  'mode': MODE,
  'client_id': CLIENT_ACCESS_KEY,
  'client_secret': CLIENT_SECRET_KEY}
)

payment = paypalrestsdk.Payment.find("123", api=my_api)

if payment.execute({"payer_id": "123"}):
  print("Payment execute successfully")
else:
  print(payment.error) # Error Hash