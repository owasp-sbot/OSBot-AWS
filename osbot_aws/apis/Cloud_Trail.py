import datetime

import boto3

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.Session import Session


class Cloud_Trail(Boto_Helpers):

    def __init__(self):
        self.cloudtrail = Session().client('cloudtrail')

    def events(self):
        endtime = datetime.datetime.utcnow()
        starttime = datetime.datetime.utcnow() - datetime.timedelta(minutes=55)

        return Boto_Helpers.invoke_using_paginator(self.cloudtrail,'lookup_events','Events',
                                                    LookupAttributes=[                ],
                                                    StartTime=starttime,
                                                    EndTime=endtime, MaxResults=1000)