# add your create-obituary function here
import base64
import hashlib
import json
import os
import time
import boto3
import requests
from requests_toolbelt.multipart import decoder




dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('image_table')



ssm = boto3.client('ssm')

params = ssm.get_parameters_by_path(
    Path='/the-last-show/', WithDecryption=True)

params = {item['Name']: item['Value'] for item in params['Parameters']}


def get_param(param_name):
    return params[param_name]



def upload_to_cloudinary(filename, resource_type="image", ):
    """Uploads file at filename path to Cloudinary"""
    api_key = get_param("/the-last-show/cloud-api-key")
    cloud_name = "da8urr8xp"
    api_secret = get_param("/the-last-show/cloud-api-secret")
    timestamp = int(time.time())

    body = {
        "api_key": api_key,
        "timestamp": timestamp,
        "eager": "e_art:zorro"}
    files = {
        "file": open(filename, "rb")}

    body["signature"] = create_signature(body, api_secret)
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload"
    res = requests.post(url, data=body, files=files)
    if resource_type == "image":
        return res.json()["eager"][0]["secure_url"]
    else:
        return res.json()["secure_url"]


def create_signature(body, api_secret):
    exclude = ["api_key", "resource_type", "cloud_name"]
    sorted_body = sort_dictionary(body, exclude)
    query_string = create_query_string(sorted_body)
    query_string_appended = f"{query_string}{api_secret}"
    hashed = hashlib.sha1(query_string_appended.encode())
    signature = hashed.hexdigest()
    return signature


def sort_dictionary(dictionary, exclude):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[0]) if k not in exclude}


def create_query_string(body):
    query_string = ""
    for idx, (k, v) in enumerate(body.items()):
        query_string += f"{k}={v}" if idx == 0 else f"&{k}={v}"
    return query_string


def ask_gpt(name, born_year, died_year):
    url = "https://api.openai.com/v1/completions"
    api_key = get_param("/the-last-show/chat-gpt-api")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "text-curie-001",
        "prompt": f"write an obituary about a fictional character named {name} who was born on {born_year} and died on {died_year}",
        "max_tokens": 400,
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['text']


def read_this(text, name):
    client = boto3.client('polly')
    response = client.synthesize_speech(
        Engine='standard',
        LanguageCode='en-US',
        OutputFormat='mp3',
        Text=text,
        TextType='text',
        VoiceId='Joanna'
    )
    filename = f"/tmp/{name}.mp3"
    with open(filename, "wb") as f:
        f.write(response["AudioStream"].read())

    mp3_url = upload_to_cloudinary(filename, resource_type="raw")
    return mp3_url


def lambda_handler(event, context):

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    
    # Parse the request body
    body = event['body']
    body = base64.b64decode(body)
    decoded = decoder.MultipartDecoder(body, event['headers']['content-type'])

    # Extract the fields from the request
    name = decoded.parts[0].text
    born_year = decoded.parts[1].text
    died_year = decoded.parts[2].text
    image = decoded.parts[3].content

    # Save the image to local disk
    filename = "/tmp/image.jpeg"
    with open(filename, "wb") as f:
        f.write(image)

    # Generate an obituary using an AI model
    obituary = ask_gpt(name, born_year, died_year)

    # Convert the obituary to an MP3 audio file using a text-to-speech API
    mp3_url = read_this(obituary, name)

    # Store the data in a DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    table.put_item(Item={
        'name': name,
        'born_year': born_year,
        'died_year': died_year,
        'obituary': obituary,
        'mp3_url': mp3_url,
    })

    # Return an HTTP response with the header
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'message': 'success'
        })
    }


