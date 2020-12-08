


def run(event, context):
    from osbot_utils.utils.Files import Files
    return 'checking python utils: {0}'.format(Files.temp_file())