import boto3

from osbot_aws.Globals import Globals


class Session:

    @staticmethod
    def client(service_name):                               # todo: add caching to this call
        profile_name = Globals.aws_session_profile_name
        region_name  = Globals.aws_session_region_name
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        return session.client(service_name=service_name)