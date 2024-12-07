from osbot_utils.base_classes.Type_Safe         import Type_Safe
from osbot_utils.decorators.methods.type_safe   import type_safe
from osbot_utils.helpers.Safe_Id                import Safe_Id
from osbot_utils.utils.Misc                     import utc_now, date_today

S3_PATH__WHEN_BLOCK_SIZE   = 5

class S3__Key_Generator(Type_Safe):
    root_folder        : str  = None
    server_name        : str  = None
    use_when           : bool = True
    use_date           : bool = True
    use_hours          : bool = True
    use_minutes        : bool = True
    save_as_gz         : bool = False
    split_when         : bool = False
    s3_path_block_size : int = S3_PATH__WHEN_BLOCK_SIZE

    def calculate_minute_block(self, minute):
        block_size   = self.s3_path_block_size                                  # get the block size in minutes (configurable)
        minute_block = f"{(int(minute) // block_size) * block_size:02d}"        # Calculate the block using the configurable block size
        return minute_block

    @type_safe
    def create__for_area_and_file_id(self, area: Safe_Id, file_id: Safe_Id):
        path_elements = self.create_path_elements__from_when(area=area)
        s3_key = self.create_s3_key(path_elements=path_elements, file_id=file_id)
        return s3_key

    def create_path_elements__for_server(self):
        path_elements = []
        if self.root_folder: path_elements.append(self.root_folder)
        if self.server_name: path_elements.append(self.server_name)
        return path_elements

    def create_path_elements__from_when(self, when=None, area: Safe_Id = None):
        path_elements = self.create_path_elements__for_server()
        if area:
            path_elements.append(area)
        if self.use_when:
            if not when:
                when = self.path__for_date_time__now_utc()
            if when:                                            # for the cases when path__for_date_time__now_utc returns and empty value
                path_elements.append(when)



        return path_elements

    def create_s3_key(self, path_elements, file_id):
        path_elements.append(file_id)
        s3_key = '/'.join(path_elements) + '.json'
        if self.save_as_gz:
            s3_key += ".gz"
        return s3_key

    def create_s3_folder(self, path_elements):
        s3_folder = '/'.join(path_elements)
        return s3_folder

    def path__for_date_time__now_utc(self):
        return self.path__for_date_time(utc_now())

    def path__for_date_time(self, date_time):
        minute       = date_time.minute
        date_path    = date_time.strftime('%Y-%m-%d')                          # Format the date as YYYY-MM-DD
        hour_path    = date_time.strftime('%H')                                # Format the hour
        minute_block = self.calculate_minute_block(minute)
        path_components = []
        if self.use_date:
            if self.split_when:
                path_components.extend(date_path.split('-'))
            else:
                path_components.append(date_path   )
        if self.use_hours:
            path_components.append(hour_path   )
        if self.use_minutes:
            path_components.append(minute_block)
        s3_path = '/'.join(path_components)
        return s3_path

    def s3_key(self, area: Safe_Id, file_id: Safe_Id):
        s3_key = self.create__for_area_and_file_id(area=area,file_id=file_id)
        return s3_key

    def s3_folder__for_day(self, day=None):
        path_elements = self.create_path_elements__for_server()
        if day is None:
            day = date_today()
        path_elements.append(day)
        return self.create_s3_folder(path_elements)

    @type_safe
    def s3_folder__for_area(self, area: Safe_Id):
        path_elements = self.create_path_elements__for_server()
        path_elements.append(area)
        return self.create_s3_folder(path_elements)
