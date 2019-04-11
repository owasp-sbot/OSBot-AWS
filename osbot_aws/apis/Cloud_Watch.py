import boto3

from osbot_aws.apis.Session import Session


class Cloud_Watch():
    def __init__(self):
        self.cloudwatch = Session().client('cloudwatch')



