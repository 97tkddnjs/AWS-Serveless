import json
import boto3
from boto3.dynamodb.conditions import Key

# DynamoDB 클라이언트 설정

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('chatapp-chat-messages')

def lambda_handler(event, context):
    print('get param ', event)

    # 쿼리 파라미터에서 room_id 가져오기 (현재는 'test'로 하드코딩)
    room_id = 'test'  # event['queryStringParameters'].get('room_id', 'defaultRoomId')
    
    print('room_id ', room_id)

    # DynamoDB에서 데이터 조회
    try:
        response = table.query(
            KeyConditionExpression=Key('room_id').eq(room_id)
        )
        print('res : ', response)
        # 응답 생성
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Expose-Headers': '*',
                'Access-Control-Allow-Origin': '*',
            },
            'body': response.get('Items', [])  # 조회된 아이템이 없으면 빈 리스트
        }
    except Exception as e:
        print(e)
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps('error')
        }