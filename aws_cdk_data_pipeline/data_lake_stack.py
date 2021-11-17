from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_glue as glue,
    aws_kinesisfirehose as firehose,
    aws_kinesisfirehose_destinations as firehose_destinations,
    aws_lambda,
    core
)


class DataLakeStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # S3
        bucket = s3.Bucket(self, "bucket")

        # Firehose
        firehose_role = iam.Role(
            self,
            'firehose-role',
            assumed_by=iam.ServicePrincipal('firehose.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                              iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")]
        )

        destination = firehose_destinations.S3Bucket(bucket,
                                                     buffering_interval=core.Duration.minutes(
                                                         1),
                                                     buffering_size=core.Size.mebibytes(
                                                         1)
                                                     )
        delivery_steam = firehose.DeliveryStream(self, "delivery_stream",
                                                 destinations=[destination],
                                                 role=firehose_role
                                                 )

        # Glue Crawler
        glue_database_name = "glue_database"

        glue_role = iam.Role(
            self,
            'glue-role',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
                              iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")]
        )

        database = glue.Database(self, "glue_database",
                                 database_name=glue_database_name
                                 )

        crawler = glue.CfnCrawler(
            self,
            "glue_crawler",
            role=glue_role.role_arn,
            database_name=glue_database_name,
            targets={
                's3Targets': [{"path": f"s3://{bucket.bucket_name}"}]
            },
            schedule={
                "schedule_expression": "cron(0 0 * * ? *)"
            }
        )

        # # S3 Event
        # event_notification_lambda = aws_lambda.Function(self, "event_notification_function",
        #                                                 runtime=aws_lambda.Runtime.PYTHON_3_6,
        #                                                 handler="s3_event.lambda_handler",
        #                                                 code=aws_lambda.Code.asset(
        #                                                     "./lambda"),
        #                                                 environment={
        #                                                     "CodeVersionString": code_version
        #                                                 }
        #                                                 )
        # bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(event_notification_lambda))

        core.CfnOutput(self, "delivery_stream_name",
                       value=delivery_steam.delivery_stream_name)
        self.delivery_stream = delivery_steam
