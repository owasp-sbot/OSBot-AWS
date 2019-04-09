def run(event, context):
    return 'From lambda code, hello {0}'.format(event.get('name'))