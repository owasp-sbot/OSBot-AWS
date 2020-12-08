from osbot_utils.utils.Files import Files


def run(event, context):
    file_name = event.get('file_name')                                           # get file_name from lambda params
    tmp_path  = '/tmp'                                                           # location of lambda temp folder
    tmp_file  = Files.path_combine(tmp_path,file_name)                           # create file name (in temp folder)

    Files.write(tmp_file, 'some text')                                           # create file (with some text)

    return Files.find(tmp_path + '/*.*')                                         # return list of files in temp folder