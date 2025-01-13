import json
import re
import uuid
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

        # Initialize an errors list
        errors = []

        # Extract and validate fields
        email = body.get("email")
        if not email or not validate_email(email):
            errors.append("Invalid or missing email")

        password = body.get("password")
        if not password:
            errors.append("Password is missing")
        elif not validate_password(password):
            errors.append("Password must have at least 8 characters and one special character")

        # Return validation errors, if any
        if errors:
            return create_response(400, {"errors": errors})

        # Generate user data
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        timestamp = current_timestamp()

        user_item = {
            "id": user_id,
            "name": body.get("name", ""),
            "email": email,
            "password": hashed_password,
            "address": body.get("address", ""),
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }

        # Insert into DynamoDB
        table.put_item(Item=user_item)

        return create_response(201, {"message": "User created ", "id": user_id})

    except Exception as e:
        print("Error occurred:", str(e))  # Log the exception
        return create_response(500, {"message": "An internal server error occurred", "details": str(e)})
