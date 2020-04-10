def run(event, context):
    from osbot_aws.apis.shell.Shell_Server import Shell_Server
    return Shell_Server().invoke(event)

    # executable=event.get('executable')
    # params    = event.get('params')
    # cwd       = event.get('cwd')
    # return Process.run(executable, params = params, cwd=cwd)
    #
    # #return Files.contents('/opt/file_in_layer.py')
    # return Files.find('/opt/*')
    # #return Files.find('/opt/nodejs/node_modules*')
    # return 'here 123'