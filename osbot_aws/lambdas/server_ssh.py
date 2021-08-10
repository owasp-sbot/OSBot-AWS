from osbot_utils.utils.Files   import file_create
from osbot_utils.utils.Process import start_process

def run(event, context=None):
    target_host  = event.get('target_host' )
    ssh_key      = event.get('ssh_key'     )
    ssh_key_name = event.get('ssh_key_name')
    ssh_user     = event.get('ssh_user'    )
    ssh_command  = event.get('ssh_command' )
    ssh_key_file = f'/tmp/{ssh_key_name}'
    file_create  (ssh_key_file, ssh_key)
    start_process('chmod', ['600', ssh_key_file])

    result = start_process("ssh", ['-o', 'StrictHostKeyChecking=no',
                                   '-i', ssh_key_file              ,
                                  f'{ssh_user}@{target_host}'      ,
                                    ssh_command])
    return result.get('stdout')