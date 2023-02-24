import os
import time
import boto3
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()

AUTOMATION_DOCUMENT_NAME = os.environ.get('AUTOMATION_DOCUMENT_NAME')
ACCOUNT_ID = os.environ.get('ACCOUNT_ID')
REGION = os.environ.get('REGION')
OUTPUT_BUCKET_NAME = os.environ.get('OUTPUT_BUCKET_NAME')

logger.info({
    'function': 'Environment Variable',
    'Value:': {
        'AUTOMATION_DOCUMENT_NAME': AUTOMATION_DOCUMENT_NAME,
        'ACCOUNT_ID': ACCOUNT_ID,
        'REGION': REGION,
        'SSM_OUTPUT_BUCKET_NAME': OUTPUT_BUCKET_NAME,
    }})

ssm = boto3.client('ssm')


def start_ssm_automation():
    response = ssm.start_automation_execution(
        DocumentName=AUTOMATION_DOCUMENT_NAME,
        Parameters={
            # 'AutomationAssumeRole': [f'arn:aws:iam::{ACCOUNT_ID}:role/AWS-SystemsManager-AutomationAdministrationRole'],
            'Commands': [
                'echo --- yum update ---',
                'sudo yum -y update',
                'echo --- curl google ---',
                'curl https://www.google.com/',
            ],
            'WorkingDirectory': ['/usr/bin'],
            'ExecutionTimeout': ['7200'],
            'OutputS3BucketName': [OUTPUT_BUCKET_NAME],
            'OutputS3KeyPrefix': ['run-shell'],
            'FunctionName': ['ssm_action_get_instance_id'],
            'TagKey': ['InstanceName'],
            'TagValue': ['handson_1'],
        },
    )

    logger.info({
        'function': 'start_ssm_automation()',
        'response:': response})

    return response['AutomationExecutionId']


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info({'function': 'lambda_handler()'})

    try:
        automation_execution_id = start_ssm_automation()

        time.sleep(3)

        response = ssm.get_automation_execution(AutomationExecutionId=automation_execution_id)
        logger.info({
            'function': 'ssm.get_automation_execution()',
            'response:': response})

        return

    except Exception as e:
        logger.error(e)
        raise e
