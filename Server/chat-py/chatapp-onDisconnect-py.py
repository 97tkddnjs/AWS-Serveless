import json
import boto3

# DynamoDB 클라이언트 설정
dynamoDB_client = boto3.client('dynamodb', region_name='ap-northeast-2')

def lambda_handler(event, context):
    # connection_id를 이벤트에서 가져오기
    connection_id = event['requestContext']['connectionId']

    # 삭제할 아이템의 파라미터 설정
    params = {
        'TableName': 'chatapp-userlist',
        'Key': {
            'connection_id': {'S': connection_id}  # connection_id를 문자열로 처리
        }
    }

    try:
        # 삭제 요청을 DynamoDB에 전송
        dynamoDB_client.delete_item(**params)

        return {
            'statusCode': 200,
            'body': json.dumps("Disconnected")  # 성공 응답 반환
        }

    except Exception as e:
        print(e)
        
        return {
            'statusCode': 500,
            'body': json.dumps({'message': "Error disconnecting", 'error': str(e)})  # 에러 응답 반환
        }