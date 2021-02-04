from osbot_aws.helpers.SQS_Queue import SQS_Queue


def run(event, context):
    queue_url = event.get('queue_url')
    message   = event.get('message'  )
    Queue(url=queue_url).push(message)
    return {'status': 'ok'}