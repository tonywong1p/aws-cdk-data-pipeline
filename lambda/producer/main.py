import json
import boto3
import datetime
import uuid
import os
import random
from datetime import datetime


def lambda_handler(event, context):
    # TODO implement

    client = boto3.client('firehose')
    response = client.put_record_batch(
        DeliveryStreamName=os.environ['delivery_stream_name'],
        Records=[
            {
                'Data': json.dumps({
                    "uuid": str(uuid.uuid4()),
                    "value": random.randint(0, 1000),
                    "timestamp": str(datetime.now())
                })
            },
            {
                'Data': json.dumps({
                    "uuid": str(uuid.uuid4()),
                    "value": random.randint(0, 1000),
                    "timestamp": str(datetime.now())
                })
            }
        ]
    )

    return {
        'statusCode': 200,
        'body': response
    }
