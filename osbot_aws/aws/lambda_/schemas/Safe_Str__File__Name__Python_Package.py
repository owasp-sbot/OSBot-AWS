import re
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Name import Safe_Str__File__Name

TYPE_SAFE_STR__FILE__PATH__PYTHON_PACKAGE__REGEX      = re.compile(r'[^a-zA-Z0-9_\-. =]')  # Allow alphanumerics, underscores, hyphens, dots, slashes, spaces and equal

class Safe_Str__File__Name__Python_Package(Safe_Str__File__Name):
    regex = TYPE_SAFE_STR__FILE__PATH__PYTHON_PACKAGE__REGEX
