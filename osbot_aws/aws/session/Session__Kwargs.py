from osbot_utils.base_classes.Type_Safe import Type_Safe


class Session__Kwargs(Type_Safe):
    aws_access_key_id       : str = None                                # todo: refactor these client setup details into a common base class since (this is should be usable by all osbot-aws boto3 wrapper classes)
    aws_secret_access_key   : str = None
    endpoint_url            : str = None
    region_name             : str = None