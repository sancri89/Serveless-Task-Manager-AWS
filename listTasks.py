import json, os, boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    claims = event['requestContext']['authorizer']['jwt']['claims']
    user_id = claims['sub']

    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response.get('Items', []))
    }
