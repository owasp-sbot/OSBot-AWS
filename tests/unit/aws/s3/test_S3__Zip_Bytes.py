from unittest import TestCase

import boto3

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.s3.S3__Zip_Bytes                     import S3__Zip_Bytes
from osbot_aws.aws.sts.STS import STS
from osbot_aws.testing.TestCase__S3                     import TestCase__S3
from osbot_utils.decorators.methods.capture_exception   import capture_exception
from osbot_utils.utils.Dev                              import pprint
from osbot_utils.utils.Objects import obj_info


class test_S3__Zip_Bytes(TestCase__S3):


    #@print_boto3_calls()
    def test_buckets(self):
        with S3__Zip_Bytes(s3=self.s3) as _:
            pprint(AWS_Config().region_name())
            return
            #pprint(_.s3.buckets())
            s3_client = _.s3.client()
            #obj_info(_.s3.client().meta)
            pprint(_.s3.sts().caller_identity())
            #pprint(STS().caller_identity())
            role_arn = 'arn:aws:sts::381492182978:assumed-role/osbot__temp_role_for__test_S3/osbot_sts_session__brmwdja'
            role_name = 'osbot__temp_role_for__test_S3'
            #iam_client = _.s3.iam_assume_role().boto3_client('iam')
            #pprint(iam_client.list_attached_role_policies(RoleName=role_name))
            pprint(IAM(role_name=role_name).role_policies())



