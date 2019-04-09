def run(event, context):
    return 'BBBB From lambda code, hello {0}'.format(event.get('name'))