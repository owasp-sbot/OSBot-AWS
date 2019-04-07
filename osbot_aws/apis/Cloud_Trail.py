import datetime

import boto3

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.aws.Boto_Helpers import Boto_Helpers


class Cloud_Trail(Boto_Helpers):

    def __init__(self):
        self.cloudtrail = boto3.client('cloudtrail')

    def events(self):
        endtime = datetime.datetime.utcnow()
        starttime = datetime.datetime.utcnow() - datetime.timedelta(minutes=55)

        return Boto_Helpers.invoke_using_paginator(self.cloudtrail,'lookup_events','Events',
                                                    LookupAttributes=[                ],
                                                    StartTime=starttime,
                                                    EndTime=endtime, MaxResults=1000)