from aws_cdk import (
    aws_iam as iam,
    aws_lambda,
    aws_events,
    aws_events_targets,
    aws_kinesisfirehose as firehose,
    aws_kinesisfirehose_destinations as firehose_destinations,
    core
)


class ProducerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

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
        delivery_stream = firehose.DeliveryStream(self, "delivery_stream",
                                                 destinations=[destination],
                                                 role=firehose_role
                                                 )

        # Lambda
        lambda_role = iam.Role(
            self,
            'lambda-role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKinesisFirehoseFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")]
        )

        producer_lambda = aws_lambda.Function(self, "producer_function",
                                              runtime=aws_lambda.Runtime.PYTHON_3_6,
                                              handler="main.lambda_handler",
                                              code=aws_lambda.Code.asset(
                                                  "./lambda/producer"),
                                              environment={
                                                  "delivery_stream_name": delivery_stream.delivery_stream_name
                                              },
                                              role=lambda_role
                                              )

        lambda_schedule = aws_events.Schedule.rate(core.Duration.minutes(1))
        event_lambda_target = aws_events_targets.LambdaFunction(
            producer_lambda)
        lambda_cloudwatch_event = aws_events.Rule(
            self,
            "event_bridge_rule",
            description="The once per minute CloudWatch event trigger for the Lambda",
            enabled=True,
            schedule=lambda_schedule,
            targets=[event_lambda_target])
