from typing                                                                   import List
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                         import Safe_Float
from osbot_aws.aws.comprehend.schemas.Schema__Comprehend__Toxic_Content_Label import Schema__Comprehend__Toxic_Content_Label


class Schema__Comprehend__Detect_Toxic_Content(Type_Safe):
    labels   : List[Schema__Comprehend__Toxic_Content_Label]
    duration : Safe_Float