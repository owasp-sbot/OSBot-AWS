from osbot_aws.apis.Logs import Logs


def run(event, context):
    group_name   = event.get('group_name' )
    stream_name  = event.get('stream_name')
    message      = event.get('message'    )
    logs         = Logs(group_name=group_name,
                        stream_name=stream_name)
    return logs.event_add(message)