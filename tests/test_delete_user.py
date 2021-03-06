import boto3
import json
import os
from moto import mock_dynamodb2
from unittest.mock import patch
from src.delete_user import app
from contextlib import contextmanager

table_name = 'Users'

event_data = 'events/delete_user_event.json'
with open(event_data, 'r') as f:
    event = json.load(f)


@contextmanager
def do_test_setup():
    with mock_dynamodb2():
        set_up_dynamodb()
        put_item_dynamodb()
        yield


def set_up_dynamodb():
    conn = boto3.client(
        'dynamodb',
        region_name='us-east-1',
        aws_access_key_id='mock',
        aws_secret_access_key='mock',
    )
    conn.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'},
            {'AttributeName': 'date', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'date', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        },
    )


def put_item_dynamodb():
    conn = boto3.client(
        'dynamodb',
        region_name='us-east-1',
        aws_access_key_id='mock',
        aws_secret_access_key='mock',
    )

    conn.put_item(
        TableName=table_name,
        Item={
            'id': {'S': '#123#123#'},
            'date': {'S': '9999999999.999999'},
            'stage': {'S': 'BACKLOG'},
            'description': {'S': 'New User'}
        }
    )


@patch.dict(os.environ, {
    'TABLE': 'Users',
    'REGION': 'us-east-1',
    'AWSENV': 'MOCK'
})
def test_update_user_200():
    with do_test_setup():
        response = app.lambda_handler(event, '')

        payload = {
            'msg': 'User deleted'
        }

        data = json.loads(response['body'])

        users_table = boto3.resource(
            'dynamodb',
            region_name='us-east-1',
            aws_access_key_id='mock',
            aws_secret_access_key='mock',
        )

        table = users_table.Table(table_name)

        response = table.scan()

        assert event['httpMethod'] == 'DELETE'
        assert data == payload
        assert response['Items'] == []


@patch.dict(os.environ, {
    'TABLE': 'Users',
    'REGION': 'us-east-1',
    'AWSENV': 'MOCK'
})
def test_update_user_400():
    with do_test_setup():
        response = app.lambda_handler({}, '')

        payload = {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }

        assert response == payload
