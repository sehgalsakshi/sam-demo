import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime
from user_schema import get_user_data

def lambda_handler(message, context):

    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }

    table_name = os.environ.get('TABLE', 'Users')
    region = os.environ.get('REGION', 'us-east-1')
    aws_environment = os.environ.get('AWSENV', 'AWS')

    if aws_environment == 'AWS_SAM_LOCAL':
        users_table = boto3.resource(
            'dynamodb',
            endpoint_url='http://dynamodb:8000'
        )
    else:
        users_table = boto3.resource(
            'dynamodb',
            region_name=region
        )

    table = users_table.Table(table_name)
    user = json.loads(message['body'])
    username = user.get('username', None)
    tenant_id = user.get('tenant_id', None)
    password = user.get('password', None)
    if not username or not tenant_id or not password:
        return return_failure_response("User Id/ Password and Tenant Id must be present")
    is_user_unique = len(table.query(
        KeyConditionExpression=Key('username').eq(username)
    )) == 0
    if not is_user_unique:
        return return_failure_response("User Id must be unique")

    is_user_request_valid, user_params = get_user_data(user) 


    if not is_user_request_valid:
        return return_failure_response(user_params)
    
    response = table.put_item(
        TableName=table_name,
        Item=user_params
    )
    print(response)

    return {
        'statusCode': 201,
        'headers': {},
        'body': json.dumps({'msg': 'User created'})
    }

def return_failure_response(error_message):
    return {
        'statusCode': 422,
        'headers': {},
        'body': json.dumps({'msg': error_message})
    }