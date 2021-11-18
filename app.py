#!/usr/bin/env python3

from aws_cdk import core

from aws_cdk_data_pipeline.data_lake_stack import DataLakeStack
from aws_cdk_data_pipeline.producer_stack import ProducerStack
from aws_cdk_data_pipeline.ingestion_stack import IngestionStack



app = core.App()

prefix = "fai"

data_lake_stack = DataLakeStack(app, f"{prefix}-cdk-data-lake")
producer_stack = ProducerStack(app, f"{prefix}-cdk-producer", bucket=data_lake_stack.bucket)
ingestion_stack = IngestionStack(app, f"{prefix}-cdk-ingestion")

app.synth()
