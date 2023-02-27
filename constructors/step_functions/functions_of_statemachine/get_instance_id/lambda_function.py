import os
import time
import boto3
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()

ec2 = boto3.client('ec2')


class InstanceNotFoundException(Exception):
    pass


def select_ec2_instance(tag) -> list:
    resp = ec2.describe_instances(
        Filters=[{
                    'Name': f'tag:{tag.get("Key")}',
                    'Values': [tag.get('Value')]
                }])

    logger.info({
        'function': 'ec2.describe_instances()',
        'resp:': resp})

    instances = [instance['InstanceId']
                 for reservation in resp['Reservations']
                 for instance in reservation['Instances']]
    return instances


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info({
        'function': 'lambda_handler()',
        'event': event,
    })

    tag = event.get('tag')

    try:
        instances = select_ec2_instance(tag=tag)

        instance = instances[0] if len(instances) else None
        logger.info({'function': 'lambda_handler() return', 'instance:': instance})

        if instance is None:
            raise InstanceNotFoundException(f'instance: {instance}')

        return {
            'instance_id': instance
        }

    except Exception as e:
        logger.error(e)
        raise e
