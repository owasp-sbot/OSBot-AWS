from osbot_aws.helpers.SQS_Queue import SQS_Queue


def run(event, context):
    queue_2 = SQS_Queue(url='https://sqs.eu-west-2.amazonaws.com/244560807427/unit_tests_temp_queue')
    queue_2.push(event)
    return {'status': 'ok'}