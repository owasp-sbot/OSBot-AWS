## NOT WORKING (TO TRY Later)

# from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda
#
# from gw_bot.helpers.Test_Helper import Test_Helper
# from osbot_aws.apis.Lambda_Http import Lambda_Http
# from osbot_aws.helpers.Method_Wrappers import aws_inject
#
#
# class test_Lambda_Http(Test_Helper):
#
#     #@aws_inject('region,account_id')
#     def setUp(self):#, region, account_id):
#         super().setUp()
#         self.lambda_name  = 'temp_lambda_LVY1LL'
#         self.lambda_http = Lambda_Http(self.lambda_name)
#
#     def test_create_temp_lambda(self):
#         with Temp_Lambda() as temp_lambda:
#             temp_lambda.delete_on_exit = False
#             #self.result = temp_lambda.delete_on_exit
#             self.result = temp_lambda.lambda_name     # temp_lambda_LVY1LL
#
#     def test_make_request(self):
#         self.result = self.lambda_http.make_request()