from pbx_gs_python_utils.utils.Files import Files
from pbx_gs_python_utils.utils.Process import Process


def run(event, context):

    executable=event.get('executable')
    params    = event.get('params')
    cwd       = event.get('cwd')
    return Process.run(executable, params = params, cwd=cwd)

    #return Files.contents('/opt/file_in_layer.py')
    return Files.find('/opt/*')
    #return Files.find('/opt/nodejs/node_modules*')
    return 'here 123'