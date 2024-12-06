from unittest                               import TestCase
from datetime                               import datetime
from osbot_utils.helpers.Safe_Id            import Safe_Id
from osbot_utils.utils.Misc                 import utc_now, date_today
from osbot_aws.aws.s3.S3__Key_Generator     import S3__Key_Generator


class test_S3__Key_Generator(TestCase):

    def test_calculate_minute_block(self):
        with S3__Key_Generator() as _:                                       # Test with default block size (5 minutes)
            minute         = 12
            expected_block = '10'                                            # (12 // 5) * 5 = 10
            result         = _.calculate_minute_block(minute)
            assert result == expected_block

            minute         = 3
            expected_block = '00'                                            # (3 // 5) * 5 = 0
            result         = _.calculate_minute_block(minute)
            assert result == expected_block

            minute         = 59
            expected_block = '55'                                            # (59 // 5) * 5 = 55
            result         = _.calculate_minute_block(minute)
            assert result == expected_block

    def test_create_path_elements__for_server(self):
        with S3__Key_Generator() as _:                                       # Test with both root_folder and server_name
            _.root_folder = 'root'
            _.server_name = 'server1'
            expected      = ['root', 'server1']
            result        = _.create_path_elements__for_server()
            assert result == expected

        with S3__Key_Generator() as _:                                       # Test with only root_folder
            _.root_folder = 'root'
            _.server_name = None
            expected      = ['root']
            result        = _.create_path_elements__for_server()
            assert result == expected

        with S3__Key_Generator() as _:                                       # Test with only server_name
            _.root_folder = None
            _.server_name = 'server1'
            expected      = ['server1']
            result        = _.create_path_elements__for_server()
            assert result == expected

    def test_create_path_elements__from_when(self):
        with S3__Key_Generator() as _:                                       # Test with use_when = True
            _.use_when    = True
            _.root_folder = 'root'
            _.server_name = 'server1'
            when          = '2021-01-01/12/00'

            expected      = ['root', 'server1', when]
            result        = _.create_path_elements__from_when(when)
            assert result == expected

        with S3__Key_Generator() as _:                                       # Test with use_when = False
            _.use_when    = False
            _.root_folder = 'root'
            _.server_name = 'server1'
            when          = '2021-01-01/12/00'

            expected      = ['root', 'server1']
            result        = _.create_path_elements__from_when(when)
            assert result == expected

    def test_create_s3_key(self):
        path_elements = ['root', 'server1', '2021-01-01/12/00']
        file_id       = 'file123'

        with S3__Key_Generator() as _:                                       # Test without gzip
            _.save_as_gz = False
            expected     = 'root/server1/2021-01-01/12/00/file123.json'
            result       = _.create_s3_key(path_elements.copy(), file_id)
            assert result == expected

        with S3__Key_Generator() as _:                                       # Test with gzip
            _.save_as_gz = True
            expected     = 'root/server1/2021-01-01/12/00/file123.json.gz'
            result       = _.create_s3_key(path_elements.copy(), file_id)
            assert result == expected

    def test_create_s3_folder(self):
        path_elements = ['root', 'server1', '2021-01-01']
        expected      = 'root/server1/2021-01-01'

        with S3__Key_Generator() as _:
            result = _.create_s3_folder(path_elements)
            assert result == expected

    def test_path__for_date_time__now_utc(self):
        with S3__Key_Generator() as _:
            expected = _.path__for_date_time(utc_now())
            result   = _.path__for_date_time__now_utc()
            assert result == expected

    def test_path__for_date_time(self):
        date_time = datetime(2021, 1, 1, 12, 34)
        with S3__Key_Generator() as _:
            _.use_date    = True
            _.use_hours   = True
            _.use_minutes = True

            expected_minute_block = _.calculate_minute_block(date_time.minute)
            expected              = f"2021-01-01/12/{expected_minute_block}"
            result                = _.path__for_date_time(date_time)
            assert result == expected

            _.use_date    = False                                            # Test with use_date = False
            expected      = f"12/{expected_minute_block}"
            result        = _.path__for_date_time(date_time)
            assert result == expected

            _.use_hours   = False                                            # Test with use_hours = False
            expected      = expected_minute_block
            result        = _.path__for_date_time(date_time)
            assert result == expected

            _.use_minutes = False                                            # Test with use_minutes = False
            expected      = ''
            result        = _.path__for_date_time(date_time)
            assert result == expected

    def test_s3_folder__for_day(self):

        with S3__Key_Generator() as _:
            expected_date = date_today()
            _.root_folder = 'root'
            _.server_name = 'server1'
            day           = None                                         # Will use date_today()

            expected      = f'root/server1/{expected_date}'
            result        = _.s3_folder__for_day(day)
            assert result == expected

            day           = '2020-12-31'                                 # Test with specific day
            expected      = 'root/server1/2020-12-31'
            result        = _.s3_folder__for_day(day)
            assert result == expected

    def test_create_path_elements__from_when__with_area_and_split(self):
        with S3__Key_Generator() as _:
            # Test with area parameter
            _.use_when = True
            _.root_folder = 'root'
            _.server_name = 'server1'
            when = '2021-01-01/12/00'
            area = Safe_Id('test-area')

            # Test area parameter
            expected = ['root', 'server1', 'test-area', when]
            result = _.create_path_elements__from_when(when=when, area=area)
            assert result == expected

            # Test split_when parameter
            _.split_when = True
            expected = ['root', 'server1', 'test-area', '2021','01','01/12/00']
            result = _.create_path_elements__from_when(when=when, area=area)

            assert result == expected

            # Test with no area but split_when
            _.split_when = True
            area = None
            expected = ['root', 'server1', '2021','01','01/12/00']
            result = _.create_path_elements__from_when(when=when, area=area)
            assert result == expected

            # Test with use_when=False
            _.use_when = False
            area = Safe_Id('test-area')
            expected = ['root', 'server1', 'test-area']
            result = _.create_path_elements__from_when(when=when, area=area)
            assert result == expected

            # Test with actual datetime path generation
            _.use_when = True
            _.split_when = True
            now_path = _.path__for_date_time__now_utc()
            result = _.create_path_elements__from_when(area=area)
            assert len(result) == len(now_path.split('/')) + 3  # root, server1, area + split path
            assert result[0] == 'root'
            assert result[1] == 'server1'
            assert result[2] == 'test-area'

    def test_create__for_area_and_file_id(self):
        with S3__Key_Generator() as _:
            # Basic test with all components
            _.root_folder = 'root'
            _.server_name = 'server1'
            _.use_when = True
            area = Safe_Id('test-area')
            file_id = Safe_Id('test-file')

            result = _.create__for_area_and_file_id(area=area, file_id=file_id)
            assert 'root/server1/test-area' in result
            assert result.endswith('test-file.json')

            # Test with gzip
            _.save_as_gz = True
            result = _.create__for_area_and_file_id(area=area, file_id=file_id)
            assert result.endswith('test-file.json.gz')

            # Test with split_when
            _.split_when = True
            _.save_as_gz = False
            result = _.create__for_area_and_file_id(area=area, file_id=file_id)
            path_parts = result.split('/')
            assert path_parts[0] == 'root'
            assert path_parts[1] == 'server1'
            assert path_parts[2] == 'test-area'
            assert len(path_parts) >= 6  # root/server1/area/date/hour/minute/file
            assert path_parts[-1] == 'test-file.json'

            # Test without when
            _.use_when = False
            result = _.create__for_area_and_file_id(area=area, file_id=file_id)
            assert result == 'root/server1/test-area/test-file.json'

            # Test minimal configuration
            _.root_folder = ''
            _.server_name = ''
            result = _.create__for_area_and_file_id(area=area, file_id=file_id)
            assert result == 'test-area/test-file.json'

    def test_s3_key(self):
        with S3__Key_Generator() as _:
            _.root_folder = 'root'
            _.server_name = 'server1'
            area = Safe_Id('test-area')
            file_id = Safe_Id('test-file')

            result = _.s3_key(area=area, file_id=file_id)
            assert result == _.create__for_area_and_file_id(area=area, file_id=file_id)

            # Test with different configurations
            _.save_as_gz = True
            assert _.s3_key(area=area, file_id=file_id) == _.create__for_area_and_file_id(area=area, file_id=file_id)

            _.split_when = True
            assert _.s3_key(area=area, file_id=file_id) == _.create__for_area_and_file_id(area=area, file_id=file_id)