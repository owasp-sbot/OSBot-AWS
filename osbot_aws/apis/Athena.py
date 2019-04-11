import boto3
import json
import time

from osbot_aws.apis.Session import Session


class Athena:
    def __init__(self):
        self.aws_athena = Session().client('athena')

    def execute_query_and_return_csv(self, query, database,s3_output):
        query_id = self.start_query(query, database, s3_output)
        self.wait_for_query(query_id)
        return self.query_csv(query_id)

    def query_csv(self,query_id):
        details = self.query_details(query_id)
        return details.get('QueryExecution').get('ResultConfiguration').get('OutputLocation')

    def query_details(self, query_id):
        return  self.aws_athena.get_query_execution(QueryExecutionId=query_id)

    def query_status(self, query_id):
        exectution = self.aws_athena.get_query_execution(QueryExecutionId=query_id)
        return exectution.get('QueryExecution').get('Status').get('State')

    def start_query(self, query, database, s3_output):
        response = self.aws_athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': s3_output,
            }
        )
        return response.get('QueryExecutionId')

    def query_as_json(self, query_id):
        return json.dumps(self.query_results(query_id))

    def query_results(self, query_id, next_Token = None):
        if next_Token is None:
            results = self.aws_athena.get_query_results(QueryExecutionId = query_id)
        else:
            results = self.aws_athena.get_query_results(QueryExecutionId=query_id, NextToken=next_Token)

        headers       = [h['Name'] for h in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        query_results = []

        for i, row in enumerate(results['ResultSet']['Rows']):
            if i == 0 and next_Token is None:
                continue
            row_data = {}
            for j, value in enumerate(row['Data']):
                row_data[headers[j]] = value['VarCharValue']
            query_results.append(row_data)
        return query_results, results.get('NextToken')

    def wait_for_query(self, query_id):
        while True:
            status = self.query_status(query_id)
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                return self
            time.sleep(0.2)     # 200,s



