import boto3

from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.Session import Session


class Lambdas(Boto_Helpers):
    def __init__(self):
        self.region_name  = 'eu-west-2'
        self._boto_lambda = None

    def boto_lambda(self):
        if self._boto_lambda is None:
            self._boto_lambda = Session().client('lambda')
        return self._boto_lambda

    def list(self):
        data = {}
        functions = self.invoke_using_paginator(self.boto_lambda(), 'list_functions', 'Functions')
        for function in functions:
            data[function['FunctionName']] = function
        return data