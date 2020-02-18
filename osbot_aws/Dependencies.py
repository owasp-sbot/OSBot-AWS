import os

from pbx_gs_python_utils.utils.Files import Files

#todo: use AWS Lambda Layers
from osbot_aws.apis.S3 import S3


def load_dependencies(targets):
    for target in targets.split(','):
        load_dependency(target.strip())


def load_dependency(target):
    if os.getenv('AWS_REGION') is None:
        return

    from osbot_aws.apis.S3 import S3
    import shutil
    import sys
    s3         = S3()
    s3_bucket  = 'gw-bot-lambdas'
    s3_key     = 'lambdas-dependencies/{0}.zip'.format(target)
    tmp_dir    = Files.path_combine('/tmp/lambdas-dependencies', target)
    #return s3.file_exists(s3_bucket,s3_key)

    if s3.file_exists(s3_bucket,s3_key) is False:
        raise Exception("In Lambda load_dependency, could not find dependency for: {0}".format(target))

    if Files.not_exists(tmp_dir):                               # if the tmp folder doesn't exist it means that we are loading this for the first time (on a new Lambda execution environment)
        zip_file = s3.file_download(s3_bucket, s3_key,False)    # download zip file with dependencies
        shutil.unpack_archive(zip_file, extract_dir = tmp_dir)  # unpack them
        sys.path.append(tmp_dir)                                # add tmp_dir to the path that python uses to check for dependencies
    return Files.exists(tmp_dir)

#todo: use AWS Lambda Layers
def upload_dependency(target):
    s3        = S3()
    s3_bucket = 'gw-bot-lambdas'
    s3_file   = 'lambdas-dependencies/{0}.zip'.format(target)
    path_libs = Files.path_combine('../../../_lambda_dependencies/', target)
    if Files.not_exists(path_libs):
        raise Exception("In Lambda upload_dependency, could not find dependency for: {0}".format(target))
    s3.folder_upload(path_libs, s3_bucket, s3_file)
    return s3.file_exists(s3_bucket, s3_file)