# todo recreate with CLI util (see FastAPI recomendation)
# import os
# import boto3
# import json
# import shutil
#
# from osbot_aws.apis.Session import Session
#
#
# class Aws_Cli:
#     def __init__(self, **kwargs):
#         self.aws_lambda = Session().client('lambda', region_name = kwargs.get('region_name'))
#         self.aws_s3     = Session().client('s3'    , region_name = kwargs.get('region_name'))
#
#
#         #
#
#     # def lambda_delete_function      (self, name                                                                 ):
#     #     if self.lambda_function_exists(name):
#     #         self.aws_lambda.delete_function( FunctionName = name)
#     #     return self
#     #     #
#
#     # def lambda_functions            (self                                                                       ):
#     #     data = {}
#     #     for function in self.aws_lambda.list_functions().get('Functions'):
#     #         data[function['FunctionName']] = function
#     #     return data
#
#
#
#         #
#
#     # def lambda_function_info        (self, name                                                                 ):
#     #     return self.aws_lambda.get_function(FunctionName = name)
#
#     def lambda_invoke_function      (self, name, payload                                                        ):
#         response      = self.aws_lambda.invoke(FunctionName=name, Payload = json.dumps(payload) )
#
#         result_bytes  = response.get('Payload').read()
#         result_string = result_bytes.decode('utf-8')
#         result        = json.loads(result_string)
#         return result, response
#
#         #
#
#     # def lambda_invoke_function_async(self, name, payload                                                        ):
#     #     return  self.aws_lambda.invoke(FunctionName=name, Payload = json.dumps(payload), InvocationType='Event')
#
#     def lambda_update_function      (self, name, s3_bucket,s3_key                                               ):
#         return self.aws_lambda.update_function_code(FunctionName = name,
#                                                     S3Bucket     = s3_bucket ,
#                                                     S3Key        = s3_key    )
#
#         #
#
#     def s3_buckets                  (self                                                                       ):
#         data = {}
#         for bucket in self.aws_s3.list_buckets().get('Buckets'):
#             data[bucket['Name']] = bucket
#         return data
#
#         #
#
#     #def s3_add_notification        (self, s)
