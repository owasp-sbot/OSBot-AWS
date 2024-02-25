import zlib

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Json import json_dumps
from osbot_utils.utils.Misc import str_to_bytes


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

    def compress_binary_data(self):
        """Compresses the binary data stored in data_binary using zlib with maximum compression."""
        if self.data_binary is not None:
            self.data_binary = zlib.compress(self.data_binary, level=9)  # Level 9 for maximum compression
        return self

    def uncompress_binary_data(self):
        """Decompresses the binary data stored in data_binary using zlib."""
        if self.data_binary is not None:
            self.data_binary = zlib.decompress(self.data_binary)
        return self

    def set_binary_data__from_dict(self, data_as_str):
        data_as_str = json_dumps(data_as_str, pretty=False)
        self.data_binary = str_to_bytes(data_as_str)
        return self

    def set_binary_data__from_str(self, data_as_str):
        self.data_binary = str_to_bytes(data_as_str)
        return self

