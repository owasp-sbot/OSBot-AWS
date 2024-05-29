def run(event, context):
    return '\nFrom lambda code, hello {0}\n'.format(event.get('name'))