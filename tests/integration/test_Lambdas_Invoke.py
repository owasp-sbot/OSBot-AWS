import unittest
from time import sleep

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.S3 import S3
from osbot_aws.apis.Logs                import Logs
from osbot_aws.apis.Queue               import Queue
from osbot_aws.helpers.IAM_Policy       import IAM_Policy
from osbot_aws.helpers.Lambda_Package   import Lambda_Package
from osbot_aws.apis.IAM                 import IAM
from osbot_aws.apis.Lambda              import Lambda
from unittest                           import TestCase

# these tests require lambdas to already exist in AWS
from osbot_utils.utils.Dev import Dev


class test_Lambdas_Invoke(TestCase):

    def test_dev_hello_world(self):
        assert Lambda('dev_hello_world').invoke() == 'hello None'

    def test_lambdas_gsbot_gsbot_graph(self):
        assert Lambda('lambdas_gsbot_gsbot_graph').invoke_raw().get('status') == 'ok'

    def test_lambda_write_cloud_watch(self):
        group_name      = '/aws/lambda/unit-tests/test_log_group'
        stream_name     = Misc.random_string_and_numbers(prefix='tmp_stream_')
        message         = 'this is a message sent from an lambda function'
        lambda_name     = 'osbot_aws.lambdas.dev.write_cloud_watch_log'
        logs            = Logs(group_name=group_name, stream_name=stream_name).create()
        lambda_obj      = Lambda_Package(lambda_name)

        payload = {'group_name': group_name, 'stream_name': stream_name, 'message': message}

        assert lambda_obj.invoke(payload).get('status') == 'ok'

        #sleep(0.8)
        # assert logs.messages() == ['this is a message sent from an lambda function']
        assert logs.group_delete() is True

    def test_lambda_write_to_queue(self):
        queue_name  = 'unit_tests_temp_queue'                       # Queue(queue_name).create()
        lambda_name = 'osbot_aws.lambdas.dev.write_queue'
        message     = 'this is a message sent from an lambda function...'
        queue       = Queue(queue_name)
        queue_url   = queue.url()
        payload     = {'queue_url': queue_url, 'message': message}

        lambda_obj  = Lambda_Package(lambda_name)

        assert lambda_obj.invoke(payload) == {'status': 'ok'}
        assert Queue(queue_name).pull()   == message

        # def add_sqs_send_message_priv(role_arn):
        #     role = IAM(role_name='temp_role_for_lambda_invocation')
        #     resource = 'arn:aws:sqs:{0}:{1}:*'.format('eu-west-2', role.account_id())
        #     policy = IAM_Policy(policy_name='SQS_Send_Message').add_statement_allow(['sqs:SendMessage'], [resource])
        #     policy_arn = policy.create().get('policy_arn')
        #     role.role_policy_attach(policy_arn)

        # add_sqs_send_message_priv(lambda_obj.role_arn)


    # bug  NOT WORKING
    @unittest.skip
    def _test_s3_bucket_to_sqs(self):
        s3 = S3()
        queue        = Queue('unit_tests_temp_queue') #.create()
        bucket_name  = 'bucket-42-temp'
        region       = 'eu-west-2'
        lambda_obj   = Lambda_Package('osbot_aws.lambdas.pocs.send_event_data_to_queue').update_with_root_folder()
        lambda_arn   = lambda_obj._lambda.function_Arn()
        bucket_arn   = s3.bucket_arn(bucket_name)
        queue_arn    = queue.arn()
        #lambda_obj.invoke({'a':43})

        #s3.bucket_create(s3_bucket, region)
        def add_notification(source_arn):
            result = lambda_obj._lambda.client().permission_add(
                FunctionName=lambda_arn,
                StatementId='1',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn= source_arn,
                SourceAccount = IAM().account_id()
            )
            Dev.pprint(result)
            #Dev.pprint(result == {  'Statement': '{"Sid":"1","Effect":"Allow","Principal":{"Service":"s3.amazonaws.com"},"Action":"lambda:InvokeFunction","Resource":"arn:aws:lambda:eu-west-2:244560807427:function:osbot_aws_lambdas_pocs_send_event_data_to_queue","Condition":{"StringEquals":{"AWS:SourceAccount":"244560807427"},"ArnLike":{"AWS:SourceArn":"arn:aws:sqs:eu-west-2:244560807427:unit_tests_temp_queue"}}}'})

        #add_notification(bucket_arn)

        #return


        # resource = s3.s3_bucket_notification(bucket_name)
        # config = { 'LambdaFunctionConfigurations': [{ 'LambdaFunctionArn': lambda_arn           ,
        #                                               'Events'           : ['s3:ObjectCreated:*']}]}
        # Dev.pprint(config)
        # Dev.pprint(resource.put(NotificationConfiguration=config))

        #Dev.pprint(resource.lambda_function_configurations)

        #Dev.pprint(s3.s3().get_bucket_notification_configuration(Bucket=bucket_name))

        #bucket_notification = s3.BucketNotification('bucket_name')
        #Dev.pprint(bucket_notification)

        #s3.boto_client_s3().bucket_notification()

        Dev.pprint(queue.pull())
        Dev.pprint(queue.pull())
        #assert s3.bucket_delete(s3_bucket) is True

    # SKIPPED tests

    @unittest.skip
    def _test_sqs_to_lamdba_to_sqs(self):
        queue_1 = Queue('unit_tests_temp_queue__1').create()
        queue_2 = Queue('unit_tests_temp_queue__2').create()
        lambda_obj = Lambda_Package('osbot_aws.lambdas.pocs.send_event_data_to_queue')   #.update_with_root_folder()
        payload = {'queue_url': queue_2.url(), 'message': 'test 123'}

        #queue_1.attributes_update({'VisibilityTimeout': '61'}) # needs to be bigger than lambda timeout

        queue_1_arn  = queue_1.attributes().get('QueueArn')
        function_arn = lambda_obj.aws_lambda.function_Arn()
        #Dev.pprint(lambda_obj.role_arn)            # needed to add the extra priv to pull SQS messages

        #result = lambda_obj._lambda.boto_lambda().list_event_source_mappings(EventSourceArn=queue_1_arn)
        # result = lambda_obj._lambda.boto_lambda().create_event_source_mapping(
        #     EventSourceArn=queue_1_arn,
        #     FunctionName=function_arn,
        #     Enabled=True,
        #     BatchSize=1
        # )

        queue_1.push('some message 1')
        queue_1.push('some message 2')
        queue_1.push('some message 3')
        queue_1.push('some message 4')
        #lambda_obj.invoke(payload)
        sleep(2)

        Dev.pprint(queue_2.pull())
        Dev.pprint(queue_2.pull())
        Dev.pprint(queue_2.pull())
        Dev.pprint(queue_2.pull())

        queue_1.delete()
        queue_2.delete()

    @unittest.skip
    def _test_confirm_tmp_reuse(self):
        lambda_name = 'osbot_aws.lambdas.pocs.confirm_tmp_reuse'                # lambda to execute

        lambda_obj = Lambda_Package(lambda_name).update_with_root_folder()      # create lambda and upload code

        payload_1 = { 'file_name': 'file_1.txt'}                                # first file to create
        result_1  = lambda_obj.invoke(payload_1)                                # invoke lambda function

        payload_2 = {'file_name': 'file_2.txt'}                                 # 2nd file to create
        result_2  = lambda_obj.invoke(payload_2)                                # invoke lambda function again (no update)

        lambda_obj = Lambda_Package(lambda_name).update_with_root_folder()      # update lambda code
        payload_3 = {'file_name': 'file_3.txt'}                                 # 3rd file to create
        result_3   = lambda_obj.invoke(payload_3)                               # invoke lambda function (after update)

        assert len(result_1) is 1                                               # confirm we have 1 temp file in 1st execution
        assert len(result_2) is 2                                               # confirm we have 2 temp files in 2nd execution
        assert len(result_3) is 1                                               # confirm we have 1 temp files in 3rd execution

        assert '/tmp/file_1.txt' in result_1                                    # confirm 1st file was there on 1st execution

        assert '/tmp/file_1.txt' in result_2                                    # confirm 1st file was there on 2nd execution
        assert '/tmp/file_2.txt' in result_2                                    # confirm 2nd file was there on 2nd execution

        assert '/tmp/file_3.txt' in result_3                                    # confirm 3rd file was there on 3rd execution

        lambda_obj.delete()                                                     # delete lambda

    @unittest.skip
    def _test_confirm_process_stay_alive(self):

        lambda_name = 'osbot_aws.lambdas.pocs.confirm_process_stay_alive'       # lambda to execute

        lambda_obj = Lambda_Package(lambda_name).update_with_root_folder()      # create lambda and upload code

        result_1 = lambda_obj.invoke({'port': 11111, 'count': 3
                                      })
        result_2 = lambda_obj.invoke()
        sleep(1)
        result_3 = lambda_obj.invoke()
        sleep(10)
        result_4 = lambda_obj.invoke()

        print()
        print('\n***1st Execution***\n'               , result_1)
        print('\n***2nd Execution (no delay)***\n'    , result_2)
        print('\n***3rd Execution (1 sec delay) ***\n', result_3)
        print('\n***4th Execution (10 sec delay)***\n', result_4)














        # result_1 = lambda_obj.invoke({'port': "11111"})
        # result_2 = lambda_obj.invoke({'port': "22222"})
        # result_3 = lambda_obj.invoke({'port': "33333"})
        # result_4 = lambda_obj.invoke({'port': "44444"})
        #
        # Dev.print(result_1.get('stdout'))
        # #sleep(2)
        # Dev.print(result_2.get('stdout'))
        # #sleep(2)
        # Dev.print(result_3.get('stdout'))
        # #sleep(2)
        # Dev.print(result_4.get('stdout'))









    @unittest.skip('Long running test (20Secs) move to separate class')
    def _test_lambda_write_cloud_watch__with_asserts(self):
        group_name      = '/unit-tests/test_log_group'
        stream_name     = Misc.random_string_and_numbers(prefix='tmp_stream_')
        message         = 'this is a message sent from an lambda function'
        lambda_name     = 'osbot_aws.lambdas.dev.write_cloud_watch_log'
        log_group_arn   = 'arn:aws:logs:eu-west-2:244560807427:log-group:{0}*'.format(group_name)
        policy_name     = 'temp_policy_for_lambda_write_cloud_watch'
        role_name       = 'temp_role_for_lambda_invocation'
        policy_actions  = ['logs:PutLogEvents']

        logs = Logs(group_name= group_name,stream_name=stream_name)
        logs.group_create()
        logs.stream_create()

        iam_role        = IAM(role_name=role_name)
        iam_policy      = IAM_Policy(policy_name=policy_name)
        iam_policy.add_statement_allow(policy_actions,[log_group_arn])

        policy_arn = iam_policy.create(delete_before_create=True).get('policy_arn')

        assert iam_policy.exists()           is True
        assert iam_role.role_exists()        is True
        assert logs.group_exists()           is True
        assert logs.stream_exists()          is True
        assert set(iam_role.role_policies()) == {'AWSXrayWriteOnlyAccess'                    ,
                                                 'policy_temp_role_for_lambda_invocation'    }

        iam_role.role_policy_attach(policy_arn)

        assert set(iam_role.role_policies()) == { 'AWSXrayWriteOnlyAccess'                   ,
                                                  'policy_temp_role_for_lambda_invocation'   ,
                                                  'temp_policy_for_lambda_write_cloud_watch' }

        sleep(10)                                        # wait for AWS to propagate role update
        payload = { 'group_name' : group_name  ,
                    'stream_name': stream_name ,
                    'message'    : message     }
        lambda_obj = Lambda_Package(lambda_name)        #.update_with_root_folder()
        result     = lambda_obj.invoke(payload)

        sleep(1)                                        # wait for Cloudwatch to update
        assert result.get('status') == 'ok'
        assert logs.messages() == [message]

        assert iam_policy.delete()           is True
        assert logs.group_delete()           is True
        assert logs.group_exists()           is False
        assert set(iam_role.role_policies()) == {'AWSXrayWriteOnlyAccess'                    ,
                                                'policy_temp_role_for_lambda_invocation'    }


    @unittest.skip
    def _test_run_lambdas_in_multiple_accounts(self):

        from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda
        AWS_Config().set_aws_session_profile_name('gs-detect-aws')
        AWS_Config().set_lambda_s3_bucket('gs-detect-lambda')

        with Temp_Lambda() as _:
            _.invoke_raw().get('status') == 'ok'

        AWS_Config().set_aws_session_profile_name('default')












































