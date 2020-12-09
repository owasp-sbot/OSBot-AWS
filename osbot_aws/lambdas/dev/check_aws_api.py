
def run(event, context):
    from osbot_aws.AWS_Config import AWS_Config
    return 'checking aws api: {0}'.format(AWS_Config)