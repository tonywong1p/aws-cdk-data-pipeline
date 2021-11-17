from aws_cdk import (
    aws_iam as iam,
    aws_glue as glue,
    aws_ec2 as ec2,
    core
)


class IngestionStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # glue_role = iam.Role(
        #     self,
        #     'glue-role',
        #     assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
        #     managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
        #                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")]
        # )

        stack = core.Stack(self, "MyStack", env=core.Environment(account="290455323267", region="ap-east-1"))
        
        vpc = ec2.Vpc.from_lookup(stack, "VPC",
                                  vpc_id="vpc-09025e1f8ca7ccf5a"
                                  )

        glue_source_connection = glue.Connection(
            self,
            "glue_source_connection",
            type=glue.ConnectionType("JDBC"),
            properties={
                "JDBC_CONNECTION_URL": "jdbc:mysql://example.com/exampledatabase",
                "PASSWORD": "examplepassword",
                "USERNAME": "exampleusername",
            }
        )
