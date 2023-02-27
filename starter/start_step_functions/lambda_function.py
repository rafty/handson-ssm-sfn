import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger  # pip install aws-lambda-powertools
from aws_xray_sdk import core as x_ray  # pip install aws-xray-sdk
from aws_xray_sdk.core import xray_recorder  # x-ray for StepFunctions


logger = Logger()
x_ray.patch_all()

STATEMACHINE_ARN_FOR_HANDSON = os.environ.get('STATEMACHINE_ARN_FOR_HANDSON')

stepfunction = boto3.client('stepfunctions')
ssm = boto3.client('ssm')


def xray_integrate_upstream_services():
    # StepFunctionsのupstream呼び出しをX-Rayに出力
    # https://docs.aws.amazon.com/ja_jp/step-functions/latest/dg/concepts-xray-tracing.html
    if (xray_recorder.current_subsegment() is not None
            and xray_recorder.current_subsegment().sampled):
        trace_id = f'Root={xray_recorder.current_subsegment().trace_id};Sampled=1'
    else:
        trace_id = 'Root=not enabled;Sampled=0'
    return trace_id


def start_state_machine():

    # StateMachine起動時のinput data
    input_json = """{
        "tag": {
            "Key": "InstanceName", 
            "Value": "handson_1"
        }
    }"""

    try:

        now = datetime.now()
        unique = now.strftime('%Y-%m-%d-%H-%M-%S')

        trace_id = xray_integrate_upstream_services()
        resp = stepfunction.start_execution(
            name=f'handson-{unique}',  # must be unique for aws account & region
            stateMachineArn=STATEMACHINE_ARN_FOR_HANDSON,
            input=input_json,
            traceHeader=trace_id  # for x-ray
        )

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code in ['ExecutionLimitExceeded',
                          'ExecutionAlreadyExists',
                          'InvalidArn',
                          'InvalidExecutionInput',
                          'InvalidName',
                          'StateMachineDoesNotExist',
                          'StateMachineDeleting',
                          'ValidationException']:
            print(e)
            raise e
        else:
            print(e)
            raise e

    except Exception as e:
        print(e)
        raise Exception


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info({'function': 'lambda_handler()'})

    try:
        response = start_state_machine()
        return

    except Exception as e:
        logger.error(e)
        raise e
