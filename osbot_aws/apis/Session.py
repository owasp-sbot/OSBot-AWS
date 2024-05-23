import  boto3
from    boto3                   import Session
from botocore.exceptions import ClientError
from    botocore.session        import get_session

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Status import status_ok, status_error

from    osbot_aws.AWS_Config    import AWS_Config
from osbot_aws.exceptions.Session_Bad_Credentials import Session_Bad_Credentials
from osbot_aws.exceptions.Session_Client_Creation_Fail import Session_Client_Creation_Fail
from osbot_aws.exceptions.Session_No_Credentials import Session_No_Credentials


class Session(Kwargs_To_Self):                  # todo: refactor to AWS_Session so it doesn't clash with boto3.Session object
    account_id      = None
    profile_name    = None
    region_name     = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aws_config   = AWS_Config()
        #self.account_id   = self.account_id   or self.aws_config.aws_session_account_id()          # note: we can't do this here, since this will trigger a recursive call with with STS().caller_identity()
        #self.profile_name = self.profile_name or self.aws_config.aws_session_profile_name()
        #self.region_name  = self.region_name  or self.aws_config.aws_session_region_name()

    def boto_session(self) -> Session:
        return get_session()

    @cache
    def botocore_session(self, aws_access_key_id=None , aws_secret_access_key=None , aws_session_token= None, region_name= None, botocore_session=None, profile_name=None ):
        kwargs = {  "aws_access_key_id"     : aws_access_key_id     ,
                    "aws_secret_access_key" : aws_secret_access_key ,
                    "aws_session_token"     : aws_session_token     ,
                    "region_name"           : region_name           ,                   # todo: I don't think we need this
                    "botocore_session"      : botocore_session      ,
                    "profile_name"          : profile_name          }
        session = boto3.Session(**kwargs)

        # todo, move this into a different workflow, since this was adding 300ms 500ms to every creation of an botocore_session object
        #self.credentials(session)                                                       # confirm credentials were found
        #status_ok("[botocore_session] found credentials created base session object")   # todo: after refactoring is done, see if this is still needed

        #self.caller_identity(session)                                                   # confirm credentials are least active (i.e. not expired)
        #status_ok("[botocore_session] credentials are valid and can be used")           # todo: after refactoring is done, see if this is still needed
        return session

    def credentials(self, session=None):
        session = session or self.botocore_session()
        credentials  = session.get_credentials()
        if credentials is None:
            raise Session_No_Credentials()
        return { "access_key"   : credentials.access_key ,
                 "method"       : credentials.method     ,
                 "profile"      : session.profile_name   ,
                 "secret_key"   : credentials.secret_key ,
                 "token"        : credentials.token      }

    def credentials_ok(self):                                   # see if we still need this method
        return self.credentials() is not None
        #sts = self.botocore_session().client('sts')
        #return sts.get_caller_identity()
        # try:
        # except ClientError as exception:
        #
        #     print(exception.response['Error']['Code'] == 'ResourceAlreadyExistsException')
        #     print(exception.response['Error']['Code'])
        #     raise

    def caller_identity(self, session=None):
        session = session or self.botocore_session()
        try:
            return session.client('sts').get_caller_identity()             # few cases where we want to call this directly (since the STS class will use the session() method from this class
        except ClientError as client_error:
            exception = client_error.response.get('Error')
            raise Session_Bad_Credentials(exception)

    @cache_on_self
    def session(self) -> boto3.Session:
        return boto3.Session()

    def session_default(self):
        return get_session()

    def client(self, service_name, region_name=None):
        status = self.client_boto3(service_name, region_name=region_name)
        if status.get('status') == 'ok':
            client = status.get('data',{}).get('client')
            return client
        else:
            raise Session_Client_Creation_Fail(status=status)

    def client_boto3(self,service_name, region_name=None):                   # todo: refactor with resource_boto3
        try:

            self.region_name  = region_name or self.region_name  or self.aws_config.aws_session_region_name()        # todo: figure out better way todo do this
            self.profile_name = self.profile_name or self.aws_config.aws_session_profile_name()
            if self.profile_name and self.profile_name in self.profiles():                                                  # seeing if this is a more efficient way to get the data
                session = boto3.Session(profile_name=self.profile_name, region_name=self.region_name)      # tried to pass this params but had side effects: , botocore_session=self.boto_session()
                client  = session.client(service_name=service_name)
                message = f"Created client_boto3 session using profile: {self.profile_name}"
            else:
                client = boto3.client(service_name=service_name, region_name=self.region_name)
                session = None
                message = "Created client_boto3 session using environment variables"             # todo: see if this is 100% correct, or if there are other ways credentials can be found inside boto3 client

            data = {"client" : client, "session" : session }
            return status_ok(message=message, data=data)
        except Exception as error:

            message = f"client_boto3 failed with error: {error}"
            return status_error(message=message, data=None, error=error)

    def profiles(self):
        return self.session().available_profiles

    def profiles_map(self):
        return get_session()._build_profile_map()

        #return self.boto_session()._build_profile_map()

    def resource_boto3(self,service_name, profile_name=None, region_name=None):                 # todo: refactor with client_boto3
        try:
            profile_name = profile_name or AWS_Config().aws_session_profile_name()
            region_name  = region_name  or AWS_Config().aws_session_region_name()

            profiles = get_session()._build_profile_map()
            if profile_name in profiles:
                session = boto3.Session(profile_name=profile_name, region_name=region_name)
                return {'status': 'ok', 'resource': session.resource(service_name=service_name) }
            return { 'status' : 'ok', 'resource': boto3.resource(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }

    def resource(self, service_name,profile_name=None, region_name=None):
        return self.resource_boto3(service_name,profile_name,region_name).get('resource')

    # client helpers

    # putting all these here in global location so that we limit the calls to authenticate
    # important when making lots of calls of multiple apis (like when running multiple tests)
    # todo find good way to add support for refreshing these references (for exemple to use a different region)
    # todo: refactor this out of this session object
    @cache
    def client_secrets_manager(self):
        return self.client('secretsmanager')

    # todo: refactor into this class (from IAM.py)
    # def access_key__is_key_working(self, access_key):       # refactor to Sessions class
    #     aws_access_key_id     = access_key.get('AccessKeyId')
    #     aws_secret_access_key = access_key.get('SecretAccessKey')
    #     try:
    #         session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    #         session.client('sts').get_caller_identity()
    #         return True
    #     except Exception as error:
    #         assert error.__str__() == 'An error occurred (InvalidClientTokenId) when calling the GetCallerIdentity operation: The security token included in the request is invalid.'
    #         return False

