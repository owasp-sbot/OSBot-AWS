# OSBot-AWS

![Current Release](https://img.shields.io/badge/release-v2.39.9-blue)

A comprehensive Python library for interacting with AWS services, providing simplified and type-safe wrappers around boto3.

## Overview

OSBot-AWS is a powerful toolkit that makes working with AWS services easier and more pythonic. It provides:

- **Type-safe wrappers** around common AWS services
- **Simplified APIs** that reduce boilerplate code
- **Testing utilities** for local development with MinIO and LocalStack
- **Caching mechanisms** for improved performance
- **Helper classes** for common AWS patterns

## Supported AWS Services

- **IAM** - Identity and Access Management
- **S3** - Simple Storage Service
- **Lambda** - Serverless Functions
- **EC2** - Elastic Compute Cloud
- **ECS** - Elastic Container Service
- **DynamoDB** - NoSQL Database
- **API Gateway** - REST and WebSocket APIs
- **Bedrock** - AI/ML Models
- **Route 53** - DNS Service
- **STS** - Security Token Service
- **CloudWatch Logs** - Logging Service
- **Organizations** - Account Management
- **CodeArtifact** - Package Repository

## Installation

```bash
pip install osbot-aws
```

## Quick Start

### Basic AWS Session Setup

```python
from osbot_aws.apis.Session import Session

# Create a session (uses default AWS credentials)
session = Session()

# Get a client for any AWS service
s3_client = session.client('s3')
lambda_client = session.client('lambda')
```

### Working with S3

```python
from osbot_aws.aws.s3.S3 import S3

s3 = S3()

# Create a bucket
s3.bucket_create('my-bucket', region='us-east-1')

# Upload a file
s3.file_upload_to_key('/path/to/file.txt', 'my-bucket', 'file.txt')

# Download a file
s3.file_download('my-bucket', 'file.txt')

# List files
files = s3.find_files('my-bucket', prefix='folder/')

# Delete a file
s3.file_delete('my-bucket', 'file.txt')
```

### Working with Lambda

```python
from osbot_aws.aws.lambda_.Lambda import Lambda

# Create a Lambda handler
lambda_func = Lambda('my-function')

# Configure the function
lambda_func.set_role('arn:aws:iam::123456789:role/lambda-role')
lambda_func.set_s3_bucket('my-deployment-bucket')
lambda_func.set_s3_key('deployments/my-function.zip')

# Create or update the function
lambda_func.update()

# Invoke the function
result = lambda_func.invoke({'key': 'value'})

# Get function logs
logs = lambda_func.log_group().messages()
```

### Working with DynamoDB

```python
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table

# Create a table handler
table = Dynamo_DB__Table(table_name='my-table', key_name='id')

# Create the table
table.create_table()

# Add a document
document = {'id': '123', 'name': 'John', 'age': 30}
table.add_document(document)

# Get a document
doc = table.document('123')

# Query all documents
all_docs = table.documents_all()

# Delete the table
table.delete_table()
```

### Working with IAM

```python
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.iam.IAM_Role import IAM_Role

# Create a role
role = IAM_Role('my-lambda-role')

# Define assume role policy for Lambda
assume_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

# Create the role
role.create(assume_policy)

# Attach a policy
role.attach_policy('my-policy', policy_document={
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "s3:*",
        "Resource": "*"
    }]
})
```

### Using Temporary Roles

```python
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role

# Create a temporary role with specific permissions
role = IAM_Assume_Role(
    role_name='temp-role',
    policies_to_add=[
        {'service': 's3', 'action': '*', 'resource': '*'}
    ]
)

# Create the role and get credentials
role.create_role()

# Use the role to create a boto3 client
s3_client = role.boto3_client('s3')
```

## Configuration

### Environment Variables

OSBot-AWS uses several environment variables for configuration:

```bash
# AWS Credentials (if not using default profile)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Optional: Skip AWS credential checks (for development)
DEV_SKIP_AWS_KEY_CHECK=True

# Optional: S3 bucket for Lambda deployments
OSBOT_AWS_LAMBDA_S3_BUCKET=my-lambda-bucket
```

### Using .env Files

Create a `.env` file in your project root:

```bash
AWS_PROFILE=my-profile
AWS_DEFAULT_REGION=us-east-1
```

Load it in your code:

```python
from osbot_utils.utils.Env import load_dotenv

load_dotenv()
```

## Advanced Features

### Lambda Dependencies Management

```python
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency import Lambda__Dependency

# Install a package and upload to S3 for Lambda use
dependency = Lambda__Dependency('requests')
dependency.install_and_upload()

# Load dependency inside Lambda function
from osbot_aws.aws.lambda_.boto3__lambda import load_dependency

def lambda_handler(event, context):
    load_dependency('requests')
    import requests
    # Use requests...
```

### S3 Virtual Storage

```python
from osbot_aws.aws.s3.S3__Virtual_Storage import Virtual_Storage__S3
from osbot_aws.aws.s3.S3__DB_Base import S3__DB_Base

# Create virtual storage backed by S3
s3_db = S3__DB_Base()
s3_db.setup()

storage = Virtual_Storage__S3(s3_db=s3_db)

# Use like local storage
storage.json__save('data/config.json', {'setting': 'value'})
data = storage.json__load('data/config.json')
```

### Bedrock AI Integration

```python
from osbot_aws.aws.bedrock.Bedrock import Bedrock

bedrock = Bedrock(region_name='us-east-1')

# List available models
models = bedrock.models()

# Invoke a model
response = bedrock.model_invoke(
    model_id='anthropic.claude-v2',
    body={
        'prompt': 'Hello, how are you?',
        'max_tokens_to_sample': 100
    }
)
```

## Testing

### Using LocalStack

```python
from osbot_aws.aws.s3.S3 import S3
from osbot_aws.aws.session.Session__Kwargs__S3 import Session__Kwargs__S3

# Configure S3 to use LocalStack
session_kwargs = Session__Kwargs__S3(
    endpoint_url='http://localhost:4566'
)

s3 = S3(session_kwargs__s3=session_kwargs)
```

### Using MinIO

```python
from osbot_aws.aws.s3.S3__Minio import S3__Minio

# Connect to MinIO (compatible with S3 API)
minio = S3__Minio()
s3 = minio.s3()

# Use like regular S3
s3.bucket_create('test-bucket', region='us-east-1')
```

## Error Handling

```python
from osbot_aws.aws.sts.STS import check_current_aws_credentials

# Check AWS credentials before proceeding
result = check_current_aws_credentials(raise_exception=False)

if result.get('status') == 'error':
    print(f"AWS credentials error: {result.get('message')}")
else:
    print("AWS credentials are valid")
```

## Best Practices

1. **Always use context managers** when available:
```python
with IAM_Role('my-role') as role:
    role.create(assume_policy)
```

2. **Use type-safe classes** for better IDE support and error checking

3. **Cache expensive operations** using the built-in caching decorators

4. **Use temporary roles** for least-privilege access:
```python
from osbot_aws.aws.s3.S3__with_temp_role import S3__with_temp_role

s3 = S3__with_temp_role()
# Automatically creates and uses a temporary role
```

5. **Handle AWS rate limits** with built-in waiters:
```python
lambda_func.wait_for_function_update_to_complete()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Related Projects

- **OSBot-Utils** - Utility functions and helpers
- **OSBot-Local-Stack** - LocalStack integration utilities

## Support

For issues, questions, or contributions, please visit the GitHub repository.