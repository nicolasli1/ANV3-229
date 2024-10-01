import os.path
import json 

from aws_cdk.aws_s3_assets import Asset

from aws_cdk import (
    aws_dynamodb as db,
    aws_apigateway as api_gw,
    aws_lambda as lb,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_ec2 as ec2,
    aws_iam as iam,
    App, Stack,
    aws_events as events,
    aws_events_targets as targets,
    
    
)
from pathlib import Path
from constructs import Construct


dirname = os.path.dirname(__file__)


class Taller_dos (Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        
        # Deinifir la funcion lambda de administracion 
        lambda_taller_2_order_manager = lb.Function(
            self, 
            id = "eventBridge_lambda_taller2",
            runtime = lb.Runtime.PYTHON_3_12,
            handler = "lambda_function.lambda_handler",
            code= lb.Code.from_asset(str(Path(__file__).parent / 'orderManager')),
        )
        
        #Definir la función lambda de pizzahut 
        lambda_taller_2_pizzahut = lb.Function(
            self, 
            id = "eventBridge_lambda_taller2_pizzahut",
            runtime = lb.Runtime.PYTHON_3_12,
            handler = "lambda_function.lambda_handler",
            code= lb.Code.from_asset(str(Path(__file__).parent / 'pizzaHut')),
        )
        
        #Definir la función lambda de pizzahut 
        lambda_taller_2_Thailandes = lb.Function(
            self, 
            id = "eventBridge_lambda_taller2_Thailandes",
            runtime = lb.Runtime.PYTHON_3_12,
            handler = "lambda_function.lambda_handler",
            code= lb.Code.from_asset(str(Path(__file__).parent / 'Thailandes')),
        )
        
        
        #asignar permisos a lambda para poner eventos 
        lambda_taller_2_order_manager.add_to_role_policy(iam.PolicyStatement(
            actions=['events:PutEvents'],
            resources=['*'], 
        ))
        
        #Crea el bus de eventos 
        event_bus = events.EventBus(self, 'BusdeEventos',
                event_bus_name = 'eventBus_taller2'

            )
        
        # Crea una regla en EventBridge que invoque la función Lambda
        rulePizzaHut = events.Rule(self, "MyRulePizzaHut",
            event_pattern=events.EventPattern(
                source=["custom.orderManager"],
                detail_type=["order"]
            )
        )
        
        
        # Crea una regla en EventBridge que invoque la función Lambda
        ruleThailandes = events.Rule(self, "MyRuleThailandes",
            event_pattern=events.EventPattern(
                source=["custom.orderManager"],
                detail_type=["order"]
                
            )
        )
        
        rulePizzaHut.add_target(targets.LambdaFunction(lambda_taller_2_pizzahut))
        ruleThailandes.add_target(targets.LambdaFunction(lambda_taller_2_Thailandes))

        lambda_taller_2_pizzahut.add_permission("EventBridgeInvokePermission",
            principal=events.EventBus,
            action="lambda:InvokeFunction",
            source_arn=rulePizzaHut.rule_arn
        )
        
        lambda_taller_2_Thailandes.add_permission("EventBridgeInvokePermission",
            principal=events.EventBus,
            action="lambda:InvokeFunction",
            source_arn=ruleThailandes.rule_arn
        )
        
        # api gateway 
        api = api_gw.RestApi (self, 'Api_for_lambda',
                rest_api_name = 'Servicio',
                description = "Servicio de lambda funtion"                               
            )

        integracion = api_gw.LambdaIntegration(lambda_taller_2_order_manager)
        
        api.root.add_method('POST', integracion)


app = App()
Taller_dos(app, "Tallerdos")

app.synth()


from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
)

class MyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Crea la función Lambda
        my_function = _lambda.Function(self, 'MyFunction',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='index.handler',
            code=_lambda.Code.from_asset('lambda')  # Ruta a tu código de Lambda
        )

        # Crea un bus de eventos
        event_bus = events.EventBus(self, 'MyEventBus',
            event_bus_name='MyCustomEventBus'
        )

        # Crea una regla en EventBridge que invoque la función Lambda
        rule = events.Rule(self, "MyRule",
            event_pattern=events.EventPattern(
                source=["my.custom.source"],
                detail_type=["MyDetailType"]
            )
        )
        rule.add_target(targets.LambdaFunction(my_function))

        # Permiso para que EventBridge invoque la función Lambda
        my_function.add_permission("EventBridgeInvokePermission",
            principal=events.EventBus,
            action="lambda:InvokeFunction",
            source_arn=rule.rule_arn
        )

