class Aws_Utils:

    @staticmethod
    def run_code_in_lambda(code):
        file_Path = 'temp_code/code.py'
        temp_Dir  = 'temp_code'
        zip_file  = 'temp_code.zip'

        def create_temp_files():
            if not os.path.exists(temp_Dir):
                os.mkdir(temp_Dir)
            with open(file_Path, "w+") as f:
                f.write(code)

        def delete_temp_files():
            os.remove(file_Path)
            os.remove(zip_file)
            os.rmdir(temp_Dir)

        create_temp_files()

        name      = 'dynamic_code'
        role      = 'arn:aws:iam::244560807427:role/lambda_basic_execution'
        handler   = 'code.dynamic_method'
        s3_bucket = 'gs-lambda-tests'
        s3_key    = 'dinis/lambda-using-dynamic-code.zip'

        aws = Aws_Cli()
        aws.lambda_delete_function(name)
        aws.s3_upload_folder      (temp_Dir, s3_bucket, s3_key)
        aws.lambda_create_function(name, role, handler, s3_bucket, s3_key)

        (result, response) = aws.lambda_invoke_function(name, {})

        aws.lambda_delete_function(name)
        delete_temp_files()
        return result

    @staticmethod
    def zip_folder(root_dir):
        return shutil.make_archive(root_dir, "zip", root_dir)