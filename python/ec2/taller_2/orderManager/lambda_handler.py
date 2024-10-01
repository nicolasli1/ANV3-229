import boto3
import os
import json 

def lambda_handler(event, context):
    event_bridge = boto3.client('events')
    
    
    response = event_bridge.put_events(
        
        Entries = [
            {
                'Source' : 'custom.orderManager',
                'DetailType' : 'order',
                'Detail' : json.dumps(event),
                'EventBusName': 'eventBus_taller2',
            }
        ]
        
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }