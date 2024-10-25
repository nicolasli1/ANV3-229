from os import path
import os.path
import json
import aws_cdk as cdk

from aws_cdk.aws_s3_assets import Asset
from aws_cdk import Size, Duration, RemovalPolicy
from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
    aws_lambda as lb,
    aws_dynamodb as table,
    aws_apigateway as api_g,
    aws_iam as iam,
    aws_wafv2 as waf,
    aws_secretsmanager as secrets,
    App,
    Stack,
)

from constructs import Construct

dirname = os.path.dirname(__file__)


class EC2InstanceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
        )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Instance
        instance = ec2.Instance(
            self,
            "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=amzn_linux,
            vpc=vpc,
            role=role,
        )


class WafStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket_jose = s3.Bucket(
            self,
            id="bucket_website",
            removal_policy=RemovalPolicy.DESTROY,
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
        )

        ipSet = waf.CfnIPSet(
            self,
            id="mi-primer-ipset",
            addresses=[
                "45.238.183.61/32",
                "103.219.169.165/32",
                "181.61.205.212/32",
                "186.29.5.57/32",
            ],
            ip_address_version="IPV4",
            scope="CLOUDFRONT",
            description="mi primer descripcion del ipset",
            name="Bloqueo_Ip_Maligna",
        )

        rule = waf.CfnWebACL.RuleProperty(
            name="Rule_Bloqueo_Ip_Maligna",
            priority=101,
            action=waf.CfnWebACL.RuleActionProperty(block={}),
            statement=waf.CfnWebACL.StatementProperty(
                ip_set_reference_statement=waf.CfnWebACL.IPSetReferenceStatementProperty(
                    arn=ipSet.attr_arn
                )
            ),
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="RulemetricName",
                sampled_requests_enabled=True,
            ),
        )

        GeoRule = waf.CfnWebACL.RuleProperty(
            name="Rule_Geo_Bloqueo",
            priority=707,
            action=waf.CfnWebACL.RuleActionProperty(block={}),
            statement=waf.CfnWebACL.StatementProperty(
                not_statement=waf.CfnWebACL.NotStatementProperty(
                    statement=waf.CfnWebACL.StatementProperty(
                        geo_match_statement=waf.CfnWebACL.GeoMatchStatementProperty(
                            ##
                            ## block connection if source not in the below country list
                            ##
                            country_codes=[
                                "AR",  ## Argentina
                                "BO",  ## Bolivia
                                "BR",  ## Brazil
                                "CL",  ## Chile
                                # "CO",  ## Colombia
                                "EC",  ## Ecuador
                                "FK",  ## Falkland Islands
                                "GF",  ## French Guiana
                                "GY",  ## Guiana
                                "GY",  ## Guyana
                                "PY",  ## Paraguay
                                "PE",  ## Peru
                                "SR",  ## Suriname
                                "UY",  ## Uruguay
                                "VE",  ## Venezuela
                                "NL",
                                "HK",
                                "SG",
                            ]  ## country_codes
                        )  ## geo_match_statement
                    )  ## statement
                )  ## not_statement
            ),  ## statement
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="RulemetricName",
                sampled_requests_enabled=True,
            ),
        )

        acl = waf.CfnWebACL(
            self,
            id="mi-primer-waf",
            default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
            scope="CLOUDFRONT",
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=False,
                metric_name="metricName",
                sampled_requests_enabled=False,
            ),
            name="name-mi-primer-waf",
            description="Mi primera descripcion de mi waf",
            rules=[rule, GeoRule],
        )

        DistribucionCloudJose = cf.CloudFrontWebDistribution(
            self,
            "MyDistribution",
            origin_configs=[
                cf.SourceConfiguration(
                    s3_origin_source=cf.S3OriginConfig(s3_bucket_source=bucket_jose),
                    behaviors=[cf.Behavior(is_default_behavior=True)],
                )
            ],
            web_acl_id=acl.attr_arn,
        )


class EC2AutoScaling(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
        )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Instance
        instance = ec2.Instance(
            self,
            "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=amzn_linux,
            vpc=vpc,
            role=role,
        )


class ApiDynamo(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        fn_get_items_table = lb.Function(
            self,
            id="Fn_get_items_table",
            handler="lambda_get_items_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/Fn_api_dynamo"),
            timeout=Duration.seconds(60),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        fn_post_items_table = lb.Function(
            self,
            id="Fn_get_menu_id",
            handler="lambda_post_items_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/Fn_api_dynamo"),
            timeout=Duration.seconds(60),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        global_table = table.TableV2(
            self,
            id="GlobalTable",
            table_name="My_primera_global_table_292",
            billing=table.Billing.on_demand(),
            partition_key=table.Attribute(
                name="id_pk", type=table.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        global_table.grant_full_access(fn_get_items_table)
        global_table.grant_full_access(fn_post_items_table)

        api_1 = api_g.RestApi(self, id="Class-229", rest_api_name="Api-Anv3-292")

        items_table = api_1.root.add_resource("items")

        integration_fn_get_items = api_g.LambdaIntegration(fn_get_items_table)
        integration_fn_post_items = api_g.LambdaIntegration(fn_post_items_table)

        items_table.add_method("GET", integration_fn_get_items)
        items_table.add_method("POST", integration_fn_post_items)
        items_table.add_method("PUT", integration_fn_post_items)

        # Agregar el método OPTIONS para CORS
        items_table.add_method(
            "OPTIONS",
            api_g.MockIntegration(
                passthrough_behavior=api_g.PassthroughBehavior.NEVER,
                request_templates={"application/json": '{"statusCode": 200}'},
                integration_responses=[
                    api_g.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Methods": "'GET, POST, PUT, OPTIONS'",
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type'",
                        },
                    )
                ],
            ),
            method_responses=[
                api_g.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                    },
                )
            ],
        )


app = App()
EC2InstanceStack(app, "ec2-instance")
WafStack(app, "mi-segundo-waf")
EC2AutoScaling(app, "autoscaling")
ApiDynamo(app, "api-dynamo")
app.synth()
