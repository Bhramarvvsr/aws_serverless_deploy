import boto3
import urllib.parse
import uuid
import logging

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('bhramarvvsr_tf')  # ✅ Your table name

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", event.get("httpMethod", "GET"))
    logger.info(f"Method: {method}")
    logger.info(f"Event: {event}")

    if method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": """
            <html>
            <head><title>Contact Form</title></head>
            <body>
              <h2>Contact Form</h2>
              <form action="https://vwc5xdy5p6.execute-api.ap-south-1.amazonaws.com/dev/form" method="post">
                Name: <input type="text" name="name"><br>
                Email: <input type="email" name="email"><br>
                Message: <textarea name="message"></textarea><br>
                <input type="submit" value="Submit">
              </form>
            </body>
            </html>
            """
        }

    elif method == "POST":
        body = event.get('body')
        if not body:
            logger.error("POST body is missing")
            return {
                "statusCode": 400,
                "body": "Missing form data"
            }

        params = urllib.parse.parse_qs(body)
        logger.info(f"Parsed params: {params}")

        name = params.get('name', [''])[0]
        email = params.get('email', [''])[0]
        message = params.get('message', [''])[0]
        message_id = str(uuid.uuid4())

        try:
            table.put_item(
                Item={
                    'id': message_id,
                    'name': name,
                    'email': email,
                    'message': message
                }
            )
            logger.info(f"Data saved to DynamoDB with ID: {message_id}")
        except Exception as e:
            logger.error(f"DynamoDB Error: {str(e)}")
            return {
                "statusCode": 500,
                "body": "Error saving to database"
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": """
            <html>
            <head><title>Thank You</title></head>
            <body>
              <h2>Thank you! Your message has been received.</h2>
            </body>
            </html>
            """
        }

    else:
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }
