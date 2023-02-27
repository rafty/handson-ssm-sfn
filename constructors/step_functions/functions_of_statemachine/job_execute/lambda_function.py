import os
import time
import boto3
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()

# SSM_OUTPUT_BUCKET_NAME = os.environ.get('SSM_OUTPUT_BUCKET_NAME')
# logger.info({'SSM_OUTPUT_BUCKET_NAME': SSM_OUTPUT_BUCKET_NAME})

ssm = boto3.client('ssm')


def run_commands(instances):

    # commands = [
    #     'echo --- yum update ---',
    #     'sudo yum -y update',
    #     'echo --- curl google ---',
    #     'curl https://www.google.com/',
    # ]
    commands = [
        'sudo yum -y update',
    ]

    response = ssm.send_command(
        InstanceIds=instances,  # InstanceIds or Targets
        DocumentName='AWS-RunShellScript',
        Parameters={
            'workingDirectory': ['/usr/bin'],  # default work directory: /usr/bin
            'commands': commands,
            'executionTimeout': ['7200'],
        },
        # OutputS3BucketName=SSM_OUTPUT_BUCKET_NAME,
        OutputS3KeyPrefix='run-shell',
        CloudWatchOutputConfig={
            # 'CloudWatchLogGroupName': 'aws/ssm/AWS-RunShellScript'   # default
            # log: command_id/instance_id/aws-runShellScript/stdout or /stderr
            'CloudWatchOutputEnabled': True
        }
    )

    logger.info({'function': 'ssm.send_command', 'response:': response})

    command_id = response.get('Command', {}).get('CommandId', {})
    return command_id


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info({'function': 'lambda_handler()'})

    try:
        instance_id = event.get('instance_id')
        command_id = run_commands(instances=[instance_id])
        return {
            'command_id': command_id
        }

    except Exception as e:
        logger.error(e)
        raise e
