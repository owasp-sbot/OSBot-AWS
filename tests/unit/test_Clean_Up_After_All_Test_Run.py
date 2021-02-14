from unittest import TestCase

from osbot_aws.apis.Cloud_Watch import Cloud_Watch
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Logs import Logs
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, list_filter, list_filter_starts_with, list_filter_contains


# todo: also create class to check if after an full test execution there is anything left behind
# todo: find way to execute this last (i.e. at the end of a last run
class Clean_Up_After_All_Test_Run:

    def __init__(self):
        pass

    @cache
    def aws_lambda(self):
        return Lambda()

    @cache
    def logs(self):
        return Logs()

    def delete_temp_lambdas(self):                      # eventually this shouldn't be needed since there should be none of these left behind
        temp_prefix       = 'temp_lambda'
        all_lambdas_names = list_set(self.aws_lambda().functions_names())
        lambdas_to_delete = list_filter_starts_with(all_lambdas_names, temp_prefix)
        for lambda_to_delete in lambdas_to_delete:
            if Lambda(name=lambda_to_delete).delete():
                print(f'deleted lambda function: {lambda_to_delete}')
        return lambdas_to_delete

    def delete_temp_logs(self):
        all_groups       = self.logs().groups_names()
        temp_ids         = ['temp_lambda', 'osbot']
        groups_to_delete = []
        for temp_id in temp_ids:
            groups_to_delete.extend(list_filter_contains(all_groups, temp_id))

        for group_to_delete in groups_to_delete:
            if Logs(group_name=group_to_delete).group_delete():
                print(f'deleted cloudwatch group: {group_to_delete}')
        return groups_to_delete

class test_Clean_Up_After_All_Test_Run(TestCase):

    def setUp(self):
        self.clean_up = Clean_Up_After_All_Test_Run()
        print()

    def test_delete_temp_lambdas(self):
        self.clean_up.delete_temp_lambdas()

    def test_delete_temp_logs(self):
        self.clean_up.delete_temp_logs()

