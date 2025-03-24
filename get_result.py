import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("TripwiseResults")

def handler(event, context):
    request_id = event["queryStringParameters"].get("request_id")

    if not request_id:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.loads({"error": "Missing 'request_id'"})
        }

    response = table.get_item(Key={"request_id": request_id})

    if "Item" not in response:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.loads({"error": "Result not ready"})
        }

        
    raw_json_string = response["Item"]["result"] 
    # Parse & re-dump to remove escaping
    parsed_data = json.loads(raw_json_string)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": parsed_data
    }
