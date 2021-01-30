from botocore.exceptions import ClientError
from osbot_aws.AWS_Config import AWS_Config

from osbot_utils.decorators.methods.cache import cache

class STS:
    """
    Helper methods for the AWS STS (Security Token Service)
    """
    def __init__(self, print_error_message=True):
        self.print_error_message = print_error_message                  # todo: need to find a better way to have the bad credentials errors showing up in IDE when development

    @cache
    def sts(self):
        from osbot_aws.apis.Session import Session                      # recursive dependency
        return Session().client('sts', check_credentials=False)

    def called_identity(self):
        return self.sts().get_caller_identity()

    @cache
    def check_current_session_credentials(self):        # todo: see if there is a faster way to do this, at the moment it takes about 500ms which is quite a lot
        if AWS_Config().dev_skip_aws_key_check() == "True":
            return
        exception = None
        try:
            self.called_identity()
        except ClientError as client_error:
            exception = client_error.response.get('Error')
        if exception:
            error_code    = exception.get("Code")
            error_message = exception.get('Message')
            message = (f"\tCurrent Security credentials are invalid! \n\n"
                       f"\tPlease check: current environment values, "
                       f"profile name or value in your ~/.aws/credentials file"
                       f"\n\n"
                       f"\tBoto3 Error message: {error_code}  {error_message}")
            self.raise_bad_credentials_exception(message)

    def raise_bad_credentials_exception(self, message):
        if self.print_error_message:
            print("\n*********** OSBot_AWS ***********\n")             # todo move to OSBot_AWS Logging class
            print(f"{message}")
            print("\n*********** OSBot_AWS ***********\n")
        raise Exception(message)