from os import environ

from osbot_aws.aws.s3.S3                         import S3
from osbot_aws.apis.shell.Lambda_Shell           import lambda_shell
from osbot_aws.aws.sts.STS                       import STS


def lambda_handler(event, context):
    s3 = S3()
    body = s3.buckets()
    return {
        'statusCode': 200,
        'body'      : body
    }
