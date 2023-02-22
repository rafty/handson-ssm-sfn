import os
import time
import json
import boto3
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()


dynamo = boto3.client('dynamodb')
sfn = boto3.client('stepfunctions')

callback_table_name = os.getenv('CALLBACK_TABLE_NAME')


def store_callback_token(ssm_run_command_id, instance_id, token):

    dynamo.put_item(
        TableName=callback_table_name,
        Item={
            'ssm_run_command_id': {
                'S': ssm_run_command_id
            },
            'instance_id': {
                'S': instance_id
            },
            'task_token': {
                'S': token
            },
        }
    )


# def send_to_sfn(result, token):
#     if result:
#         output = json.dumps(
#             {
#                 'result': 'SUCCESS',
#                 'reason': 'no error',
#             }
#         )
#         sfn.send_task_success(
#             taskToken=token,
#             output=output
#         )
#         print('Success Callback called')
#     else:
#         output = json.dumps(
#             {
#                 'result': 'ERROR',
#                 'reason': 'some error',
#             }
#         )
#         sfn.send_task_failure(
#             taskToken=token,
#             output=output
#         )
#         print('Success Callback called')


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):

    task_token = event.get('task_token')
    ssm_run_command_id = event.get('command_id')
    instance_id = event.get('instance_id')

    try:
        store_callback_token(ssm_run_command_id, instance_id, task_token)

        # time.sleep(5)

        # send_to_sfn(result=True, token=task_token)

        return {
            'instance_id': instance_id
        }

    except Exception as e:
        logger.error(e)
        raise e
