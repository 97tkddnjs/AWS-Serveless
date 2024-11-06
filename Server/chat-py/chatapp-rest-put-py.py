import json
import boto3
import time
import os
from botocore.exceptions import ClientError

# DynamoDB DocumentClient 생성
doc_client = boto3.resource('dynamodb')
api_gateway_client = boto3.client('apigatewaymanagementapi', 
    endpoint_url=f"https://{os.environ['API_GATEWAY_ENDPOINT']}.execute-api.ap-northeast-2.amazonaws.com/dev"
)

def lambda_handler(event, context):
    # 입력 객체 가져오기
    input_object = event
    
    # 해당 채팅방의 접속한 모든 유저를 가져온다.
    params = {
        'TableName': 'chatapp-userlist',
        'IndexName': 'room_id-user_id-index',
        'KeyConditionExpression': '#HashKey = :hkey',
        'ExpressionAttributeNames': { '#HashKey': 'room_id' },
        'ExpressionAttributeValues': {
            ':hkey': input_object['room_id']
        }
    }
    
    try:
        result = doc_client.Table('chatapp-userlist').query(**params)
        print('res1 ', result)
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error querying user list',
                'message': e.response['Error']['Message']
            })
        }

    now = int(time.time() * 1000)  # 현재 시간 (밀리초)
    
    # 채팅 메시지 아이템 구성
    item = {
        'room_id': input_object['room_id'],
        'timestamp': now,
        'message': input_object['text'],
        'user_id': input_object['user_id'],
        'name': input_object['name']
    }

    # 채팅 메시지를 DB에 저장
    try:
        doc_client.Table('chatapp-chat-messages').put_item(Item=item)
    except ClientError as e:
        print('errpor')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error saving chat message',
                'message': e.response['Error']['Message']
            })
        }

    if 'Items' in result:
        for user in result['Items']:
            connection_id = user['connection_id']
            dt = {
                'ConnectionId': connection_id,
                'Data': json.dumps(item)
            }
            try:
                api_gateway_client.post_to_connection(**dt)
            except ClientError as e:
                print(e)
                if e.response['Error']['Code'] == 'GoneException':
                    print(f"Found stale connection, deleting {connection_id}")
                    delete_params = {
                        'TableName': 'chatapp-userlist',
                        'Key': {
                            'connection_id': connection_id
                        }
                    }
                    doc_client.Table('chatapp-userlist').delete_item(**delete_params)

    # 응답 구성
    response = {
        'isBase64Encoded': True,
        'statusCode': 200,
        'headers': {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Expose-Headers": "*",
            "Access-Control-Allow-Origin": "*",
        },
        'body': result.get('Items', [])
    }
    
    return response