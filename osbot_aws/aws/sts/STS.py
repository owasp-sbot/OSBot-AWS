import sys
from botocore.exceptions                                    import ClientError, NoCredentialsError
from osbot_utils.decorators.methods.remove_return_value     import remove_return_value
from osbot_utils.utils.Misc                                 import random_string
from osbot_utils.utils.Status                               import status_ok, status_error, status_warning
from osbot_utils.decorators.methods.cache_on_self           import cache_on_self
from osbot_aws.AWS_Config                                   import AWS_Config

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

    @remove_return_value('ResponseMetadata')
    def assume_role(self, role_arn, role_session_name=None, duration_seconds=900):
        role_session_name = role_session_name or random_string(prefix='osbot_sts_session_')
        kwargs = { "DurationSeconds" : duration_seconds , # minumum 900 seconds (15 minutes) manximum 43200 seconds (15 hour)
                    "RoleArn"        : role_arn         ,
                    "RoleSessionName": role_session_name or ''}
        return self.client().assume_role(**kwargs)

    def current_account_id(self):
        return self.caller_identity_account()

    def current_region_name(self):
        return self.client().meta.region_name

    @remove_return_value('ResponseMetadata')
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

    def caller_identity_user(self):
        arn = self.caller_identity().get('Arn')
        if ':user/' in arn:
            return arn.split(':user/')[-1]
        elif ':assumed-role/' in arn:
            return arn.split(':assumed-role/')[-1].split('/')[1]
        else:
            raise ValueError("ARN does not contain a user or assumed-role")

    def check_aws_session(self):
        try:
            caller_arn = self.caller_identity().get('Arn')
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

    @cache_on_self
    def check_current_session_credentials(self, raise_exception=True):          # todo: see if there is a faster way to do this, at the moment it takes about 500ms which is quite a lot
        if AWS_Config().dev_skip_aws_key_check() == "True":
            return status_warning(message="check was skipped")
        result = self.check_aws_session()
        if result.get('status') == 'error':
            self.print_bad_credentials_exception(result.get('message'))
            #if exit_on_error:                                                  # todo: see better way to do this
            #    self.end_process_bad_credentials_exception()
            if raise_exception:
                self.raise_bad_credentials_exception(result.get('message'))
        return result

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