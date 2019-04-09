


def run(event, context):
    from pbx_gs_python_utils.utils.Files import Files
    return 'checking python utils: {0}'.format(Files.temp_file())