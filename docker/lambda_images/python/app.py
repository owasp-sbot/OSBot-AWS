def run(event, context):
    return '\nCreated from a Docker image\nHello {0}\n'.format(event.get('name'))