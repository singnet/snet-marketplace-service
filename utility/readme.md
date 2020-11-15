## Upload Utility
Utility to put files on S3 using lambda through API gateway. File will be sent using HTTP request body, 
File size is limited as AWS Lambda has payload limit of 6MB.

API gateway has need to be configured for binary support using the API Gateway Console.
Here is reference the for that, 
<a href="https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-payload-encodings-configure-with-console.html"> 
AWS docs </a>