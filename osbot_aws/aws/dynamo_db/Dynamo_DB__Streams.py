from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Dynamo_DB__Streams(Kwargs_To_Self):

    dynamo_db_table : Dynamo_DB__Table



