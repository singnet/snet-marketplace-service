


import paypalrestsdk
my_api = paypalrestsdk.Api({
  'mode': 'sandbox',
  'client_id': '...',
  'client_secret': '...'})

payment = paypalrestsdk.Payment({...}, api=my_api)
