import json
import boto3
import re
import hashlib
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user-table-crud-lambda')  # Replace with your table name

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# Helper function to validate password format
def is_valid_password(password):
    return len(password) >= 8 and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

# Lambda handler
def lambda_handler(event, context):
    try:
        # Extract 'id' from pathParameters
        user_id = event.get("pathParameters", {}).get("id")
        if not user_id:
            return response(400, {"message": "Missing id in path"})

        # Parse and validate the request body
        body = json.loads(event.get("body", "{}"))
        if not body:
            return response(400, {"message": "Request body is required"})

        # Collect validation errors
        errors = []

        # Validate email
        if "email" in body and not is_valid_email(body["email"]):
            errors.append("Invalid email format")

        # Validate password
        if "password" in body:
            if not is_valid_password(body["password"]):
                errors.append("Password must have at least 8 characters and one special character")
            else:
                # Hash the password if valid
                body["password"] = hashlib.md5(body["password"].encode()).hexdigest()

        # If there are validation errors, return them
        if errors:
            return response(400, {"errors": errors})

        # Add updatedAt timestamp
        body["updatedAt"] = datetime.utcnow().isoformat()

        # Build the UpdateExpression and ExpressionAttributeValues
        update_expression = "SET " + ", ".join(f"#{key} = :{key}" for key in body)
        expression_attribute_names = {f"#{key}": key for key in body}
        expression_attribute_values = {f":{key}": value for key, value in body.items()}

        # Update the item in DynamoDB
        table.update_item(
            Key={"id": user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )

        return response(200, {"message": "User updated successfully", "id": user_id})

    except Exception as e:
        print(f"Error occurred: {e}")
        return response(500, {"error": str(e)})

# Helper function to format responses
def response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }
