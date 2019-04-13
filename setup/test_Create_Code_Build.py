from time                                import sleep
from unittest                            import TestCase
from osbot_aws.apis.IAM                  import IAM
from osbot_aws.helpers.Create_Code_Build import Create_Code_Build


class test_Create_Code_Build(TestCase):

    def setUp(self):
        self.project_name    = 'osbot_aws'
        self.account_id      = IAM().account_id()
        self.api             = Create_Code_Build(account_id=self.account_id, project_name=self.project_name)

    # this needs to be updated to take into account the policies manually added to the arn:aws:iam::244560807427:role/osbot-aws
    # via the AWS Console API
    def test_create_polcies(self):
        policies = {"Cloud-Watch-Policy"     : { "Version": "2012-10-17",
                                                 "Statement": [{   "Sid": "GsBotPolicy",
                                                                   "Effect": "Allow",
                                                                   "Action": [ "logs:CreateLogGroup"  ,
                                                                               "logs:CreateLogStream" ,
                                                                               "logs:PutLogEvents"   ],
                                                                   "Resource": [ cloud_watch_arn ]}]},
                    "Download_Image"         : { "Version": "2012-10-17",
                                                 "Statement": [{   "Effect": "Allow",
                                                                   "Action": [   "ecr:GetAuthorizationToken",
                                                                                 "ecr:BatchCheckLayerAvailability",
                                                                                 "ecr:GetDownloadUrlForLayer",
                                                                                 "ecr:GetRepositoryPolicy",
                                                                                 "ecr:DescribeRepositories",
                                                                                 "ecr:ListImages",
                                                                                 "ecr:DescribeImages",
                                                                                 "ecr:BatchGetImage"],
                                                                   "Resource": "*"}]}}
                    # "Secret-Manager"        : {
                    #                             "Version"  : "2012-10-17",
                    #                             "Statement": [{   "Effect"  : "Allow",
                    #                                               "Action"  : [ "secretsmanager:GetSecretValue","secretsmanager:DescribeSecret"          ],
                    #                                               "Resource": [ "arn:aws:secretsmanager:eu-west-2:244560807427:secret:slack-gs-bot-*"     ,
                    #                                                             "arn:aws:secretsmanager:eu-west-2:244560807427:secret:elastic*"           ,
                    #                                                             "arn:aws:secretsmanager:eu-west-2:244560807427:secret:gsuite*"        ]}]},
                    # "Update_Lambda"         : { "Version"  : "2012-10-17",
                    #                             "Statement": [ {    "Effect": "Allow", "Action" : ["s3:PutObject"         ], "Resource": ["arn:aws:s3:::gs-lambda-tests/dinis/lambdas/gsbot_gsuite_lambdas_gdocs.zip"] },
                    #                                            {    "Effect": "Allow", "Action" : ["lambda:CreateFunction"], "Resource": ["arn:aws:lambda:eu-west-2:244560807427:function:gsbot_gsuite_lambdas_gdocs"] } ]}}


    def test_create(self):
        policies = self.api.policies__with_ecr()
        self.api.create_role_and_policies(policies)
        sleep(5)                                                        # to give time for AWS to sync up internally
        self.api.create_project_with_container__gs_docker_codebuild()
        self.api.code_build.build_start()

