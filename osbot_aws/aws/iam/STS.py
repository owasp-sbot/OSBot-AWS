import sys
from botocore.exceptions                            import ClientError, NoCredentialsError
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import wait
from osbot_utils.utils.Status                       import status_ok, status_error, status_warning
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_aws.AWS_Config                           import AWS_Config
from osbot_aws.exceptions.Session_Bad_Credentials import Session_Bad_Credentials


class STS:
    """
    Helper methods for the AWS STS (Security Token Service)
    """
    def __init__(self, print_error_message=True):
        self.print_error_message = print_error_message                  # todo: need to find a better way to have the bad credentials errors showing up in IDE when development

    @cache_on_self
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

        from osbot_aws.aws.iam.IAM_Role import IAM_Role
        iam_role = IAM_Role(role_name=role_name)
        current_user_arn = self.caller_identity_arn()
        temp_policy      = {'Statement': [{'Action'   : 'sts:AssumeRole'           ,
                                           'Effect'   : 'Allow'                    ,
                                           'Principal': {'AWS': '*'}}]}

        current_assume_policy = iam_role.iam.role_assume_policy()
        iam_role.iam.role_assume_policy_update(temp_policy)
        pprint(iam_role.iam.role_assume_policy())
        role_arn = iam_role.arn()
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
        return role_arn


    def current_account_id(self):
        return self.caller_identity_account()

    def current_region_name(self):
        return self.client().meta.region_name

    def caller_identity(self):
        try:
            return self.client().get_caller_identity()
        except ClientError as client_error:
            print(f"[error][STS] - ClientError {client_error}")                 # todo: add better logging support
        except NoCredentialsError as no_credentials_error:
            print(f"[error][STS] - NoCredentialsError {no_credentials_error}")  # todo: add better logging support
        except Exception as exception:
            print(f"[error][STS] - Exception {exception}")                      # todo: add better logging support
        return {}

    def caller_identity_account(self):
        return self.caller_identity().get('Account')

    def caller_identity_arn(self):
        return self.caller_identity().get('Arn')

    def check_aws_session(self):
        try:
            self.caller_identity()
            return status_ok()
        except ClientError as client_error:
            exception = client_error.response.get('Error')
            error_code    = exception.get("Code")
            error_message = exception.get('Message')
            message = (f"\tCurrent Security credentials are invalid! \n\n"
                       f"\tPlease check: current environment values, "
                       f"profile name or value in your ~/.aws/credentials file"
                       f"\n\n"
                       f"\tBoto3 Error message: {error_code}  {error_message}")
            return status_error(message=message, error=client_error)

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

    def print_bad_credentials_exception(self, message):
        if self.print_error_message:
            print("\n*********** OSBot_AWS ***********\n")             # todo move to OSBot_AWS Logging class
            print(f"{message}")
            print("\n*********** OSBot_AWS ***********\n")

    def raise_bad_credentials_exception(self, message):
        sys.trackbacklimit = 0
        raise Exception(message)

    # def end_process_bad_credentials_exception(self):          # todo: figure out how to do this (since this always throws an exception stack trace, at least in testing)
    #     quit(0)
    #     exit(0)

def check_current_aws_credentials(raise_exception=True):
    return STS().check_current_session_credentials(raise_exception=raise_exception)

def current_aws_region():
    return STS().current_region_name()
