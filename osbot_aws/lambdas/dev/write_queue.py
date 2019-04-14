from osbot_aws.apis.Queue import Queue


def run(event, context):
    queue_url = event.get('queue_url')
    message   = event.get('message'  )
    Queue(url=queue_url).push(message)
    return {'status': 'ok'}