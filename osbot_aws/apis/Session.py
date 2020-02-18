import boto3
from botocore.session import get_session

from osbot_aws.Globals import Globals


class Session:

    def session(self,profile_name=None, region_name=None):
        profile_name = profile_name or Globals.aws_session_profile_name
        region_name  = region_name  or Globals.aws_session_region_name

        profiles = get_session()._build_profile_map()
        if profile_name in profiles:
            return boto3.Session(profile_name=profile_name, region_name=region_name)
        else:
            return boto3.Session()

    def client_boto3(self,service_name, profile_name=None, region_name=None):
        try:
            profile_name = profile_name or Globals.aws_session_profile_name
            region_name  = region_name  or Globals.aws_session_region_name

            profiles = get_session()._build_profile_map()
            if profile_name in profiles:
                session = boto3.Session(profile_name=profile_name, region_name=region_name)
                return {'status': 'ok', 'client': session.client(service_name=service_name) }
            return { 'status' : 'ok', 'client': boto3.client(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }


    def resource_boto3(self,service_name, profile_name=None, region_name=None):          # refactor with client_boto3
        try:
            profile_name = profile_name or Globals.aws_session_profile_name
            region_name  = region_name  or Globals.aws_session_region_name

            profiles = get_session()._build_profile_map()
            if profile_name in profiles:
                session = boto3.Session(profile_name=profile_name, region_name=region_name)
                return {'status': 'ok', 'resource': session.resource(service_name=service_name) }
            return { 'status' : 'ok', 'resource': boto3.resource(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }

    def client(self, service_name, profile_name=None, region_name=None):
        return self.client_boto3(service_name,profile_name,region_name).get('client')

    def resource(self, service_name,profile_name=None, region_name=None):
        return self.resource_boto3(service_name,profile_name,region_name).get('resource')
