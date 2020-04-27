from osbot_aws.Globals                                        import Globals
from gw_bot.helpers.Test_Helper                               import Test_Helper
from osbot_aws.apis.Lambda_Layer                              import Lambda_Layer
from osbot_utils.utils.Files import temp_folder_with_temp_file, Files
from osbot_aws.apis.test_helpers.Temp_Folder_With_Lambda_File import Temp_Folder_With_Lambda_File


class test_Lambda_Layer(Test_Helper):

    def setUp(self):                    # todo: fix scenario when running this for the first time (test layer will be missing)
        super().setUp()
        self.layer_name = 'test_simple_layer'

    # helpers

    def assert_lambda_created_ok(self, params, result):
        layer_name = params.get('layer_name')
        assert set(result)                      == { 'CompatibleRuntimes', 'Content', 'CreatedDate', 'Description', 'LayerArn', 'LayerVersionArn', 'LicenseInfo','Version'}
        assert result.get('LayerArn'          ) == f'arn:aws:lambda:{Globals.aws_session_region_name}:{Globals.aws_session_account_id}:layer:{layer_name}'
        assert result.get('Description'       ) == params.get('description')
        assert result.get('CompatibleRuntimes') == params.get('runtimes')

    # tests
    def test_create_from_zip_bytes(self):
        with Temp_Folder_With_Lambda_File('file_in_layer') as temp_folder:
            params     = { 'layer_name'          : self.layer_name       ,
                           'description'         : 'this is a test layer',
                           'runtimes'            : ['python3.8']         }

            lambda_layer = Lambda_Layer(**params)
            result = lambda_layer.create_from_folder(temp_folder.folder)           # uses create_from_zip_bytes
            self.assert_lambda_created_ok(params, result)

    def test_create_from_pip(self):
        package_name = 'urllib3'
        lambda_layer = Lambda_Layer('created_from_pip')

        self.result = lambda_layer.create_from_pip(package_name)

        zip_file     =  lambda_layer.code_zip()
        files_in_zip = Files.zip_file_list(zip_file)
        assert len(files_in_zip) > 10
        assert 'urllib3/util/' in files_in_zip
        assert lambda_layer.delete() is True

        # check when trying to create a layer from a package that throws an exception
        assert 'ERROR: Could not find a version that satisfies the requirement' in lambda_layer.create_from_pip('aaaaaaa-1234').get('error')

    def test_create_from_folder_via_s3(self):
        with Temp_Folder_With_Lambda_File('file_in_layer') as temp_folder:
            params       = { 'layer_name'          : 'layer_created_via_s3' ,
                             'description'         : 'this is a test layer' ,
                             'runtimes'            : ['python3.8']          }
            lambda_layer = Lambda_Layer(**params)
            result       = lambda_layer.create_from_folder_via_s3(temp_folder.folder)     # calls create_from_s3
            self.assert_lambda_created_ok(params, result)

    #def test
    def test_delete(self):
        temp_layer_name   = 'temp_layer'
        temp_layer_folder = temp_folder_with_temp_file()

        lambda_layer = Lambda_Layer(temp_layer_name)

        assert lambda_layer.exists() is False                   # confirm layer doesn't exists
        lambda_layer.create_from_folder(temp_layer_folder)      # create two versions
        lambda_layer.create_from_folder(temp_layer_folder)
        assert lambda_layer.exists() is True                    # confirm it exists
        assert len(lambda_layer.versions()) == 2                # and that we have two
        assert lambda_layer.delete() is True                    # delete layers
        assert lambda_layer.exists() is False                   # confirm it doesn't exists

    def test_exists(self):
        assert Lambda_Layer(layer_name=self.layer_name).exists() is True
        assert Lambda_Layer(layer_name='aaaaaa'       ).exists() is False

    def test_code_zip(self):
        zip_file = Lambda_Layer(layer_name=self.layer_name).code_zip()
        assert Files.zip_file_list(zip_file) == ['file_in_layer.py']

    def test_layers(self):
        assert len(Lambda_Layer().layers(index_by='LayerName')) > 0

    def test_latest(self):
        assert set(Lambda_Layer(layer_name=self.layer_name).latest()) == { 'CompatibleRuntimes','CreatedDate','Description','LayerVersionArn','LicenseInfo','Version'}
        assert Lambda_Layer(layer_name='aaaa').latest() == {}

    def test_s3_folder_files(self):
        self.result = Lambda_Layer().s3_folder_files()

    def test_versions(self):
        assert len(Lambda_Layer(self.layer_name).versions()) >0




