from os import path
import os.path
import json

from aws_cdk.aws_s3_assets import Asset
from aws_cdk import Size, Duration, RemovalPolicy
from aws_cdk import (
    RemovalPolicy as RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
    aws_lambda as lb,
    aws_dynamodb as table,
    aws_apigateway as api_g,
    aws_iam as iam,
    aws_wafv2 as waf,
    aws_route53 as r53,
    aws_secretsmanager as secrets,
    App, Stack
)

from constructs import Construct

dirname = os.path.dirname(__file__)

class StaticSiteStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        BucketStaticSite=s3.Bucket(
            self,
            id="StaticWebHosting",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
                ),
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        CloudFrontStatic=cf.CloudFrontWebDistribution(
           self, "CF-StaticWebDistribution1",
           origin_configs=[cf.SourceConfiguration(
               s3_origin_source=cf.S3OriginConfig(
                   s3_bucket_source=BucketStaticSite
               ),
               behaviors=[cf.Behavior(is_default_behavior=True)]
           )
           ]
        )

       #Se deja comentariado por tema de costos
       #  domain=r53.ARecord(
       #     self,
       #     "birds.com",
       #     target=r53.RecordTarget.from_ip_addresses
       # )



app = App()
StaticSiteStack(app, "Mintic-test")

app.synth()