def run(event, context):
    return '\n....Created from a Docker image\nHello {0}\n'.format(event.get('name'))