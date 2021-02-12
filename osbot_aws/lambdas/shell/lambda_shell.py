from osbot_aws.apis.shell.Lambda_Shell      import lambda_shell

@lambda_shell
def run(event, context=None):
    return 'in lambda shell'
