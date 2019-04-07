def run(event, context):
    return 'hello {0}'.format(event.get('name'))