import re
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path


TYPE_SAFE_STR__FILE_PATH__PYTHON_PACKAGE__REGEX      = re.compile(r'[^a-zA-Z0-9_\-./\\ =]')  # Allow alphanumerics, underscores, hyphens, dots, slashes, spaces and equal

class Safe_Str__File__Path__Python_Package(Safe_Str__File__Path):
    regex = TYPE_SAFE_STR__FILE_PATH__PYTHON_PACKAGE__REGEX
