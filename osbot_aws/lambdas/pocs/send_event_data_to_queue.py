from osbot_aws.apis.Queue import Queue


def run(event, context):
    queue_2 = Queue('unit_tests_temp_queue__2')
    queue_2.push(event)
    return {'status': 'ok'}