from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Files import Files

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Folder_Code


class Lambda_Package:
    def __init__(self,lambda_name):
        self.lambda_name   = lambda_name
        self._lambda       = Lambda(self.lambda_name)
        self.tmp_s3_bucket = 'gs-lambda-tests'
        self.tmp_s3_key    = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.role_arn      = Temp_Aws_Roles().for_lambda_invocation()
        self.tmp_folder    = Files.temp_folder('tmp_lambda_')

        (self._lambda.set_s3_bucket  (self.tmp_s3_bucket)
                     .set_s3_key     (self.tmp_s3_key   )
                     .set_role       (self.role_arn     )
                     .set_folder_code(self.tmp_folder  ))

    # helper methods
    @staticmethod
    def get_root_folder():
        return Files.path_combine(__file__, '../..')

    # Lambda class wrappers

    def create(self             ): return self._lambda.create()
    def delete(self             ): return self._lambda.delete()
    def invoke(self, params=None): return self._lambda.invoke(params)
    def update(self             ): return self._lambda.update()

    # main methods

    def add_folder(self, folder):
        Files.copy(folder, self.tmp_folder)

    def get_files(self):
        return Files.find('{0}/**.*'.format(self.tmp_folder))

    def use_lambda_file(self,lambda_file):
        file_path = Files.path_combine(self.get_root_folder(), lambda_file)
        if Files.exists(file_path) is False:
            return { 'status': 'error', 'data': 'could not find lambda file `{0}` in root folder `{1}`'.format(lambda_file, self.get_root_folder())}
        target_file = Files.path_combine(self.tmp_folder, '{0}.py'.format(self.lambda_name))
        Files.copy(file_path,target_file)
        #Dev.pprint(__file__)

        return  { 'status': 'ok', 'file_path': file_path, 'target_file': target_file }

    # def use_temp_folder_code(self):
    #     self.tmp_folder = Temp_Folder_Code(self.lambda_name).folder
    #     self._lambda.set_folder_code(self.tmp_folder)
    #     return self