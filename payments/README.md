# Payment service

It consist of three components

Order, Payment and Refund

A order can have mulitple payments and multiple refunds

##### Order  -* Payments

##### Order  -* Refunds

Right now we only have payments associated with order , refund will come later 

Payment consist of paypal implementation as of now.

It is two step process
##### Initiate payment 
Initiates a payment for a given order, amount ,callback_url and returns a PaypalURl,
```eg : callback_url  :/yourdomain/path/order_id/payment_id```

user logs in to papyaplURL and authorizes payment 
after authorization paypal returns flow back to a callback_url along with payment and order metadata which was passed during initiate call.


##### Execute payment 
 
When paypal gives control back to your callback_url you redirect it to appropiate page on your frontend 
and call execute payment api to execute the payment on paypal ,and process the order in backend.

#### Reference: 
<a href="https://github.com/paypal/PayPal-Python-SDK"> PayPal Python SDK </a>
