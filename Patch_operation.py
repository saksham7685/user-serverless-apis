import json
import re
import hashlib
from datetime import datetime
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user-table-crud-lambda')  # Replace with your table name

# Validate email
def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# Validate password
def validate_password(password):
    return len(password) >= 8 and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

# Hash password
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Get current timestamp
def current_timestamp():
    return datetime.utcnow().isoformat()

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
        print("Event received:", event)  # Log the raw event

        # Handle cases where the body is either a string or a dictionary
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)
        elif isinstance(body, dict):
            body = body  # Already a dictionary
        else:
            return create_response(400, {"message": "Invalid request format"})

        print("Parsed body:", body)  # Log the parsed body

        # Extract path parameters
        path_parameters = event.get("pathParameters", {})
        user_id = path_parameters.get("id")
        if not user_id:
            return create_response(400, {"message": "User ID is required "})

        # Initialize an errors list
        errors = []

        # Validate fields
        if "email" in body and not validate_email(body["email"]):
            errors.append("Invalid email format")

        if "password" in body:
            if not validate_password(body["password"]):
                errors.append("Password must have at least 8 characters and one special character")
            else:
                body["password"] = hash_password(body["password"])  # Hash password if valid

        # Check for other fields if needed
        if "name" in body and not body["name"].strip():
            errors.append("Name can't be empty!!")
        if "address" in body and not body["address"].strip():
            errors.append("Address can't be empty !!")

        # Return validation errors, if any
        if errors:
            return create_response(400, {"errors": errors})

        # Build the update expression for DynamoDB
        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}
        for key, value in body.items():
            update_expression += f"#key_{key} = :val_{key}, "
            expression_attribute_names[f"#key_{key}"] = key
            expression_attribute_values[f":val_{key}"] = value

        # Add updatedAt timestamp
        update_expression += "#key_updatedAt = :val_updatedAt"
        expression_attribute_names["#key_updatedAt"] = "updatedAt"
        expression_attribute_values[":val_updatedAt"] = current_timestamp()

        # Update the item in DynamoDB
        table.update_item(
            Key={"id": user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )

        return create_response(200, {"message": "User updated "})

    except Exception as e:
        print("Error occurred:", str(e))  # Log the exception
        return create_response(500, {"message": "internal server error", "details": str(e)})
