import boto3

class Cloud_Watch():
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')



