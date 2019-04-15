import gzip
import os
import boto3
import tempfile
from   io import BytesIO
from   gzip import GzipFile
from   botocore.errorfactory import ClientError
from   urllib.parse          import urlparse

from    pbx_gs_python_utils.utils.Files import Files

from osbot_aws.apis.Session import Session


class S3:
    def __init__(self):
        self.boto_client_s3  = None
        self.boto_resource_s3 = None
        self.tmp_file_folder = 's3_temp_files'

    # helpers
    def s3(self):
        if self.boto_client_s3 is None : self.boto_client_s3 = Session().client('s3')
        return self.boto_client_s3

    def s3_resource(self):
        if self.boto_resource_s3 is None : self.boto_resource_s3 = Session().resource('s3')
        return self.boto_resource_s3

    def s3_bucket_notification(self,bucket_name):
        return self.s3_resource().BucketNotification(bucket_name)

    # main methods
    def bucket_arn(self,bucket):
        return 'arn:aws:s3:::{0}'.format(bucket)

    def bucket_create(self, bucket,region):
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

    def bucket_exists(self, bucket):
        try:
            self.s3().head_bucket(Bucket=bucket)
            return True
        except:
            return False



    def buckets(self):
        data = []
        for bucket in self.s3().list_buckets().get('Buckets'):
            data.append(bucket['Name'])
        return sorted(data)
        #return sorted(list({ bucket['Name'] for bucket in self.s3().list_buckets().get('Buckets')}))
        #

    def _files_raw              (self, bucket, prefix='', filter=''                 ):
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

    def find_files              (self, bucket, prefix='', filter=''                 ):
        return list({ item['Key'] for item in self._files_raw(bucket, prefix, filter) })

        #

    def file_contents           (self, bucket, key                                  ):
        obj = self.s3().get_object(Bucket=bucket, Key=key)                    # get object data from s3
        return obj['Body'].read().decode('utf-8')                               # extract body and decode it

    def file_contents_as_gzip   (self, bucket, key                                  ):
        obj = self.s3().get_object(Bucket=bucket, Key=key)                    # get object data from s3
        bytestream = BytesIO(obj['Body'].read())
        return GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')

    def file_download           (self, bucket, key , use_cache = False               ):
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

    def file_download_to        (self, bucket, key, target_file, use_cache = False  ):
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

    def file_copy               (self, src_bucket, src_key, dest_bucket, dest_key   ):
        return self.s3().copy({'Bucket': src_bucket, 'Key': src_key}, dest_bucket,dest_key )

    def file_create_from_string_as_gzip (self, file_contents, bucket, key                   ):
        tmp_path = tempfile.NamedTemporaryFile().name

        with gzip.open(tmp_path,'w') as file:                       # create gzip on tmp_file
            file.write(file_contents.encode())                      # write contents
        self.s3().upload_file(tmp_path, bucket,key)               # upload file using s3 api
        os.remove(tmp_path)                                         # delete tmp file
        return True

    def file_create_from_string (self, file_contents, bucket, key                   ):
        with tempfile.NamedTemporaryFile() as temp:                     # use tempfile api to create temp file
            temp.write(str.encode(file_contents))                       # write contents
            temp.flush()                                                # flush contents to make sure everything has been written
            self.s3().upload_file(temp.name, bucket,key)              # upload file using s3 api
            return True

    def file_delete             (self, bucket, key                                  ):
        result = self.s3().delete_object(Bucket=bucket, Key=key)              # delete file from s3
        return result.get('ResponseMetadata').get('HTTPStatusCode') == 204

    def file_details(self, bucket, key):
        return self.s3().head_object(Bucket = bucket, Key= key);

    def file_size_in_Mb(self, bucket, key):
        details = self.file_details(bucket,key)
        return '{0:.1f} Mb'.format(int(details['ResponseMetadata']['HTTPHeaders']['content-length']) / 1024 / 1024)

    def file_exists(self, bucket, key):
        try:
            self.s3().head_object(Bucket=bucket, Key=key)                     # calls head_object function
            return True                                                       # if it works, file exists (return true)
        except:                                                               # if we get an exception
            return False                                                      # file doesn't exists (return false)

    def file_move               (self,src_bucket, src_key, dest_bucket, dest_key):
        self.file_copy(src_bucket, src_key, dest_bucket, dest_key)
        self.file_delete(src_bucket, src_key)
        return self.file_exists(dest_bucket, dest_key)

    def file_upload             (self,file , bucket, folder):
        if not os.path.isfile(file):                                            # check that file to upload exists locally
            return None                                                         # if not return None

        key = os.path.join(folder, os.path.basename(file))                      # create key from folder and file's filename

        self.file_upload_to_key(file, bucket, key)                                # upload file
        return key                                                              # return path to file uploaded (if succeeded)

    def file_upload_to_key(self, file, bucket, key):
        self.s3().upload_file(file, bucket, key)                                # upload file
        return True                                                             # return true (if succeeded)

    def file_upload_as_temp_file(self, file, bucket):
        key = '{0}/{1}'.format(self.tmp_file_folder, Files.temp_filename(Files.file_extension(file)))
        self.file_upload_to_key(file, bucket, key)
        return key


    def folder_upload (self, folder, s3_bucket, s3_key):
        file = Files.zip_folder(folder)
        self.file_upload_to_key(file, s3_bucket, s3_key)
        os.remove(file)
        return self



# def split_s3_url(s3_url):
#     url = urlparse(s3_url)
#     bucket = url.netloc
#     path = url.path.lstrip('/')
#     return bucket, path