from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self


class Organizations(Kwargs_To_Self):
    aws_config: AWS_Config

    @cache_on_self
    def client(self):
        return Session().client('organizations')

    def account(self, account_id):
        return self.client().describe_account(AccountId=account_id)


    def accounts(self):
        return self.client().list_accounts()