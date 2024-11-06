import json
import boto3
import time

# DynamoDB 클라이언트 설정
dynamoDB_client = boto3.client('dynamodb', region_name='ap-northeast-2')

def lambda_handler(event, context):
    # 쿼리 파라미터에서 데이터 가져오기
    Queries = event['queryStringParameters']
    print('connect ',Queries  , 'event ',event)
    input_object = event['queryStringParameters']

    # 로그 출력
    now_time = str(int(time.time() * 1000))
    user_id = now_time

    # 아이템 생성
    item = {
        'room_id': {'S': input_object['room_id']},
        'connection_id': {'S': event['requestContext']['connectionId']},
        'user_id': {'S': user_id},      # 현재 시간을  id로 저장
        'timestamp': {'N': now_time}    # 현재 시간을 밀리초로 변환
    }

    try:
        params = {
            'TableName': 'chatapp-userlist',
            'Item': item
        }

        # 데이터 저장
        dynamoDB_client.put_item(**params)

        response = {
            'isBase64Encoded': True,
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Expose-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
            'body': json.dumps({"statue" : "ok" , "user_id": user_id})  # 응답을 JSON 문자열로 변환
        }

        return response

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': "Error", 'error': str(e)}),  # 예외 메시지 반환
        }