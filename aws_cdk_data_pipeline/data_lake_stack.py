from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
    aws_glue as glue,
    core
)


class DataLakeStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # S3
        bucket = s3.Bucket(self, "bucket")

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

        core.CfnOutput(self, "bucket_name",
                       value=bucket.bucket_name)
        self.bucket = bucket
