def run(event, context):
    return '\n.....using run v3.... Created from a Docker image\n....Hello {0}\n'.format(event.get('name'))