# import os
# import json
# import os.path
# import unittest
# import warnings
# from   zipfile import ZipFile
# #from   Aws_Cli import Aws_Cli,Aws_Utils
#
# @unittest.skip
# class Test_Aws_Cli(unittest.TestCase):
#     def setUp(self):
#         warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
#
#         self.aws       = Aws_Cli()
#         self.name      = 'test_from_python'
#         self.role      = 'arn:aws:iam::244560807427:role/lambda_basic_execution'
#         self.handler   = 'handler.hello'
#         self.s3_bucket = 'gs-lambda-tests'
#         self.s3_key    = 'dinis/lambda-mvp-via-tests.zip'
#
#     def test_lambda_create_function (self):
#         self.aws.lambda_delete_function(self.name)
#         result = self.aws.lambda_create_function(self.name, self.role, self.handler, self.s3_bucket, self.s3_key)
#         assert result['Runtime'] == 'python3.6'
#         #
#     #def test_lambda_delete_function (self):
#         # this is tested inside the test_lambda_create_function test
#         # and running it here will break the tests below :)
#         #
#     @unittest.skip  # needs fixing (since this function is not there
#     def test_lambda_functions       (self):
#         name     = 'Lambda_MVP'
#         runtime  = "python3.6"
#         handler  = "handler.hello"
#
#         function = self.aws.lambda_functions()['Lambda_MVP']
#
#         assert function['FunctionName'] == name
#         assert function['Runtime'     ] == runtime
#         assert function['Handler'     ] == handler
#
#         #
#     def test_lambda_function_exists (self):
#         assert self.aws.lambda_function_exists('test_from_python') is True
#         assert self.aws.lambda_function_exists('aaaaaaa'         ) is False
#
#         #
#     def test_lambda_invoke_function (self):
#         payload = { "a": 42}
#         (result, response) = self.aws.lambda_invoke_function(self.name, payload)
#         body = json.loads(result['body'])
#         assert result.get('statusCode')   is 200
#         assert ("This was edited locally" in body.get('message')) is True
#         assert body.get('input') == payload
#
#         #
#     def test_lambda_update_function (self):
#         response = self.aws.lambda_update_function(self.name, self.s3_bucket, self.s3_key)
#         assert response['FunctionName'] == self.name
#
#         #
#     def test_s3_buckets             (self):
#         buckets = self.aws.s3_buckets()
#         name = 'gs-lambda-tests'
#         assert buckets[name]['Name'] == name
#
#         #
#
#     @unittest.skip  # needs fixing (since code folder doesn't exist anymore, in this repo (maybe add it as a test artifact))
#     def test_s3_upload_folder         (self):
#         folder    = '../code'
#         s3_bucket = 'gs-lambda-tests'
#         s3_key    = 'dinis/lambda-mvp-via-tests.zip'
#         zip_file  = self.aws.s3_upload_folder(folder, s3_bucket, s3_key)
#         assert os.path.isfile(zip_file) is True
#         os.remove(zip_file)
#         #
#         #
#
#
# # @unittest.skip
# # class Test_Aws_Utils(unittest.TestCase):
# #     def setUp(self):
# #         self.aws_Utils = Aws_Utils()
# #
# #     def test_zip_folder             (self):
# #         dir_Name      = 'temp_dir'
# #         file_Path     = 'temp_dir/a_file.txt'
# #         file_Contents = 'some contents'
# #
# #         if not os.path.exists(dir_Name):
# #             os.mkdir(dir_Name)
# #
# #         with open(file_Path, "w+") as f:
# #             f.write(file_Contents)
# #
# #         result = self.aws_Utils.zip_folder(dir_Name)
# #
# #         assert os.path.basename(result) == 'temp_dir.zip'
# #
# #         with ZipFile(result, 'r') as f:
# #             names = f.namelist()
# #             assert names == ['a_file.txt']
# #
# #         os.remove(result)
# #         os.remove(file_Path)
# #         os.rmdir(dir_Name)
#
# if __name__ == '__main__':
#     unittest.main()