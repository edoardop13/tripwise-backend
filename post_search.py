import json
import boto3
import uuid

sqs = boto3.client("sqs", region_name="eu-central-1")
try:
    response = sqs.get_queue_url(QueueName="TripwiseQueue")
    QUEUE_URL = response["QueueUrl"]
except sqs.exceptions.QueueDoesNotExist:
    print("Errore: La coda TripwiseQueue non esiste")
    QUEUE_URL = None

def handler(event, context):
    body = json.loads(event["body"])
    city = body.get("city")
    month = body.get("month")
    days = body.get("days")
    number_of_people = body.get('people', 1)
    withKids = body.get('withKids', False)

    missing_params = []
    if not city:
        missing_params.append("city")
    if not days:
        missing_params.append("days")
    if not month:
        missing_params.append("month")

    if missing_params:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing required parameter(s)",
                "missing_params": missing_params
            })
        }

    request_id = str(uuid.uuid4())

    message = {
        "request_id": request_id, 
        "city": city, 
        "days": days,
        "number_of_people": number_of_people,
        "month": month,
        "withKids": withKids
    }
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(message))

    return {
        "statusCode": 202,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"request_id": request_id})
    }
