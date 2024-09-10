import  gzip
import  json
import  os
import  tempfile
from    io                                                  import BytesIO
from    gzip                                                import GzipFile
from    boto3.s3.transfer                                   import TransferConfig
from    botocore.errorfactory                               import ClientError

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from    osbot_utils.base_classes.Type_Safe                  import Type_Safe
from    osbot_utils.decorators.lists.group_by               import group_by
from    osbot_utils.decorators.lists.index_by               import index_by
from    osbot_aws.apis.Session                              import Session
from    osbot_utils.decorators.methods.cache_on_self        import cache_on_self
from    osbot_utils.decorators.methods.remove_return_value  import remove_return_value
from    osbot_utils.testing.Temp_File                       import Temp_File
from    osbot_utils.utils.Files                             import Files, file_extension
from    osbot_utils.utils.Zip                               import zip_folder

S3_DEFAULT_FILE_CONTENT_TYPE = 'binary/octet-stream'
S3_HTML_PAGE_CONTENT_TYPE    = 'text/html; charset=utf-8'
S3_FILES_CONTENT_TYPES       = { '.js'  : 'application/javascript; charset=utf-8',
                                 '.jpg' : 'image/jpeg'                           ,
                                 '.jpeg': 'image/jpeg'                           ,
                                 '.png' : 'image/png'                            ,
                                 '.txt' : 'text/plain; charset=utf-8'            ,
                                 '.pdf' : 'application/pdf'                      ,
                                 '.html': 'text/html; charset=utf-8'             ,
                                 '.css' : 'text/css; charset=utf-8'              ,
                                 '.svg' : 'image/svg+xml'                        ,
                                 '.gif' : 'image/gif'                            ,
                                 '.webp': 'image/webp'                           ,
                                 '.json': 'application/json; charset=utf-8'      ,
                                 '.xml' : 'application/xml; charset=utf-8'       ,
                                 '.zip' : 'application/zip'                      ,
                                 '.mp3' : 'audio/mpeg'                           ,
                                 '.mp4' : 'video/mp4'                            ,
                                 '.avi' : 'video/x-msvideo'                      ,
                                 '.mov' : 'video/quicktime'                      }


# helper methods

def s3_file_download(s3_bucket, s3_key, use_cache = False):
    return S3().file_download(s3_bucket, s3_key, use_cache)

def s3_file_download_to(s3_bucket, s3_key, target_file, use_cache = False):
    return S3().file_download_to(s3_bucket, s3_key,target_file, use_cache)


class S3(Type_Safe):
    aws_access_key_id       : str = None                                # todo: refactor these client setup details into a common base class since (this is should be usable by all osbot-aws boto3 wrapper classes)
    aws_secret_access_key   : str = None
    endpoint_url            : str = None
    region_name             : str = None
    service_name            : str = 's3'
    tmp_file_folder         : str = 's3_temp_files'
    use_threads             : bool = True


    @cache_on_self
    def client(self):
        kwargs = dict(aws_access_key_id     = self.aws_access_key_id    ,
                      aws_secret_access_key = self.aws_secret_access_key,
                      endpoint_url          = self.endpoint_url         ,
                      region_name           = self.region_name          ,
                      service_name          = self.service_name         )
        return self.session().client(**kwargs)

    # todo: see if we still need this code below to set the region, since the session.client_boto3 should do it
    # @cache_on_self
    # def client(self):
    #     # todo: understand the impact of having to add the endpoint_url below
    #     #       we needed this because (some, not all, which is really weird) buckets
    #     #       were throwing this error when creating the pre-signed URL
    #     #       <Code>SignatureDoesNotMatch</Code>
    #     #           <Message>The request signature we calculated does not match the signature you provided. Check your key and signing method.</Message>
    #     #       this is the comment that gave the solution https://github.com/boto/boto3/issues/1149#issuecomment-793737086
    #     region_name = aws_config.region_name()
    #     # endpoint_url = f'https://s3.{region_name}.amazonaws.com'            # this was causing issues uploading files
    #     # return boto3.client('s3', region_name=region_name,  endpoint_url=endpoint_url)
    #     return boto3.client('s3', region_name=region_name)

    @cache_on_self
    def s3(self):                               # todo replace usages below with this method
        return self.client()

    @cache_on_self
    def s3_resource(self):                                      # todo refactor this method to be called resource()
        return self.session().resource('s3')

    @cache_on_self
    def session(self):
        return Session()

    @remove_return_value(field_name='ResponseMetadata')
    def bucket_notification(self, bucket_name):
        #if self.boto_notification is None : self.boto_notification = self.s3_resource().BucketNotification(bucket_name=bucket_name)
        #return self.boto_notification
        return self.s3().get_bucket_notification_configuration(Bucket=bucket_name)

    def bucket_notification_set_lambda_permission(self, s3_bucket, lambda_arn):
        from osbot_aws.apis.Lambda import Lambda
        statement_id = 'allow_s3_notifications_to_invoke_function'
        action       = 'lambda:InvokeFunction'
        principal    = 's3.amazonaws.com'
        aws_lambda   = Lambda()
        aws_lambda.permission_delete(lambda_arn, statement_id)
        return aws_lambda.permission_add(lambda_arn, statement_id, action, principal, )

    def bucket_notification_create(self, s3_bucket, notification_config):
        try:

            params = { 'Bucket'                   : s3_bucket,
                       'NotificationConfiguration': notification_config }
            # todo: refactor code bellow to an Lambda specific class and tests
            # self.bucket_notification_set_lambda_permission(s3_bucket, lambda_arn)  # configure permissions
               # {
               #  'LambdaFunctionConfigurations': [{
               #                                    'LambdaFunctionArn': lambda_arn,
               #                                    'Events'           : events,
               #                                    'Filter'           : { 'Key': { 'FilterRules': [ {'Name' : 'prefix',
               #                                                                                     'Value': prefix }]}}}]}}
            return self.s3().put_bucket_notification_configuration(**params)
        except Exception as error:
            return {'error': f'{error}'}

    # main methods
    def bucket_arn(self,bucket):
        return 'arn:aws:s3:::{0}'.format(bucket)

    def bucket_create(self, bucket, region):
        try:
            location=self.s3().create_bucket(Bucket=bucket,CreateBucketConfiguration={'LocationConstraint': region }).get('Location')
            return { 'status':'ok', 'data':location}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error)}

    def bucket_delete(self, bucket):
        if self.bucket_exists(bucket) is False:
            return False
        self.s3().delete_bucket(Bucket=bucket)
        return self.bucket_exists(bucket) is False

    def bucket_exists(self, bucket_name):
        try:
            self.s3().head_bucket(Bucket=bucket_name)
            return True
        except:
            return False

    def bucket_not_exists(self, bucket_name):
        return self.bucket_exists(bucket_name) is False

    def buckets(self):
        data = []
        buckets = self.s3().list_buckets()
        if buckets:
            for bucket in buckets.get('Buckets'):
                data.append(bucket['Name'])
        return sorted(data)
        #return sorted(list({ bucket['Name'] for bucket in self.s3().list_buckets().get('Buckets')}))

    def create_pre_signed_url(self, bucket_name, object_name, operation='get_object', expiration=3600):     # 3600 is one hour (60 seconds * 60 minutes)
        response = self.client().generate_presigned_url(operation, Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
        return response

    def dont_use_threads(self):
        self.use_threads = False
        return self

    def files_raw(self, bucket, prefix='', filter=''):
        params = {'Bucket': bucket}
        if isinstance(prefix, str):                                            # if prefix is a string, filter on list_objects_v2
            params['Prefix'] = prefix

        while True:
            resp = self.s3().list_objects_v2(**params)
            try:
                contents = resp['Contents']
            except KeyError:
                return

            for obj in contents:
                key = obj['Key']
                if (not filter) or (filter and filter in key):
                    yield obj
            try:
                params['ContinuationToken'] = resp['NextContinuationToken']     # token for next batch of 1000 results
            except KeyError:
                break

    def find_files(self, bucket, prefix='', filter=''):
        return list({ item['Key'] for item in self.files_raw(bucket, prefix, filter) })

    def file_bytes(self, bucket, key):
        obj = self.s3().get_object(Bucket=bucket, Key=key)                      # get object data from s3
        return obj['Body'].read()                                               # returns all bytes

    def file_content_type(self, bucket, key):
        return self.file_details(bucket, key).get('ContentType')

    def file_content_type_update(self, bucket, key, metadata, content_type):
        file_copy_kwargs = dict(bucket_source      = bucket      ,
                                key_source         = key         ,
                                bucket_destination = bucket      ,
                                key_destination    = key         ,
                                metadata           = metadata    ,      # in S3 we can't update the content type with also updating the metadata
                                content_type       = content_type)      # i guess this is related to the fact that the content_type is stored as a metadata item
        return self.file_copy(**file_copy_kwargs)


    def file_contents(self, bucket, key, encoding='utf-8'):
        return self.file_bytes(bucket,key).decode(encoding)                      # extract body and decode it

    def file_contents_from_gzip(self, bucket, key):
        obj = self.s3().get_object(Bucket=bucket, Key=key)                    # get object data from s3
        bytestream = BytesIO(obj['Body'].read())
        return GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')

    def file_download(self, bucket, key, use_cache = False):
        if bucket and key:
            tmp_file = '/tmp/' + key.replace('/','_')
            if self.file_download_to(bucket, key, tmp_file, use_cache):
                return tmp_file
        return None

    def file_download_and_delete(self, bucket, key):
        tmp_file = '/tmp/' + key.replace('/','_')
        if self.file_download_to(bucket, key, tmp_file):
            self.file_delete(bucket,key)
            return tmp_file
        return None

    def file_download_to(self, bucket, key, target_file, use_cache = False):
        try:
            if use_cache is True:
                if os.path.exists(target_file):
                    return True
            else:
                if os.path.exists(target_file):
                    os.remove(target_file)
            self.s3().download_file(bucket, key, target_file)
            return os.path.exists(target_file)
        except ClientError:                                     # when file not found
            return False

    @remove_return_value('ResponseMetadata')
    def file_copy(self, bucket_source, key_source, bucket_destination, key_destination, metadata=None,
                  content_type=None):
        kwargs_file_copy = dict(CopySource={'Bucket': bucket_source, 'Key': key_source},
                                Bucket=bucket_destination,
                                Key=key_destination)
        if metadata is not None:
            kwargs_file_copy['Metadata'] = metadata
            kwargs_file_copy['MetadataDirective'] = 'REPLACE'
        if content_type is not None:
            kwargs_file_copy['ContentType'] = content_type
        return self.client().copy_object(**kwargs_file_copy)

    def file_create_from_bytes(self, file_bytes, bucket, key):
        return self.file_upload_from_bytes(file_bytes, bucket, key)

    def file_create_from_string_as_gzip(self, file_contents, bucket, key):
        tmp_path = tempfile.NamedTemporaryFile().name

        with gzip.open(tmp_path,'w') as file:                       # create gzip on tmp_file
            file.write(file_contents.encode())                      # write contents
        self.s3().upload_file(tmp_path, bucket,key)               # upload file using s3 api
        os.remove(tmp_path)                                         # delete tmp file
        return True


    def file_create_from_string (self, file_contents, bucket, key):
        with Temp_File(contents=file_contents, extension=file_extension(key)) as temp_file:
            return self.file_upload_to_key(temp_file.file_path, bucket,key)


    def file_delete(self, bucket, key):
        result = self.client().delete_object(Bucket=bucket, Key=key)              # delete file from s3
        return result.get('ResponseMetadata').get('HTTPStatusCode') == 204

    @remove_return_value('ResponseMetadata')
    def file_details(self, bucket, key):
        return self.client().head_object(Bucket = bucket, Key= key)

    def file_metadata(self, bucket, key):
        return self.file_details(bucket, key).get('Metadata')

    def file_metadata_update(self, bucket, key, metadata):
        file_copy_kwargs = dict(bucket_source      = bucket  ,
                                key_source         = key     ,
                                bucket_destination = bucket  ,
                                key_destination    = key     ,
                                metadata           = metadata)
        return self.file_copy(**file_copy_kwargs)

    def file_size_in_Mb(self, bucket, key):
        details = self.file_details(bucket,key)
        return '{0:.1f} Mb'.format(int(details['ResponseMetadata']['HTTPHeaders']['content-length']) / 1024 / 1024)

    def file_exists(self, bucket, key):
        try:
            self.s3().head_object(Bucket=bucket, Key=key)                     # calls head_object function
            return True                                                       # if it works, file exists (return true)
        except:                                                               # if we get an exception
            return False                                                      # file doesn't exists (return false)

    def file_move(self,src_bucket, src_key, dest_bucket, dest_key):
        self.file_copy(src_bucket, src_key, dest_bucket, dest_key)
        self.file_delete(src_bucket, src_key)
        return self.file_exists(dest_bucket, dest_key)

    def file_not_exists(self,bucket, key):
        return self.file_exists(bucket=bucket, key=key) is False

    def file_upload(self,file , bucket, folder):
        if not os.path.isfile(file):                                            # check that file to upload exists locally
            return None                                                         # if not return None

        key = os.path.join(folder, os.path.basename(file))                      # create key from folder and file's filename

        self.file_upload_to_key(file, bucket, key)                                # upload file
        return key                                                              # return path to file uploaded (if succeeded)

    def file_upload_from_bytes(self, file_body, bucket, key):
        self.s3().put_object(Body=file_body, Bucket=bucket, Key=key)
        return True

    # def file_upload_to_key(self, file, bucket, key):
    #     self.s3().upload_file(file, bucket, key)                                # upload file
    #     return True                                                             # return true (if succeeded)

    def file_upload_to_key(self, file, bucket, key, set_content_type=True):
        extra_args   = None
        if set_content_type:
            extension = file_extension(file)
            if extension:
                content_type = S3_FILES_CONTENT_TYPES.get(extension)
                if content_type:
                    extra_args = {'ContentType': content_type}
        upload_args   = [file, bucket, key, extra_args]
        upload_kwargs =  dict(Config=self.transfer_config())
        self.client().upload_file(*upload_args, **upload_kwargs)      # upload file
        return True

    def file_upload_as_temp_file(self, file, bucket):
        key = '{0}/{1}'.format(self.tmp_file_folder, Files.temp_filename(Files.file_extension(file)))
        self.file_upload_to_key(file, bucket, key)
        return key

    def folder_contents(self, s3_bucket, parent_folder='', return_full_path=False):
        folders = []
        files = []
        paginator = self.client().get_paginator('list_objects_v2')
        if not parent_folder.endswith('/'):
            parent_folder += '/'

        operation_parameters = {
            'Bucket': s3_bucket,
            'Delimiter': '/'
        }
        if parent_folder != '/':
            operation_parameters['Prefix'] = parent_folder              # add support for also listing files in the root of the bucket

        for page in paginator.paginate(**operation_parameters):
            # Loop through and add files
            for obj in page.get('Contents', []):
                file_path = obj.get('Key')
                if return_full_path:
                    files.append(file_path)
                else:
                    file_name = file_path.replace(parent_folder, '')
                    if file_name:  # Ensure we don't add the parent folder itself
                        files.append(file_name)

            # Loop through and add subfolders
            for common_prefix in page.get('CommonPrefixes', []):
                folder_path = common_prefix.get('Prefix')
                if return_full_path:
                    folders.append(folder_path)
                else:
                    folder_name = folder_path.replace(parent_folder, '').rstrip('/')
                    folders.append(folder_name)

        return {'folders': folders, 'files': files}


    def folder_files(self, s3_bucket, parent_folder='', return_full_path=False):
        files = []
        paginator = self.client().get_paginator('list_objects_v2')
        if not parent_folder.endswith('/'):
            parent_folder += '/'

        operation_parameters = {
            'Bucket': s3_bucket,
            'Delimiter': '/'
        }
        if parent_folder != '/':
            operation_parameters['Prefix'] = parent_folder              # add support for also listing files in the root of the bucket

        for page in paginator.paginate(**operation_parameters):
            # Loop through the files in the specified folder
            for obj in page.get('Contents', []):
                file_path = obj.get('Key')
                if return_full_path:
                    files.append(file_path)
                else:
                    file_name = file_path.replace(parent_folder, '')
                    files.append(file_name)

        return files

    def folder_list(self, s3_bucket, parent_folder='', return_full_path=False):
        folders = []
        paginator = self.client().get_paginator('list_objects_v2')
        if parent_folder.endswith('/') is False:
            parent_folder += '/'

        operation_parameters = {
            'Bucket': s3_bucket    ,
            'Delimiter': '/'
        }
        if parent_folder != '/':
            operation_parameters['Prefix'] = parent_folder              # add support for also listing files in the root of the bucket

        for page in paginator.paginate(**operation_parameters):
            for common_prefix in page.get('CommonPrefixes', []):
                folder_path = common_prefix.get('Prefix')
                if return_full_path:
                    folders.append(folder_path)
                else:
                    folder_name = folder_path.replace(parent_folder, '').replace('/', '')
                    folders.append(folder_name)
        return folders

    def folder_upload (self, folder, s3_bucket, s3_key):
        file = zip_folder(folder)
        self.file_upload_to_key(file, s3_bucket, s3_key)
        os.remove(file)
        return self

    def policy(self, s3_bucket):
        try:
            return json.loads(self.s3().get_bucket_policy(Bucket=s3_bucket).get('Policy'))
        except:
            return {'Statement': []}

    @index_by
    @group_by
    def policy_statements(self, s3_bucket):
        return self.policy(s3_bucket).get('Statement')

    def policy_statements__resource_arn(self, s3_bucket, trail_name, account_id):
        return f'arn:aws:s3:::{s3_bucket}/{trail_name}/AWSLogs/{account_id}/*'

    def policy_statements__new(self, action, effect, service, resource_arn ):
        return { 'Action'   : action,
                 'Effect'   : effect,
                 'Principal': {'Service': service },
                 'Resource' : resource_arn}

    def policy_statements__without(self, s3_bucket, key, value):
        statements = self.policy_statements(s3_bucket)
        new_list = []
        for statement in statements:
            if statement.get(key) != value:
                new_list.append(statement)
        return new_list

    def policy_create(self, s3_bucket, statements):
        #if (type(statements) is str) is False:
        #    statements = json.dumps(statements)

        policy = json.dumps({ 'Statement': statements   ,
                            'Version'  : '2012-10-17' })
        return self.s3().put_bucket_policy(Bucket= s3_bucket, Policy=policy)
        #return policy

    def transfer_config(self):
        return TransferConfig(use_threads=self.use_threads)