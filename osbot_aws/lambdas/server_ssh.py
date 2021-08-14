from osbot_utils.utils.Files import file_create, file_not_exists
from osbot_utils.utils.Process import start_process

def run(event, context=None):
    target_host    = event.get('target_host'   )
    ssh_key        = event.get('ssh_key'       )
    ssh_key_name   = event.get('ssh_key_name'  )
    ssh_user       = event.get('ssh_user'      )
    ssh_command    = event.get('ssh_command'   )
    # port_forward   = event.get('port_forwards' )              # not implemented:
    include_stderr = event.get('include_stderr')
    ssh_key_file   = f'/tmp/{ssh_key_name}'

    if file_not_exists(ssh_key_file):                           # create local key if it doesn't exist
        file_create(ssh_key_file, ssh_key)
        start_process('chmod', ['600', ssh_key_file])

    ssh_params = ['-o', 'StrictHostKeyChecking=no']             # todo: add support for updating the local hosts file
    if ssh_key_file:
        ssh_params.append('-i')                                 # set key to use
        ssh_params.append(ssh_key_file)
    # if port_forward:                                          # todo see if we do actually need this (main use case would be to allow direct HTTP access to an internal server)
    #     local_port  = port_forward.get('local_port' )         #      need to see if Lambda will allow binding ports like this
    #     remote_ip   = port_forward.get('remote_ip'  )
    #     remote_port = port_forward.get('remote_port')
    ssh_params.append(f'{ssh_user}@{target_host}')              # set user and target ip
    ssh_params.append(ssh_command)                              # add command to execute

    result = start_process("ssh", ssh_params)                   # execute command

    if include_stderr:                                          # see if we need to include stderr in return value
        return result.get('stdout') + result.get('stderr')
    return result.get('stdout')