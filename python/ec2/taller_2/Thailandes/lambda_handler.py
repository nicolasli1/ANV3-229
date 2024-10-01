import boto3
import os
import json 

def lambda_handler(event, context):
    print('El restaurante thailandes recibió una orden')
    print(event)
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }