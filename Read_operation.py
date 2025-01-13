import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user-table-crud-lambda')  # Replace with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # Extract 'id' from pathParameters
        user_id = event.get("pathParameters", {}).get("id")
        if not user_id:
            return response(400, {"message": "Missing id in path"})

        # Query DynamoDB
        result = table.get_item(Key={"id": user_id})
        if "Item" not in result:
            return response(404, {"message": "User not found"})

        return response(200, result["Item"])

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        return response(500, {"error": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }

