from botocore.exceptions                  import ClientError
from osbot_aws.AWS_Config                 import AWS_Config
from osbot_aws.exceptions.Session_Bad_Credentials import Session_Bad_Credentials
from osbot_utils.testing.Catch            import Catch
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc               import wait
from osbot_utils.utils.Status import status_warning, status_ok, status_error


class STS:
    """
    Helper methods for the AWS STS (Security Token Service)
    """
    def __init__(self, print_error_message=True):
        self.print_error_message = print_error_message                  # todo: need to find a better way to have the bad credentials errors showing up in IDE when development

    @cache
    def client(self):
        from osbot_aws.apis.Session import Session                      # recursive dependency
        return Session().client('sts')

    def assume_role(self, role_arn, role_session_name='temp_session'):
        kwargs = { "RoleArn"        : role_arn,
                   "RoleSessionName": role_session_name}
        return self.client().assume_role(**kwargs)

    def assume_role__wait_until_enabled(self, role_name, sleep_for=1, max_attempts=10):
        """this method will try to get a valid assume_role result for the role provided
            it will do this by temporarily replacing the current assume policy with one
            that has the current user as the principal
            """
        from osbot_aws.helpers.IAM_Role import IAM_Role
        iam_role = IAM_Role(role_name=role_name)
        current_user_arn = self.caller_identity_arn()
        temp_policy      = {'Statement': [{'Action'   : 'sts:AssumeRole'           ,
                                           'Effect'   : 'Allow'                    ,
                                           'Principal': {'AWS': '*'}}]}

        current_assume_policy = iam_role.iam.role_assume_policy()
        iam_role.iam.role_assume_policy_update(temp_policy)
        pprint(iam_role.iam.role_assume_policy())

        for i in range(0,max_attempts):
            try:
                self.assume_role(role_arn=role_arn)
                self.assume_role(role_arn=role_arn)
                pprint('got credentials')
                break
            except Exception as exception:
                pprint(exception)
            print(f'after {i} seconds')
            wait(sleep_for)
        #return role_arn


    def current_account_id(self):
        return self.caller_identity_account()

    def current_region_name(self):
        return self.client().meta.region_name

    def caller_identity(self):
        return self.client().get_caller_identity()

    def caller_identity_account(self):
        return self.caller_identity().get('Account')

    def caller_identity_arn(self):
        return self.caller_identity().get('Arn')



    @cache
    def check_current_session_credentials(self):        # todo: see if there is a faster way to do this, at the moment it takes about 500ms which is quite a lot
        if AWS_Config().dev_skip_aws_key_check() == "True":
            return status_warning("dev_skip_aws_key_check was true")
        try:
            caller_arn = self.caller_identity().get('Arn')
        except ClientError as client_error:
            exception = client_error.response.get('Error')
            raise Session_Bad_Credentials(exception)
        return status_ok(f'AWS credentials are ok for {caller_arn}')