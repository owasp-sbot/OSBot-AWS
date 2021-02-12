from osbot_aws.apis.shell.Shell_Server import Shell_Server

def run(event, context=None):
    return Shell_Server().invoke(event)