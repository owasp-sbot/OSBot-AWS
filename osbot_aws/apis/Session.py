import  boto3
from botocore.config                                    import Config
from botocore.exceptions                                import ClientError
from botocore.session                                   import get_session
from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self
from osbot_utils.decorators.methods.cache               import cache
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.utils.Status                           import status_ok, status_error
from osbot_aws.AWS_Config                               import aws_config
from osbot_aws.exceptions.Session_Bad_Credentials       import Session_Bad_Credentials
from osbot_aws.exceptions.Session_Client_Creation_Fail  import Session_Client_Creation_Fail
from osbot_aws.exceptions.Session_No_Credentials        import Session_No_Credentials


class Session(Kwargs_To_Self):                  # todo: refactor to AWS_Session so it doesn't clash with boto3.Session object
    account_id      = None
    endpoint_url    = None
    config          = None
    profile_name    = None
    region_name     = None                      # keep a copy of this value


    def boto_session(self) -> boto3.Session:
        return get_session()

    @cache
    def botocore_session(self, aws_access_key_id=None , aws_secret_access_key=None , aws_session_token= None, region_name= None, botocore_session=None, profile_name=None ):
        import boto3
        kwargs = {  "aws_access_key_id"     : aws_access_key_id     ,
                    "aws_secret_access_key" : aws_secret_access_key ,
                    "aws_session_token"     : aws_session_token     ,
                    "region_name"           : region_name           ,
                    "botocore_session"      : botocore_session      ,
                    "profile_name"          : profile_name          }
        session = boto3.Session(**kwargs)
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
        import boto3
        return boto3.Session()

    def session_default(self):
        return get_session()

    def client(self, service_name, **kwargs):
        status = self.client_boto3(service_name, **kwargs)
        if status.get('status') == 'ok':
            client = status.get('data',{}).get('client')
            return client
        else:
            raise Session_Client_Creation_Fail(status=status)

    def client_boto3(self,service_name, aws_access_key_id=None, aws_secret_access_key=None, region_name=None, config=None, endpoint_url=None, profile_name=None):                   # todo: refactor add this to resource_boto3
        import boto3
        try:
            self.config       = config       or self.config       or self.default_config                ()
            self.region_name  = region_name  or self.region_name  or aws_config.aws_session_region_name ()
            self.profile_name = profile_name or self.profile_name or aws_config.aws_session_profile_name()
            self.endpoint_url = endpoint_url or self.endpoint_url or self.resolve_endpoint_url_for_service(service_name)

            client_kwargs = dict( service_name = service_name , config = self.config)

            if aws_access_key_id    : client_kwargs['aws_access_key_id'    ] = aws_access_key_id
            if aws_secret_access_key: client_kwargs['aws_secret_access_key'] = aws_secret_access_key
            if self.endpoint_url    : client_kwargs['endpoint_url'         ] = self.endpoint_url
            if self.region_name     : client_kwargs['region_name'          ] = self.region_name

            if self.profile_name and self.profile_name in self.profiles():                                                  # seeing if this is a more efficient way to get the data
                session = boto3.Session(profile_name=self.profile_name, region_name=self.region_name)      # tried to pass this params but had side effects: , botocore_session=self.boto_session()
                client  = session.client(**client_kwargs)
                message = f"Created client_boto3 session using profile: {self.profile_name}"
            else:
                client = boto3.client(**client_kwargs)
                session = None
                message = "Created client_boto3 session using environment variables"             # todo: see if this is 100% correct, or if there are other ways credentials can be found inside boto3 client

            data = {"client" : client, "session" : session }
            return status_ok(message=message, data=data)
        except Exception as error:

            message = f"client_boto3 failed with error: {error}"
            print(message)
            return status_error(message=message, data=None, error=error)

    @cache_on_self
    def default_config(self):
        retries = {
            'max_attempts': 1,  # set retry to 1  (when used 0 it was causing some side effects)
            'mode': 'standard'  # Standard retry mode
        }
        kwargs = dict(retries=retries)
        # if get_env('ENV_NAME__OSBOT_AWS__SESSION__SET_SIGNATURE_VERSION', 'True') == 'True':      # this was causing issues in other clients like lambda # todo: move this to only the S3
        #     kwargs['signature_version'] = 's3v4'                                                  # todo: also document where this is needed
        return Config(**kwargs)

    def profiles(self):
        return self.session().available_profiles

    def profiles_map(self):
        return get_session()._build_profile_map()
        #return self.boto_session()._build_profile_map()

    def resolve_endpoint_url_for_service(self, service):                                   # todo: find a better way to do this mapping to the local_stack services that are supported
        supported_local_stack_services = ['s3', 'lambda','logs']                           # for now only these 3 services have been tested with local stack , all others will ahve the default
        endpoint_url = aws_config.aws_endpoint_url()
        if endpoint_url == 'http://localhost:4566':
            if service in supported_local_stack_services:
                return endpoint_url
            else:
                region = aws_config.aws_session_region_name()
                if region:
                    return f'https://{service}.{region}.amazonaws.com'
                else:
                    return None
        else:
            return endpoint_url

    def resource_boto3(self,service_name, profile_name=None, region_name=None):                 # todo: refactor with client_boto3
        import boto3
        try:
            profile_name = profile_name or aws_config.aws_session_profile_name()
            region_name  = region_name  or aws_config.aws_session_region_name()

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

