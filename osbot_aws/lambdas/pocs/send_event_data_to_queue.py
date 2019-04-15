from osbot_aws.apis.Queue import Queue


def run(event, context):
    queue_2 = Queue(url='https://sqs.eu-west-2.amazonaws.com/244560807427/unit_tests_temp_queue')
    queue_2.push(event)
    return {'status': 'ok'}