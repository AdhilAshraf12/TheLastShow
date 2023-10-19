# add your get-obituaries function here

import boto3
from boto3.dynamodb.conditions import Key
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('obituaries')


def lambda_handler(event, context):
    try:
       # Scan the table to get all items
        res = table.scan()

        # Extract the desired attributes from each item and return a list of all items
        items = []
        for item in res['Items']:
            name = item['name']
            born_year = item['born_year']
            died_year = item['died_year']
            obituary = item['obituary']
            image_url = item['image_url']
            mp3_url = item['mp3_url']

            items.append({
                'name': name,
                'born_year': born_year,
                'died_year': died_year,
                'obituary': obituary,
                'image_url': image_url,
                'mp3_url': mp3_url,
            })

        # Return the list of items as the function response
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': str(e)
            })
        }

def get_obituary(image_id):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('your_table_name')

    # Get item from DynamoDB table
    response = table.get_item(
        Key={
            'image_id': image_id
        }
    )

    # Check if item exists
    if 'Item' not in response:
        return None

    # Extract image URL and generated text
    item = response['Item']
    image_url = item['image_url']
    generated_text = item['generated_text']

    # Return obituary
    obituary = {
        'image_id': image_id,
        'image_url': image_url,
        'generated_text': generated_text
    }
    return obituary
