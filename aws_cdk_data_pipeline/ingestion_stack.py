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

        vpc = ec2.Vpc(self, "VPC",
                      cidr="10.0.0.0/21",
                      max_azs=3,
                      nat_gateways=1,
                      subnet_configuration=[
                            ec2.SubnetConfiguration(
                                subnet_type=ec2.SubnetType.PUBLIC,
                                name="Ingress",
                                cidr_mask=24
                            ),
                           ec2.SubnetConfiguration(
                                subnet_type=ec2.SubnetType.PRIVATE,
                                name="Application",
                                cidr_mask=24,
                            ),
                           ec2.SubnetConfiguration(
                                subnet_type=ec2.SubnetType.ISOLATED,
                                name="Database",
                                cidr_mask=28,
                                reserved=True
                            )
                      ]
                      )

        security_group = ec2.SecurityGroup(self, "SecurityGroup",
                                           vpc=vpc,
                                           description="Allow ssh access to ec2 instances",
                                           allow_all_outbound=True
                                           )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.all_tcp(), "allow ssh access from the world")

        host = ec2.BastionHostLinux(self, "cdk-vpc-BastionHost",
                                    vpc=vpc,
                                    subnet_selection=ec2.SubnetSelection(
                                          subnet_type=ec2.SubnetType.PUBLIC),
                                    security_group=security_group
                                    )

        glue_source_connection = glue.Connection(
            self,
            "glue_source_connection",
            connection_name="glue_source_connection",
            type=glue.ConnectionType("JDBC"),
            properties={
                "JDBC_CONNECTION_URL": "jdbc:mysql://16.162.19.80:3306/fai_test",
                "USERNAME": "admin",
                "PASSWORD": "roottoor",
            },
            subnet=vpc.private_subnets[0],
            security_groups=[security_group]
        )

        glue_destination_connection = glue.Connection(
            self,
            "glue_destination_connection",
            connection_name="glue_destination_connection",
            type=glue.ConnectionType("NETWORK"),
            subnet=vpc.private_subnets[0],
            security_groups=[security_group]
        )
