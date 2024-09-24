import os.path
import aws_cdk as cdk
from aws_cdk.aws_s3_assets import Asset

from aws_cdk import (
    aws_dynamodb as table,
    aws_apigateway as api_gw,
    aws_lambda as lb,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_ec2 as ec2,
    aws_iam as iam,
    App, Stack
    
)
from pathlib import Path
from constructs import Construct


dirname = os.path.dirname(__file__)


class Taller_uno (Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #Crear la base de dynamo en us-east-1 con replica a us-west-1
        

        
        stack = Stack(app, "Stack", env=cdk.Environment(region="us-east-1"))
        
        dynamo_table_1 = table.TableV2(stack, "GlobalTable",
            partition_key=table.Attribute(name="pk", type=table.AttributeType.STRING),
            # applys to all replicas, i.e., us-west-2, us-east-1, us-east-2
            removal_policy=cdk.RemovalPolicy.DESTROY,
            replicas=[table.ReplicaTableProps(region="us-west-2"), table.ReplicaTableProps(region="us-east-2")
            ]
        )
        
        #Crear el bucket 
        #bucket = s3.Bucket(self, "Bucket_taller_1")
        
        #        dynamo_table = db.TableV2(
        #    self, 
        #    id="taller_1",
        #    table_name = "taller_1_tabla_1",
        #    billing = db.Billing.on_demand(),
        #    deletion_protection = False,
        #    partition_key = db.Attribute(name="id_curso", type = db.AttributeType.STRING),
        #    replicas=[db.ReplicaTableProps(region="us-west-2")]
        #)
        
        # Deinifir la funcion lambda 
        lambda_taller_1 = lb.Function(
            self, 
            id = "S3ToLambda_taller1",
            runtime = lb.Runtime.PYTHON_3_12,
            handler = "lambda_function.lambda_handler",
            code= lb.Code.from_asset(str(Path(__file__).parent / 'lambda')),
            environment={
                'TABLE_NAME': "GlobalTable",
                'BUCKET_NAME': bucket.bucket_name
            }
        
        )
        
        # Dar permisos sobre el S3 
        bucket.grant_read(lambda_taller_1)
        
        # Dar permisos sobre la tabla de dynamo 
        #dynamo_table.grant_write_data(lambda_taller_1)
        #dynamo_table.grant_read_data(lambda_taller_1)
    
        # añadir una notificación en el bucket que active el lambda 
        
        notification = s3_notifications.LambdaDestination(lambda_taller_1)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
   
      


app = App()
Taller_uno(app, "Talleruno")

app.synth()
