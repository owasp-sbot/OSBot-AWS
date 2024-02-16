from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class Dynamo_DB__Record__Metadata(Kwargs_To_Self):
    created_by       : str
    timestamp_created: int
    timestamp_updated: int
    updated_by       : str

class Dynamo_DB__Record(Kwargs_To_Self):

    data       : dict
    data_binary: bytes
    key_value  : str
    metadata   : Dynamo_DB__Record__Metadata

    def contents(self):
        return self.__locals__()