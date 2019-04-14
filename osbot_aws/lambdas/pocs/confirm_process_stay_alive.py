import subprocess
from pbx_gs_python_utils.utils.Process import Process


def run(event, context):
    port = event.get('port')
    proc = subprocess.Popen(["python", "-m", "SimpleHTTPServer", port, "&"], cwd='/tmp')
    ps_exec = Process.run('ps',['-aux'])
    return ps_exec
