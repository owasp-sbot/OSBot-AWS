import subprocess

from osbot_utils.utils.Process import Process


def run(event, context):
    port  = event.get('port')
    count = event.get('count')
    if port and count:
        for i in range(0,count):
            subprocess.Popen(["python", "-m", "http.server", str(port+i),"&"], cwd='/tmp')

    return Process.run('ps',['-aux']).get('stdout')
