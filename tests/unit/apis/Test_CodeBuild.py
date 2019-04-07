from time import sleep
from unittest                                   import TestCase
from pbx_gs_python_utils.utils.Assert           import Assert
from pbx_gs_python_utils.utils.Dev              import Dev
from pbx_gs_python_utils.utils.aws.CodeBuild    import CodeBuild
from pbx_gs_python_utils.utils.aws.IAM          import IAM

delete_on_setup    = False
delete_on_teardown = False
aws_region         = "eu-west-2"
account_id         = '244560807427'
project_name       = 'Code_Build_Test'
project_repo       = 'https://github.com/pbx-gs/gsbot-build'
service_role       = 'arn:aws:iam::{0}:role/Code_Build_Test'.format(account_id)
#service_role_2     = 'arn:aws:iam::244560807427:role/service-role/gsbot-code-build-service'
project_arn        = 'arn:aws:codebuild:eu-west-2:{0}:project/Code_Build_Test'.format(account_id)
assume_policy      = {'Statement': [ { 'Action': 'sts:AssumeRole',
                                                 'Effect': 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}

#CodeBuildBasePolicy-GSBot_code_build-eu-west-2
class Test_CodeBuild(TestCase):

    @classmethod
    def setUpClass(cls):
        code_build = CodeBuild(project_name=project_name, role_name=project_name)
        iam        = IAM(role_name=project_name)
        if delete_on_setup:
            code_build.project_delete()
            iam.role_delete()
        if code_build.project_exists() is False:
            assert code_build.project_exists() is False
            iam.role_create(assume_policy)                                # create role
            assert iam.role_info().get('Arn') == service_role             # confirm the role exists
            sleep(1)
            code_build.project_create(project_repo, service_role)         # in a non-deterministic way, this sometimes throws the error: CodeBuild is not authorized to perform: sts:AssumeRole

    @classmethod
    def tearDownClass(cls):
        code_build = CodeBuild(project_name=project_name,role_name=project_name)
        iam        = IAM(role_name=project_name)
        assert code_build.project_exists() is True
        assert iam.role_exists()           is True
        if delete_on_teardown:
            code_build.project_delete()
            iam       .role_delete()
            assert code_build.project_exists() is False
            assert iam.role_exists()           is False

    def setUp(self):
        self.code_build = CodeBuild(project_name=project_name,role_name=project_name)
        self.iam        = IAM(role_name=project_name)

    def test_all_builds_ids(self):                      # LONG running test
        ids = list(self.code_build.all_builds_ids())
        Assert(ids).size_is(100)
        ids = list(self.code_build.all_builds_ids(use_paginator=True))
        Assert(ids).is_bigger_than(1000)

    def test_create_policies(self):
        policies = {
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
                                                                   "Resource": "*"}]},
            "CodeBuildBasePolicy" : {"Version"  : "2012-10-17",
                                     "Statement": [ { "Effect"   :   "Allow",
                                                      "Resource" : [ "arn:aws:logs:eu-west-2:244560807427:log-group:/aws/codebuild/GSBot_code_build",
                                                                     "arn:aws:logs:eu-west-2:244560807427:log-group:/aws/codebuild/GSBot_code_build:*"],
                                                      "Action"   : [ "logs:CreateLogGroup",
                                                                     "logs:CreateLogStream",
                                                                     "logs:PutLogEvents" ]},
                                                    { "Effect"   :   "Allow",
                                                      "Resource" : [ "arn:aws:s3:::codepipeline-eu-west-2-*"],
                                                      "Action"   : [ "s3:PutObject",
                                                                     "s3:GetObject",
                                                                     "s3:GetObjectVersion",
                                                                     "s3:GetBucketAcl",
                                                                     "s3:GetBucketLocation"]}]},
            "Cloud_Watch_Policy": {
                                      "Version": "2012-10-17",
                                      "Statement": [ {  "Effect": "Allow",
                                                        "Action": [ "logs:CreateLogGroup",
                                                                    "logs:CreateLogStream",
                                                                    "logs:PutLogEvents" ],
                                                        "Resource": ["*"]},
                                                     {  "Effect": "Allow",
                                                        "Action": ["codecommit:GitPull"],
                                                        "Resource": ["*"] },
                                                     {  "Effect": "Allow",
                                                                  "Action": [ "s3:GetObject",
                                                                              "s3:GetObjectVersion"],
                                                                  "Resource": ["*"]},
                                        {
                                          "Sid": "S3PutObjectPolicy",
                                          "Effect": "Allow",
                                          "Action": [
                                            "s3:PutObject"
                                          ],
                                          "Resource": [
                                            "*"
                                          ]
                                        }
                                      ]
                                    }
                , "Access_Secret_Manager": {
                                                "Version": "2012-10-17",
                                                "Statement": [
                                                    {
                                                        "Sid": "VisualEditor0",
                                                        "Effect": "Allow",
                                                        "Action": [
                                                            "secretsmanager:GetResourcePolicy",
                                                            "secretsmanager:GetSecretValue",
                                                            "secretsmanager:DescribeSecret",
                                                            "secretsmanager:ListSecretVersionIds"
                                                        ],
                                                        "Resource": "arn:aws:secretsmanager:*:*:secret:*"
                                                    }
                                                ]
                                            },
                "Invoke_Lambda_Functions": {
                                                "Version": "2012-10-17",
                                                "Statement": [
                                                    {
                                                        "Sid": "VisualEditor0",
                                                        "Effect": "Allow",
                                                        "Action": "lambda:InvokeFunction",
                                                        "Resource": "arn:aws:lambda:*:*:function:*"
                                                    }
                                                ]
                                            },
                "Create_Update_Lambda_Functions": { "Version": "2012-10-17",
                                                    "Statement": [ {  "Effect": "Allow",
                                                                      "Action": ["lambda:ListFunctions","lambda:GetFunction","lambda:CreateFunction","lambda:UpdateFunctionCode"],
                                                                      "Resource": "arn:aws:lambda:*:*:function:*" } ]},
                "ECS_Management"                : { "Version": "2012-10-17",
                                                    "Statement": [ {  "Effect": "Allow",
                                                                      "Action": ["ecs:ListClusters", "ecs:ListTaskDefinitions"],
                                                                      "Resource": "*" } ]},
                "Pass_Role": {
                                "Version": "2012-10-17",
                                "Statement": [{
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:GetRole",
                                        "iam:PassRole"
                                    ],
                                    "Resource": "arn:aws:iam::244560807427:role/lambda_with_s3_access"
                                }]
                            }
            }


        policies_arns = list(self.code_build.iam.role_policies().values())
        policies_names = list(self.code_build.iam.role_policies().keys())
        self.code_build.iam.role_policies_detach(policies_arns)
        for policies_name in policies_names:
            self.code_build.iam.policy_delete(policies_name)

        self.code_build.policies_create(policies)



    def test_build_start(self):
        build_id     = self.code_build.build_start()
        build_info   = self.code_build.build_wait_for_completion(build_id,1, 60)
        build_phases = build_info.get('phases')

        phase        = build_phases.pop(-2)

        Dev.pprint(phase.get('phaseType'),phase.get('phaseStatus'),phase.get('contexts')[0].get('message') )


    def test_project_builds(self):
        ids = list(self.code_build.project_builds_ids('GSBot_code_build'))
        assert len(self.code_build.project_builds(ids[0:2])) == 3

    def test_project_builds_ids(self):                  # LONG running test
        assert len(list(self.code_build.project_builds_ids('GSBot_code_build'             )))  > 20
        assert len(list(self.code_build.project_builds_ids('pbx-group-security-site'      ))) == 100
        assert len(list(self.code_build.project_builds_ids('GSBot_code_build'       , True)))  > 20
        assert len(list(self.code_build.project_builds_ids('pbx-group-security-site', True)))  > 1200

    def test_project_info(self):
        project = self.code_build.project_info()
        (
            Assert(project).field_is_equal('arn'        , project_arn )
                           .field_is_equal('name'       , project_name)
                           .field_is_equal('serviceRole', service_role)
        )

    def test_projects(self):
        result = self.code_build.projects()
        Assert(result).is_bigger_than(2).is_smaller_than(100)


