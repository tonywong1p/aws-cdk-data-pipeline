from aws_cdk import (
    aws_iam as iam,
    aws_lambda,
    aws_events,
    aws_events_targets,
    core
)


class ProducerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, delivery_stream, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

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



        # Glue Job for data load
