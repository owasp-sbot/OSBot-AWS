## NOT WORKING (TO TRY Later)

# import sys, os, base64, datetime, hashlib, hmac
# import requests
# from osbot_aws.apis.IAM import IAM
#
# # based on the example from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
#
#
# class Lambda_Http:
#     @aws_inject('region')
#     def __init__(self, lambda_name, region):
#         self.lambda_name = lambda_name
#         self.region      = region
#
#     def sign(self, key, msg):
#         return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
#
#     def getSignatureKey(self, key, dateStamp, regionName, serviceName):
#         kDate    = self.sign(('AWS4' + key).encode('utf-8'), dateStamp)
#         kRegion  = self.sign(kDate, regionName)
#         kService = self.sign(kRegion, serviceName)
#         kSigning = self.sign(kService, 'aws4_request')
#         return kSigning
#
#     @catch
#     def make_request(self):
#
#         # ************* REQUEST VALUES *************
#         # method = 'POST'
#         # service = 'dynamodb'
#         # host = 'dynamodb.us-west-2.amazonaws.com'
#         # region = 'us-west-2'
#         # endpoint = 'https://dynamodb.us-west-2.amazonaws.com/'
#
#         method   = 'POST'
#         service  = 'lambda'
#         host     = f'lambda.{self.region}.amazonaws.com'
#         region   = self.region
#         endpoint = f'https://{host}/'
#
#         # POST requests use a content type header. For DynamoDB,
#         # the content is JSON.
#         content_type = 'application/x-amz-json-1.0'
#         # DynamoDB requires an x-amz-target header that has this format:
#         #     DynamoDB_<API version>.<operationName>
#         amz_target = 'DynamoDB_20120810.CreateTable'
#
#         # Request parameters for CreateTable--passed in a JSON block.
#         request_parameters =  '{'
#         request_parameters +=  '"KeySchema": [{"KeyType": "HASH","AttributeName": "Id"}],'
#         request_parameters +=  '"TableName": "TestTable","AttributeDefinitions": [{"AttributeName": "Id","AttributeType": "S"}],'
#         request_parameters +=  '"ProvisionedThroughput": {"WriteCapacityUnits": 5,"ReadCapacityUnits": 5}'
#         request_parameters +=  '}'
#
#         # Key derivation functions. See:
#         # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
#         def sign(key, msg):
#             return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
#
#         def getSignatureKey(key, date_stamp, regionName, serviceName):
#             kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
#             kRegion = sign(kDate, regionName)
#             kService = sign(kRegion, serviceName)
#             kSigning = sign(kService, 'aws4_request')
#             return kSigning
#
#         # Read AWS access key from env. variables or configuration file. Best practice is NOT
#         # to embed credentials in code.
#
#         session = IAM().session()
#         credentials = session.get_credentials()
#         access_key = credentials.access_key
#         secret_key = credentials.secret_key
#
#         #access_key = os.environ.get('AWS_ACCESS_KEY_ID')
#         #secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
#         if access_key is None or secret_key is None:
#             print('No access key is available.')
#             sys.exit()
#
#         # Create a date for headers and the credential string
#         t = datetime.datetime.utcnow()
#         amz_date = t.strftime('%Y%m%dT%H%M%SZ')
#         date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope
#
#
#         # ************* TASK 1: CREATE A CANONICAL REQUEST *************
#         # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
#
#         # Step 1 is to define the verb (GET, POST, etc.)--already done.
#
#         # Step 2: Create canonical URI--the part of the URI from domain to query
#         # string (use '/' if no path)
#         canonical_uri = '/'
#
#         ## Step 3: Create the canonical query string. In this example, request
#         # parameters are passed in the body of the request and the query string
#         # is blank.
#         canonical_querystring = ''
#
#         # Step 4: Create the canonical headers. Header names must be trimmed
#         # and lowercase, and sorted in code point order from low to high.
#         # Note that there is a trailing \n.
#         canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' + 'x-amz-target:' + amz_target + '\n'
#
#         # Step 5: Create the list of signed headers. This lists the headers
#         # in the canonical_headers list, delimited with ";" and in alpha order.
#         # Note: The request can include any headers; canonical_headers and
#         # signed_headers include those that you want to be included in the
#         # hash of the request. "Host" and "x-amz-date" are always required.
#         # For DynamoDB, content-type and x-amz-target are also required.
#         signed_headers = 'content-type;host;x-amz-date;x-amz-target'
#
#         # Step 6: Create payload hash. In this example, the payload (body of
#         # the request) contains the request parameters.
#         payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()
#
#         # Step 7: Combine elements to create canonical request
#         canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
#
#
#         # ************* TASK 2: CREATE THE STRING TO SIGN*************
#         # Match the algorithm to the hashing algorithm you use, either SHA-1 or
#         # SHA-256 (recommended)
#         algorithm = 'AWS4-HMAC-SHA256'
#         credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
#         string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
#
#         # ************* TASK 3: CALCULATE THE SIGNATURE *************
#         # Create the signing key using the function defined above.
#         signing_key = getSignatureKey(secret_key, date_stamp, region, service)
#
#         # Sign the string_to_sign using the signing_key
#         signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
#
#
#         # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
#         # Put the signature information in a header named Authorization.
#         authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
#
#         # For DynamoDB, the request can include any headers, but MUST include "host", "x-amz-date",
#         # "x-amz-target", "content-type", and "Authorization". Except for the authorization
#         # header, the headers must be included in the canonical_headers and signed_headers values, as
#         # noted earlier. Order here is not significant.
#         # # Python note: The 'host' header is added automatically by the Python 'requests' library.
#         headers = {'Content-Type':content_type,
#                    'X-Amz-Date':amz_date,
#                    'X-Amz-Target':amz_target,
#                    'Authorization':authorization_header}
#
#
#         # ************* SEND THE REQUEST *************
#         print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
#         print('Request URL = ' + endpoint)
#
#         r = requests.post(endpoint, data=request_parameters, headers=headers)
#
#         print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
#         print('Response code: %d\n' % r.status_code)
#         print(r.text)
#
#     def make_request__2(self):
#         # request_url = f'https://lambda.{self.region}.amazonaws.com/2015-03-31/functions/{self.lambda_name}/invocations'
#         method             = 'GET'
#         service            = 'lambda'
#         host               = f'lambda.{self.region}.amazonaws.com'
#         region             = self.region
#         canonical_uri      = f'/2015-03-31/functions/{self.lambda_name}/invocations'
#         endpoint           = f'https://lambda.{self.region}.amazonaws.com{canonical_uri}'
#         request_parameters = ''
#
#         session = IAM().session()
#         credentials = session.get_credentials()
#         access_key = credentials.access_key
#         secret_key = credentials.secret_key
#
#         t             = datetime.datetime.utcnow()
#         amzdate       = t.strftime('%Y%m%dT%H%M%SZ')
#         datestamp     = t.strftime('%Y%m%d')
#
#         canonical_querystring = request_parameters
#         canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
#         signed_headers = 'host;x-amz-date'
#         payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
#         canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
#         algorithm = 'AWS4-HMAC-SHA256'
#         credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
#         string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
#         signing_key = self.getSignatureKey(secret_key, datestamp, region, service)
#         signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
#         authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
#         headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}
#         request_url = endpoint + '?' + canonical_querystring
#
#         print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
#         print('Request URL = ' + request_url)
#
#
#         #return request_url
#
#         r = requests.get(request_url, headers=headers)
#
#         print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
#         print('Response code: %d\n' % r.status_code)
#         print(r.text)
#
