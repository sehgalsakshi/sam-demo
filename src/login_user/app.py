import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime
from validate_password import check_password

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
    password = user.get('password', None)
    if not username or not password:
        return return_failure_response("User Id/ Password must be present")
    user_document = table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    if (len(user_document)) == 0:
        return return_failure_response("User not found")
    hashed_password = user_document['password_salt']
    is_password_correct = check_password(password, hashed_password)
    if not is_password_correct:
        return_failure_response('Incorrect password')
    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps({'msg': 'Login successfull'})
    }

def return_failure_response(error_message):
    return {
        'statusCode': 422,
        'headers': {},
        'body': json.dumps({'msg': error_message})
    }