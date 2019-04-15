import boto3
from botocore.session import get_session

from osbot_aws.Globals import Globals


class Session:

    def client_boto3(self,service_name):
        try:
            profile_name = Globals.aws_session_profile_name
            region_name  = Globals.aws_session_region_name

            profiles = get_session()._build_profile_map()
            if profile_name in profiles:
                session = boto3.Session(profile_name=profile_name, region_name=region_name)
                return {'status': 'ok', 'client': session.client(service_name=service_name) }
            return { 'status' : 'ok', 'client': boto3.client(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }


    def resource_boto3(self,service_name):          # refactor with client_boto3
        try:
            profile_name = Globals.aws_session_profile_name
            region_name  = Globals.aws_session_region_name

            profiles = get_session()._build_profile_map()
            if profile_name in profiles:
                session = boto3.Session(profile_name=profile_name, region_name=region_name)
                return {'status': 'ok', 'resource': session.resource(service_name=service_name) }
            return { 'status' : 'ok', 'resource': boto3.resource(service_name=service_name)}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error) }

    def client(self, service_name):
        return self.client_boto3(service_name).get('client')

    def resource(self, service_name):
        return self.resource_boto3(service_name).get('resource')
