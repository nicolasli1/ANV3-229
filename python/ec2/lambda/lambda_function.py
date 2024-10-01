import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Obtener la información del archivo subido
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Leer el archivo del bucket S3
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = s3_object['Body'].read().decode('utf-8')

    # Suponiendo que el archivo tiene formato CSV o por líneas
    for line in file_content.splitlines():
        # Procesar cada línea del archivo y escribir en DynamoDB
        data = line.split(',')  # Ejemplo simple para CSV
        table.put_item(Item={
            'id': data[0],  # Suponiendo que la primera columna es el ID
            'content': ','.join(data[1:])  # El resto de la línea
        })

    return {
        'statusCode': 200,
        'body': f'Archivo {object_key} procesado y cargado en DynamoDB.'
    }
