import  boto3
from    boto3                import Session
from    botocore.session     import get_session
from    osbot_aws.AWS_Config import AWS_Config
from    osbot_aws.apis.STS   import STS


class Session:

    def boto_session(self):
        return get_session()

    def session(self,profile_name=None, region_name=None) -> Session:                           # todo: refactor with resource_boto3
        profile_name = profile_name or AWS_Config().aws_session_profile_name()
        region_name  = region_name  or AWS_Config().aws_session_region_name()

        profiles = get_session()._build_profile_map()
        if profile_name in profiles:
            return boto3.Session(profile_name=profile_name, region_name=region_name)
        else:
            return boto3.Session()

    def client_boto3(self,service_name, profile_name=None, region_name=None):                   # todo: refactor with resource_boto3
        try:
            profile_name = profile_name or AWS_Config().aws_session_profile_name()
            region_name  = region_name  or AWS_Config().aws_session_region_name()

            # profiles = get_session()._build_profile_map()
            # if profile_name in profiles:
            #     session = boto3.Session(profile_name=profile_name, region_name=region_name)
            if profile_name in self.profiles():                                                  # seeing if this is a more efficient way to get the data
                session = boto3.Session(profile_name=profile_name, region_name=region_name)      # tried to pass this params but had side effects: , botocore_session=self.boto_session()
                return {'status': 'ok', 'client': session.client(service_name=service_name) , "session": session }
            return { 'status' : 'ok', 'client': boto3.client(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }


    def profiles(self):
        return self.boto_session()._build_profile_map()

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

    def client(self, service_name, profile_name=None, region_name=None, check_credentials=True):
        client = self.client_boto3(service_name,profile_name,region_name).get('client')
        if check_credentials:
            STS().check_current_session_credentials()
        return client

    def resource(self, service_name,profile_name=None, region_name=None):
        return self.resource_boto3(service_name,profile_name,region_name).get('resource')
