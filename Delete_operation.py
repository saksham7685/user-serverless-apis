import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user-table-crud-lambda')  # Replace with your DynamoDB table name

# Create response
def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }

# Lambda handler
def lambda_handler(event, context):
    try:
        # Log the event for debugging
        print("Event received:", event)

        # Extract path parameters
        path_parameters = event.get("pathParameters", {})
        user_id = path_parameters.get("id")

        # Check if the user ID is provided
        if not user_id:
            return create_response(400, {"message": "id is required"})

        # Check if the item exists using get_item
        response = table.get_item(
            Key={"id": user_id}
        )

        # If the item doesn't exist, return 404
        if 'Item' not in response:
            return create_response(404, {"message": f"User ID {user_id} not found"})

        # If the item exists, proceed with delete operation
        delete_response = table.delete_item(
            Key={"id": user_id}
        )

        # If the delete operation is successful, return 200
        return create_response(200, {"message": f"User ID {user_id} deleted "})

    except Exception as e:
        print("Error occurred:", str(e))  # Log the exception
        return create_response(500, {"message": "An internal server error occurred", "details": str(e)})
