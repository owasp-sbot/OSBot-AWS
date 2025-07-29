import boto3, zipfile, sys, io, os

def ping():
    return 'pong'


def load_dependency(package_name):                                              # Load a single dependency from S3
    if os.getenv('AWS_REGION') is None:                                         # skip if we are not running inside an AWS Lambda function
        return

    sts         = boto3.client('sts')                                           # Get account and region for bucket name
    account_id  = sts.get_caller_identity()['Account']
    region_name = boto3.session.Session().region_name
    bucket_name = f'{account_id}--osbot-lambdas--{region_name}'
    s3_key      = f'lambdas-dependencies/{package_name}.zip'
    temp_folder = f'/tmp/lambdas-dependencies/{package_name}'

    s3          = boto3.client('s3')
    response    = s3.get_object(Bucket=bucket_name, Key=s3_key)                 # Download dependency
    zip_bytes   = response['Body'].read()

    os.makedirs(temp_folder, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:                # extract it to dependencies folder
        zip_ref.extractall(temp_folder)

    sys.path.append(temp_folder)
    return f'{package_name} (loaded from S3)'


def load_dependencies(packages):                                        # Load multiple dependencies - just calls load_dependency for each
    if isinstance(packages, str):                                       # Ensure packages is a list
        packages = [packages]

    return [load_dependency(package_name) for package_name in packages]