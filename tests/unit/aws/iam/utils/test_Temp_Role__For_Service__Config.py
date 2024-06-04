from unittest import TestCase

from osbot_aws.aws.iam.utils.Temp_Role__For_Service__Config import Temp_Role__For_Service__Config


class test_Temp_Role__For_Service__Config(TestCase):

    def setUp(self):
        self.temp_role_for_service__config = Temp_Role__For_Service__Config()

    def test_data(self):
        with self.temp_role_for_service__config as _:
            with self.assertRaises(ValueError) as value_error:
                _.data()
            assert value_error.exception.args == ('boto3_service_name is required',)

            _.boto3_service_name = 'an-service-name'
            with self.assertRaises(ValueError) as value_error:
                self.temp_role_for_service__config.data()
            assert value_error.exception.args == ('required_services is required',)
            _.required_services = ['required-service-A']

            expected_data = { 'action'              : '*'                                                    ,
                              'boto3_service_name'  : 'an-service-name'                                      ,
                              'random_role_name'    : False                                                  ,
                              'recreate'            : False                                                  ,
                              'required_services'   : ['required-service-A']                                 ,
                              'resource'            : '*'                                                    ,
                              'role_access_type'    : 'Full_Access'                                          ,
                              'role_name'           : 'ROLE__temp__Full_Access__osbot__for__an-service-name' }

            assert _.data().__locals__() == expected_data
